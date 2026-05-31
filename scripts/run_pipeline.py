#!/usr/bin/env python3
"""Convenience script to run the full pipeline."""

from datetime import date

from enterprise_pipeline.main import run_pipeline

if __name__ == "__main__":
    run_pipeline(as_of_date=date(2026, 5, 28))
