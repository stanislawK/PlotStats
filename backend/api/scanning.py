from .settings import settings
import aiohttp
import asyncio
import json

referer = settings.base_url
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": referer,
    "Sec-Ch-Ua-Platform": '"Linux"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua": '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "*/*",
}

url = (
    referer
    + "/_next/data/cXum9ePye3URXYcgekl6V/pl/wyniki/sprzedaz/dzialka/pomorskie/gdansk/gdansk/gdansk.json"
)
params = {
    "ownerTypeSingleSelect": "ALL",
    "distanceRadius": 10,
    "priceMin": 100000,
    "priceMax": 150000,
    "viewType": "listing",
    "searchingCriteria": "sprzedaz",
    "searchingCriteria": "dzialka",
    "searchingCriteria": "pomorskie",
    "searchingCriteria": "gdansk",
    "searchingCriteria": "gdansk",
    "searchingCriteria": "gdansk",
}


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as resp:
            print(50 * "-")
            print(resp.status)
            print(50 * "-")
            print(resp.headers)
            print(50 * "-")
            body = await resp.json()
            print(50 * "-")
            print(body)
            if body:
                json.dump(body, "body.json")
            print(50 * "-")
            print(resp)
            print(50 * "-")
            print(dir(resp))


asyncio.run(main())
