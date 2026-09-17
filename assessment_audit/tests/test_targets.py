import copy
import unittest
from hospital_audit.engine import UNITS
from assessment_audit.extract import extract
from assessment_audit.engine import TargetEngine
from assessment_audit.__main__ import validate
from hospital_4.submission import build_rows


class TargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.refs={h:extract(h) for h in (2,3,5)}

    def audit(self,h,entries,header_changes=None):
        engine=TargetEngine(copy.deepcopy(self.refs[h]));hs=[];ls=[]
        for n,entry in enumerate(entries,1):
            service,q,date=entry[:3];changes=entry[3] if len(entry)>3 else {}
            cat=engine.catalogue[service]['action'];rate=cat['base_rate_cents']
            header=dict(invoice_id=f'INV-H{h}-{n:06d}',hospital_id=f'H{h}',contract_number=engine.contract['contract_number'],
                invoice_date='2025-12-31',patient_id='P1',facility_code='F-MAIN',plan_tier='SILVER',discharge_date='2025-12-20',admission_date='2024-01-01')
            if header_changes:header.update(header_changes[n-1])
            line=dict(line_id=f'H{h}-L{n:05d}-01',invoice_id=header['invoice_id'],line_no='1',service_date=date,
                description=service,quantity=str(q),unit_basis_as_billed=UNITS.get(cat['unit_basis'],'per_hour_per_item'),
                unit_price_cents=str(rate),line_total_cents=str(rate*q));line.update(changes)
            header['invoice_total_cents']=line['line_total_cents'];hs.append(header);ls.append(line)
        original=copy.deepcopy((hs,ls));result=engine.audit(hs,ls);self.assertEqual((hs,ls),original)
        return result,hs

    def test_extraction_counts_and_sources(self):
        for h,count in [(2,76),(3,120),(5,84)]:
            r=self.refs[h];self.assertEqual(r['counts']['service_catalogue'],count)
            for rule in r['rules']:
                self.assertTrue(rule['source']);self.assertTrue(all(s['quote'] and s['sha256'] for s in rule['source']))
        self.assertEqual(self.refs[3]['counts']['rate_version'],7)
        self.assertEqual(self.refs[5]['counts']['facility_rates'],84)
        self.assertEqual(self.refs[2]['counts']['bundle'],3) # reciprocal prose deduplicated
        self.assertEqual(self.refs[2]['counts']['volume_discount'],12)

    def test_h3_rate_effective_on_service_date_not_invoice_date(self):
        service='Ambulatory Otolaryngologic Imaging Interpretation'
        result,_=self.audit(3,[(service,1,'2024-12-31'),(service,1,'2025-01-01')])
        self.assertEqual([l['expected_payable_cents'] for l in result['lines']],[182625,208200])
        self.assertTrue(any('A1.1.2' in l['source_clauses'] for l in result['lines']))

    def test_h3_amended_rate_precedes_weekend_rounding(self):
        result,_=self.audit(3,[('Specialist Psychiatric Discharge Planning',1,'2025-01-05')])
        self.assertEqual(result['lines'][0]['expected_payable_cents'],48455)

    def test_h3_added_service_before_and_on_start(self):
        s='Advanced Dermatologic Nutritional Support'
        result,_=self.audit(3,[(s,1,'2024-12-31'),(s,1,'2025-01-01')])
        self.assertEqual([l['expected_payable_cents'] for l in result['lines']],[0,86525])
        self.assertIn('uncontracted_service_date',result['lines'][0]['violations'])
        self.assertEqual(result['lines'][0]['calculation_steps'][-1]['reason'],'service_not_effective')

    def test_h3_unknown_version_date_never_guesses(self):
        result,_=self.audit(3,[('Specialist Psychiatric Discharge Planning',1,'unknown')])
        self.assertIsNone(result['lines'][0]['expected_payable_cents'])
        self.assertIsNone(result['lines'][0]['expected_unit_rate_cents'])

    def test_h5_facility_then_plan_round_each_step(self):
        result,_=self.audit(5,[('Advanced Cardiac Ventilation Support',2,'2024-01-01')],[{'facility_code':'F-NORTH'}])
        line=result['lines'][0]
        self.assertEqual(line['expected_payable_cents'],3639*2) # 3375*1.1 ->3713; *.98 ->3639
        self.assertIn('approved_header_facility_as_line_context',line['context_assumptions'])

    def test_h5_cross_invoice_bundle_before_multipliers(self):
        result,_=self.audit(5,[('Elective Ophthalmic Recovery Room Occupancy',2,'2024-01-01'),
                               ('Supervised Palliative Consultation',1,'2024-01-01')],
                             [{'facility_code':'F-NORTH','plan_tier':'GOLD'}]*2)
        self.assertEqual([l['expected_payable_cents'] for l in result['lines']],[176934*2,410981])

    def test_h5_unknown_facility_or_plan_withheld(self):
        for changes in ({'facility_code':'UNKNOWN'},{'plan_tier':'UNKNOWN'}):
            result,_=self.audit(5,[('Advanced Cardiac Ventilation Support',1,'2024-01-01')],[changes])
            self.assertIsNone(result['lines'][0]['expected_payable_cents'])
            self.assertIsNone(result['lines'][0]['expected_unit_rate_cents'])

    def test_h5_cumulative_scope_explicit_and_strict_threshold(self):
        s='Ambulatory Hepatic Case Conference'
        result,_=self.audit(5,[(s,80,'2024-01-01'),(s,1,'2024-01-02'),(s,1,'2024-01-03')],
                            [{'patient_id':p} for p in ('P1','P2','P3')])
        self.assertEqual([l['expected_unit_rate_cents'] for l in result['lines']],[19775,19775,17402])
        self.assertEqual(result['lines'][2]['prior_billed_usage']['exact'],81)

    def test_h2_threshold_all_units_and_half_cent(self):
        s='Focused Palliative Recovery Room Occupancy'
        for q,rate in ((12,52775),(13,68608)):
            result,_=self.audit(2,[(s,q,'2024-01-01')])
            self.assertEqual(result['lines'][0]['expected_payable_cents'],q*rate)
            self.assertIn('approved_recorded_date_as_service_day',result['lines'][0]['context_assumptions'])

    def test_h2_weekend_on_recorded_service_date(self):
        result,_=self.audit(2,[('Emergency Renal Infusion Therapy',2,'2024-01-06')])
        self.assertEqual(result['lines'][0]['expected_payable_cents'],6636*2)

    def test_h2_exclusions_inside_both_directions_endpoint_unresolved(self):
        for date,expected in [('2024-01-02',0),('2024-01-14',0),('2024-01-01',None),('2024-01-15',None)]:
            result,_=self.audit(2,[('Intermittent Psychiatric Laboratory Panel',1,'2024-01-08'),('Emergency Pulmonary Ventilation Support',1,date)])
            self.assertEqual(result['lines'][0]['expected_payable_cents'],expected)
            self.assertGreater(result['lines'][1]['expected_payable_cents'],0)

    def test_h3_positive_exclusion_not_forced(self):
        result,_=self.audit(3,[('Advanced Gastrointestinal Telemetry Monitoring',1,'2024-01-01'),('Advanced Geriatric Nutritional Support',1,'2024-01-02')])
        self.assertIsNone(result['lines'][0]['expected_payable_cents'])

    def test_caps_and_duplicates_not_given_h4_correction_policy(self):
        for h,s,q in [(2,'Focused Cardiac Dialysis Session',7),(3,'Ambulatory Otolaryngologic Imaging Interpretation',13),(5,'Advanced Cardiac Ventilation Support',25)]:
            result,_=self.audit(h,[(s,q,'2024-01-01')])
            self.assertIn('daily_cap',result['lines'][0]['violations']);self.assertIsNone(result['lines'][0]['expected_payable_cents'])
            result,_=self.audit(h,[(s,1,'2024-01-01'),(s,1,'2024-01-01')])
            self.assertTrue(all(l['expected_payable_cents'] is None for l in result['lines']))
            if h==2:self.assertTrue(all('duplicate_billing' not in l['violations'] for l in result['lines']))

    def test_unknown_prior_unit_propagates_discount(self):
        s='Ambulatory Hepatic Case Conference'
        result,_=self.audit(5,[(s,1,'2024-01-01',{'unit_basis_as_billed':'per_day'}),(s,1,'2024-01-02')])
        self.assertIsNone(result['lines'][1]['prior_billed_usage']['upper'])
        self.assertIsNone(result['lines'][1]['expected_payable_cents'])

    def test_h2_deadline_unknown_submission_not_zero(self):
        result,_=self.audit(2,[('Advanced Endocrine Case Conference',1,'2024-01-01')],[{'discharge_date':'2024-01-02'}])
        row=result['invoices'][0];self.assertIn('submission_deadline_evidence_requires_review',row['uncertainty'])
        self.assertEqual(row['expected_total_cents'],17400)

    def test_final_validation_and_tampering(self):
        result,headers=self.audit(3,[('Advanced Dermatologic Nutritional Support',1,'2025-01-01')])
        method={'classes':{'0':{'submission_confidence':0.892297}}};rows,_=build_rows(result['invoices'],method)
        validate(rows,headers,result['invoices'],result['lines'],method)
        for field,value in [('confidence','NaN'),('billed_total_cents',0),('expected_total_cents','1.5'),('invoice_id','INV-H1-000001'),('flagged',1)]:
            altered=copy.deepcopy(rows);altered[0][field]=value
            with self.assertRaises(ValueError):validate(altered,headers,result['invoices'],result['lines'],method)

if __name__=='__main__':unittest.main()
