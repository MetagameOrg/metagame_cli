import aiohttp
import asyncio
import argparse

EVENTS_URL = "/api/spaces/{space_codename}/profiles/{profile_username}/events/"
METAGAME_DOMAIN = "https://meta-game.io"

async def main(domain: str, token: str, space_codename: str, profile_username: str, verify_ssl: bool):

    url = f'{domain}{EVENTS_URL.format(space_codename=space_codename, profile_username=profile_username)}'
    async with aiohttp.ClientSession() as session:
        headers = {'Authorization': f'Bearer {token}'}
        async with session.get(url, verify_ssl=verify_ssl, headers=headers) as response:

            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])

            data = await response.json()
            print(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Metagame export data script")
    parser.add_argument("--domain", help="The domain of the metagame instance", default=METAGAME_DOMAIN)
    parser.add_argument("token", help="Auth token")
    parser.add_argument("space", help="Space codename")
    parser.add_argument("profile", help="Profile username")
    parser.add_argument("--verifyssl", action=argparse.BooleanOptionalAction, default=True, help="Verify SSL. Disable for local development.")
    args = parser.parse_args()
    asyncio.run(main(args.domain, args.token, args.space, args.profile, args.verifyssl))