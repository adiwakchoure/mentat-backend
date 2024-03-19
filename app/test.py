from typing import List
from pydantic import BaseModel, HttpUrl
from settings import tavily, braveSync, marvin
from models import InsightCreate
import trafilatura
import time


@marvin.fn
def generate_insights(question: str, Dict) -> InsightCreate:
    """
    This function takes a question and some useful information as input and returns an Insight object.
    The insight object should be filled in the context of answering the question
    """
    return


class SearchResultSite(BaseModel):
    title: str
    url: HttpUrl
    description: str = None
    # content: str = None
    # summary: str = None


def get_link_text(url: str) -> str:
    try:
        downloaded = trafilatura.fetch_url(str(url))
        if downloaded is None:
            raise ValueError("Failed to download the page")
        result = trafilatura.extract(downloaded)
        if not result:
            raise ValueError("No content extracted")
        return result
    except Exception as e:
        raise ValueError(str(e))


def search_and_extract_content(
    query: str, num_results: int = 1
) -> List[SearchResultSite]:
    search_results = braveSync.search(q=query, count=num_results)
    sites = []
    for result in search_results.web_results:
        if result:
            filtered_data = {
                key: value
                for key, value in result.items()
                if key in SearchResultSite.__annotations__
            }
            site = SearchResultSite(**filtered_data)
            try:
                # site.content = get_link_text(url=site.url)
                sites.append(site)
            except ValueError as ve:
                print(f"Error processing URL {site.url}: {ve}")
    return sites


query = "What has Amazon done to differentiate itself from its competitors?"
# sites = search_and_extract_content(query=query, num_results=3)
# for site in sites:
#     # print(
#     #     f"\n\nTitle: {site.title}, \nURL: {site.url}, \nDesc: {site.description}"
#     #     f"\n\nTitle: {site.title}, \nURL: {site.url}, \nDesc: {site.description}, \nContent: {site.content}"
#     # )
#     print(generate_insights(query, site))

# # print(sites)


def generate_n_insights(question: str, n: int) -> List[InsightCreate]:
    sites = search_and_extract_content(query=question, num_results=n)
    insights = [generate_insights(question, site) for site in sites]
    return insights


x = generate_n_insights(question=query, n=1)
print(x)
