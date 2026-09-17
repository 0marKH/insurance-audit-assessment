"""Reproduce Hospital 4 audit evidence; the combined runner owns submission.csv."""
import argparse
import csv
import hashlib
import io
import json
from collections import Counter

from hospital_audit.data import read_csv
from hospital_audit.__main__ import fingerprints
from .extract import extract, ROOT
from .engine import Hospital4Engine
from .submission import FIELDS, build_rows, confidence_method, validate


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def pretty(value): return json.dumps(value, indent=2, ensure_ascii=False) + '\n'
def jsonl(rows): return ''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) + '\n' for r in rows)
def csv_text(rows, fields):
    buf = io.StringIO(newline='')
    writer = csv.DictWriter(buf, fieldnames=fields)
    writer.writeheader(); writer.writerows(rows)
    return buf.getvalue()


def preserved():
    source = json.loads((ROOT / 'data/assessment/SOURCE.json').read_text())
    for name, expected in source['files'].items():
        if digest(ROOT / 'data/assessment' / name) != expected: raise ValueError('Original assessment data changed: ' + name)
    freeze = json.loads((ROOT / 'outputs/hospital_1/evaluation_freeze.json').read_text())
    if fingerprints() != freeze['implementation_sha256']: raise ValueError('Frozen Hospital 1 implementation changed')
    manifest = json.loads((ROOT / 'outputs/hospital_1/run_manifest.json').read_text())
    for name, expected in manifest['artifact_sha256'].items():
        if digest(ROOT / 'outputs/hospital_1' / name) != expected: raise ValueError('Frozen Hospital 1 output changed: ' + name)
    return {p.relative_to(ROOT).as_posix():digest(p) for p in sorted((ROOT / 'outputs/hospital_1').glob('*')) if p.is_file()}


