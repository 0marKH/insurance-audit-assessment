import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/assessment"


def split(invoice_id):
    return "held_aside" if int(hashlib.sha256(invoice_id.encode()).hexdigest()[:8], 16) % 5 == 0 else "development"


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load(directory=DATA / "invoices"):
    directory = Path(directory)
    return (read_csv(directory / "hospital_1_invoices.csv"),
            read_csv(directory / "hospital_1_line_items.csv"))
