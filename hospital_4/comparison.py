"""Compare current H4 outputs with the immutable, hash-checked v1 snapshot."""
import csv
import hashlib
import json
from .extract import ROOT

BASELINE = ROOT / 'baselines/hospital_4_v1'


def verified_baseline():
    manifest = json.loads((BASELINE/'manifest.json').read_text())
    for name, expected in manifest['files_sha256'].items():
        if hashlib.sha256((BASELINE/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Hospital 4 baseline changed: ' + name)
    return manifest


def compare(rows, result, summary):
    manifest = verified_baseline()
    with (BASELINE/'submission.csv').open(newline='') as handle:
        old = {r['invoice_id']:r for r in csv.DictReader(handle)}
    new = {r['invoice_id']:{k:str(v) for k,v in r.items()} for r in rows}
    old_lines = {r['line_id']:r for r in map(json.loads,(BASELINE/'outputs/hospital_4/line_audit.jsonl').read_text().splitlines())}
    old_invoices = {r['invoice_record_index']:r for r in map(json.loads,(BASELINE/'outputs/hospital_4/invoice_audit.jsonl').read_text().splitlines())}
    old_summary = json.loads((BASELINE/'outputs/hospital_4/summary.json').read_text())
    line_changes=[]
    for line in result['lines']:
        before = old_lines[line['line_id']]
        fields = ('expected_payable_cents','uncertainty','violations')
        changes = {k:{'before':before[k],'after':line[k]} for k in fields if before[k]!=line[k]}
        if changes:
            line_changes.append({'line_id':line['line_id'],'invoice_id':line['invoice_id'],
                'source_clauses':line['source_clauses'],'changes':changes,
                'duplicate_resolution':line.get('duplicate_resolution'), 'exclusion':line.get('exclusion')})
    invoice_changes=[]
    for invoice in result['invoices']:
        before=old_invoices[invoice['invoice_record_index']]
        fields=('expected_total_cents','decision','requires_review','violations','uncertainty')
        changes={k:{'before':before[k],'after':invoice[k]} for k in fields if before[k]!=invoice[k]}
        if changes:invoice_changes.append({'invoice_id':invoice['invoice_id'],'invoice_record_index':invoice['invoice_record_index'],'changes':changes})
    additions=[]
    for key in sorted(new.keys()-old.keys()):
        additions.append({'row':new[key], 'evidence':[c for c in line_changes if c['invoice_id']==key]})
    changed=[]
    for key in sorted(old.keys() & new.keys()):
        fields={k:{'before':old[key][k],'after':new[key][k]} for k in old[key] if old[key][k]!=new[key][k]}
        if fields:changed.append({'invoice_id':key,'changes':fields})
    caps=[{'invoice_id':r['invoice_id'],'expected_total_cents':r['expected_total_cents'],
           'line_ids':r['amount_assumption_line_ids'],'amount_assumptions':r['amount_assumptions'],
           'confirmed_violations':r['confirmed_violations'], 'amount_dependent_violations':r['amount_dependent_violations'],
           'confidence':new[r['invoice_id']]['confidence']} for r in result['invoices']
          if r['invoice_id'] in new and r['amount_assumptions']]
    return {'baseline':'baselines/hospital_4_v1','baseline_files_verified':len(manifest['files_sha256']),
        'before':{k:old_summary[k] for k in ('submission_rows','submitted_correct','submitted_erroneous','omitted_unique_invoice_ids','unique_id_coverage')},
        'after':{k:summary[k] for k in ('submission_rows','submitted_correct','submitted_erroneous','omitted_unique_invoice_ids','unique_id_coverage')},
        'added_rows':additions,'removed_rows':[old[k] for k in sorted(old.keys()-new.keys())],
        'changed_existing_rows':changed,'changed_invoice_evidence':invoice_changes,'changed_line_evidence':line_changes,
        'submitted_cap_estimates':caps, 'remaining_omission_reasons':summary['omission_reasons_by_unique_invoice'],
        'interpretation':'Approved H4 policies; no H4 label validation. H1 evidence uses already-exposed development analysis. No confidence penalty or matching change.'}


def markdown(report):
    before,after=report['before'],report['after']
    out=['# Hospital 4 approved-policy comparison','',
        f"Submission: {before['submission_rows']} → {after['submission_rows']} rows; "
        f"correct {before['submitted_correct']} → {after['submitted_correct']}; erroneous "
        f"{before['submitted_erroneous']} → {after['submitted_erroneous']}. "
        f"Coverage {before['unique_id_coverage']:.2%} → {after['unique_id_coverage']:.2%}. "
        f"{after['omitted_unique_invoice_ids']} unique H4 IDs remain omitted.",'',
        f"Added {len(report['added_rows'])}; removed {len(report['removed_rows'])}; changed existing submission rows "
        f"{len(report['changed_existing_rows'])} (including expected cents, categories and confidence). "
        "Existing class confidence values remain 0.892297 / 0.581503.",'',
        '| Added invoice | Flag | Billed cents | Expected cents | Confidence | Evidence |',
        '|---|---:|---:|---:|---:|---|']
    for item in report['added_rows']:
        r=item['row'];e=[]
        for change in item['evidence']:
            d=change.get('duplicate_resolution')
            e.append(('Exact copy; retained '+d['retained_line_id']+' (§11.3)') if d else
                     (change['line_id']+' inclusive exclusion (§9.1); approved interpretation, not H4 validation'))
        out.append('| '+ ' | '.join([r['invoice_id'],r['flagged'],r['billed_total_cents'],r['expected_total_cents'],r['confidence'],'; '.join(e)])+' |')
    out+=['','## Cap estimates retained','',
        'Confirmed daily-cap violations are separate from assumption-dependent corrected amounts. Actual delivered quantities are not established. '
        'No new confidence penalty; the shared class score is not cap-specific calibration. Already-exposed H1 development evidence suggests below-cap quantities in four cases, with an unproven explanation.','',
        '| Invoice | Expected cents | Evidence line | Confidence |','|---|---:|---|---:|']
    for r in report['submitted_cap_estimates']:
        out.append(f"| {r['invoice_id']} | {r['expected_total_cents']} | {', '.join(r['line_ids'])} | {r['confidence']} |")
    out+=['','## Changes on still-omitted invoices','',
        'Line and invoice changes, including newly determined amounts on omitted invoices, are fully recorded in policy_change_report.json. '
        'Endpoint targets 000168, 000473 and 000658 remain blocked by other evidence. '
        'Discarded copies on 000309, 000473 and 000693 now have zero payable amounts; other unresolved lines still prevent submission.','',
        '## Remaining omissions (overlapping reasons)','', '| Reason | Unique invoices |','|---|---:|']
    out += [f'| {k} | {v} |' for k,v in report['remaining_omission_reasons'].items()]
    out+=['',report['interpretation'],'',
        'All baseline files are hash-checked on every run. Original assessment and H1 implementation/evaluation are checked by their existing manifests. '
        'Matching aliases and acceptance thresholds are unchanged; Jev remains experimental.','']
    return '\n'.join(out)
