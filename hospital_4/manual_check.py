"""Replay independently reviewed Hospital 4 calculations against saved audit output."""
import json
from datetime import date
from .extract import ROOT


def main():
    lines={r['line_id']:r for r in map(json.loads,(ROOT/'outputs/hospital_4/line_audit.jsonl').read_text().splitlines())}
    invoices={r['invoice_id']:r for r in map(json.loads,(ROOT/'outputs/hospital_4/invoice_audit.jsonl').read_text().splitlines())}
    # Constants transcribed from the contract and original records during review;
    # no call to the engine, matcher or extractor to obtain expected values.
    expected_lines={
        'H4-L00009-03':4571*34,
        'H4-L00003-06':13900*3,
        'H4-L00003-07':91600*2,
        'H4-L00017-04':97925*6,
        'H4-L00165-05':8450*8,
        'H4-L00540-02':15025*8,
        'H4-L00554-08':58925*6,
        'H4-L00583-03':1250*3,
        'H4-L00583-04':111675,
        'H4-L00583-05':74700*2,
        'H4-L00645-10':4571*17,
        'H4-L00645-11':2675*10,
        'H4-L00719-08':22050*3,
        'H4-L00018-07':40*3575, 'H4-L00693-16':0,
        'H4-L00069-13':5*162775, 'H4-L00309-14':0,
        'H4-L00084-02':2*365675, 'H4-L00473-07':0,
        'H4-L00235-06':0,
    }
    for key,expected in expected_lines.items():
        assert lines[key]['expected_payable_cents']==expected,(key,expected)
    # Review every erroneous submission's independent invoice-level delta.
    expected_invoices={17:(4939975,25000),104:(763938,0),165:(3413175,-42250),
                       235:(1538350,-20200),323:(1906175,-1000),540:(2195250,-75125),554:(3608010,-142850),
                       583:(947375,-127800),645:(2403195,23512),719:(2370128,1000)}
    for number,(billed,delta) in expected_invoices.items():
        row=invoices[f'INV-H4-{number:06d}']
        assert row['billed_total_cents']==billed
        assert row['expected_total_cents']==billed+delta
        assert row['decision']=='erroneous' and not row['requires_review']
    endpoint_pairs=[('H4-L00168-14','H4-L00168-07',10),('H4-L00235-06','H4-L00235-03',21),('H4-L00473-08','H4-L00084-14',7),('H4-L00658-19','H4-L00217-01',7)]
    for a,b,days in endpoint_pairs:
        left,right=lines[a],lines[b]
        assert left['patient_id']==right['patient_id']
        assert abs((date.fromisoformat(left['original']['service_date'])-date.fromisoformat(right['original']['service_date'])).days)==days
        assert left['exclusion']['applies'] is True and left['expected_payable_cents']==0
    for key in ('H4-L00002-15','H4-L00051-01','H4-L00053-15'):
        assert lines[key]['expected_payable_cents'] is None and lines[key]['uncertainty']
    for n,total in ((18,1493475),(69,3522700),(84,4715550)):
        row=invoices[f'INV-H4-{n:06d}']
        assert row['decision']=='correct' and row['expected_total_cents']==row['billed_total_cents']==total
    for n in (168,309,473,658,693):
        assert invoices[f'INV-H4-{n:06d}']['requires_review']
    for n in (165,540,554):
        row=invoices[f'INV-H4-{n:06d}']
        assert row['expected_amount_status']=='assumption_dependent'
        assert 'daily_cap' in row['confirmed_violations']
        assert 'invoice_amount' in row['amount_dependent_violations']
    assert invoices['INV-H4-000009']['decision']=='correct'
    assert invoices['INV-H4-000104']['violations']==['contract_number']
    print(json.dumps({'reviewed_line_calculations':len(expected_lines),'reviewed_erroneous_invoices':len(expected_invoices),
                      'reviewed_endpoint_pairs':len(endpoint_pairs),'other_review_cases':3,'added_correct_invoice_checks':3,'submitted_cap_estimates':3,
                      'status':'review expectations reproduced; not an accuracy estimate'},indent=2))

if __name__=='__main__': main()
