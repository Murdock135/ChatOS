"""Reproducible passage checks and dated map diagnostics, not quality claims."""

from collections import Counter
import hashlib
import json
import math
from pathlib import Path
from typing import Callable, Optional

from .core import Store, digest, now
from .retrieval import retrieve


def evaluate(
    store: Store, cases_path: Path, limit: int = 8, backend: Optional[Callable] = None
) -> dict:
    """Score labeled passages separately from message hits and negative queries."""
    if not 1 <= limit <= 30:
        raise ValueError("Evaluation limit must be between 1 and 30")
    raw = cases_path.read_bytes()
    cases = json.loads(raw)["cases"]
    if not isinstance(cases, list) or not cases:
        raise ValueError("At least one labeled evaluation case is required")
    records = {(r["source"], r["id"]): r for r in store.records()}
    seen = set()
    results = []
    methods = set()
    for case in cases:
        identity = case["id"]
        if identity in seen:
            raise ValueError("Duplicate evaluation case ID: " + identity)
        seen.add(identity)
        target = case["expected"]
        expected_ids = set()
        if target is not None:
            record = records.get((target["source"], target["conversation_id"]))
            if not record:
                raise ValueError("Evaluation source is not captured: " + identity)
            if not isinstance(target.get("contains"), str) or not target["contains"]:
                raise ValueError("Expected wording must be non-empty")
            expected_ids = {
                m["id"]
                for m in record["messages"]
                if m["role"] == target.get("role", "user")
                and target["contains"] in m["text"]
            }
            if not expected_ids:
                raise ValueError("Expected source wording is not present: " + identity)
            if case.get("project") and case["project"] not in record.get(
                "projects", []
            ):
                raise ValueError(
                    "Expected source is outside the requested project: " + identity
                )
        packet = (backend or retrieve)(
            store, case["question"], case.get("project"), limit
        )
        methods.add(packet.get("method", "custom backend"))
        passages = packet["passages"]
        message_ranks = []
        passage_ranks = []
        scope_violations = 0
        for rank, passage in enumerate(passages, 1):
            if case.get("project") and case["project"] not in passage.get(
                "projects", []
            ):
                scope_violations += 1
            if (
                target is not None
                and passage["source"] == target["source"]
                and passage["id"] == target["conversation_id"]
                and passage.get("message_id") in expected_ids
            ):
                message_ranks.append(rank)
                if (
                    target.get("passage_contains", target["contains"])
                    in passage["excerpt"]
                ):
                    passage_ranks.append(rank)
        results.append(
            {
                "id": identity,
                "question": case["question"],
                "negative": target is None,
                "first_relevant_rank": min(passage_ranks) if passage_ranks else None,
                "message_hit": bool(message_ranks),
                "found": bool(passage_ranks),
                "returned": len(passages),
                "scope_violations": scope_violations,
                "embedding_coverage": packet.get("coverage"),
            }
        )
    positive = [r for r in results if not r["negative"]]
    negative = [r for r in results if r["negative"]]
    return {
        "checked_at": now(),
        "k": limit,
        "cases": results,
        "methods": sorted(methods),
        "cases_sha256": hashlib.sha256(raw).hexdigest(),
        "corpus_fingerprint": digest(
            sorted(
                (r["source"], r["id"], r["content_hash"])
                for r in store.db.execute(
                    "SELECT source,id,content_hash FROM conversations"
                )
            )
        ),
        "positive_cases": len(positive),
        "negative_cases": len(negative),
        "recall_at_k": sum(r["found"] for r in positive) / len(positive)
        if positive
        else None,
        "message_hit_rate": sum(r["message_hit"] for r in positive) / len(positive)
        if positive
        else None,
        "mean_reciprocal_rank": sum(
            1 / r["first_relevant_rank"] if r["found"] else 0 for r in positive
        )
        / len(positive)
        if positive
        else None,
        "negative_queries_with_results": sum(r["returned"] > 0 for r in negative),
        "scope_violations": sum(r["scope_violations"] for r in results),
        "limits": "Small hand-authored labeled diagnostic, not blinded or representative. A correct message with the wrong excerpt is not a passage hit. Negative-query results measure retrieval noise, not answer hallucination. Other relevant unlabeled sources may exist; clustering meaning needs separate human labels.",
    }


