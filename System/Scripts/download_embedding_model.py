"""Download pinned public model data only; never upload archive content or use a saved token."""
from pathlib import Path
import hashlib
import json
import os

ROOT=Path(__file__).resolve().parents[2]
MODEL='Qwen/Qwen3-Embedding-0.6B'
REVISION='d67280f96c9df4c40d7c6986f4a51c54ac950c0f'
WEIGHTS_SHA256='0437e45c94563b09e13cb7a64478fc406947a93cb34a7e05870fc8dcd48e23fd'


def main():
    directory=ROOT/'System/Models/qwen3-embedding-0.6b'
    os.environ['HF_HOME']=str(ROOT/'System/Models/hf-cache')
    os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
    os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN']='1'
    os.environ['DO_NOT_TRACK']='1'
    for name in ['HF_TOKEN','HUGGING_FACE_HUB_TOKEN','HUGGINGFACEHUB_API_TOKEN']:os.environ.pop(name,None)
    from huggingface_hub import snapshot_download
    snapshot_download(MODEL,revision=REVISION,local_dir=str(directory),token=False,
                      allow_patterns=['config.json','config_sentence_transformers.json','modules.json',
                                      'sentence_bert_config.json','1_Pooling/config.json','tokenizer.json',
                                      'tokenizer_config.json','vocab.json','merges.txt','model.safetensors'])
    config=json.loads((directory/'config.json').read_text())
    modules=json.loads((directory/'modules.json').read_text())
    allowed={'sentence_transformers.models.Transformer','sentence_transformers.models.Pooling','sentence_transformers.models.Normalize'}
    if config.get('auto_map') or config.get('model_type')!='qwen3' or any(m['type'] not in allowed for m in modules):
        raise ValueError('Unexpected custom model code/module configuration; model not enabled')
    weights=directory/'model.safetensors'
    fingerprint=hashlib.sha256()
    with weights.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):fingerprint.update(block)
    if fingerprint.hexdigest()!=WEIGHTS_SHA256:raise ValueError('Pinned model weight hash mismatch')
    report={'model':MODEL,'revision':REVISION,'directory':str(directory),'weights_sha256':WEIGHTS_SHA256,
            'license':'Apache-2.0 according to official model card',
            'source':'https://huggingface.co/Qwen/Qwen3-Embedding-0.6B',
            'remote_code':False,'token':False,'note':'Downloaded model data; not yet an evaluated/enabled search backend.'}
    directory.mkdir(parents=True,exist_ok=True)
    (directory/'download-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
