import time
from functools import wraps

from _chains.chains import IRChain
from prompts import DOCUMENT_PROMPT
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts.base import BasePromptTemplate
from langchain.schema import BaseRetriever
from langchain.schema.language_model import BaseLanguageModel


def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        elapsed = end - start
        return (result, elapsed)

    return wrapper


def load_ir_chain(
    llm: BaseLanguageModel,
    retriever: BaseRetriever,
    prompt: BasePromptTemplate,
    input_key: str,
    document_variable_name: str,
    memory: bool = None,
    memory_key: str = "",
    verbose: bool = False,
):
    if memory is not None:
        if memory_key == "":
            raise ValueError("You must specify memory_key if you want to add memory to the Chain.")
        memory = ConversationBufferWindowMemory(
            k=3,
            memory_key=memory_key,
            input_key=input_key,
            output_key="answer",
            return_messages=True,
        )

    chain = IRChain(
        llm=llm,
        retriever=retriever,
        prompt=prompt,
        document_prompt=DOCUMENT_PROMPT,
        document_variable_name=document_variable_name,
        output_key="answer",
        memory=memory,
        verbose=verbose,
    )

    return chain
