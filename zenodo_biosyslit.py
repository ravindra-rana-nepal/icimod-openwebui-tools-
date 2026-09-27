"""
title: Zenodo — Biodiversity Literature Repository
author: Ravindra Rana
version: 1.0.0
license: MIT
description: Search the Biodiversity Literature Repository (biosyslit) Zenodo community.
requirements: requests
"""

import requests
from pydantic import BaseModel, Field
from typing import Callable, Any


COMMUNITY_ID = "biosyslit"
COMMUNITY_NAME = "Biodiversity Literature Repository"
BASE_URL = f"https://zenodo.org/api/communities/{COMMUNITY_ID}/records"


class Tools:
    class Valves(BaseModel):
        """Admin-configurable settings."""
        timeout: int = Field(default=30, description="HTTP timeout (seconds).")
        default_size: int = Field(default=10, description="Default records per query.")
        max_size: int = Field(default=50, description="Hard cap on records per query.")

    def __init__(self):
        self.valves = self.Valves()

    # ------------------------------------------------------------------
    def _fetch(
        self,
        page: int = 1,
        size: int = None,
        query: str = "",
        sort: str = "newest",
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> dict:
        size = min(size or self.valves.default_size, self.valves.max_size)
        params = {"q": query or "", "l": "list", "p": page, "s": size, "sort": sort}

        if __event_emitter__:
            __event_emitter__({
                "type": "status",
                "data": {"description": "Querying Biodiversity Literature Repository...", "done": False},
            })

        try:
            r = requests.get(BASE_URL, params=params, timeout=self.valves.timeout)
            r.raise_for_status()
            data = r.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Zenodo request failed: {e}"}
        except ValueError as e:
            return {"error": f"Invalid JSON: {e}"}

        hits = data.get("hits", {})
        records = hits.get("hits", [])
        total = hits.get("total", 0)

        results = []
        for rec in records:
            md = rec.get("metadata", {}) or {}
            results.append({
                "id": rec.get("id"),
                "doi": rec.get("doi"),
                "title": md.get("title"),
                "publication_date": md.get("publication_date"),
                "resource_type": (md.get("resource_type") or {}).get("title"),
                "creators": [c.get("name") for c in (md.get("creators") or [])],
                "description": (md.get("description") or "")[:500],
                "url": rec.get("links", {}).get("self_html") or rec.get("links", {}).get("self"),
                "keywords": md.get("keywords", []),
                "taxonomic_keywords": md.get("taxonomic_keywords", []),
            })

        if __event_emitter__:
            __event_emitter__({
                "type": "status",
                "data": {"description": f"Retrieved {len(results)} of {total} records.", "done": True},
            })

        return {
            "community": COMMUNITY_NAME,
            "community_id": COMMUNITY_ID,
            "page": page,
            "size": size,
            "total": total,
            "returned": len(results),
            "records": results,
        }

    @staticmethod
    def _format(result: dict) -> str:
        if "error" in result:
            return f"⚠️ {result['error']}"
        lines = [
            f"# {result['community']}",
            f"*Page {result['page']} · showing {result['returned']} of {result['total']} total records*\n",
        ]
        for i, r in enumerate(result["records"], 1):
            creators = ", ".join(r["creators"][:5]) or "Unknown"
            if len(r["creators"]) > 5:
                creators += " et al."
            taxa = ", ".join(r.get("taxonomic_keywords", [])[:5])
            taxa_line = f"- Taxa: {taxa}\n" if taxa else ""
            lines.append(
                f"**{i}. {r['title']}**\n"
                f"- Authors: {creators}\n"
                f"- Date: {r['publication_date']} · Type: {r['resource_type']}\n"
                f"- DOI: {r['doi']}\n"
                f"- URL: {r['url']}\n"
                f"{taxa_line}"
                f"- Abstract: {r['description']}...\n"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def search_biosyslit(
        self,
        query: str = "",
        page: int = 1,
        size: int = 10,
        sort: str = "newest",
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Search the Biodiversity Literature Repository (biosyslit) Zenodo community.

        :param query: Free-text search query (empty string lists everything).
        :param page: Page number (1-based).
        :param size: Number of records per page.
        :param sort: 'newest', 'oldest', 'bestmatch', or 'mostviewed'.
        :return: Formatted list of matching records, including taxonomic keywords.
        """
        return self._format(
            self._fetch(page=page, size=size, query=query, sort=sort,
                        __event_emitter__=__event_emitter__)
        )