from langchain.prompts import PromptTemplate

DOCUMENT_PROMPT = PromptTemplate.from_template("Title {title}\n{page_content}")