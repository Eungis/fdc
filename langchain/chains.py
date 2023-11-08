from __future__ import annotations
import inspect
from typing import Any, Dict, List, Optional, Tuple

from pydantic import Extra, Field

from langchain.schema.language_model import BaseLanguageModel
from langchain.schema import (
    BaseRetriever,
    BaseLLMOutputParser,
    StrOutputParser,
    Document,
    PromptValue,
    LLMResult,
    format_document
)
from langchain.prompts.base import BasePromptTemplate
from langchain.chains import LLMChain
from langchain.callbacks.manager import (
    CallbackManagerForChainRun,
    AsyncCallbackManagerForChainRun
)
from langchain.utils.input import get_colored_text

NO_DOCUMENT_FOUND_PROMPT = "No documents found related to the question."

class IRChain(LLMChain):

    prompt: BasePromptTemplate
    """Overall prompt template to put into the llm."""
    document_prompt: BasePromptTemplate
    """Document prompt template."""
    llm: BaseLanguageModel
    """LLM model to use"""
    retriever: BaseRetriever
    document_variable_name:str = "context"
    document_separator:str = "\n\n"
    output_key: str = "answer"
    output_parser: BaseLLMOutputParser = Field(default_factory=StrOutputParser)
    return_final_only: bool = False
    """Output parser to use.
    Defaults to one that takes the most likely string but does not change it 
    otherwise."""
    return_source_documents: bool = True
    """Return the retrieved source documents as part of the final result."""
    response_if_no_docs_found: str = NO_DOCUMENT_FOUND_PROMPT
    """If specified, the chain will return a fixed response if no docs 
    are found for the question. """
    
    """Retrieve the relevant documents given the user question, organize and format the prompt at once.
    Internally it uses `BaseRetriever` (here typically means IR) to get relevant documents,
    and format the documents according to the `document_prompt` to get doc_strings.
    Finally, format the prompt and put into the llm.
    
    Example:
        .. code-block:: python
        
            from chains import IRChain
            from retrievers import IRRetriever
            from langchain.prompts import PromptTemplate
            from langchain.llms import OpenAI
            
            # This controls how each document will be formatted. Specifically,
            # it will be passed to `format_document` - see that function for more
            # details.
            document_prompt = PromptTemplate.from_template(
                "Title {title}\n{page_content}"
            )
            
            prompt = PromptTemplate.from_template(
                "Answer the best as you can given the context: {context}"
            )
            
            # Prepare IRRetriever
            retriever = IRRetriever(ir_model=<YOUR_IR_MODEL>, top_k=5)
            
            # Initialize llm and IRChain
            llm = OpenAI(temperature=0)
            chain = IRChain(
                prompt = prompt,
                document_prompt = document_prompt,
                llm = llm,
                retriever = retriever,
                document_variable_name = "context",
                document_separator = "\n\n",
                output_key = "answer",
                return_source_documents = True
            )
            chain.predict(question="YOUR QUESTION")
    """

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
    
    @property
    def input_keys(self) -> List[str]:
        """Exclude document_variable_name from the input_variables to avoid validation error."""
        self.prompt = self.prompt.partial(**{self.document_variable_name:""})
        return self.prompt.input_variables

    @property
    def output_keys(self) -> List[str]:
        """Return the output keys."""
        _output_keys = [self.output_key]
        if self.return_source_documents and not self.return_final_only:
            _output_keys = _output_keys + ["source_documents"]
        return _output_keys
    
    def _get_docs(
        self,
        question: str,
        inputs: Dict[str, Any],
        *,
        run_manager: CallbackManagerForChainRun,
    ) -> List[Document]:
        """Get relevant documents."""
        docs = self.retriever.get_relevant_documents(
            question, callbacks=run_manager.get_child()
        )
        return docs
    
    async def _aget_docs(
        self,
        question: str,
        inputs: Dict[str, Any],
        *,
        run_manager: AsyncCallbackManagerForChainRun
    ) -> List[Document]:
        """Get relevant documents."""
        docs = await self.retriever.aget_relevant_documents(
            question, callbacks=run_manager.get_child()
        )
        return docs
    
    
    def _get_inputs(self, docs: List[Document]) -> str:
        """Construct document_variable_name.

        Args:
            docs: List of documents to format and then join into single input

        Returns:
            doc string of combined retrieved documents
        """
        # Format each document according to the prompt
        doc_strings = [format_document(doc, self.document_prompt) for doc in docs]
        doc_strings = self.document_separator.join(doc_strings)
        return doc_strings
    
    
    def create_outputs(self, llm_result: LLMResult) -> List[Dict[str, Any]]:
        """Create outputs from response."""
        result = [
            # Get the text of the top generated string.
            {
                self.output_key: self.output_parser.parse_result(generation),
                "full_generation": generation,
            }
            for generation in llm_result.generations
        ]
        
        if self.return_source_documents:
            docs = self.retriever.retrieved_docs
            for r, doc in zip(result, docs):
                r["source_documents"] = doc
            
        if self.return_final_only:
            result = [{self.output_key: r[self.output_key]} for r in result]
        return result
    
    
    def generate(
        self,
        input_list: List[Dict[str, Any]],
        run_manager: Optional[CallbackManagerForChainRun] = None,
    ) -> LLMResult:
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        questions = [inputs["question"] for inputs in input_list]
        
        accepts_run_manager = (
            "run_manager" in inspect.signature(self._get_docs).parameters
        )
        if accepts_run_manager:
            docs_list = [
                self._get_docs(question, inputs, run_manager=_run_manager)
                for question, inputs in zip(questions, input_list)
            ]
        else:
            docs_list = [
                self._get_docs(question, inputs)
                for question, inputs in zip(questions, input_list)
            ]
            
        doc_strings_list = [self._get_inputs(docs) for docs in docs_list]
        
        prompts, stop = self.prep_prompts(
            input_list = input_list,
            doc_strings_list = doc_strings_list,
            run_manager = _run_manager
        )
        
        return self.llm.generate_prompt(
            prompts,
            stop,
            callbacks=_run_manager.get_child(),
            **self.llm_kwargs
        )
    
    
    async def agenerate(
        self,
        input_list: List[Dict[str, Any]],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> LLMResult:
        _run_manager = run_manager or CallbackManagerForChainRun.get_noop_manager()
        questions = [inputs["question"] for inputs in input_list]
        
        accepts_run_manager = (
            "run_manager" in inspect.signature(self._get_docs).parameters
        )
        if accepts_run_manager:
            docs_list = [
                await self._aget_docs(question, inputs, run_manager=_run_manager)
                for question, inputs in zip(questions, input_list)
            ]
        else:
            docs_list = [
                await self._aget_docs(question, inputs)
                for question, inputs in zip(questions, input_list)
            ]
        
        doc_strings_list = [self._get_inputs(docs) for docs in docs_list]
        
        prompts, stop = await self.aprep_prompts(
            input_list = input_list,
            doc_strings_list = doc_strings_list,
            run_manager = _run_manager
        )
        
        return await self.llm.agenerate_prompt(
            prompts,
            stop,
            callbacks=_run_manager.get_child(),
            **self.llm_kwargs
        )
    
    
    def prep_prompts(
        self,
        input_list: List[Dict[str, Any]],
        doc_strings_list: List[str],
        run_manager: Optional[CallbackManagerForChainRun] = None
    ) -> Tuple[List[PromptValue], Optional[List[str]]]:
        stop = None
        if len(input_list) == 0:
            return [], stop
        if "stop" in input_list[0]:
            stop = input_list[0]["stop"]
        prompts = []
        for inputs, doc_strings in zip(input_list, doc_strings_list):
            inputs[self.document_variable_name] = doc_strings
            if self.memory is not None:
                inputs[self.memory.memory_key] = self.memory.buffer_as_str
            prompt = self.prompt.format_prompt(**inputs)
            _colored_text = get_colored_text(prompt.to_string(), "green")
            _text = "Prompt after formatting:\n" + _colored_text
            if run_manager:
                run_manager.on_text(_text, end="\n", verbose=self.verbose)
            if "stop" in inputs and inputs["stop"] != stop:
                raise ValueError(
                    "If `stop` is present in any inputs, should be present in all."
                )
            prompts.append(prompt)
        return prompts, stop
    
    
    async def aprep_prompts(
        self,
        input_list: List[Dict[str, Any]],
        doc_strings_list: List[str],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None
    ) -> Tuple[List[PromptValue], Optional[List[str]]]:
        stop = None
        if len(input_list) == 0:
            return [], stop
        if "stop" in input_list[0]:
            stop = input_list[0]["stop"]
        prompts = []
        for inputs, doc_strings in zip(input_list, doc_strings_list):
            inputs[self.document_variable_name] = doc_strings
            if self.memory is not None:
                inputs[self.memory.memory_key] = self.memory.buffer_as_str
            prompt = self.prompt.format_prompt(**inputs)
            _colored_text = get_colored_text(prompt.to_string(), "green")
            _text = "Prompt after formatting:\n" + _colored_text
            if run_manager:
                run_manager.on_text(_text, end="\n", verbose=self.verbose)
            if "stop" in inputs and inputs["stop"] != stop:
                raise ValueError(
                    "If `stop` is present in any inputs, should be present in all."
                )
            prompts.append(prompt)
        return prompts, stop

    @property
    def _chain_type(self) -> str:
        return "IR Chain"