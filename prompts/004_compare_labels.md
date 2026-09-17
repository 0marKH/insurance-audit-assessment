# Prompt 004 — compare labelled output with the built engine

Date: 17 September 2026.

## User prompt

Great, i see decision coverage more than necessary but we can move forward, now do this:

Create a script to compare the labeled output against what we have built.

## Implementation note

Added a standalone comparison of the original label CSV with the saved invoice
audit JSONL. It produces invoice-level comparisons, differences, review cases
and a summary, reusing the existing evaluation metric definitions. The frozen
engine, existing predictions, original data and evaluation files are unchanged.
