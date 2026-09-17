"""Reproduce frozen H4 v1 in a temporary workspace; never overwrite current outputs."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from hospital_4.comparison import BASELINE, verified_baseline


def main():
    verified_baseline()
    # Copy modules so their resolved __file__ roots point at the temporary tree.
    # Original assessment data is read-only input through a directory symlink.
    with tempfile.TemporaryDirectory(prefix='h4-v1-reproduction-') as folder:
        target=Path(folder)
        (target/'data').symlink_to(ROOT/'data',target_is_directory=True)
        for name in ('hospital_audit','contract_extractor','tests','profiles'):
            shutil.copytree(ROOT/name,target/name,ignore=shutil.ignore_patterns('__pycache__'))
        (target/'policies').mkdir()
        for p in (ROOT/'policies').glob('hospital_1*.json'):shutil.copy2(p,target/'policies'/p.name)
        shutil.copytree(ROOT/'outputs/hospital_1',target/'outputs/hospital_1')
        shutil.copy2(ROOT/'outputs/hospital_1.rules.json',target/'outputs/hospital_1.rules.json')
        for name in ('hospital_4','outputs/hospital_4'):
            shutil.copytree(BASELINE/name,target/name)
        for p in (BASELINE/'policies').glob('*.json'):shutil.copy2(p,target/'policies'/p.name)
        shutil.copy2(BASELINE/'submission.csv',target/'submission.csv')
        subprocess.run([sys.executable,'-m','hospital_4','--check'],cwd=target,check=True,stdout=subprocess.DEVNULL)
    print('Frozen H4 v1: all 25 snapshot hashes and byte-for-byte pipeline reproduction passed.')

if __name__=='__main__':main()
