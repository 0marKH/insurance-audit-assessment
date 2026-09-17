"""Small source-pinned adapters for H2 prose, H3 amendment and H5 tables."""
import hashlib
import json
import re
from collections import Counter
from fractions import Fraction
from pathlib import Path
from contract_extractor.extract import cents, STAGES

ROOT=Path(__file__).resolve().parents[1]


def mult(value):
    f=Fraction(str(value));return {'numerator':f.numerator,'denominator':f.denominator}


def extract(h):
    policy=json.loads((ROOT/f'policies/hospital_{h}.json').read_text())
    rules=[]; documents={}; tables={}; clauses={}; inventory=[]
    for name,expected in policy['sources_sha256'].items():
        p=ROOT/name;raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==expected, name
        lines=raw.decode().splitlines();documents[name]=lines; heading='preamble'; table=None
        for n,line in enumerate(lines,1):
            if line.startswith('#'):
                heading=line.lstrip('# ').strip();table=None
            m=re.match(r'((?:A1\.)?\d+\.\d+(?:\.\d+)?) ',line)
            if m:clauses[(name,m[1])]=(n,heading,line)
            if line.startswith('|'):
                cells=[c.strip() for c in line.strip('|').split('|')]
                if table is None:table=[];tables[(name,heading)]=table
                table.append((n,cells))
    def src(name,n):
        return {'document':name,'sha256':policy['sources_sha256'][name],'line_start':n,'line_end':n,
                'section':next((key[1] for key,v in clauses.items() if key[0]==name and v[0]==n),
                               next((key[1] for key,t in tables.items() if key[0]==name and any(r[0]==n for r in t)),'preamble')),
                'quote':documents[name][n-1]}
    def clause(name,key):return src(name,clauses[(name,key)][0])
    def add(kind,services,action,evidence,condition=None,scope=None,questions=None):
        rule={'id':f'H{h}-{len(rules)+1:03d}','kind':kind,'applies_to':{'services':services},
            'condition':condition or {'always':True},'action':action,
            'scope':{'hospital_id':f'hospital_{h}','group_by':scope or ['applicable_contract_number']},
            'order':{'stages':STAGES},'source':evidence,
            'uncertainty':{'status':'unresolved' if questions else 'reviewed','interpretation':kind.replace('_',' '),'questions':questions or []}}
        rules.append(rule);return rule
    daygroup=['applicable_contract_number','patient_id','service_date','service']
    names=list(documents);base=next(n for n in names if any(s in n for s in ['master_services','base_agreement','network_reimbursement']))
    meta={m[1]:m[2] for line in documents[base] for m in [re.fullmatch(r'\*\*(.+):\*\* (.+)',line)] if m}
    contract={'hospital_id':f'hospital_{h}','contract_number':meta['Contract number'],'provider':meta['Provider'],
              'payer':meta['Payer'],'effective_from':'2024-01-01','effective_to':'2025-12-31','currency':'GBP'}
    term='1.1' if h==5 else '1.2'
    add('contract_scope',[],contract,[clause(base,term)])
    rounding='3.2' if h==5 else '3.1';order='3.1' if h==5 else '3.2'
    for kind,ref in [('rounding',rounding),('adjustment_order',order),('line_calculation','3.3')]:
        add(kind,[],{'mode':'half_up_each_step','stages':STAGES},[clause(base,ref)])
    for kind in ('facility_scope','plan_scope'):
        add(kind,[],{'multiplier':mult(1)},[clause(base,'1.3' if h==2 else '1.5' if h==3 else '3.3')])
    add('contract_number_restriction',[],{'require_contract_number':True},[clause(base,'13.11' if h==2 else '10.1')])
    add('valid_service_dates',[],{'term_inclusive':True},[clause(base,term if h==2 else '10.2')])
    if h==3:add('document_precedence',[],{'order':['amendment','appendix_b','base_agreement']},[clause(base,'1.3')])
    if h!=2:add('duplicate_billing',[],{'same_service_patient_day':True,'correction':'unresolved'},[clause(base,'10.3')],questions=['No correction convention imported from H1/H4.'])
    for key in (['2.2','2.3','2.4','2.5','2.7','3.4','3.5','3.6','13.1','13.6'] if h==2 else ['2.1','2.2','2.3']):
        add('definition',[],{'text':clauses[(base,key)][2]},[clause(base,key)])
    def catalogue(name,unit,rate,source):
        return add('service_catalogue',[name],{'service_name':name,'unit_basis':unit,'base_rate_cents':cents(rate),'currency':'GBP'},source,
                   questions=['Meaning of per hour, per item cannot be established from the quantity column.'] if ',' in unit else None)
    def premium(name,threshold,pct,evidence,weekend=False):
        return add('weekend_uplift' if weekend else 'threshold_premium',[name],{'percent':pct,'multiplier':mult(Fraction(100+pct,100)),'applies_to':'all_units'},evidence,
            {'operator':'>','threshold':{'value':threshold},'metric':'delivered_daily_quantity'} if not weekend else {'weekday':'Saturday_or_Sunday'},daygroup)
    def cap(name,value,evidence):
        add('daily_quantity_cap',[name],{'maximum_billable_units':{'value':value},'correction':'review'},evidence,{'operator':'>','threshold':{'value':value}},daygroup,
            ['Cap establishes a maximum, not actual delivered quantity; violated-cap amounts withheld for this hospital.'])
    def discount(name,threshold,pct,evidence):
        add('volume_discount',[name],{'percent':pct,'multiplier':mult(Fraction(100-pct,100))},evidence,
            {'operator':'>','threshold':{'value':threshold},'exclude_current_line':True},['applicable_contract_number','service'])
    def exclusion(name,trigger,days,evidence):
        add('exclusion_window',[name],{'type':'not_billable','target_service':name},evidence,
            {'trigger_service':trigger,'window_days':days,'direction':'both','same_patient':True,'endpoint':'unresolved'},['patient_id'],
            ['Exact endpoint unapproved for this hospital.'] if h==2 else ['Same-patient bidirectional context is inspected; positive exclusion cases withheld because scope/direction/endpoints are not explicit.'])
    if h==2:
        pattern=r'(\d+\.\d+) In respect of (.+?), the Provider shall invoice the Payer at the rate of (GBP [\d,.]+) (per .+?)\.'
        for n,line in enumerate(documents[base],1):
            m=re.match(pattern,line)
            if not m:continue
            sec,name,rate,unit=m.groups();e=[src(base,n)];catalogue(name,unit,rate,e)
            for match in re.finditer(r'aggregate quantity .*? exceeds .*?\((\d+)\).*? increased by .*?\((\d+)%\)',line):premium(name,int(match[1]),int(match[2]),e+[clause(base,'3.4')])
            for match in re.finditer(r'not fall on a Business Day.*?\((\d+)%\)',line):premium(name,0,int(match[1]),e+[clause(base,'2.4')],True)
            for match in re.finditer(r'not bill more than .*?\((\d+)\)',line):cap(name,int(match[1]),e)
            for match in re.finditer(r'cumulative utilisation .*? exceeds .*?\((\d+)\).*?discount of .*?\((\d+)%\)',line):
                assert 'across the whole term' in match[0] and 'all Patients' in match[0]
                discount(name,int(match[1]),int(match[2]),e+[clause(base,'2.7'),clause(base,'3.5')])
            for match in re.finditer(r'not billable where (.+?) has been delivered to the same Patient within .*?\((\d+)\) days',line):exclusion(name,match[1],int(match[2]),e+[clause(base,'3.6')])
            match=re.search(r'Where this Service and (.+?) are both delivered.*?this Service at (GBP [\d,.]+).*? and .+? at (GBP [\d,.]+).*?standalone rates',line)
            if match:
                other,ra,rb=match.groups();key=tuple(sorted([name,other]));rates={name:cents(ra),other:cents(rb)}
                existing=next((r for r in rules if r['kind']=='bundle' and tuple(sorted(r['applies_to']['services']))==key),None)
                if existing:assert existing['action']['rates_cents']==rates;existing['source']+=e
                else:add('bundle',[name,other],{'rates_cents':rates},e,{'same_patient':True,'same_service_day':True},daygroup)
        assert sum(r['kind']=='service_catalogue' for r in rules)==76
    else:
        for (document,heading),entries in sorted(tables.items(), key=lambda item: (0 if "appendix_b" in item[0][0] else 2 if "amendment" in item[0][0] else 1, list(tables).index(item[0]))):
            for n,cells in entries[2:]:
                e=[src(document,n)];name=cells[0]
                if 'Appendix' in documents[document][0] or heading=='4. Table 1 — Base Rates':
                    catalogue(name,cells[1],cells[2],e)
                    if h==5 and cells[3]!='—':cap(name,int(cells[3].split()[0]),e)
                elif heading=='A1.2 Substituted Rates':
                    old=next(r for r in rules if r['kind']=='service_catalogue' and r['action']['service_name']==name)
                    assert old['action']['base_rate_cents']==cents(cells[2]) and old['action']['unit_basis']==cells[1]
                    add('rate_version',[name],{'base_rate_cents':cents(cells[3]),'effective_from':'2025-01-01'},e+[clause(document,'A1.1.2')])
                elif heading=='A1.3 Additional Services':
                    r=catalogue(name,cells[1],cells[2],e);r['action']['effective_from']='2025-01-01'
                elif 'Threshold Premiums' in heading:premium(name,int(cells[1].split()[2]),int(cells[2].strip('+%')),e)
                elif 'Non-Business-Day' in heading:premium(name,0,int(cells[1].strip('+%')),e,True)
                elif 'Cumulative Volume' in heading:
                    discount(name,int(cells[1].split()[2]),int(cells[2].strip('%')),e+[clause(base,'6.1' if h==3 else '8.1')])
                elif 'Daily Quantity Caps' in heading:cap(name,int(cells[1].split()[0]),e)
                elif 'Bundled Services' in heading:
                    a,b,ra,rb=cells if h==3 else [cells[0],cells[2],cells[1],cells[3]]
                    add('bundle',[a,b],{'rates_cents':{a:cents(ra),b:cents(rb)}},e+[clause(base,'8.1' if h==3 else '7.1')],{'same_patient':True,'same_service_day':True},daygroup)
                elif 'Exclusion Windows' in heading:exclusion(name,cells[2],int(cells[1].split()[0]),e)
                elif 'Multipliers' in heading:
                    kind='facility_rates' if 'Facility' in heading else 'plan_rates'
                    add(kind,[name],{'multipliers':{col:mult(val) for col,val in zip(entries[0][1][1:],cells[1:])}},e)
                elif heading=='1. Parties, Term and Network':pass
                else:raise ValueError('Unreviewed table '+heading)
    catalogue_names={r['action']['service_name'] for r in rules if r['kind']=='service_catalogue'}
    for r in rules:
        assert set(r['applies_to']['services'])<=catalogue_names
        if r['kind']=='exclusion_window':assert r['condition']['trigger_service'] in catalogue_names
    for (document,sec),(n,heading,line) in clauses.items():
        used=any(any(s['document']==document and s['line_start']==n for s in r['source']) for r in rules)
        inventory.append({'document':document,'section':sec,'line':n,'heading':heading,
            'disposition':'machine_reference' if used else 'documentary_or_not_machine_testable; retained for review'})
    return {'schema_version':'target-1.0','status':'reviewed_with_explicit_limits','contract':contract,'policy':policy,'rules':rules,
            'counts':dict(Counter(r['kind'] for r in rules)),'clause_inventory':inventory}
