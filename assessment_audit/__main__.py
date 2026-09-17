"""Reproduce the final H2-5 submission and all target-hospital evidence offline."""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter,defaultdict
from decimal import Decimal
from pathlib import Path
from hospital_audit.data import read_csv
from hospital_4.__main__ import run as run_h4, preserved, pretty, jsonl, csv_text, digest
from hospital_4.submission import FIELDS, build_rows, confidence_method, defensible
from .extract import ROOT,extract
from .engine import TargetEngine


def validate(rows,headers,invoices,lines,method):
    if len({r['invoice_id'] for r in rows})!=len(rows):raise ValueError('Repeated submission ID')
    hs=defaultdict(list);inv=defaultdict(list);ls=defaultdict(list)
    for r in headers:hs[r['invoice_id']].append(r)
    for r in invoices:inv[r['invoice_id']].append(r)
    for r in lines:ls[r['invoice_id']].append(r)
    for r in rows:
        if list(r)!=FIELDS:raise ValueError('Template columns differ')
        key=r['invoice_id']
        if len(hs[key])!=1 or len(inv[key])!=1:raise ValueError('Missing or ambiguous identifier')
        h=hs[key][0];a=inv[key][0]
        if h['hospital_id'] not in ('H2','H3','H4','H5') or not re.fullmatch('INV-'+h['hospital_id']+r'-[0-9]{6}',key):raise ValueError('Hospital identity mismatch')
        if not defensible(a):raise ValueError('Indefensible prediction '+key)
        if str(r['flagged']) not in ('0','1') or int(r['flagged'])!=int(a['decision']=='erroneous'):raise ValueError('Flag mismatch')
        if r['error_category']!=('|'.join(a['violations']) if int(r['flagged']) else ''):raise ValueError('Category mismatch')
        for field in ('expected_total_cents','billed_total_cents'):
            if not str(r[field]).isdigit() or int(r[field])!=a[field]:raise ValueError('Invalid integer cents')
        if int(r['billed_total_cents'])!=int(h['invoice_total_cents']):raise ValueError('Changed source amount')
        if not ls[key] or any(type(l['expected_payable_cents']) is not int or l['uncertainty'] for l in ls[key]):raise ValueError('Unresolved submitted line')
        if sum(l['expected_payable_cents'] for l in ls[key])!=int(r['expected_total_cents']):raise ValueError('Expected line sum differs')
        score=Decimal(str(r['confidence']))
        if not score.is_finite() or not 0<=score<=1 or score!=Decimal(str(method['classes'][str(r['flagged'])]['submission_confidence'])):raise ValueError('Invalid confidence')
        if not int(r['flagged']) and int(r['expected_total_cents'])!=int(r['billed_total_cents']):raise ValueError('Correct amount mismatch')
    return {'validated_rows':len(rows),'checks':['exact six template columns','unique source identifiers','H2-5 only','original billed cents','integer expected cents and line sums','no blocking uncertainty','flags/categories','finite unchanged confidence heuristic']}


def baseline_checks():
    for version in ('hospital_4_v1','hospital_4_v2'):
        folder=ROOT/'baselines'/version;manifest=json.loads((folder/'manifest.json').read_text())
        for name,expected in manifest['files_sha256'].items():
            if digest(folder/name)!=expected:raise ValueError('Archived baseline changed: '+name)
    # V2 code/policies/outputs are frozen too; final submission and documents change.
    manifest=json.loads((ROOT/'baselines/hospital_4_v2/manifest.json').read_text())
    for name,expected in manifest['files_sha256'].items():
        if name.startswith(('hospital_4/','policies/','outputs/hospital_4/')) and digest(ROOT/name)!=expected:raise ValueError('H4 v2 changed: '+name)


