"""Conservative row selection and an explicitly unvalidated confidence heuristic."""
import math
import re
from collections import Counter, defaultdict
from decimal import Decimal

FIELDS = ['invoice_id', 'flagged', 'error_category', 'expected_total_cents', 'billed_total_cents', 'confidence']
APPROVED_AMOUNT_ASSUMPTIONS = {'cap_quantity_is_reimbursable_estimate'}


def defensible(row, count=1):
    return (count == 1 and row['decision'] in ('correct', 'erroneous')
            and not row['requires_review'] and not row['uncertainty']
            and set(row.get('amount_assumptions', [])) <= APPROVED_AMOUNT_ASSUMPTIONS
            and type(row['expected_total_cents']) is int and row['expected_total_cents'] >= 0
            and type(row['billed_total_cents']) is int and row['billed_total_cents'] >= 0)


def confidence_method(labels, audits):
    """Use already-exposed H1 results; never fit H4 rules or claim fresh validation."""
    truth = {r['invoice_id']: r for r in labels}
    counts = Counter(r['invoice_id'] for r in audits)
    samples = {0: [], 1: []}
    for row in audits:
        label = truth.get(row['invoice_id'])
        if not label or not defensible(row, counts[row['invoice_id']]) or label['expected_total_cents'] == '':
            continue
        flag = int(row['decision'] == 'erroneous')
        success = int(label['is_erroneous']) == flag and int(label['expected_total_cents']) == row['expected_total_cents']
        samples[flag].append(success)
    classes = {}
    for flag, outcomes in samples.items():
        n, k = len(outcomes), sum(outcomes)
        if not n:
            raise ValueError('No measurable Hospital 1 evidence for confidence class')
        z = 1.96
        p = k / n
        lower = (p + z*z/(2*n) - z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))) / (1 + z*z/n)
        classes[str(flag)] = {'sample_size': n, 'joint_successes': k,
                             'wilson_95_lower_bound': round(lower, 9),
                             'submission_confidence': round(0.90 * lower, 6)}
    return {'classes': classes, 'success_definition': 'Correct flagged value AND exact expected cents in a defensible unique-ID row.',
            'evidence': 'Existing exposed Hospital 1 development and held-aside outputs combined. No new holdout; no rule retuning.',
            'formula': '0.90 * Wilson 95% lower bound of joint success rate, separately by predicted flagged value (z=1.96).',
            'transfer_factor': 0.90, 'validated_on_hospital_4': False,
            'cap_estimates': {'submission_authorized': True, 'amount_status': 'assumption_dependent',
                'numerical_adjustment': None, 'class_scores_unchanged': True,
                'evidence': 'Development analysis of already-exposed H1 labels: four cap cases imply quantities below their caps; three residual reconstructions have unrelated unresolved lines. The explanation is unproven.',
                'interpretation': 'A confirmed cap violation does not validate its corrected amount. The shared class heuristic is not a cap-specific probability or calibration; no new penalty is invented.'},
            'limitations': ['The 0.90 transfer factor is a declared heuristic, not an estimated domain-shift correction.',
                           'Invoice outcomes are correlated; Wilson is a finite-sample caution, not a formal coverage guarantee here.',
                           'Matching, new contract interpretations and category correctness are not separately calibrated.',
                           'These scores are not established probabilities or validated calibration on Hospital 4.']}


def build_rows(invoices, method):
    counts = Counter(r['invoice_id'] for r in invoices)
    rows, omissions = [], []
    for row in sorted(invoices, key=lambda r: (r['invoice_id'], r['invoice_record_index'])):
        if not defensible(row, counts[row['invoice_id']]):
            reasons = set(row['uncertainty'])
            if counts[row['invoice_id']] != 1: reasons.add('nonunique_invoice_id')
            if row['expected_total_cents'] is None: reasons.add('expected_total_unknown')
            if row['billed_total_cents'] is None: reasons.add('billed_total_invalid')
            omissions.append({'invoice_id':row['invoice_id'], 'invoice_record_index':row['invoice_record_index'],
                              'decision':row['decision'], 'known_violation':row['known_violation'],
                              'reasons':'|'.join(sorted(reasons))})
            continue
        flag = int(row['decision'] == 'erroneous')
        rows.append({'invoice_id':row['invoice_id'], 'flagged':flag,
                     'error_category':'|'.join(row['violations']) if flag else '',
                     'expected_total_cents':row['expected_total_cents'], 'billed_total_cents':row['billed_total_cents'],
                     'confidence':format(method['classes'][str(flag)]['submission_confidence'], '.6f')})
    return rows, omissions


