from typing import Any

import aiohttp

from api.settings import settings

HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    ),
    "Referer": settings.base_url,
    "Sec-Ch-Ua-Platform": '"Linux"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "*/*",
}

TOKEN_REGEX = r"(?<=buildId\":).+?(?=\",)"


async def make_request(url: str) -> tuple[int, dict[str, Any]]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as resp:
            if resp.status != 200:
                return resp.status, {}
            body = await resp.json()
            return 200, body
