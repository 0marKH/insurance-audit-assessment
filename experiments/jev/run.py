"""Small explicit Jev trial, cached by exact request; never changes audit outputs."""
import argparse
import hashlib
import json
import math
import os
import shlex
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
ENDPOINT='https://api.typesafe.ai/v1/systemone'


def api_key():
    key=os.environ.get('TYPESAFE_API_KEY')
    if key:return key
    source=ROOT/'.env'
    if source.is_file():
        for line in source.read_text().splitlines():
            line=line.strip().removeprefix('export ')
            if '=' not in line:continue
            name,value=line.split('=',1)
            if name.strip()=='TYPESAFE_API_KEY':
                parts=shlex.split(value,comments=True)
                if len(parts)==1 and parts[0]:return parts[0]
    raise ValueError('TYPESAFE_API_KEY is not configured')


def validate(response, payload):
    if not isinstance(response,dict) or not isinstance(response.get('answers'),dict):raise ValueError('Missing answer object')
    if response.get('model') not in (payload['model'],'jev-latest'):raise ValueError('Unexpected response model')
    if set(response['answers'])!=set(payload['questions']):raise ValueError('Question IDs differ')
    for name,question in payload['questions'].items():
        answer=response['answers'][name]
        if answer.get('type')!='choice' or answer.get('choice') not in question['criteria']:raise ValueError('Invalid choice')
        probs=answer.get('probabilities',{})
        if set(probs)!=set(question['criteria']):raise ValueError('Probability options differ from request')
        values=list(probs.values())+[answer.get('confidence')]
        if any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1 for v in values):raise ValueError('Invalid probabilities/confidence')
        if abs(sum(probs.values())-1)>0.01 + 1e-9:raise ValueError('Probability mass is not approximately one')
        if probs[answer['choice']] < max(probs.values()):raise ValueError('Selected choice is not highest probability')
    usage=response.get('usage',{})
    if any(type(usage.get(k)) is not int or usage[k]<0 for k in ('input_tokens','output_tokens')):raise ValueError('Invalid usage')


def call(payload, key):
    body=json.dumps(payload,sort_keys=True,separators=(',',':')).encode()
    req=urllib.request.Request(ENDPOINT,data=body,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
    attempts=0;start=time.monotonic()
    while True:
        attempts+=1
        try:
            with urllib.request.urlopen(req,timeout=45) as response:
                value=json.loads(response.read().decode())
            return value, attempts, round(time.monotonic()-start,4)
        except urllib.error.HTTPError as error:
            # Do not log headers, credentials or an uncontrolled provider error body.
            if error.code in (429,529) and attempts<3:
                time.sleep(2**(attempts-1));continue
            raise ValueError(f'TypeSafe HTTP {error.code}; request failed after {attempts} attempt(s)') from None
        except urllib.error.URLError:
            raise ValueError('TypeSafe connection failed; no response cached') from None


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--requests',type=Path,default=HERE/'requests.jsonl')
    parser.add_argument('--limit',type=int,default=23)
    args=parser.parse_args()
    if not 1<=args.limit<=50:parser.error('Use a bounded pilot of 1-50 requests')
    requests=[json.loads(s) for s in args.requests.read_text().splitlines()][:args.limit]
    cache=HERE/'responses';cache.mkdir(exist_ok=True)
    key=None
    for index,row in enumerate(requests,1):
        payload=row['request'];body=json.dumps(payload,sort_keys=True,separators=(',',':')).encode()
        digest=hashlib.sha256(body).hexdigest();path=cache/(digest+'.json')
        if path.exists():
            stored=json.loads(path.read_text());validate(stored['response'],payload)
            print(f'{index}/{len(requests)} {row["request_id"]}: cached',flush=True);continue
        if key is None:key=api_key()
        response,attempts,elapsed=call(payload,key)
        stored={'request_sha256':digest,'request_id':row['request_id'],'endpoint':ENDPOINT,
                'requested_model':payload['model'],'received_at_utc':datetime.now(timezone.utc).isoformat(),
                'elapsed_seconds':elapsed,'http_attempts':attempts,'response':response}
        # Preserve raw model evidence even if it fails schema validation.
        path.write_text(json.dumps(stored,indent=2)+'\n')
        validate(response,payload)
        a=response['answers']['service_match']
        print(f'{index}/{len(requests)} {row["request_id"]}: {a["choice"]}, confidence={a["confidence"]}',flush=True)

if __name__=='__main__':main()
