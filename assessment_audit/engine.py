"""Isolated hospital adapters; frozen Hospital 1 and Hospital 4 remain untouched."""
import copy
from collections import Counter, defaultdict
from hospital_audit.engine import Engine, UNITS, day
from hospital_audit.matching import Matcher
from .extract import ROOT


class ContractMatcher(Matcher):
    def __init__(self,catalogue,h):
        super().__init__(catalogue,ROOT/f'policies/hospital_{h}_aliases.json')
        self.unsupported={name for name,r in catalogue.items() if r['action']['unit_basis'] not in UNITS}

    def match(self,text):
        result=super().match(text)
        if result['service'] in self.unsupported:
            result['recognized_service']=result['service'];result['service']=None
            result['method']='contractual_unit_unresolved'
        return result


class TargetEngine(Engine):
    def __init__(self,reference):
        self.ref=reference;self.contract=reference['contract'];self.h=int(self.contract['hospital_id'].split('_')[-1])
        assert self.h in (2,3,5)
        self.policy={'line_ordering':{'expected_line_id_pattern':rf'^H{self.h}-L[0-9]{{5}}-[0-9]{{2}}$'}}
        self.by_kind=defaultdict(list)
        for r in reference['rules']:self.by_kind[r['kind']].append(r)
        self.catalogue={r['action']['service_name']:r for r in self.by_kind['service_catalogue']}
        self.matcher=ContractMatcher(self.catalogue,self.h)
        self.start,self.end=day(self.contract['effective_from']),day(self.contract['effective_to'])
        self.single={k:{r['applies_to']['services'][0]:r for r in self.by_kind[k]} for k in
            ('threshold_premium','weekend_uplift','daily_quantity_cap','exclusion_window','rate_version','facility_rates','plan_rates')}
        self.discounts=defaultdict(list)
        for r in self.by_kind['volume_discount']:self.discounts[r['applies_to']['services'][0]].append(r)

    def presence(self,line,service,lines,window=0):
        if not window:return super().presence(line,service,lines,window)
        possible=[]
        for other in self.context[service]:
            if other is line or not self.patient_possible(line,other):continue
            distance=abs((line['_date']-other['_date']).days) if line['_date'] and other['_date'] else None
            if distance is not None and distance>window:continue
            # H2 explicitly states same patient and both date directions. H3/H5
            # positive cases remain uncertain; no H4 endpoint approval transfer.
            if (self.h==2 and distance is not None and distance<window and other['matched_service']==service
                and other['_qty'] is not None and line['_patient'] and line['_patient']==other['_patient']):return True,[other]
            possible.append(other)
        return (None,possible) if possible else (False,[])

    def price(self,line,lines):
        service=line['matched_service'];catalogue=self.catalogue[service]
        saved_rate=catalogue['action']['base_rate_cents'];saved_mult={};unknown_stage=None
        line['context_assumptions']=[]
        if self.h==2:line['context_assumptions'].append('approved_recorded_date_as_service_day')
        version=self.single['rate_version'].get(service)
        if version:
            self.use(line,version)
            if line['_date'] is None:
                self.uncertain(line,'rate_version_date_unknown');unknown_stage='base_rate'
            elif line['_date']>=day(version['action']['effective_from']):
                catalogue['action']['base_rate_cents']=version['action']['base_rate_cents'];self.use(line,version,True)
                line['rate_version_effective_from']=version['action']['effective_from']
            else:line['rate_version_effective_from']=self.contract['effective_from']
        introduced=catalogue['action'].get('effective_from')
        if introduced and line['_date'] and line['_date']<day(introduced):
            line['_excluded']=True;line['nonpayable_basis']='service_not_effective'
            self.violation(line,'uncontracted_service_date');self.use(line,catalogue,True)
        if self.h==5:
            for kind,table,field,stage in [('facility_scope','facility_rates','facility_code','facility_multiplier'),
                                          ('plan_scope','plan_rates','plan_tier','plan_tier_multiplier')]:
                rule=self.by_kind[kind][0];saved_mult[kind]=rule['action']['multiplier']
                schedule=self.single[table][service];self.use(line,schedule,True)
                value=line['_header'].get(field); multiplier=schedule['action']['multipliers'].get(value)
                if multiplier is None:
                    self.uncertain(line,field+'_multiplier_unknown');unknown_stage=unknown_stage or stage
                    multiplier={'numerator':1,'denominator':1}
                rule['action']['multiplier']=multiplier
                line.setdefault('multiplier_context',{})[field]={'value':value,'source':'invoice_header','rule_id':schedule['id']}
            line['context_assumptions'].append('approved_header_facility_as_line_context')
        try:super().price(line,lines)
        finally:
            catalogue['action']['base_rate_cents']=saved_rate
            for kind,value in saved_mult.items():self.by_kind[kind][0]['action']['multiplier']=value
        if unknown_stage:
            line['expected_unit_rate_cents']=None;unknown=False
            for step in line['calculation_steps']:
                unknown=unknown or step['stage']==unknown_stage
                if unknown:step['result_cents']=None;step['context_unresolved']=True

    @staticmethod
    def withhold(line,reason):
        line['expected_payable_cents']=None;line['quantities']['expected_payable_quantity']=None
        line.pop('retained_record_key',None)
        line['calculation_steps']=[s for s in line['calculation_steps'] if s['stage'] not in ('nonpayable_charge','quantity_multiplication')]
        line['violations']=[v for v in line['violations'] if v!='line_amount']
        if reason not in line['uncertainty']:line['uncertainty'].append(reason)

    def audit(self,headers,records):
        translated=copy.deepcopy(headers)
        for row in translated:row['hospital_id']='H1' if row.get('hospital_id')==f'H{self.h}' else 'INVALID_CONTEXT'
        result=super().audit(translated,records)
        children=defaultdict(list);groups=defaultdict(list)
        for line in result['lines']:
            children[line['invoice_id']].append(line)
            if line['matched_service']:groups[(line['patient_id'],line['original']['service_date'],line['matched_service'])].append(line)
        old_flags={key:{v for l in group for v in l['violations']} for key,group in children.items()}
        old_uncertainty={key:{v for l in group for v in l['uncertainty']} for key,group in children.items()}
        for group in groups.values():
            if len(group)>1:
                for line in group:
                    self.withhold(line,'duplicate_correction_not_approved_for_hospital')
                    if self.h==2:line['violations']=[v for v in line['violations'] if v!='duplicate_billing']
                    elif 'duplicate_billing' not in line['violations']:line['violations'].append('duplicate_billing')
        for line in result['lines']:
            if 'daily_cap' in line['violations'] and line['expected_payable_cents']!=0:
                self.withhold(line,'cap_actual_quantity_unknown')
            if line['match']['method']=='contractual_unit_unresolved':
                line['uncertainty'].append('contractual_dual_unit_unresolved')
                r=self.catalogue[line['match']['recognized_service']]
                line['rules_considered'].append(r['id']);line['source_clauses']=sorted(set(line['source_clauses'])|{s['section'] for s in r['source']})
            for s in line['calculation_steps']:
                if s['stage']=='nonpayable_charge' and line.get('nonpayable_basis'):s['reason']=line['nonpayable_basis']
            line['uncertainty']=sorted(set(line['uncertainty']));line['violations']=sorted(set(line['violations']))
            line['expected_amount_status']='unresolved' if line['expected_payable_cents'] is None else 'determined_under_documented_policies'
            line['decision']='erroneous' if line['violations'] else 'review' if line['uncertainty'] or line['expected_payable_cents'] is None else 'correct'
        counts=Counter(r['invoice_id'] for r in headers)
        for original,invoice in zip(headers,result['invoices']):
            key=invoice['invoice_id'];group=children[key];invoice['original']=copy.deepcopy(original)
            vs=(set(invoice['violations'])-old_flags[key]-{'invoice_amount'})|{v for l in group for v in l['violations']}
            us=(set(invoice['uncertainty'])-old_uncertainty[key])|{u for l in group for u in l['uncertainty']}
            if self.h==2:
                discharge,issued=day(original.get('discharge_date')),day(original.get('invoice_date'))
                # No submission timestamp: late issue is a review signal, never
                # an invented submission date or automatic zero reimbursement.
                if discharge is None or issued is None or (issued-discharge).days>60:
                    us.add('submission_deadline_evidence_requires_review')
                invoice['administrative_limits']=['Actual submission timestamp and waiver evidence unavailable; invoice issue date is only a screening signal.']
            total=sum(l['expected_payable_cents'] for l in group) if group and counts[key]==1 and all(l['expected_payable_cents'] is not None for l in group) else None
            if total is not None and invoice['billed_total_cents'] is not None and total!=invoice['billed_total_cents']:vs.add('invoice_amount')
            invoice.update(expected_total_cents=total,violations=sorted(vs),uncertainty=sorted(us),known_violation=bool(vs),
                requires_review=bool(us) or total is None,
                decision='erroneous' if vs else 'review' if us or total is None else 'correct',
                expected_amount_status='unresolved' if total is None else 'determined_under_documented_policies',
                context_assumptions=sorted({a for l in group for a in l.get('context_assumptions',[])}))
        return result
