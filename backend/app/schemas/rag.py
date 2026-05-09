"""Interface contract §7.1 — locked by Day 2.

A calls index_chunks(run_id, docs: list[RawDoc]) after Scraper finishes.
B owns chunking.py / index.py; A imports RawDoc from here.
"""
from typing import Literal

from pydantic import BaseModel


class RawDoc(BaseModel):
    url: str
    text: str
    source_type: Literal[
        "landing", "pricing", "review_snippet", "community", "hn", "stackexchange"
    ]
    competitor: str | None = None
