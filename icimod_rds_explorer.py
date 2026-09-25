"""
title: ICIMOD RDS Dataset Explorer
author: Ravindra Rana
version: 1.0.0
license: MIT
description: Tools for exploring and searching ICIMOD Regional Database System (RDS) datasets via GeoAPI
"""

import json
import requests
from typing import Optional
from pydantic import BaseModel, Field

BASE_URL = "https://rds.icimod.org/geoapi/public"


class Tools:
    def __init__(self):
        """Initialize the ICIMOD RDS tools."""
        self.base_url = BASE_URL

    class ListDatasetsInput(BaseModel):
        page: int = Field(
            default=1, description="Page number for pagination (starts from 1)"
        )
        limit: int = Field(
            default=20, description="Number of results per page (max recommended: 50)"
        )
        theme: Optional[str] = Field(
            default=None, description="Filter datasets by theme keyword"
        )

    def list_datasets(
        self, page: int = 1, limit: int = 20, theme: Optional[str] = None
    ) -> str:
        """
        List datasets from ICIMOD Regional Database System (RDS).
        Returns paginated list of dataset metadata including titles, abstracts, and URLs.

        :param page: Page number for pagination (default: 1)
        :param limit: Number of results per page (default: 20)
        :param theme: Optional theme filter for datasets
        :return: JSON string containing dataset listings
        """
        try:
            params = {"page": page, "limit": limit}
            if theme:
                params["theme"] = theme

            response = requests.get(
                f"{self.base_url}/datasets", params=params, timeout=30
            )
            response.raise_for_status()
            data = response.json()

            # Format results for readability
            results = []
            for item in data.get("results", []):
                results.append(
                    {
                        "title": item.get("title"),
                        "abstract": (
                            item.get("abstract", "")[:300] + "..."
                            if item.get("abstract")
                            and len(item.get("abstract", "")) > 300
                            else item.get("abstract")
                        ),
                        "published_date": item.get("published_date"),
                        "page_url": item.get("page_url"),
                        "thumbnail_url": item.get("thumbnail_url"),
                    }
                )

            output = {
                "total": data.get("total"),
                "page": data.get("page"),
                "limit": data.get("limit"),
                "results_count": len(results),
                "results": results,
            }
            return json.dumps(output, indent=2)

        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Failed to parse response: {str(e)}"})

    def search_datasets(self, query: str, page: int = 1, limit: int = 20) -> str:
        """
        Search datasets in ICIMOD RDS by keyword in title or abstract.

        :param query: Search keyword (e.g., 'glacier', 'Nepal', 'precipitation')
        :param page: Page number for pagination (default: 1)
        :param limit: Number of results per page (default: 20)
        :return: JSON string containing matching datasets
        """
        try:
            # Fetch a larger batch to search through
            params = {"page": 1, "limit": 100}
            response = requests.get(
                f"{self.base_url}/datasets", params=params, timeout=30
            )
            response.raise_for_status()
            data = response.json()

            query_lower = query.lower()
            matches = []

            for item in data.get("results", []):
                title = (item.get("title") or "").lower()
                abstract = (item.get("abstract") or "").lower()

                if query_lower in title or query_lower in abstract:
                    matches.append(
                        {
                            "title": item.get("title"),
                            "abstract": (
                                item.get("abstract", "")[:300] + "..."
                                if item.get("abstract")
                                and len(item.get("abstract", "")) > 300
                                else item.get("abstract")
                            ),
                            "published_date": item.get("published_date"),
                            "page_url": item.get("page_url"),
                            "thumbnail_url": item.get("thumbnail_url"),
                        }
                    )

            # Apply pagination on matches
            start = (page - 1) * limit
            end = start + limit
            paginated = matches[start:end]

            output = {
                "query": query,
                "total_matches": len(matches),
                "page": page,
                "limit": limit,
                "results": paginated,
            }
            return json.dumps(output, indent=2)

        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Failed to parse response: {str(e)}"})

    def get_dataset_details(self, dataset_uuid: str) -> str:
        """
        Get detailed metadata for a specific dataset by its UUID.
        Extract UUID from page_url like: https://rds.icimod.org/metadata/{uuid}

        :param dataset_uuid: The UUID of the dataset (e.g., '6672c5e7-eb77-4a60-ba9d-87999be32226')
        :return: JSON string with dataset details
        """
        try:
            # Try to get metadata from the API
            url = f"{self.base_url}/datasets/{dataset_uuid}"
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                return json.dumps(response.json(), indent=2)

            # Fallback: try to fetch the metadata page
            return json.dumps(
                {
                    "note": "Direct API endpoint not available for this UUID",
                    "metadata_url": f"https://rds.icimod.org/metadata/{dataset_uuid}",
                    "suggestion": "Visit the metadata URL for full details",
                },
                indent=2,
            )

        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})

    def get_datasets_by_theme(self, theme: str, page: int = 1, limit: int = 20) -> str:
        """
        Get datasets filtered by a specific theme.

        :param theme: Theme name to filter by (e.g., 'climate', 'water', 'land cover')
        :param page: Page number for pagination (default: 1)
        :param limit: Number of results per page (default: 20)
        :return: JSON string containing datasets for the theme
        """
        try:
            params = {"page": page, "limit": limit, "theme": theme}
            response = requests.get(
                f"{self.base_url}/datasets", params=params, timeout=30
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("results", []):
                results.append(
                    {
                        "title": item.get("title"),
                        "abstract": (
                            item.get("abstract", "")[:300] + "..."
                            if item.get("abstract")
                            and len(item.get("abstract", "")) > 300
                            else item.get("abstract")
                        ),
                        "published_date": item.get("published_date"),
                        "page_url": item.get("page_url"),
                        "thumbnail_url": item.get("thumbnail_url"),
                    }
                )

            output = {
                "theme": theme,
                "total": data.get("total"),
                "page": data.get("page"),
                "limit": data.get("limit"),
                "results": results,
            }
            return json.dumps(output, indent=2)

        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})

    def get_recent_datasets(self, limit: int = 10) -> str:
        """
        Get the most recently published datasets.

        :param limit: Number of recent datasets to return (default: 10)
        :return: JSON string containing recent datasets sorted by published date
        """
        try:
            params = {"page": 1, "limit": 50}
            response = requests.get(
                f"{self.base_url}/datasets", params=params, timeout=30
            )
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            # Sort by published_date descending
            results.sort(key=lambda x: x.get("published_date") or "", reverse=True)

            recent = []
            for item in results[:limit]:
                recent.append(
                    {
                        "title": item.get("title"),
                        "published_date": item.get("published_date"),
                        "abstract": (
                            item.get("abstract", "")[:200] + "..."
                            if item.get("abstract")
                            and len(item.get("abstract", "")) > 200
                            else item.get("abstract")
                        ),
                        "page_url": item.get("page_url"),
                        "thumbnail_url": item.get("thumbnail_url"),
                    }
                )

            return json.dumps(
                {"recent_datasets": recent, "count": len(recent)}, indent=2
            )

        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})

    def get_dataset_statistics(self) -> str:
        """
        Get summary statistics about the ICIMOD RDS dataset collection.

        :return: JSON string with total dataset count and sample information
        """
        try:
            response = requests.get(
                f"{self.base_url}/datasets", params={"page": 1, "limit": 1}, timeout=30
            )
            response.raise_for_status()
            data = response.json()

            # Get a sample of datasets to analyze
            sample_response = requests.get(
                f"{self.base_url}/datasets",
                params={"page": 1, "limit": 100},
                timeout=30,
            )
            sample_data = sample_response.json()

            # Analyze countries mentioned in abstracts
            countries = [
                "Nepal",
                "India",
                "Bhutan",
                "Pakistan",
                "Afghanistan",
                "Bangladesh",
                "China",
                "Myanmar",
            ]
            country_counts = {c: 0 for c in countries}

            data_types = {
                "raster": 0,
                "vector": 0,
                "point": 0,
                "polygon": 0,
                "line": 0,
                "grid": 0,
            }

            for item in sample_data.get("results", []):
                text = (
                    (item.get("title") or "") + " " + (item.get("abstract") or "")
                ).lower()
                for country in countries:
                    if country.lower() in text:
                        country_counts[country] += 1

                for dtype in data_types:
                    if dtype in text:
                        data_types[dtype] += 1

            return json.dumps(
                {
                    "total_datasets": data.get("total"),
                    "sample_size_analyzed": len(sample_data.get("results", [])),
                    "country_mentions": {
                        k: v for k, v in country_counts.items() if v > 0
                    },
                    "data_type_mentions": {
                        k: v for k, v in data_types.items() if v > 0
                    },
                },
                indent=2,
            )

        except requests.exceptions.RequestException as e:
            return json.dumps({"error": f"Request failed: {str(e)}"})
