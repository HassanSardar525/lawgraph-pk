from __future__ import annotations

from .extraction import DelimitedClaimExtractor
from .ingestion import IncrementalIndexer
from .retrieval import HierarchicalRetriever
from .store import SQLiteGraphStore


class LawGraphService:
    def __init__(self, database_path: str = ":memory:") -> None:
        self.store = SQLiteGraphStore(database_path)
        self.indexer = IncrementalIndexer(self.store, DelimitedClaimExtractor())
        self.retriever = HierarchicalRetriever(self.store)
