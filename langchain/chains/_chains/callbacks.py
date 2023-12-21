from typing import Any
from langchain.callbacks.base import AsyncCallbackHandler


class StreamingLLMCallbackHandler(AsyncCallbackHandler):
    """Callback handler to streaming llm tokens through the websocket.
    Example:
        .. code-block:: python

            Example:
        .. code-block:: python
            import asyncio
            import json
            from {YOUR_IR} import IR
            from retrievers import IRRetriever
            from chains import IRChain
            from callbacks import StreamingLLMCallbackHandler
            from langchain.prompts import PromptTemplate
            from langchain.llms import OpenAI

            # Prepare IRRetriever (Below usage may be different)
            ir_model = IR()
            retriever = IRRetriever(ir_model=ir_model, top_k=5)

            # Initialize llm and IRChain
            llm_config = {"temperature": 0}
            streaming_config = {
                "streaming": True,
                "verbose": True,
                "callback_manager": AsyncCallbackManager(
                    [
                        StreamingLLMCallbackHandler(websocket)
                    ]
                )
            }
            llm_config.update(streaming_config)
            llm = OpenAI(**llm_config)

            # Initialize chain
            prompt = PromptTemplate.from_template(
                "Answer the best as you can given the context: \n{context}\n"
                "Answer the question: \n{question}"
            )
            chain = load_ir_chain(
                llm = llm,
                retriever = retriever,
                prompt = prompt,
                input_key = "question",
                document_variable_name = "context"
            )

            async def accept(websocket):
                request = websocket.recv()
                request = json.loads(request)

                query = request["question"]
                answer = await chain.acall({"question": query})

            if __name__ == "__main__":
                logger.info("Backend application is on.")

                # Run backend socket
                try:
                    start_server = websockets.serve(accept, {backend_ip}, {backend_port})
                    asyncio.get_event_loop().run_until_complete(start_server)
                    asyncio.get_event_loop().run_forever()
                    logger.info("WebSocket connection is on.")
                except KeyboardInterrupt as e:
                    logger.info("Backend application is teminated by administrator command.")
                except Exception as e:
                    logger.debug(f"Error occured while answering the question : {e}")
    """

    def __init__(self, websocket):
        self.websocket = websocket

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        await self.websocket.send(token)
