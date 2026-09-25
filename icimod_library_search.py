"""
title: ICIMOD Library Search
author: Ravindra Rana
version: 0.1.0
license: MIT
description: Search the ICIMOD knowledge library via its public records API.
requirements: requests
"""

import asyncio
from typing import Optional, Callable, Any

import requests
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        API_URL: str = Field(
            default="https://lib.icimod.org/api/records",
            description="ICIMOD records API endpoint",
        )
        MAX_RESULTS: int = Field(
            default=10,
            description="How many records to return per search (1–50)",
        )
        SORT: str = Field(
            default="bestmatch",
            description="Sort order: bestmatch, newest, oldest, mostrecent",
        )

    def __init__(self):
        self.valves = self.Valves()
        self.citation = True

    # -------- internal (not exposed to the model) --------

    def _search_sync(self, query: str, size: int, sort: str):
        r = requests.get(
            self.valves.API_URL,
            params={"q": query, "size": size, "sort": sort},
            timeout=30,
            headers={"Accept": "application/json"},
        )
        r.raise_for_status()
        return r.json()

    async def _emit(self, emitter, description, done=False):
        if emitter:
            await emitter(
                {"type": "status", "data": {"description": description, "done": done}}
            )

    # -------- the tool the model calls --------

    async def search_icimod(
        self,
        query: str,
        max_results: int = 0,
        __event_emitter__: Optional[Callable[[dict], Any]] = None,
    ) -> str:
        """
        Search the ICIMOD knowledge library for publications, reports, datasets and
        other records.

        Use this whenever the user asks about ICIMOD, SERVIR, the Hindu Kush Himalaya,
        glaciers, cryosphere, water resources, disaster risk, climate adaptation, or any
        topic that may have an ICIMOD publication. Returns the matching records with
        their titles, dates and links.

        :param query: Search keywords, e.g. "glacier melt Nepal" or "SERVIR flood mapping".
        :param max_results: Optional override for how many records to return (1–50). Leave 0 to use the default.
        :return: A formatted list of matching records, or a message saying none were found.
        """
        size = max_results if 0 < max_results <= 50 else self.valves.MAX_RESULTS

        await self._emit(
            __event_emitter__, f'🔍 Searching ICIMOD library for "{query}"...'
        )

        try:
            data = await asyncio.to_thread(
                self._search_sync, query, size, self.valves.SORT
            )
        except requests.HTTPError as e:
            return f"ICIMOD API error: {e.response.status_code} {e.response.reason}"
        except requests.RequestException as e:
            return f"Could not reach the ICIMOD API: {e}"

        hits = data.get("hits", {}).get("hits", [])
        total = data.get("hits", {}).get("total", len(hits))

        if not hits:
            await self._emit(__event_emitter__, "No results found.", done=True)
            return f"No ICIMOD records found for '{query}'."

        lines = [f"Found {total} ICIMOD records for '{query}'. Showing {len(hits)}:\n"]
        for i, hit in enumerate(hits, 1):
            md = hit.get("metadata", {}) or {}
            rid = hit.get("id", "")
            url = (
                hit.get("links", {}).get("self_html")
                or f"https://lib.icimod.org/records/{rid}"
            )
            date = (
                md.get("publication_date")
                or md.get("created")
                or md.get("date")
                or "n/a"
            )
            creators = md.get("creators") or md.get("authors") or []
            if isinstance(creators, list):
                names = [
                    c.get("person_or_org", {}).get("name") or c.get("name") or str(c)
                    for c in creators
                ]
                authors = "; ".join(n for n in names if n)[:200]
            else:
                authors = str(creators)[:200]

            desc = (md.get("description") or "").strip().replace("\n", " ")
            desc = desc[:300] + ("…" if len(desc) > 300 else "")

            lines.append(
                f"{i}. {md.get('title', 'Untitled')}\n"
                f"   record_id: {rid}\n"
                f"   date: {date}\n"
                + (f"   authors: {authors}\n" if authors else "")
                + (f"   summary: {desc}\n" if desc else "")
                + f"   url: {url}"
            )

        await self._emit(__event_emitter__, f"✅ Found {total} records.", done=True)
        return "\n".join(lines)
