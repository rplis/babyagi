"""This file contains the code for the ChromaDB storage backend."""
import logging
import os
from typing import Dict, List

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction


class DefaultResultsStorage:
    """Default results storage class. This class uses ChromaDB
    as the storage backend."""

    def __init__(self):
        logging.getLogger("chromadb").setLevel(logging.ERROR)
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.results_store_name = os.getenv("RESULTS_STORE_NAME")
        self.llm_model = os.getenv("LLM_MODEL")
        # Create Chroma collection
        chroma_persist_dir = "chroma"
        chroma_client = chromadb.PersistentClient(
            settings=chromadb.config.Settings(
                persist_directory=chroma_persist_dir,
            )
        )

        metric = "cosine"

        embedding_function = OpenAIEmbeddingFunction(api_key=self.api_key)

        self.collection = chroma_client.get_or_create_collection(
            name=self.results_store_name,
            metadata={"hnsw:space": metric},
            embedding_function=embedding_function,
        )

    def add(self, task: Dict, result: str, result_id: str):
        """Add a result to the storage backend.
        Parameters
        ----------
        task : Dict
            Task dictionary
        result : str
            Result string
        result_id : str
            Result ID
        """
        # Break the function if LLM_MODEL starts with "human" (case-insensitive)
        if self.llm_model.startswith("human"):
            return
        # Continue with the rest of the function

        embeddings = None
        if len(self.collection.get(ids=[result_id], include=[])["ids"]) > 0:
            self.collection.update(
                ids=result_id,
                embeddings=embeddings,
                documents=result,
                metadatas={"task": task["task_name"], "result": result},
            )
        else:
            self.collection.add(
                ids=result_id,
                embeddings=embeddings,
                documents=result,
                metadatas={"task": task["task_name"], "result": result},
            )

    def query(self, query: str, top_results_num: int) -> List[dict]:
        """Query the storage backend.
        Parameters
        ----------
        query : str
            Query string
        top_results_num : int
            Number of top results to return
        Returns
        -------
        List[dict]
            List of results
        """
        count: int = self.collection.count()
        if count == 0:
            return []
        results = self.collection.query(
            query_texts=query,
            n_results=min(top_results_num, count),
            include=["metadatas"],
        )
        return [item["task"] for item in results["metadatas"][0]]
