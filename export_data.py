import aiohttp
import asyncio
import argparse
import json
from typing import Any

EVENTS_URL = "/api/spaces/{space_codename}/profiles/{profile_username}/events/"
METAGAME_DOMAIN = "https://meta-game.io"
PER_PAGE = 50

EVENTS_FILENAME = "events.json"

async def paginated_request(session: aiohttp.ClientSession, url: str, headers: dict[str, str], verify_ssl: bool):
    to_timestamp = None
    to_id = None
    result: list[dict[Any, Any]] = []
    while True:
        query_url = f'{url}?per_page={PER_PAGE}'
        if to_timestamp is not None:
            query_url = f'{query_url}&to_timestamp={to_timestamp}'
        if to_id is not None:
            query_url = f'{query_url}&to_id={to_id}'
        print(f'Querying {query_url}')
        async with session.get(query_url, verify_ssl=verify_ssl, headers=headers) as response:
            data = await response.json()
            items = data['items']
            result = result + items
            if len(items) < PER_PAGE:
                break
            if 'last_timestamp' in data:
                to_timestamp = data['last_timestamp']
            if 'last_id' in data:
                to_id = data['last_id']
    return result


async def main(domain: str, token: str, space_codename: str, profile_username: str, verify_ssl: bool):

    url = f'{domain}{EVENTS_URL.format(space_codename=space_codename, profile_username=profile_username)}'
    async with aiohttp.ClientSession() as session:
        headers = {'Authorization': f'Bearer {token}'}
        items = await paginated_request(session, url, headers, verify_ssl)
        print(f'Retrieved {len(items)} events')
        json_string = json.dumps(items, indent=4)
 
        # Writing to sample.json
        with open(EVENTS_FILENAME, "w") as outfile:
            outfile.write(json_string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Metagame export data script")
    parser.add_argument("--domain", help="The domain of the metagame instance", default=METAGAME_DOMAIN)
    parser.add_argument("token", help="Auth token")
    parser.add_argument("space", help="Space codename")
    parser.add_argument("profile", help="Profile username")
    parser.add_argument("--verifyssl", action=argparse.BooleanOptionalAction, default=True, help="Verify SSL. Disable for local development.")
    args = parser.parse_args()
    asyncio.run(main(args.domain, args.token, args.space, args.profile, args.verifyssl))