"""Evidence and conditional blocker inventory, without executing changed policies."""
import csv
import json
from collections import defaultdict
from datetime import date
from fractions import Fraction
from inspect_evidence import ROOT, OUT, load, read_csv, read_jsonl, sha

# This analysis uses only source records, saved reference rules, and saved audits.
# Money hypotheses below are case-specific reconciliation checks, not engine rules.

def money(value):return int(value)
def q(value):return Fraction(str(value))
def hu(v):return (v.numerator*2//v.denominator+1)//2

def main():
    hs,source,lines,invoices,reference=load()
    labels={r['invoice_id']:r for r in read_csv('data/assessment/labels/hospital_1_labels.csv')}
    byline={r['line_id']:r for r in lines};bykey={r['record_key']:r for r in lines}
    nested=read_jsonl('data/assessment/invoices/hospital_1_invoices.jsonl')
    owner={l['line_id']:h for h in nested for l in h['line_items']}
    boundaries=[]
    for excluded,trigger,days in [('H1-L00847-17','H1-L00830-09',7),('H1-L00211-08','H1-L00211-04',10)]:
        a,b=byline[excluded],byline[trigger];h=owner[excluded]
        gap=abs((date.fromisoformat(a['original']['service_date'])-date.fromisoformat(b['original']['service_date'])).days)
        delta=h['invoice_total_cents']-int(labels[a['invoice_id']]['expected_total_cents'])
        assert gap==days and owner[trigger]['patient_id']==h['patient_id'] and delta==money(a['original']['line_total_cents'])
        boundaries.append({'excluded_line':excluded,'trigger_line':trigger,'patient':h['patient_id'],'dates':[a['original']['service_date'],b['original']['service_date']],
                           'days':gap,'billed':h['invoice_total_cents'],'label_expected':int(labels[a['invoice_id']]['expected_total_cents']),'reduction':delta,'across_invoices':a['invoice_id']!=b['invoice_id']})
    unit_specs=[(211,'H1-L00211-05','per_item',96600,'isolated_with_other_known_correction'),
                (257,'H1-L00257-11','per_day',7500,'isolated_with_other_known_correction'),
                (369,'H1-L00369-12','per_item',0,'unknown_service_and_ambiguous_matches_confounded'),
                (457,'H1-L00483-02','per_item',0,'nested_record_resolves_line_owner_but_invoice_id_reused'),
                (552,'H1-L00552-15','per_night',-7500,'malformed_date_confounded'),
                (635,'H1-L00635-01','per_procedure',-38178,'isolated_with_other_known_correction'),
                (657,'H1-L00657-02','per_procedure',0,'both_candidate_units_agree_but_service_unresolved'),
                (677,'H1-L00677-12','per_day',704175,'isolated_with_other_known_correction'),
                (703,'H1-L00703-01','per_visit',-7500,'isolated_with_other_known_correction'),
                (717,'H1-L00717-10','per_unit_dispensed',0,'isolated_only_labelled_violation'),
                (847,'H1-L00847-02','per_item',27600,'unit_blocks_bundle_partner_but_other_delta_is_exclusion')]
    units=[]
    for num,lid,contract_unit,other_reduction,strength in unit_specs:
        invoice=f'INV-H1-{num:06d}';l=byline[lid];r=l['original'];h=owner[lid];label=labels[invoice]
        assert 'wrong_unit_basis' in label['error_categories'] and h['invoice_id']==invoice
        delta=h['invoice_total_cents']-int(label['expected_total_cents'])
        assert delta==other_reduction
        assert q(r['quantity'])*money(r['unit_price_cents'])==money(r['line_total_cents'])
        units.append({'invoice_id':invoice,'line_id':lid,'service':l['matched_service'],'candidate_services':l['match']['candidates'],
                      'billed_unit':r['unit_basis_as_billed'],'contract_unit':contract_unit,'original_quantity':r['quantity'],
                      'line_amount':money(r['line_total_cents']),'billed_rate':money(r['unit_price_cents']),'saved_adjusted_rate':l['expected_unit_rate_cents'],
                      'record_billed_total':h['invoice_total_cents'],'label_expected':int(label['expected_total_cents']),
                      'label_reduction':delta,'identified_other_reduction':other_reduction,'residual_reduction':delta-other_reduction,'evidence_class':strength})
    assert len(units)==sum('wrong_unit_basis' in r['error_categories'] for r in labels.values())==11
    duplicates=[]
    for num,repeat,prior,other in [(231,'H1-L00231-07','H1-L00079-05',0),(675,'H1-L00675-07','H1-L00450-04',70070),
                                  (677,'H1-L00677-18','H1-L00346-03',616875),(852,'H1-L00852-18','H1-L00246-02',0)]:
        a,b=byline[repeat],byline[prior];h=owner[repeat];label=labels[a['invoice_id']]
        same_fields=['description','service_date','quantity','unit_basis_as_billed','unit_price_cents','line_total_cents']
        assert all(a['original'][k]==b['original'][k] for k in same_fields)
        assert h['patient_id']==owner[prior]['patient_id'] and a['matched_service']==b['matched_service']
        assert repeat>prior and q(a['original']['quantity'])==1
        charge=money(a['original']['line_total_cents']);delta=h['invoice_total_cents']-int(label['expected_total_cents'])
        assert delta==charge+other and labels[b['invoice_id']]['is_erroneous']=='0'
        duplicates.append({'invoice_id':a['invoice_id'],'repeat_line':repeat,'prior_line':prior,'patient':h['patient_id'],'service_date':a['original']['service_date'],
                           'quantity':1,'charge':charge,'label_reduction':delta,'other_reduction':other,'original_invoice_label':'correct',
                           'rates_both_compliant':a['expected_unit_rate_cents']==b['expected_unit_rate_cents']==money(a['original']['unit_price_cents']),
                           'limitation':'Identical one-unit copies only; no rate/quantity conflict, and lexical order agrees with invoice chronology.'})
    assert len(duplicates)==sum('cross_invoice_duplicate' in r['error_categories'] for r in labels.values())==4
    # Candidate corrected rates are explicit contract calculations; for three cases
    # saved history is not bounded above, so eligibility is only label-consistent.
    volume_specs=[(4,'H1-L00004-01',10100,340743,'verified_no_prior_usage'),
                  (102,'H1-L00102-07',151975,103331,'base_rate_reconciles_label_but_prior_upper_unknown'),
                  (186,'H1-L00186-01',13450,25000,'base_rate_reconciles_label_but_prior_upper_unknown'),
                  (219,'H1-L00219-06',13450,0,'base_rate_reconciles_label_but_prior_upper_unknown'),
                  (304,'H1-L00304-08',hu(Fraction(25250*70,100)),32382,'deepest_tier_certain_from_lower_bound'),
                  (458,'H1-L00458-03',hu(Fraction(112825*90,100)),0,'deepest_tier_certain_from_lower_bound'),
                  (811,'H1-L00811-02',hu(Fraction(169825*75,100)),0,'deepest_tier_certain_from_lower_bound'),
                  (820,'H1-L00820-12',hu(Fraction(151975*80,100)),1000,'deepest_tier_certain_from_lower_bound')]
    volumes=[]
    for num,lid,rate,other,status in volume_specs:
        l=byline[lid];r=l['original'];h=owner[lid];label=labels[l['invoice_id']]
        amount=int(q(r['quantity'])*rate);change=money(r['line_total_cents'])-amount
        assert h['invoice_total_cents']-change-other==int(label['expected_total_cents'])
        own_known_prior=sum(q(x['original']['quantity']) for x in lines if x['matched_service']==l['matched_service']
            and owner[x['line_id']]['patient_id']==h['patient_id'] and x['original']['unit_basis_as_billed']==r['unit_basis_as_billed']
            and '2024-01-01'<=x['original']['service_date']<='2025-12-31'
            and (x['original']['service_date'],x['line_id'])<(r['service_date'],lid))
        volumes.append({'invoice_id':l['invoice_id'],'line_id':lid,'service':l['matched_service'],'quantity':r['quantity'],
                        'billed_rate':money(r['unit_price_cents']),'candidate_contract_rate':rate,'candidate_line_amount':amount,
                        'volume_reduction':change,'other_reduction':other,'label_expected':int(label['expected_total_cents']),
                        'saved_prior_bounds':l['prior_billed_usage'],'known_same_patient_prior':int(own_known_prior),'eligibility_status':status})
    assert len(volumes)==sum('volume_discount' in r['error_categories'] for r in labels.values())==8
    caps=[]
    for num,lid,cap,other in [(15,'H1-L00015-11',4,0),(49,'H1-L00049-04',12,108750),(227,'H1-L00227-11',12,100000),(725,'H1-L00725-10',8,0)]:
        l=byline[lid];r=l['original'];h=owner[lid];label=labels[l['invoice_id']]
        reduction=h['invoice_total_cents']-int(label['expected_total_cents'])-other
        implied=q(r['quantity'])-Fraction(reduction,money(r['unit_price_cents']))
        group=[x for j in nested if j['patient_id']==h['patient_id'] for x in j['line_items'] if x['service_date']==r['service_date']]
        caps.append({'invoice_id':l['invoice_id'],'line_id':lid,'patient':h['patient_id'],'service_date':r['service_date'],
                     'quantity':r['quantity'],'rate':money(r['unit_price_cents']),'cap':cap,'label_reduction':h['invoice_total_cents']-int(label['expected_total_cents']),
                     'other_reduction':other,'cap_attributed_reduction':reduction,'label_implied_quantity_if_other_lines_unchanged':int(implied),
                     'same_patient_day_line_ids':[x['line_id'] for x in group],
                     'other_same_service_day_candidates':[x['line_id'] for x in group if x['line_id']!=lid and l['matched_service'] in byline[x['line_id']]['match']['candidates']],
                     'literal_cap_expected_invoice':h['invoice_total_cents']-other-(int(q(r['quantity']))-cap)*money(r['unit_price_cents']),
                     'label_expected':int(label['expected_total_cents'])})
    h4_h,h4_s,h4_l,h4_i,h4_r=load(4)
    h4bykey={r['record_key']:r for r in h4_l};h4byinv=defaultdict(list)
    for r in h4_l:h4byinv[r['invoice_id']].append(r)
    h4inv={r['invoice_id']:r for r in h4_i}
    h4ex={r['applies_to']['services'][0]:r for r in h4_r['rules'] if r['kind']=='exclusion_window'}
    endpoint=[]
    for r in h4_l:
        if r.get('exclusion',{}).get('applies','not-null') is not None:continue
        rule=h4ex[r['matched_service']]
        for k in r['exclusion']['related_record_keys']:
            trigger=h4bykey[k]
            if trigger['matched_service']!=rule['condition']['trigger_service'] or not r['patient_id'] or r['patient_id']!=trigger['patient_id']:continue
            try:gap=abs((date.fromisoformat(r['original']['service_date'])-date.fromisoformat(trigger['original']['service_date'])).days)
            except ValueError:continue
            if gap!=rule['condition']['window_days'] or trigger['uncertainty']:continue
            others=[x for x in h4byinv[r['invoice_id']] if x is not r]
            blockers=[x['line_id'] for x in others if x['uncertainty'] or x['expected_payable_cents'] is None]
            endpoint.append({'invoice_id':r['invoice_id'],'line_id':r['line_id'],'trigger':trigger['line_id'],'days':gap,
                             'billed_line':money(r['original']['line_total_cents']),'other_blockers':blockers,
                             'conditional_total_if_inclusive':sum(x['expected_payable_cents'] for x in others) if not blockers else None})
    dup_groups=defaultdict(list)
    for r in h4_l:
        if 'hospital_4_duplicate_correction_unspecified' in r['uncertainty']:
            dup_groups[tuple(sorted(r['delivered_group_record_keys']))].append(r)
    duplicate_opportunities=[]
    for group in dup_groups.values():
        group.sort(key=lambda r:r['line_id']);first=group[0]
        assert all(r['original'][k]==first['original'][k] for r in group for k in ['service_date','description','quantity','unit_basis_as_billed','unit_price_cents','line_total_cents'])
        assert all(r['expected_unit_rate_cents']==money(r['original']['unit_price_cents']) for r in group)
        for n,r in enumerate(group):
            others=[x for x in h4byinv[r['invoice_id']] if x is not r]
            blockers=[x['line_id'] for x in others if x['uncertainty'] or x['expected_payable_cents'] is None]
            duplicate_opportunities.append({'invoice_id':r['invoice_id'],'line_id':r['line_id'],'would_retain':n==0,'group':[x['line_id'] for x in group],
                    'other_blockers':blockers,'conditional_total_if_exact_copy_retention':sum(x['expected_payable_cents'] for x in others)+(money(r['original']['line_total_cents']) if n==0 else 0) if not blockers else None})
    unit_opportunities=[]
    for r in h4_l:
        if 'unit_basis' not in r['violations']:continue
        other=[x for x in h4byinv[r['invoice_id']] if x is not r and (x['uncertainty'] or x['expected_payable_cents'] is None)]
        unit_opportunities.append({'invoice_id':r['invoice_id'],'line_id':r['line_id'],'quantity':r['original']['quantity'],
                                   'saved_rate':r['expected_unit_rate_cents'],'other_blockers':[(x['line_id'],x['uncertainty']) for x in other],
                                   'direct_blocker_only':not other,
                                   'only_known_dependent_bundle':bool(other) and all(x['uncertainty']==['bundle_eligibility_uncertain'] for x in other)})
    findings={'analysis_status':'Development analysis of exposed labels; no interpretation adopted, no engine replay under changed policy.',
              'boundaries':boundaries,'wrong_units':units,'duplicates':duplicates,'volumes':volumes,'caps':caps,
              'h4_conditional_opportunities':{'endpoint_cases':endpoint,'duplicate_cases':duplicate_opportunities,'unit_cases':unit_opportunities,
                 'scope':'Static blocker inventory and explicit case arithmetic, not a modified-engine evaluation or coverage promise.'}}
    (OUT/'findings.json').write_text(json.dumps(findings,indent=2)+'\n')
    frozen=json.loads((OUT/'baseline_sha256.json').read_text())
    changed=[p for p,v in frozen.items() if sha(ROOT/p)!=v]
    assert not changed,changed
    print('Verified 2 endpoint examples, all 11 wrong-unit invoices, all 4 duplicates, all 8 volume cases and 4 cap labels.')
    print('H4 hypothetical otherwise-clear invoices: endpoint',sum(not x['other_blockers'] for x in endpoint),'duplicate',sum(not x['other_blockers'] for x in duplicate_opportunities),'unit',sum(x['direct_blocker_only'] or x['only_known_dependent_bundle'] for x in unit_opportunities))
    print('All baseline hashes unchanged.')

if __name__=='__main__':main()
