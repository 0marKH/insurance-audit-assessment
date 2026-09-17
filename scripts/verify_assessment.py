"""Run the final deliverable checks without rewriting any frozen evidence."""
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    commands=[['-m','unittest','discover','-s',s,'-q'] for s in ('tests','scripts/tests','hospital_4/tests','assessment_audit/tests')]
    commands += [['-m','hospital_audit','--check'],['-m','assessment_audit','--check'],
                 ['-m','hospital_4.manual_check'],['-m','assessment_audit.manual_check'],['scripts/check_hospital_4_baseline.py']]
    for command in commands:
        result=subprocess.run([sys.executable]+command,cwd=ROOT,capture_output=True,text=True)
        if result.returncode:
            print(result.stdout);print(result.stderr);raise SystemExit(result.returncode)
        print('PASS '+ ' '.join(command),flush=True)
    print('All 103 tests and source/baseline/submission/manual/reproduction checks passed.')

if __name__=='__main__':main()
