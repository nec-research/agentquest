from pydantic import BaseModel, Field
from typing import List

prompt = """You are a generative agent.
Carefully read the provided web page and extract the text relevant to a search query.
Additionally:
1. summarize your findings in a uniform text.
2. extract the 5 links most related to the query.

Rembember! The text will be used by another generative agent to choose the next action \
or to provide an answer to a question

Query: {query}

WebPage: {text}
"""


class ExtractedLink(BaseModel):
    title: str = Field(...)
    link: str = Field(...)


class ExtractedText(BaseModel):
    relevant_text: List[str] = Field(...)
    concise_summary: str = Field(...)
    useful_links: List[ExtractedLink] = Field(...)

    def to_str(self):
        text = f"Extracted text: {self.concise_summary}\n" f"Useful links:\n"
        for link in self.useful_links:
            text += f"\t- {link.title}: {link.link}\n"
        return text


class WebBrowse(BaseModel):
    """Retrieve the text relevant to a query from a web page."""

    page_url: str = Field(..., description="the web page URL")
    web_query: str = Field(...)

    def run(self, browser, llm=None):
        web_page = browser.scrape(self.page_url)
        system_prompt = prompt.format(query=self.web_query, text=web_page["text"])
        out = llm.invoke(response_model=ExtractedText, system_prompt=system_prompt)

        return out


class OnlineSearch(BaseModel):
    """Retrieve the top-5 search results from a web browser."""

    search_query: str = Field(...)

    def run(self, browser):
        search_results = browser.search(self.search_query)
        text = ""
        for x in search_results.values():
            text += (
                f"\nTitle: {x['title']}\nLink: {x['url']}\nSnippet: {x['snippet']}\n"
            )

        return text


class FileDownload(BaseModel):
    """Download a file from a link in a web page."""

    file_url: str = Field(...)

    def run(self, browser):
        event_log = browser.download(self.file_url)

        return event_log
