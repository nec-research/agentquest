from pypdf import PdfReader
from pydantic import BaseModel, Field
from typing import List

# ==========================================================================================
# MAP STAGE
# ==========================================================================================
map_prompt = """You are a generative agent.
Carefully read the provided pdf page and extract the text relevant to a search query.

Rembember! The text will be used by another generative agent to choose the next action \
or to provide an answer to a question

Query: {query}

Text: {text}
"""


class MapText(BaseModel):
    relevant_text: List[str] = Field(...)


# ==========================================================================================
# REDUCE STAGE
# ==========================================================================================
reduce_prompt = """You are a generative agent.
I give tou the list of text extracted from a pdf relevant to a search query.

Carefully summarize the findings in a uniform text.

Rembember! The text will be used by another generative agent to choose the next action \
or to provide an answer to a question

Query: {query}

Text: {text}
"""


class ReduceText(BaseModel):
    final_text: str = Field(...)


# ==========================================================================================
# FILE READER TOOL
# ==========================================================================================
class FileReader(BaseModel):
    """Read a local .pdf file getting the text relevant to a query."""

    file_name: str = Field(...)
    file_query: str = Field(...)

    def run(self, llm=None):
        # Load the file
        try:
            reader = PdfReader(f"/tmp/{self.file_name}")
        except Exception as e:
            return f"Error: {str(e)}"
        summaries = []
        # Read the first 3 pages
        for p_idx in range(min(len(reader.pages), 3)):
            # Extract the page text
            page = reader.pages[p_idx].extract_text()
            # Map stage: LLM extract raw text relevant to a query
            system_prompt = map_prompt.format(query=self.file_query, text=page)
            out = llm.invoke(response_model=MapText, system_prompt=system_prompt)
            summaries += out.relevant_text
        # Reduce stage: LLM merges raw text and produce uniform text
        system_prompt = reduce_prompt.format(query=self.file_query, text=summaries)
        out = llm.invoke(response_model=ReduceText, system_prompt=system_prompt)
        return out.final_text


# llm = LLMClient(OPENAI_KEY, model='gpt-4o')
# tool = FileReader(
#    file_name='test_paper.pdf',
#    file_query='how many brazilian authors?'
# )
# tool.run(llm)
