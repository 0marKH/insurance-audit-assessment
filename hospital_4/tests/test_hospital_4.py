import copy
import json
import unittest
from fractions import Fraction

from hospital_audit.engine import UNITS, half_up
from hospital_4.extract import extract, ROOT
from hospital_4.engine import Hospital4Engine
from hospital_4.submission import confidence_method, build_rows, validate
from hospital_4.__main__ import preserved

PREMIUM = 'Advanced Vascular Endoscopic Procedure'
CAP = 'Ambulatory Cardiac Ward Bed Occupancy'
A = 'Ambulatory Obstetric Case Conference'
B = 'Focused Vascular Infusion Therapy'
EXCLUDED = 'Ambulatory Haematology Transfusion Service'
TRIGGER = 'Postoperative Geriatric Imaging Interpretation'
VOLUME = 'Ambulatory Musculoskeletal Ventilation Support'
DUAL = 'Intermittent Urologic Telemetry Monitoring'


class Hospital4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = extract()
        cls.catalogue = {r['action']['service_name']: r for r in cls.reference['rules'] if r['kind']=='service_catalogue'}

    def header(self, n=1, patient='P1', **changes):
        return dict(invoice_id=f'INV-H4-{n:06d}', hospital_id='H4', contract_number='INS-H4-2024-2049',
                    invoice_date='2024-12-31', patient_id=patient, invoice_total_cents='0', **changes)

    def line(self, service, qty=1, n=1, date='2024-01-01', price=None, **changes):
        action = self.catalogue[service]['action']
        rate = price if price is not None else action['base_rate_cents']
        row = dict(line_id=f'H4-L{n:05d}-01', invoice_id=f'INV-H4-{n:06d}', line_no='1', service_date=date,
                   description=service, quantity=str(qty), unit_basis_as_billed=UNITS.get(action['unit_basis'], 'per_hour'),
                   unit_price_cents=str(rate), line_total_cents=str(half_up(Fraction(str(qty))*rate)))
        row.update(changes)
        return row

    def audit(self, lines, headers=None):
        headers = copy.deepcopy(headers or [self.header(i+1) for i in range(len(lines))])
        for h in headers:
            h['invoice_total_cents'] = str(sum(int(r['line_total_cents']) for r in lines if r['invoice_id']==h['invoice_id']))
        return Hospital4Engine(self.reference).audit(headers, lines), headers

    def test_reviewed_extraction_counts_and_source(self):
        self.assertEqual(self.reference['coverage'], {'reviewed_numbered_clauses':31, 'table_rows':160})
        self.assertEqual(self.reference['counts']['service_catalogue'], 98)
        self.assertNotIn('weekend_uplift', self.reference['counts'])
        for rule in self.reference['rules']:
            self.assertTrue(rule['source'])
            self.assertTrue({'applies_to','condition','action','scope','order','source','uncertainty'} <= rule.keys())
        self.assertEqual(self.catalogue[DUAL]['uncertainty']['status'], 'unresolved')

    def test_premium_boundary_all_units_and_fractional_cent_rounding(self):
        # 25% of a base ending in 25 cents creates a fractional cent; round the rate first.
        rate = self.catalogue[PREMIUM]['action']['base_rate_cents']
        for qty in (10,11):
            result,_ = self.audit([self.line(PREMIUM,qty)])
            line=result['lines'][0]
            adjusted=half_up(Fraction(rate*125,100)) if qty>10 else rate
            self.assertEqual(line['expected_payable_cents'], adjusted*qty)
            self.assertEqual(line['premium_eligible'], qty>10)

    def test_cross_invoice_bundle_and_wrong_contract_identity(self):
        hs=[self.header(), self.header(2)];hs[1]['contract_number']='WRONG'
        result,_=self.audit([self.line(A), self.line(B,n=2)],hs)
        self.assertEqual([r['expected_payable_cents'] for r in result['lines']], [11875,4900])
        self.assertIn('contract_number',result['invoices'][1]['violations'])
        self.assertTrue(all(r['original']['hospital_id']=='H4' for r in result['invoices']))

    def test_inclusive_exclusion_both_directions_and_directional_target(self):
        for date, expected in [('2024-01-02',0),('2024-01-14',0),('2024-01-01',0),('2024-01-15',0),('2024-01-16','base')]:
            result,_=self.audit([self.line(EXCLUDED,date='2024-01-08'),self.line(TRIGGER,n=2,date=date)])
            target,trigger=result['lines']
            base=self.catalogue[EXCLUDED]['action']['base_rate_cents']
            self.assertEqual(target['expected_payable_cents'],base if expected=='base' else expected)
            self.assertGreater(trigger['expected_payable_cents'],0)
            if expected is None:self.assertIn('exclusion_presence_uncertain',target['uncertainty'])
        different,_=self.audit([self.line(EXCLUDED),self.line(TRIGGER,n=2)], [self.header(),self.header(2,'P2')])
        self.assertGreater(different['lines'][0]['expected_payable_cents'],0)

    def test_identical_multiunit_duplicate_premium_counts_once_lexical_retention(self):
        # Reverse input order to ensure retention follows IDs, not ingestion.
        result,_=self.audit([self.line(PREMIUM,6,n=2),self.line(PREMIUM,6)])
        later,earlier=result['lines']
        for row in result['lines']:
            self.assertEqual(row['quantities']['delivered_quantity'],6)
            self.assertFalse(row['premium_eligible'])
            self.assertFalse(row['uncertainty'])
            self.assertEqual(row['duplicate_resolution']['retained_line_id'],earlier['line_id'])
        self.assertEqual(later['expected_payable_cents'],0)
        self.assertEqual(earlier['expected_payable_cents'],6*self.catalogue[PREMIUM]['action']['base_rate_cents'])
        self.assertIn('duplicate_billing',later['violations'])
        self.assertNotIn('duplicate_billing',earlier['violations'])
        self.assertTrue(all(not r['requires_review'] for r in result['invoices']))

    def test_conflicting_prices_charges_units_and_eligibility_are_not_retained(self):
        rate=self.catalogue[A]['action']['base_rate_cents']
        for changes in ({'unit_price_cents':str(rate+1)}, {'line_total_cents':str(rate+1)},
                        {'unit_basis_as_billed':'per_day'}):
            result,_=self.audit([self.line(A),self.line(A,n=2,**changes)])
            for row in result['lines']:
                self.assertIsNone(row['expected_payable_cents'])
                self.assertNotIn('retained_record_key',row)
                self.assertIn('hospital_4_duplicate_conflict_requires_review',row['uncertainty'])
        hs=[self.header(),self.header(2)];hs[1]['invoice_date']='2023-12-31'
        result,_=self.audit([self.line(A),self.line(A,n=2)],hs)
        self.assertTrue(all(r['expected_payable_cents'] is None for r in result['lines']))

    def test_conflicting_duplicates_make_premium_unknown(self):
        result,_=self.audit([self.line(PREMIUM,6),self.line(PREMIUM,11,n=2)])
        self.assertTrue(all(r['premium_eligible'] is None for r in result['lines']))
        self.assertTrue(all(r['expected_payable_cents'] is None for r in result['lines']))

    def test_cap_estimate_and_exact_duplicate_cap_order(self):
        result,_=self.audit([self.line(CAP,5)])
        line=result['lines'][0]
        self.assertEqual(line['quantities']['expected_payable_quantity'],4)
        self.assertEqual(line['expected_payable_cents'],4*self.catalogue[CAP]['action']['base_rate_cents'])
        self.assertEqual(line['original']['quantity'],'5')
        self.assertEqual(line['expected_amount_status'],'assumption_dependent')
        self.assertIn('daily_cap',line['confirmed_violations'])
        self.assertIn('line_amount',line['amount_dependent_violations'])
        self.assertFalse(line['cap_evidence']['actual_delivered_quantity_established'])
        self.assertEqual(result['invoices'][0]['expected_amount_status'],'assumption_dependent')
        result,_=self.audit([self.line(CAP,5,n=2),self.line(CAP,5)])
        later,earlier=result['lines']
        self.assertEqual(later['expected_payable_cents'],0)
        self.assertEqual(earlier['quantities']['expected_payable_quantity'],4)
        self.assertEqual(earlier['expected_amount_status'],'assumption_dependent')
        self.assertFalse(later['amount_assumptions'])

    def test_volume_scope_bounds_prior_usage_and_lexical_order(self):
        lines=[self.line(VOLUME,80),self.line(VOLUME,1,n=2),self.line(VOLUME,1,n=3)]
        hs=[self.header(1,'P1'),self.header(2,'P2'),self.header(3,'P3')]
        result,_=self.audit(list(reversed(lines)),hs)
        byid={r['line_id']:r for r in result['lines']}
        at=byid[lines[1]['line_id']];after=byid[lines[2]['line_id']]
        self.assertEqual(at['prior_billed_usage']['upper'],80)
        self.assertIsNotNone(at['expected_payable_cents'])
        self.assertEqual(after['prior_billed_usage']['lower'],0)
        self.assertEqual(after['prior_billed_usage']['upper'],81)
        self.assertIsNone(after['expected_unit_rate_cents'])
        self.assertIn('volume_discount_uncertain',after['uncertainty'])

    def test_unit_and_dual_unit_uncertainty_propagate(self):
        result,_=self.audit([self.line(A),self.line(B,n=2,unit_basis_as_billed='per_day')])
        self.assertIn('bundle_eligibility_uncertain',result['lines'][0]['uncertainty'])
        self.assertIsNone(result['lines'][1]['expected_payable_cents'])
        result,_=self.audit([self.line('Intermittent Neurological Laboratory Panel'),self.line(DUAL,n=2)])
        self.assertIn('exclusion_presence_uncertain',result['lines'][0]['uncertainty'])
        self.assertIn('hospital_4_contractual_unit_unresolved',result['lines'][1]['uncertainty'])

    def test_source_records_preserved_and_wrong_hospital_rejected(self):
        hs=[self.header()];ls=[self.line(A)];old=copy.deepcopy((hs,ls))
        Hospital4Engine(self.reference).audit(hs,ls)
        self.assertEqual((hs,ls),old)
        hs[0]['hospital_id']='H1'
        result=Hospital4Engine(self.reference).audit(hs,ls)
        self.assertIsNone(result['invoices'][0]['expected_total_cents'])

    def test_submission_gate_and_tampering(self):
        result,hs=self.audit([self.line(A)])
        truth=[{'invoice_id':hs[0]['invoice_id'],'is_erroneous':'0','expected_total_cents':str(result['invoices'][0]['expected_total_cents'])}]
        # Include an erroneous calibration fixture so each class has evidence.
        err=copy.deepcopy(result['invoices'][0]);err.update(invoice_id='ERR',decision='erroneous',violations=['unit_price'])
        method=confidence_method(truth+[{'invoice_id':'ERR','is_erroneous':'1','expected_total_cents':str(err['expected_total_cents'])}],result['invoices']+[err])
        rows,omitted=build_rows(result['invoices'],method)
        self.assertEqual(len(rows),1);self.assertFalse(omitted)
        validate(rows,hs,result['invoices'],result['lines'],method)
        for field,value in [('invoice_id','INV-H1-000001'),('expected_total_cents','1.0'),('billed_total_cents','0'),('confidence','NaN'),('flagged',1)]:
            bad=copy.deepcopy(rows);bad[0][field]=value
            with self.assertRaises(ValueError):validate(bad,hs,result['invoices'],result['lines'],method)
        with self.assertRaises(ValueError):validate(rows+rows,hs,result['invoices'],result['lines'],method)
        result['invoices'][0]['uncertainty']=['unresolved']
        self.assertFalse(build_rows(result['invoices'],method)[0])
        self.assertFalse(method['validated_on_hospital_4'])
        self.assertLess(method['classes']['0']['submission_confidence'],0.9)

    def test_cap_estimate_submission_allowed_and_evidence_validated(self):
        result,hs=self.audit([self.line(CAP,5)])
        method={'classes':{'1':{'submission_confidence':0.581503}}}
        rows,omissions=build_rows(result['invoices'],method)
        self.assertEqual(len(rows),1);self.assertFalse(omissions)
        validate(rows,hs,result['invoices'],result['lines'],method)
        self.assertEqual(rows[0]['confidence'],'0.581503')
        result['invoices'][0]['expected_amount_status']='determined_under_reviewed_policies'
        with self.assertRaises(ValueError):validate(rows,hs,result['invoices'],result['lines'],method)
        result['invoices'][0]['amount_assumptions']=['unapproved_estimate']
        self.assertFalse(build_rows(result['invoices'],method)[0])

    def test_original_duplicate_history_and_unknown_prior_units_not_discarded(self):
        result,_=self.audit([self.line(VOLUME,40),self.line(VOLUME,40,n=2),self.line(VOLUME,n=3,date='2024-01-02')])
        self.assertEqual(result['lines'][1]['expected_payable_cents'],0)
        self.assertEqual(result['lines'][2]['prior_billed_usage']['upper'],80)
        self.assertEqual(result['lines'][2]['prior_billed_usage']['lower'],0)
        result,_=self.audit([self.line(VOLUME,40,unit_basis_as_billed='per_item'),self.line(VOLUME,n=2,date='2024-01-02')])
        self.assertIsNone(result['lines'][1]['prior_billed_usage']['upper'])
        self.assertIsNone(result['lines'][1]['expected_payable_cents'])

    def test_hospital_1_and_assessment_unchanged(self):
        self.assertTrue(preserved())


if __name__=='__main__':unittest.main()
