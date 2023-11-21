# [🖨️] Parser [🖨️]

## **Description**

- The purpose of the parser theme is to develop tools for preprocessing documents, particularly for exclusive use with large language models (LLM).
    - Unlike general string text, files in formats such as HTML, PDF, PPTX, etc., pose challenges for direct integration into an LLM.
    - Before providing these files to the LLM, it is advisable to preprocess, transform, and parse them into string text for feeding into the model.
    - The `parser` theme is designed to streamline the preprocessing process. It encompasses modules that cleanse and split files into several documents, enabling direct input into the LLM.
    - Additionally, you can reference it for data preprocessing, especially when creating your own LLM, retrieval model, summarizer model, or any other NLP-based AI model.



    | theme | description | location | is_project | last_update |
    | :---: | :---: | :---: | :--: | :--: |
    | html |  <b>html parser</b>  |  fdc/parser/html  | True | 23.11 |
    | pdf |  <b>pdf parser</b> (dev -ing)  |  fdc/parser/pdf  | False | 23.10 |


## **html**
**[TODO]**
- Add more funtionality in HTMLSplitter._split_chunk
- Think of how to handle the context window


**[Description]**

:: Main modules: [cleanser.py, splitter.py]

- The system pre-processes files in the html format. If your document is in another format, please convert it to an HTML file beforehand.

- The `HTMLCleanser` in cleanser.py removes invalid tags and attributes within the BeautifulSoup object.
- The `HTMLSplitter` in splitter.py divides the file into several documents without altering the HTML contents.
    - When developing an AI model or utilizing the LLM, the existence of token_max can make it challenging to input the entire document into the model.
    - Consequently, you may have been splitting the documents to avoid exceeding the token_max, using strategies such as doc_stride, etc.
    - If you simply truncate the document based on the token length, the content may be chopped off, resulting in a loss of context.
    - The `HTMLSplitter` takes into account the token_max when splitting the file, ensuring that the HTML file is divided without compromising context.

- [as-is] The contents (e.g., tables) inside the document were truncated without considering the context due to the maximum token limit imposed by the AI model.

- [to-be] The contents (e.g., tables) inside the document will be split without losing context and structure, with a guarantee that the splitted chunks do not exceed the maximum tokens.

    Firstly, split the target file into a set of documents before indexing, while considering the maximum token limit accepted by the model.

    Secondly, insert the splitted documents into the model as usual.

- For detailed usage instructions of the modules, kindly consult the `guide.ipynb` file located within the html directory.


**[Install & Usage]**
---
* use requirements.txt in `html` directory

  ```shell
  pip install -r requirements.txt
  ```

* usage of _html modules

  ```python
  from bs4 import BeautifulSoup
  from _html.cleanser import HTMLCleanser
  from _html.splitter import HTMLSplitter

  txt = """<table><thead><tr><th>Header 1</th><th>Header 2</th>
  <th>Header 3</th></tr></thead><tbody><tr><td>Data 1</td><td>Data 2</td><td>Data 3</td></tr><tr><td>Data 4</td><td>Data 5</td><td>Data 6</td></tr></tbody></table>"""
  soup = BeautifulSoup(txt, "lxml")
  cleanser = HTMLCleanser()
  soup = cleanser.cleanse_html(soup)
  splitter = HTMLSplitter(soup=soup, length_func=len, token_max=200)   chunks = splitter.get_chunks()
  chunks = splitter.split_chunks(chunks)
  documents = splitter.make_documents(chunks)
  ```
