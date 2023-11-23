# [⛓] Langchain [⛓]

## **Description**

- The purpose of the langchain theme is to log the lessons learned while using it, particularly for exclusive use with large language models (LLM).
    - The .ipynb files here are personally summarized content while reading the official documents of Langchain. In addition, the process of interpreting the source code of Langchain was included to understand specific functionalities. Through this, a foundation was established to analyze Langchain, which is relatively high-level, at a `low-level` to customize it.
    - Through the above process, a custom LLMChain and custom Retriever were created. The company the writter is personally associated with uses an undisclosed internal Retriever model, feeling the need to wrap it with Langchain's interface.
    - You can refer to it by looking into `chains` directory, and you can see a detailed guide about how to use it in guide.ipynb.
        - You must have your own IR model. Due to the confidentiality issue, here does not disclose the IR model that I have used during modules building.


    | theme | description | location | is_project | last_update |
    | :---: | :---: | :---: | :--: | :--: |
    | chains |  <b>custom LLMChain</b>  |  fdc/langchain/chains  | True | 23.11 |


## **chains**
**[TODO]**
- Solve the max_token exceeding error.
- Integrate the IRRetriever with LangChain RetrievalQA.


**[Description]**

:: Main modules: [chains.py, retrievers.py]

- Its purpose is on integrating the IR and LangChain interface.
- It wraps the IR model with LangChain BaseRetriever. (see retreivers.py)
- It inherits the LangChain LLMChain to make IRChain, which enable the user to seamlessly connect IRRetriever and LLMChain. (see chains.py)

- For detailed usage instructions of the modules, kindly consult the `guide.ipynb` file located within the chains directory.


**[Install & Usage]**
* use requirements.txt in `chains` directory

  ```shell
  pip install -r requirements.txt
  ```

* usage of _chains modules

  ```python
  from retrievers import IRRetriever
  from chains import IRChain
  from langchain.prompts import PromptTemplate
  from langchain.llms import OpenAI
  # This controls how each document will be formatted. Specifically,
  # it will be passed to `format_document` - see that function for
  # more details.
  document_prompt = PromptTemplate.from_template(
    "Title {title}\n{page_content}"
  )

  prompt = PromptTemplate.from_template(
      "Answer the best as you can given the context: {context}"
  )

  # Prepare IRRetriever (Below usage may be different by IR model)
  # Please refer to the retrievers.py code to see
  # the way to wrap your own IR model.
  import IR # YOUR IR model
  ir_model = IR()
  retriever = IRRetriever(ir_model=ir_model, top_k=5)


  # Initialize llm and IRChain
  llm = OpenAI(temperature=0)
  chain = IRChain(
      prompt = prompt,
      document_prompt = document_prompt,
      llm = llm,
      retriever = retriever,
      document_variable_name = "context",
      document_separator = "\n\n",
      output_key = "answer"
  )
  chain.predict(question="YOUR QUESTION")
  ```