def run():
    frozen = preserved()
    data = ROOT / 'data/assessment'
    with (data / 'submission_template.csv').open(newline='') as handle:
        if next(csv.reader(handle)) != FIELDS: raise ValueError('Template changed')
    reference = extract()
    headers = read_csv(data / 'invoices/hospital_4_invoices.csv')
    records = read_csv(data / 'invoices/hospital_4_line_items.csv')
    result = Hospital4Engine(reference).audit(headers, records)
    labels = read_csv(data / 'labels/hospital_1_labels.csv')
    h1 = [json.loads(s) for s in (ROOT / 'outputs/hospital_1/invoice_audit.jsonl').read_text().splitlines()]
    method = confidence_method(labels, h1)
    rows, omissions = build_rows(result['invoices'], method)
    validation = validate(rows, headers, result['invoices'], result['lines'], method)
    submission = csv_text(rows, FIELDS)
    validate(list(csv.DictReader(io.StringIO(submission))), headers, result['invoices'], result['lines'], method)
    total_ids = len({r['invoice_id'] for r in headers})
    unique_omitted = len({r['invoice_id'] for r in omissions})
    reason_ids = {}
    for row in omissions:
        for reason in row['reasons'].split('|'):
            reason_ids.setdefault(reason, set()).add(row['invoice_id'])
    all_target_ids = {r['invoice_id'] for h in (2,3,4,5) for r in read_csv(data / f'invoices/hospital_{h}_invoices.csv')}
    summary = {'hospital':'H4', 'invoice_records':len(headers), 'unique_invoice_ids':total_ids, 'line_records':len(records),
               'matched_lines':sum(r['matched_service'] is not None for r in result['lines']),
               'invoice_decisions':dict(Counter(r['decision'] for r in result['invoices'])),
               'submission_rows':len(rows), 'submitted_correct':sum(not r['flagged'] for r in rows),
               'submitted_erroneous':sum(r['flagged'] for r in rows), 'omitted_invoice_records':len(omissions),
               'omitted_unique_invoice_ids':unique_omitted, 'unique_id_coverage':len(rows)/total_ids,
               'all_target_unique_invoice_ids':len(all_target_ids), 'all_target_coverage':len(rows)/len(all_target_ids),
               'omission_reasons_by_unique_invoice':{reason:len(ids) for reason,ids in sorted(reason_ids.items())},
               'validation':validation, 'runtime_model_dependencies':[],
               'scope':'Hospital 4 component of the Hospitals 2-5 assessment. Hospital 1 frozen; excluded from submission.',
               'h4_accuracy':'Unknown: no Hospital 4 labels. Manual review and tests are not measured accuracy.'}
    submitted_ids={r['invoice_id'] for r in rows}
    evidence=[]
    for row in result['invoices']:
        if row['invoice_id'] not in submitted_ids:continue
        flag=int(row['decision']=='erroneous')
        evidence.append({k:row[k] for k in ('invoice_id','expected_total_cents','expected_amount_status',
                         'confirmed_violations','amount_dependent_violations','amount_assumptions','amount_assumption_line_ids')})
        evidence[-1].update(confidence=method['classes'][str(flag)]['submission_confidence'],
            confidence_basis='Unchanged H1 class-level joint-outcome heuristic; unvalidated on H4; not cap-specific calibration.',
            approval_prompt=reference['policy']['approval_prompt'])
    summary['submitted_amount_status_counts']=dict(Counter(r['expected_amount_status'] for r in evidence))
    summary['submitted_cap_estimate_ids']=[r['invoice_id'] for r in evidence if r['amount_assumptions']]
    files = {'rules.json':pretty(reference), 'line_audit.jsonl':jsonl(result['lines']),
             'invoice_audit.jsonl':jsonl(result['invoices']), 'summary.json':pretty(summary),
             'confidence_method.json':pretty(method),
             'submission_evidence.jsonl':jsonl(evidence),
             'omitted_invoices.csv':csv_text(omissions, ['invoice_id','invoice_record_index','decision','known_violation','reasons']),
             'review_log.jsonl':jsonl([r for r in result['lines'] if r['uncertainty'] or r['expected_payable_cents'] is None or r['amount_assumptions']])}
    paths = [p for p in (ROOT / 'hospital_4').rglob('*.py')] + list((ROOT / 'policies').glob('hospital_4*.json'))
    input_paths = [data / 'invoices/hospital_4_invoices.csv', data / 'invoices/hospital_4_line_items.csv',
                   data / 'labels/hospital_1_labels.csv', data / reference['policy']['document'].removeprefix('data/assessment/'),
                   data / 'submission_template.csv']
    manifest = {'implementation_sha256':{p.relative_to(ROOT).as_posix():digest(p) for p in sorted(paths)},
                'inputs_sha256':{p.relative_to(ROOT).as_posix():digest(p) for p in input_paths},
                'preserved_hospital_1_outputs_sha256':frozen,
                'artifacts_sha256':{name:hashlib.sha256(content.encode()).hexdigest() for name,content in files.items()},
                'submission_sha256':hashlib.sha256(submission.encode()).hexdigest(),
                'labels_used_directly_at_runtime_for_h4_matching_or_pricing':False,
                'h1_labels_read_at_runtime_only_for_confidence':True,
                'h1_exposed_label_analysis_informed_approved_h4_interpretations':True,
                'interpretation_approval_prompt':reference['policy']['approval_prompt']}
    files['run_manifest.json'] = pretty(manifest)
    return files, submission, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Recompute and byte-compare without writing')
    args = parser.parse_args()
    try:
        files, submission, summary = run()
        targets = {ROOT / 'outputs/hospital_4' / n:v for n,v in files.items()}
        if args.check:
            stale = [p.relative_to(ROOT).as_posix() for p,v in targets.items() if not p.exists() or p.read_bytes() != v.encode()]
            if stale: raise ValueError('Stale/missing output: ' + ', '.join(stale))
        else:
            for path, value in targets.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(value.encode())
        print(pretty(summary))
    except (ValueError, KeyError) as error:
        parser.error(str(error))


if __name__ == '__main__': main()
