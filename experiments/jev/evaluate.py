"""Compare cached pilot responses with pre-response semantic review (not gold labels)."""
import csv
import hashlib
import io
import json
from collections import Counter
from decimal import Decimal
from pathlib import Path

HERE=Path(__file__).resolve().parent


def evaluate():
    rows=[];usage=Counter();latencies=[]
    for cohort,request_file,reference_file in [('unresolved','requests.jsonl','pre_response_reference.json'),
                                              ('positive_control','control_requests.jsonl','control_reference.json')]:
        reference={r['request_id']:r for r in json.loads((HERE/reference_file).read_text())}
        for item in map(json.loads,(HERE/request_file).read_text().splitlines()):
            payload=item['request'];digest=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            stored=json.loads((HERE/'responses'/f'{digest}.json').read_text())
            response=stored['response'];answer=response['answers']['service_match'];ref=reference[item['request_id']]
            choice=answer['choice'];options=payload['questions']['service_match']['criteria']
            service=options[choice] if choice.startswith('S') and choice[1:].isdigit() else None
            ranked=sorted(answer['probabilities'].items(),key=lambda kv:(-kv[1],kv[0]))
            rows.append({'cohort':cohort,'request_id':item['request_id'],'description':ref['original_description'],
                         'line_count':ref['line_count'],'reviewed_target':ref['reviewed_target'],'model_choice':choice,
                         'proposed_service':service,'confidence':answer['confidence'],'top_probability':ranked[0][1],
                         'top_two_margin':round(ranked[0][1]-ranked[1][1],6),
                         'probability_sum':round(sum(answer['probabilities'].values()),9),
                         'review_agreement':choice==ref['reviewed_target'],'specific_service_proposed':service is not None,
                         'model':response['model'],'input_tokens':response['usage']['input_tokens'],
                         'output_tokens':response['usage']['output_tokens'],'elapsed_seconds':stored['elapsed_seconds']})
            usage.update(response['usage']);latencies.append(stored['elapsed_seconds'])
    cohorts={}
    for cohort in ('unresolved','positive_control'):
        subset=[r for r in rows if r['cohort']==cohort]
        cohorts[cohort]={'requests':len(subset),'represented_lines':sum(r['line_count'] for r in subset),
                        'model_outcomes':dict(Counter('specific_service' if r['specific_service_proposed'] else r['model_choice'] for r in subset)),
                        'model_outcomes_line_weighted':dict(Counter({k:sum(r['line_count'] for r in subset if ('specific_service' if r['specific_service_proposed'] else r['model_choice'])==k) for k in sorted(set('specific_service' if r['specific_service_proposed'] else r['model_choice'] for r in subset))})),
                        'exact_pre_response_review_agreements':sum(r['review_agreement'] for r in subset),
                        'specific_service_proposals_disagreeing_with_review':sum(r['specific_service_proposed'] and not r['review_agreement'] for r in subset)}
    summary={'cohorts':cohorts,'usage':dict(usage),'advertised_input_price_usd_per_million':'0.042',
             'estimated_token_cost_usd':str(Decimal(usage['input_tokens'])*Decimal('0.042')/Decimal(1000000)),
             'latency_seconds':{'mean':round(sum(latencies)/len(latencies),4),'min':min(latencies),'max':max(latencies)},
             'models':sorted({r['model'] for r in rows}), 'accepted_new_matches':0,'baseline_outputs_changed':False,
             'limitations':['Pre-response references are Codex-assisted semantic judgments, not independent human truth.',
                            'Positive controls are deliberately clear cases; agreement is not unbiased accuracy.',
                            'No confidence threshold tuned or calibrated; no invoice replay or fresh holdout evaluation.',
                            'Cost is the documented token-rate estimate, not verified account billing.']}
    (HERE/'results.json').write_text(json.dumps({'summary':summary,'rows':rows},indent=2)+'\n')
    buf=io.StringIO(newline='');writer=csv.DictWriter(buf,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (HERE/'results.csv').write_bytes(buf.getvalue().encode())
    print(json.dumps(summary,indent=2))

if __name__=='__main__':evaluate()
