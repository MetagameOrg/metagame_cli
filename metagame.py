import aiohttp
import asyncio
import argparse
import json
import os
from typing import Any

GET_EVENTS_URL = "/api/spaces/{space_codename}/profiles/{profile_username}/events/"
CREATE_EVENTS_URL = "/api/spaces/{space_codename}/profiles/{profile_username}/create_events/"
METAGAME_DOMAIN = "https://meta-game.io"
PER_PAGE = 50

EVENTS_FILENAME = "events.json"
RESULTS_DIR = 'results'

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

def create_dir(parent_dir: str, dir_name: str):
    dir_path = os.path.join(parent_dir, dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

def write_profile_json(profile_username: str, space_codename: str, item_type: str, items: list[dict[Any, Any]]):
    json_string = json.dumps(items, indent=4)
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    space_dir = create_dir(RESULTS_DIR, space_codename)
    profile_dir = create_dir(space_dir, profile_username)
    filename = os.path.join(profile_dir, f'{item_type}.json')
    print(f'Writing {profile_username} {item_type} to {filename}')
    with open(filename, "w") as outfile:
        outfile.write(json_string)


async def export_profile(domain: str, token: str, space_codename: str, profile_username: str, verify_ssl: bool):

    url = f'{domain}{GET_EVENTS_URL.format(space_codename=space_codename, profile_username=profile_username)}'
    async with aiohttp.ClientSession() as session:
        headers = {'Authorization': f'Bearer {token}'}
        items = await paginated_request(session, url, headers, verify_ssl)
        print(f'Retrieved {len(items)} events')
        write_profile_json(profile_username, space_codename, 'events', items)


async def import_profile(domain: str, token: str, space_codename: str, profile_username: str, verify_ssl: bool):
    url = f'{domain}{CREATE_EVENTS_URL.format(space_codename=space_codename, profile_username=profile_username)}'

IMPORT_COMMAND = "import"
EXPORT_COMMAND = "export"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Metagame export data script")
    parser.add_argument("command", help="action to perform", choices=[EXPORT_COMMAND, IMPORT_COMMAND])
    parser.add_argument("token", help="Auth token")
    parser.add_argument("space", help="Space codename")
    parser.add_argument("profile", help="Profile username")
    parser.add_argument("--domain", help="The domain of the metagame instance", default=METAGAME_DOMAIN)
    parser.add_argument("--verifyssl", action=argparse.BooleanOptionalAction, default=True, help="Verify SSL. Disable for local development.")
    args = parser.parse_args()
    if args.command == EXPORT_COMMAND:
        asyncio.run(export_profile(args.domain, args.token, args.space, args.profile, args.verifyssl))
    if args.command == IMPORT_COMMAND:
        asyncio.run(import_profile(args.domain, args.token, args.space, args.profile, args.verifyssl))