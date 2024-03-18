import time
from typing import List
from trafilatura import fetch_url, extract
from models import CompanyInfo, InsightPoint, InsightType
from enum import Enum
import requests
from bs4 import BeautifulSoup
from settings import braveSync


class SearchService:
    def search(self, query: str, num_results: int):
        x = time.perf_counter()
        search_results = braveSync.search(q=query, count=num_results)
        print(time.perf_counter() - x)
        return search_results.web_results


class ResearchService:
    def extract_key_points(self, text: str) -> List[str]:
        """
        Extract 3-5 key points from the given text that could be used for opposition research.
        """
        pass

    def summarize_text(self, text: str) -> str:
        """
        Generate a concise summary of the given text in 50 words or less.
        """
        pass

    def research_company(self, url: str) -> CompanyInfo:
        downloaded = fetch_url(url)
        text = extract(
            downloaded, include_comments=False, include_tables=False, no_fallback=True
        )

        return CompanyInfo(
            url=url,
            summary=self.summarize_text(text),
            key_points=self.extract_key_points(text),
        )

    def query_handler(self, query: str, id: str) -> List[InsightPoint]:
        # Simulate the process of performing market research based on the query and return a bunch of InsightPoints
        return mockData


class UrlRelevanceService:
    def url_relevance(self, url: str, description: str = None) -> "UrlRelevance":
        """
        Determines the relevance of the provided `url` for oppositional research and insight generation about a company.

        The function returns an object of type `UrlRelevance` which includes:
        - `url`: The input URL.
        - `is_relevant`: A boolean indicating whether the URL is relevant for the purpose.
        - `relevance_score`: A float between -1 (not relevant) and 1 (highly relevant) indicating the level of relevance.
        - `insights`: A list of enum values representing the types of insights about the company we could get from the content in the URL. Must be zero or more out of these: [class InsightType(str, Enum): COMPANY_OVERVIEW, PRODUCTS_SERVICES, COMPETITIVE_POSITION, MARKET_ANALYSIS, FINANCIAL_PERFORMANCE, MANAGEMENT_LEADERSHIP, STRATEGY_DIRECTION, BUSINESS_MODEL, INDUSTRY_INSIGHTS]
        - `description`: A string containing the description of the URL's content.
        """

        import time

        x = time.perf_counter()
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Extracting the description from the meta tag
        description = soup.find("meta", attrs={"name": "description"})
        if description:
            result = UrlRelevance(url, True, 0.5, [], description["content"])
        else:
            result = UrlRelevance(url, True, 0.5, [], None)

        print(time.perf_counter() - x)
        return result
