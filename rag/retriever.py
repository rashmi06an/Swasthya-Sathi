from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


@dataclass
class MedicalRAG:
    guideline_path: str
    embedding_model: str

    def __post_init__(self) -> None:
        self.guideline_path = str(Path(self.guideline_path))
        self.embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)
        self.vectorstore = self._build_vectorstore()

    def _build_vectorstore(self) -> FAISS:
        raw_text = Path(self.guideline_path).read_text(encoding="utf-8")
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_text(raw_text)
        documents = [
            Document(page_content=chunk, metadata={"source": "WHO-style guidance", "chunk_id": index})
            for index, chunk in enumerate(chunks)
        ]
        return FAISS.from_documents(documents, self.embeddings)

    def retrieve_guidance(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        results = self.vectorstore.similarity_search(query, k=top_k)
        return [
            {
                "content": item.page_content.strip().replace("\n", " "),
                "source": item.metadata.get("source", "guidance"),
            }
            for item in results
        ]