def map_diagnostics(store: Store, labels_path: Optional[Path] = None) -> dict:
    """Inspect saved geometry without rebuilding embeddings or inferring meaning."""
    path = store.state / "dense-map.json"
    if not path.exists():
        return {
            "status": "unavailable",
            "detail": "No saved pretrained map; no model was downloaded or inference started.",
        }
    data = json.loads(path.read_text())
    documents = data.get("documents", [])
    actual = {(r["source"], r["id"]) for r in store.records()}
    represented = [(d["source"], d["id"]) for d in documents]
    groups = Counter(d.get("group", "unclustered") for d in documents)
    result = {
        "status": "observed",
        "computed_at": data.get("checked_at"),
        "fresh": data.get("input_fingerprint") == digest(store.records()),
        "represented_conversations": len(set(represented) & actual),
        "current_conversations": len(actual),
        "missing_current_conversations": len(actual - set(represented)),
        "removed_conversations_still_on_map": len(set(represented) - actual),
        "duplicate_points": len(represented) - len(set(represented)),
        "nonfinite_points": sum(
            not all(
                isinstance(d.get(k), (int, float)) and math.isfinite(d[k])
                for k in ["x", "y"]
            )
            for d in documents
        ),
        "cluster_sizes": dict(groups),
        "unclustered": groups.get("unclustered", 0),
        "saved_neighbor_retention_5": data.get("neighbor_retention_5"),
        "embedding_coverage_at_computation": data.get("coverage"),
        "semantic_cluster_quality": "Unmeasured: no independently reviewed topic labels supplied.",
        "limits": "Dated geometry and coverage diagnostics. Neighbor retention measures projection distortion, not semantic relevance; project assignments are not topic ground truth. Stale maps require refresh before comparison.",
    }

    if labels_path is not None:
        labeled = json.loads(labels_path.read_text())["labels"]
        topics = {}
        for item in labeled:
            key = (item["source"], item["id"])
            if (
                key in topics
                or key not in actual
                or not isinstance(item.get("topics"), list)
                or not item["topics"]
                or not all(isinstance(topic, str) and topic for topic in item["topics"])
            ):
                raise ValueError(
                    "Topic labels require unique captured IDs and non-empty topic lists"
                )
            topics[key] = set(item["topics"])
        groups_by_id = {
            (d["source"], d["id"]): d.get("group", "unclustered") for d in documents
        }
        covered = sorted(set(topics) & set(groups_by_id))
        tp = fp = fn = tn = 0
        for i, left in enumerate(covered):
            for right in covered[i + 1 :]:
                related = bool(topics[left] & topics[right])
                together = (
                    groups_by_id[left] == groups_by_id[right]
                    and groups_by_id[left] != "unclustered"
                )
                tp += related and together
                fp += not related and together
                fn += related and not together
                tn += not related and not together
        precision = tp / (tp + fp) if tp + fp else None
        recall = tp / (tp + fn) if tp + fn else None
        result["topic_pair_evaluation"] = {
            "labels_sha256": hashlib.sha256(labels_path.read_bytes()).hexdigest(),
            "labeled_records": len(topics),
            "labeled_records_on_map": len(covered),
            "positive_pairs_found": tp,
            "false_positive_pairs": fp,
            "missed_positive_pairs": fn,
            "negative_pairs_separated": tn,
            "pair_precision": precision,
            "pair_recall": recall,
            "limits": "Only labeled pairs are scored. Topic overlap defines relevance; unclustered points are not a shared topic. Hand-authored labels and stale geometry limit conclusions.",
        }
        result["semantic_cluster_quality"] = (
            "Small supplied-label diagnostic; review label provenance and representativeness."
        )
    return result