def validate(rows, headers, invoices, lines, method):
    """Validate even a reloaded CSV, including every submitted line's exact sum."""
    source, audit, children = defaultdict(list), defaultdict(list), defaultdict(list)
    for row in headers: source[row['invoice_id']].append(row)
    for row in invoices: audit[row['invoice_id']].append(row)
    for row in lines: children[row['invoice_id']].append(row)
    seen = set()
    for row in rows:
        if list(row) != FIELDS: raise ValueError('Submission columns/order differ from template')
        key = row['invoice_id']
        if not re.fullmatch(r'INV-H4-\d{6}', key) or key in seen: raise ValueError('Invalid or duplicate submission ID: ' + key)
        seen.add(key)
        if len(source[key]) != 1 or len(audit[key]) != 1: raise ValueError('Ambiguous/missing source ID: ' + key)
        original, prediction = source[key][0], audit[key][0]
        if original['hospital_id'] != 'H4' or not defensible(prediction): raise ValueError('Indefensible submission: ' + key)
        if str(row['flagged']) not in ('0','1'): raise ValueError('Invalid flag')
        flag = int(row['flagged'])
        if flag != int(prediction['decision'] == 'erroneous'): raise ValueError('Flag differs from audit')
        if row['error_category'] != ('|'.join(prediction['violations']) if flag else ''): raise ValueError('Categories differ from audit')
        for field in ('expected_total_cents','billed_total_cents'):
            if not re.fullmatch(r'\d+', str(row[field])): raise ValueError('Amount is not nonnegative integer cents')
            if int(row[field]) != prediction[field]: raise ValueError('Amount differs from audit')
        if int(row['billed_total_cents']) != int(original['invoice_total_cents']): raise ValueError('Billed source mismatch')
        detail = children[key]
        if not detail or any(type(r['expected_payable_cents']) is not int or r['uncertainty'] for r in detail): raise ValueError('Unresolved line in submission')
        assumptions = {a for r in detail for a in r.get('amount_assumptions', [])}
        if assumptions != set(prediction.get('amount_assumptions', [])) or not assumptions <= APPROVED_AMOUNT_ASSUMPTIONS:
            raise ValueError('Unapproved or inconsistent amount assumptions')
        if assumptions and prediction.get('expected_amount_status') != 'assumption_dependent':
            raise ValueError('Cap estimate presented as determined amount')
        for line in detail:
            if line.get('amount_assumptions') and (line.get('cap_evidence', {}).get('actual_delivered_quantity_established') is not False
                    or 'daily_cap' not in line.get('confirmed_violations', [])):
                raise ValueError('Cap violation and amount evidence missing')
        if sum(r['expected_payable_cents'] for r in detail) != int(row['expected_total_cents']): raise ValueError('Expected line sum mismatch')
        score = Decimal(str(row['confidence']))
        if not score.is_finite() or not 0 <= score <= 1: raise ValueError('Invalid confidence')
        if score != Decimal(str(method['classes'][str(flag)]['submission_confidence'])): raise ValueError('Confidence differs from method')
        if not flag and row['expected_total_cents'] != row['billed_total_cents']: raise ValueError('Correct row amount mismatch')
    return {'validated_rows':len(rows), 'checks':['exact template columns', 'unique H4 IDs and header joins', 'defensible gate',
             'original billed cents', 'integer expected cents and line sums', 'flags/categories', 'approved cap amount assumptions', 'finite confidence and formula']}
