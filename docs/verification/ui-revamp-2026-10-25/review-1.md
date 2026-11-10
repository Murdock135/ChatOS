# Independent review 1

Source: Codex chat `01a1765b-8af3-7733-933c-c31806ae3ee2`. Screenshot-only assessment; preserved reviewer response.

ChatGrep has a coherent visual foundation, but these narrow layouts devote too much space to controls and supporting information before users reach their conversations. The next revision should focus on reading space, map visibility, and clearer navigation.

I inspected all seven PNGs. This is a screenshot-only review: I did not consult project files, previous chats, or memory. Higher-priority operating instructions remain applicable, so I cannot claim complete procedural isolation.

Priorities below distinguish visible problems from behavior that needs testing. **P1** means address in the next revision; **P2** means a meaningful usability improvement.

| Priority | Finding | Screenshot evidence | Recommended change |
|---|---|---|---|
| **P1** | **The notes panel competes directly with conversation reading.** The expanded “Notes & projects” area occupies roughly the bottom third of the reader, while only the beginning of the assistant message is visible. | **02-reader-notes** | Default to a compact notes disclosure at this width. Opening notes should preserve an obvious way to return to uninterrupted reading. Test whether the panel covers content or simply reduces the reading viewport. |
| **P1** | **The map receives too little initial screen space.** Title, explanatory copy, concept search, method selection, and two rows of map controls consume most of the visible height. Only a small slice of the map and a few nodes appear at the bottom. | **03-map** | Prioritize a useful map viewport. Consolidate secondary controls into one compact toolbar and move display preferences into “View options.” Verify the initial fit with realistic graph sizes. |
| **P2** | **The conversation list starts unusually far down the screen.** Search, mode selection, the assistant link, library count, page size, and disabled pagination all precede the first result. Only one result heading is visible. | **01-search** | Move pagination beneath results. Combine the count and page-size control into a compact row, and reduce spacing before the list. Preserve the prominent search field. |
| **P2** | **Primary navigation depends on interpreting unlabeled icons.** Several destinations use abstract symbols; the sliders and gear are especially difficult to distinguish by purpose. | **01, 03–07** | Provide visible destination names through an expandable rail or another compact navigation treatment. Tooltips can supplement this, but should not carry all the meaning. |
| **P2** | **Operational language exposes internal terminology.** `export_snapshot`, lowercase source identifiers, “semantic map,” and “reusable context” require interpretation. | **04-map-detail, 05-setup, 06-health** | Use plain labels such as “Imported snapshot,” explain unfamiliar concepts briefly, and put technical identifiers in diagnostics. |
| **P2** | **Sync looks partly like status and partly like an action.** The persistent green-dot “Sync” and Settings’ green-dot “Sync now” share a status-like treatment. Setup separately refers to “Sync workspace.” | **01, 03, 05, 07** | Use one action label, with a recognizable button treatment. Show success, activity, and last-sync time as separate status information. |
| **P2** | **Small, muted supporting text risks becoming difficult to read.** Navigation icons, metadata, table headings, footer text, and pale control boundaries are visually subdued. | **All; particularly 02, 06, 07** | Measure contrast and check text at normal size and increased zoom. Increase the legibility of information needed to judge capture completeness and source freshness. |

The map detail view has a useful progression: a recognizable title, a short excerpt, and a prominent **“Read conversation”** action (**04**). However, “Filters & sort” is visually separated below the detail card, and maintenance information follows immediately afterward. The relationship between exploring results, inspecting a selection, and maintaining the map could be clearer. Group exploration controls together and give map maintenance a quieter, distinct location.

Setup also needs a clearer completion path (**05**). The screenshot explicitly explains that saving a source choice does not scan it, which is helpful, but the visible action stops at **“Save source choice.”** Show an unmistakable saved state and the next action after saving. The screenshot alone cannot establish whether that feedback already exists.

**Strengths to retain**

- The restrained palette, consistent spacing, and warm accent create a recognizable product.
- The search field has clear prominence, and Keyword versus Smart search is explicit.
- Capture limitations and unknown metadata are disclosed instead of concealed (**02**).
- Source coverage and last-sync information support trust (**06–07**).
- “Similarity is a suggestion, not a decision” gives the map appropriate framing (**03**).
- The map detail’s reading action is clear and easy to identify (**04**).

**Focused next revision:** make the reader and map usable within the available height, move search pagination below results, label navigation, and standardize sync terminology. Those changes would improve the core workflows more than additional visual decoration.

Live testing is still needed for keyboard navigation, focus visibility, accessible names, notes-panel scrolling, graph selection and panning, loading/error feedback, and layout at other widths. These screenshots do not establish interaction failures, search quality, or data loss; I have not treated the fixture-count differences as defects.
