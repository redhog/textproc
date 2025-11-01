import aiohttp
import asyncio
import html2text
from jsonpath_ng import parse

from .. import jsonutils
from .. import decorators

WIKIPEDIA_API_URL = "https://en.wikipedia.org/w/api.php"

def set_by_path(item, key, value):
    if "." in key:
        path, name = key.rsplit(".", 1)
    parse(path).find(item)[0].value[name] = value

@decorators.map
async def wikipedia(pipeline, item, input_key, output_key=None):
    if output_key is None: output_key = input_key
    out = []
    for match in jsonutils.flatten_matches(parse(input_key).find(item)):
        out.append({
            "name": match,
            "content": await _fetch_wikipedia(match)})
    jsonutils.set_by_path(item, output_key, out)
    return item

async def _fetch_wikipedia(person_name: str) -> str:    
    """
    Fetches a Wikipedia article and returns it as Markdown.
    """
    headers = {
        "User-Agent": "MyWikipediaBot/1.0 (https://example.com; email@example.com)"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(
                WIKIPEDIA_API_URL,
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": person_name,
                    "format": "json"
                }) as response:
            search_result = await response.json()
            if not search_result['query']['search']:
                return f"No Wikipedia article found for '{person_name}'"
            page_title = search_result['query']['search'][0]['title']
            
        async with session.get(
                WIKIPEDIA_API_URL,
                params={
                    "action": "parse",
                    "page": page_title,
                    "prop": "text",
                    "format": "json"
                }) as response:
            page_result = await response.json()
            html_content = page_result.get("parse", {}).get("text", {}).get("*", "")
            if not html_content:
                return f"No content found for '{page_title}'"

        return html2text.html2text(html_content)
