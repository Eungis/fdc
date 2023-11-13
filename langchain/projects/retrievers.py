import asyncio
import warnings
import logging
from typing import Any, Dict, List, TypeVar, Literal
from functools import partial
from langchain.schema import BaseRetriever, Document
from langchain.callbacks.manager import CallbackManagerForRetrieverRun, AsyncCallbackManagerForRetrieverRun

logging = logging.getLogger(__name__)
warnings.filterwarnings("ignore")

# IR DB only allows two types: 'local' and 'es'
IR_DB_TYPE = Literal["local", "es"]

class IRRetriever(BaseRetriever):
    """IRRetriever(LangChain interface) to retrieve documents using IR."""
    
    ir_model: Any
    """IR vectorizer"""
    top_k: int=5
    """Number of documents to return"""
    """Search arguments of IR"""
    retrieved_docs: List[Document]=[]
    """Retrieved documents from IR"""
    
    class Config:
        """Configuration for this pydantic object"""
        arbitrary_types_allowed = True
    
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun=None
    ) -> List[Document]:
        """Get documents relevant to a query.
        Args:
            query: String to find relevant documents for
            run_manager: The callbacks handler to use
        Returns:
            List of relevant documents
        """
        
        docs = self.ir_model.search(query, top_k=self.top_k)
        
        self.retrieved_docs = []
        for i, doc in enumerate(docs, start=1):
            context = doc.pop("context")
            self.retrieved_docs += [
                Document(
                    page_content=context,
                    metadata=doc,
                    type="IR Document"
                )
            ]
        return self.retrieved_docs
    
    async def _aget_relevant_documents(
        self, query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun=None
    ) -> List[Document]:
        """Asynchronously get documents relevant to a query.
        Args:
            query: String to find relevant documents for
            run_manager: The callbacks handler to use
        Returns:
            List of relevant documents
        """
        return await asyncio.get_running_loop().run_in_executor(
            None, partial(self._get_relevant_documents, run_manager=run_manager), query
        )