def run():
    frozen=preserved();baseline_checks();files={};rows=[];all_headers=[];all_invoices=[];all_lines=[];summary={};all_omissions=[]
    h4files,h4submission,h4summary=run_h4()
    for name,value in h4files.items():
        if (ROOT/'outputs/hospital_4'/name).read_bytes()!=value.encode():raise ValueError('H4 output stale '+name)
    if h4submission.encode()!=(ROOT/'baselines/hospital_4_v2/submission.csv').read_bytes():raise ValueError('H4 submission changed')
    labels=read_csv(ROOT/'data/assessment/labels/hospital_1_labels.csv')
    h1=[json.loads(s) for s in (ROOT/'outputs/hospital_1/invoice_audit.jsonl').read_text().splitlines()]
    method=confidence_method(labels,h1)
    method['target_hospitals']=[2,3,4,5];method['validated_on_target_hospitals']=False
    method['limitations'].append('H2 date and H5 facility context assumptions and H3 amendments have no target-hospital calibration; the existing class score is retained without invented per-hospital penalties.')
    for h in (2,3,4,5):
        headers=read_csv(ROOT/f'data/assessment/invoices/hospital_{h}_invoices.csv')
        records=read_csv(ROOT/f'data/assessment/invoices/hospital_{h}_line_items.csv')
        if h==4:
            result={k:[json.loads(s) for s in h4files[n].splitlines()] for k,n in [('invoices','invoice_audit.jsonl'),('lines','line_audit.jsonl')]}
        else:
            reference=extract(h);result=TargetEngine(reference).audit(headers,records)
            files[f'outputs/hospital_{h}/rules.json']=pretty(reference)
        own,omissions=build_rows(result['invoices'],method);rows+=own
        for r in omissions:r['hospital_id']=f'H{h}'
        all_omissions+=omissions
        all_headers+=headers;all_invoices+=result['invoices'];all_lines+=result['lines']
        assert [r['original'] for r in result['lines']]==records
        assert [r['original'] for r in result['invoices']]==headers
        reasons=defaultdict(set)
        for r in omissions:
            for reason in r['reasons'].split('|'):reasons[reason].add(r['invoice_id'])
        entry={'hospital_id':f'H{h}','invoice_records':len(headers),'unique_invoice_ids':len({r['invoice_id'] for r in headers}),
               'line_records':len(records),'matched_lines':sum(bool(r['matched_service']) for r in result['lines']),
               'submitted':len(own),'correct':sum(not r['flagged'] for r in own),'erroneous':sum(r['flagged'] for r in own),
               'omitted_ids':len({r['invoice_id'] for r in omissions}),'omission_reasons':{k:len(v) for k,v in sorted(reasons.items())}}
        entry['coverage']=entry['submitted']/entry['unique_invoice_ids'];summary[f'H{h}']=entry
        if h!=4:
            for name,value in [('line_audit.jsonl',jsonl(result['lines'])),('invoice_audit.jsonl',jsonl(result['invoices'])),('summary.json',pretty(entry)),
                               ('review_log.jsonl',jsonl([r for r in result['lines'] if r['uncertainty']]))]:files[f'outputs/hospital_{h}/'+name]=value
            desc={}
            for line in result['lines']:desc.setdefault(line['original']['description'],line['match'])
            files[f'outputs/hospital_{h}/description_review.json']=pretty(dict(sorted(desc.items())))
    rows.sort(key=lambda r:r['invoice_id']);submission=csv_text(rows,FIELDS)
    template=next(csv.reader((ROOT/'data/assessment/submission_template.csv').open()))
    if template!=FIELDS:raise ValueError('Source template changed')
    validation=validate(list(csv.DictReader(io.StringIO(submission))),all_headers,all_invoices,all_lines,method)
    total={'hospitals':summary,'submitted_rows':len(rows),'target_unique_ids':len({r['invoice_id'] for r in all_headers}),
        'correct_rows':sum(not r['flagged'] for r in rows),'erroneous_rows':sum(r['flagged'] for r in rows),
        'omitted_unique_ids':len({r['invoice_id'] for r in all_omissions}),'validation':validation,
        'accuracy':'Unknown on H2-5; no target labels. H1 evaluation frozen and exposed; no fresh holdout claims.',
        'runtime_dependencies':[]}
    total['coverage']=total['submitted_rows']/total['target_unique_ids']
    files['submission.csv']=submission
    files['outputs/final/summary.json']=pretty(total)
    files['outputs/final/confidence_method.json']=pretty(method)
    files['outputs/final/omitted_invoices.csv']=csv_text(all_omissions,['invoice_id','invoice_record_index','decision','known_violation','reasons','hospital_id'])
    submitted={r['invoice_id'] for r in rows}
    files['outputs/final/submission_evidence.jsonl']=jsonl([{k:r.get(k,[]) for k in ['invoice_id','expected_amount_status','context_assumptions','amount_assumptions','confirmed_violations','amount_dependent_violations']} for r in all_invoices if r['invoice_id'] in submitted])
    paths=list((ROOT/'assessment_audit').rglob('*.py'))+[ROOT/f'policies/hospital_{h}{suffix}.json' for h in (2,3,5) for suffix in ('','_aliases')]
    manifest={'implementation_sha256':{str(p.relative_to(ROOT)):digest(p) for p in sorted(paths)},
        'frozen_hospital_1_outputs_sha256':frozen,'hospital_4_baseline_manifest_sha256':digest(ROOT/'baselines/hospital_4_v2/manifest.json'),
        'source_manifest_sha256':digest(ROOT/'data/assessment/SOURCE.json'),
        'artifacts_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in files.items()}}
    files['outputs/final/run_manifest.json']=pretty(manifest)
    return files,total


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    files,total=run()
    for name,value in files.items():
        path=ROOT/name
        if args.check:
            if not path.exists() or path.read_bytes()!=value.encode():raise ValueError('Stale output '+name)
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(value.encode())
    print(pretty(total))

if __name__=='__main__':main()
