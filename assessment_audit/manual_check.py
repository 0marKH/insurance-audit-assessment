"""Replay calculations transcribed from contract clauses and original invoice records."""
import json
from .extract import ROOT


def main():
    lines={};invoices={}
    for h in (2,3,5):
        lines.update({r['line_id']:r for r in map(json.loads,(ROOT/f'outputs/hospital_{h}/line_audit.jsonl').read_text().splitlines())})
        invoices.update({r['invoice_id']:r for r in map(json.loads,(ROOT/f'outputs/hospital_{h}/invoice_audit.jsonl').read_text().splitlines())})
    # Constants are independent of the engine/extractor's computed rates.
    expected={
        'H2-L00325-08':73625*2,'H2-L00325-09':27275*6, # reciprocal bundle clauses 14.2 /16.4
        'H2-L00607-07':13856,'H2-L00625-03':7538*12, # 18475*.75; 10050*.75 rounded first
        'H3-L00020-03':182625*2,'H3-L00461-07':208200*2, # Appendix B vs Amendment A1.2
        'H3-L00516-06':26375*7,'H3-L00516-08':26081, # weekday; 34775*.75
        'H3-L00716-02':30600*2, # no weekend rule for this service
        'H3-L00788-07':235000*2,'H3-L00788-08':12025*2, # base section 8 bundle
        'H5-L00015-10':292814*2, # 284175 *1 *.92 *1.12, round each step
        'H5-L00015-12':7510*20, # 6675*.90 ->6008; *1.25 ->7510
        'H5-L00015-13':495675, # 550750*.90; prior usage 6, no discount
        'H5-L00132-04':407650, # 431375*1.05 ->452944; *.90 ->407650
        'H5-L00298-01':2939*30, # 3750*1.10 ->4125; *.95 ->3919; *.75 ->2939
    }
    for key,total in expected.items():assert lines[key]['expected_payable_cents']==total,(key,total)
    deltas={'INV-H2-000325':-68300,'INV-H2-000607':6928,'INV-H2-000625':-30144,
            'INV-H3-000516':-44547,'INV-H3-000716':-15300,'INV-H3-000788':-87200,
            'INV-H5-000015':152267,'INV-H5-000132':-81530,'INV-H5-000298':12000}
    for key,delta in deltas.items():
        row=invoices[key];assert row['expected_total_cents']-row['billed_total_cents']==delta
        assert not row['requires_review']
    for key in ('H2-L00038-16','H2-L00183-04','H2-L00035-03','H3-L00008-07','H3-L00067-02','H3-L00044-16','H5-L00008-04','H5-L00164-02','H5-L00032-09'):
        assert lines[key]['expected_payable_cents'] is None and lines[key]['uncertainty']
    for key,threshold in [('H2-L00607-07',300),('H2-L00625-03',300),('H3-L00516-08',240),('H5-L00298-01',360)]:
        assert lines[key]['prior_billed_usage']['lower']>threshold # deepest tier invariant despite unknown upper
    print(json.dumps({'line_calculations':len(expected),'invoice_deltas':len(deltas),'uncertain_cases':9,
                      'status':'source-based manual calculations reproduced; not target-label validation'},indent=2))

if __name__=='__main__':main()
