"""
title: JARDET Zenodo Community Explorer
author: Open WebUI Tools
version: 1.0.0
license: MIT
description: Tools for exploring and searching JARDET (Journal of Agricultural Research, Development, Extension and Technology) records deposited in Zenodo
"""

import json
import requests
from typing import Optional
from pydantic import BaseModel, Field

BASE_URL = "https://zenodo.org/api"


class Tools:
    def __init__(self):
        """Initialize the JARDET Zenodo tools."""
        self.base_url = BASE_URL
        self.community_slug = "jardet"

    def list_jardet_records(self, page: int = 1, size: int = 10, sort: str = "newest") -> str:
        """
        List records from the JARDET Zenodo community.
        Returns paginated list of journal articles with titles, authors, and metadata.

        :param page: Page number for pagination (default: 1)
        :param size: Number of records per page (default: 10, max: 100)
        :param sort: Sort order - 'newest' (most recent) or 'bestmatch' (relevance)
        :return: JSON string containing record listings
        """
        try:
            params = {
                "q": "",
                "page": page,
                "size": min(size, 100),
                "sort": sort
            }

            url = f"{self.base_url}/communities/{self.community_slug}/records"
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            results = []
            for hit in data.get("hits", {}).get("hits", []):
                metadata = hit.get("metadata", {})
                results.append({
                    "id": hit.get("id"),
                    "title": metadata.get("title"),
                    "creators": self._format_creators(metadata.get("creators", [])),
                    "publication_date": metadata.get("publication_date"),
                    "description": self._truncate(metadata.get("description"), 300),
                    "doi": metadata.get("doi"),
                    "record_url": hit.get("links", {}).get("self_html") or f"https://zenodo.org/records/{hit.get('id')}",
                    "file_count": len(hit.get("files", []))
                })

            output = {
                "total": data.get("hits", {}).get("total"),
                "page": page,
                "size": size,
                "sort": sort,
                "results": results
            }
            return json.dumps(output, indent=2)

        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})

    def search_jardet(self, query: str, page: int = 1, size: int = 10) -> str:
        """
        Search JARDET records by keyword in title, abstract, or authors.

        :param query: Search keyword (e.g., 'rice', 'fertilizer', 'pest management')
        :param page: Page number for pagination (default: 1)
        :param size: Number of results per page (default: 10)
        :return: JSON string containing matching records
        """
        try:
            params = {
                "q": query,
                "page": page,
                "size": min(size, 100),
                "sort": "bestmatch"
            }

            url = f"{self.base_url}/communities/{self.community_slug}/records"
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            results = []
            for hit in data.get("hits", {}).get("hits", []):
                metadata = hit.get("metadata", {})
                results.append({
                    "id": hit.get("id"),
                    "title": metadata.get("title"),
                    "creators": self._format_creators(metadata.get("creators", [])),
                    "publication_date": metadata.get("publication_date"),
                    "description": self._truncate(metadata.get("description"), 300),
                    "doi": metadata.get("doi"),
                    "record_url": f"https://zenodo.org/records/{hit.get('id')}"
                })

            output = {
                "query": query,
                "total_matches": data.get("hits", {}).get("total"),
                "page": page,
                "size": size,
                "results": results
            }
            return json.dumps(output, indent=2)

        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})

    def get_record_details(self, record_id: str) -> str:
        """
        Get detailed metadata for a specific JARDET record by its Zenodo ID.

        :param record_id: The Zenodo record ID (e.g., '8296340')
        :return: JSON string with complete record details
        """
        try:
            url = f"{self.base_url}/records/{record_id}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            metadata = data.get("metadata", {})
            files = data.get("files", [])

            output = {
                "id": data.get("id"),
                "doi": data.get("doi"),
                "title": metadata.get("title"),
                "creators": self._format_creators(metadata.get("creators", [])),
                "publication_date": metadata.get("publication_date"),
                "description": metadata.get("description"),
                "keywords": metadata.get("keywords", []),
                "license": metadata.get("license", {}),
                "journal": metadata.get("journal", {}),
                "files": [
                    {
                        "filename": f.get("key"),
                        "size": f.get("size"),
                        "download_url": f.get("links", {}).get("self")
                    } for f in files
                ],
                "record_url": f"https://zenodo.org/records/{data.get('id')}"
            }
            return json.dumps(output, indent=2)

        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})

    def get_recent_jardet_articles(self, limit: int = 5) -> str:
        """
        Get the most recently published JARDET articles.

        :param limit: Number of recent articles to return (default: 5)
        :return: JSON string containing recent articles
        """
        try:
            params = {
                "q": "",
                "page": 1,
                "size": min(limit, 25),
                "sort": "newest"
            }

            url = f"{self.base_url}/communities/{self.community_slug}/records"
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            results = []
            for hit in data.get("hits", {}).get("hits", [])[:limit]:
                metadata = hit.get("metadata", {})
                results.append({
                    "title": metadata.get("title"),
                    "creators": self._format_creators(metadata.get("creators", [])),
                    "publication_date": metadata.get("publication_date"),
                    "doi": metadata.get("doi"),
                    "record_url": f"https://zenodo.org/records/{hit.get('id')}"
                })

            return json.dumps({
                "community": "JARDET",
                "recent_articles": results,
                "count": len(results)
            }, indent=2)

        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})

    def _format_creators(self, creators: list) -> list:
        """Format creator list into readable strings."""
        formatted = []
        for creator in creators:
            name = creator.get("name", "")
            affiliation = creator.get("affiliation", "")
            if affiliation:
                formatted.append(f"{name} ({affiliation})")
            else:
                formatted.append(name)
        return formatted

    def _truncate(self, text: Optional[str], max_length: int) -> Optional[str]:
        """Truncate text to specified length."""
        if not text:
            return text
        if len(text) <= max_length:
            return text
        return text[:max_length].rsplit(" ", 1)[0] + "..."


class Valves(BaseModel):
    """Configuration valves for JARDET tools."""
    community_slug: str = Field(
        default="jardet",
        description="Zenodo community slug for JARDET"
    )
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds",
        ge=5,
        le=120
    )