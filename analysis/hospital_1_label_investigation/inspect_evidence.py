"""Read-only development analysis of already-exposed Hospital 1 labels."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent

def read_csv(name):
    with (ROOT/name).open(newline='') as f:return list(csv.DictReader(f))
def read_jsonl(name):return [json.loads(s) for s in (ROOT/name).read_text().splitlines()]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def load(h=1):
    headers=read_csv(f'data/assessment/invoices/hospital_{h}_invoices.csv')
    lines=read_csv(f'data/assessment/invoices/hospital_{h}_line_items.csv')
    audit=read_jsonl(f'outputs/hospital_{h}/line_audit.jsonl')
    invoices=read_jsonl(f'outputs/hospital_{h}/invoice_audit.jsonl')
    rules=json.loads((ROOT/('outputs/hospital_1.rules.json' if h==1 else 'outputs/hospital_4/rules.json')).read_text())
    return headers,lines,audit,invoices,rules

if __name__=='__main__':
    headers,lines,audit,invoices,rules=load()
    labels=read_csv('data/assessment/labels/hospital_1_labels.csv')
    selected={r['invoice_id']:r for r in labels if any(c in r['error_categories'] for c in ('wrong_unit_basis','cross_invoice_duplicate','volume_discount')) or r['invoice_id']=='INV-H1-000015'}
    evidence={key:{'label':label,'headers':[r for r in headers if r['invoice_id']==key],
                   'lines':[r for r in audit if r['invoice_id']==key],
                   'invoice_audit':[r for r in invoices if r['invoice_id']==key]} for key,label in selected.items()}
    (OUT/'selected_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    paths=[p for directory in ('hospital_audit','contract_extractor','hospital_4','policies','outputs/hospital_1','outputs/hospital_4','data/assessment') for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in str(p)]+[ROOT/'submission.csv',ROOT/'outputs/hospital_1.rules.json']
    snapshot={str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)}
    frozen=OUT/'baseline_sha256.json'
    if frozen.exists():
        if json.loads(frozen.read_text()) != snapshot: raise ValueError('Baseline changed during investigation')
    else: frozen.write_text(json.dumps(snapshot,indent=2)+'\n')
    print('Saved source evidence for',len(evidence),'selected invoices. No engine/policy/output files changed.')
