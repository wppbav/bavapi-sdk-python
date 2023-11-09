import argparse
import asyncio
import sys
from typing import Dict, List, Optional

from bavapi.http import HTTPClient

QUERY_URL = "https://fount.wppbav.com/api/v2/brands/741"


async def run_test(
    url: str,
    repeat: int = 100,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 5.0,
) -> None:
    async with HTTPClient(
        url,
        headers=headers or {},
        timeout=timeout,
    ) as http:
        tasks = [http.client.get("/") for _ in range(repeat)]

        print(f"Performing {repeat} requests to {url}")
        await asyncio.gather(*tasks)
        print("Done!")


async def main(argv: List[str]) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=QUERY_URL)
    parser.add_argument("-r", "--repeat", type=int, default=100)
    parser.add_argument("-t", "--token", default="")
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args(argv)

    if args.token and args.url == QUERY_URL:
        headers = {
            "Authorization": f"Bearer {args.token}",
            "User-Agent": "BAVAPI SDK Python - SSL Tests",
        }
    else:
        headers = {}

    await run_test(args.url, args.repeat, headers, args.timeout)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]))
