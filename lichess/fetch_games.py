import argparse
import sys

import requests
from tqdm import tqdm
from . import SERVER_URI


def download_games(estimate, opts):
    """Download games as JSON objects and writes them to opts.outfile.

    Args:
        estimate (int): Estimated number of games to download (for progress bar)
        opts (argparse.Namespace): Command line options, see main()
    """
    headers = {"Accept": "application/x-ndjson"}
    if opts.token:
        headers["Authorization"] = f"Bearer {opts.token}"

    params = {"pgnInJson": "true", "clocks": "true", "opening": "true"}
    if opts.max:
        params["max"] = opts.max

    t = tqdm(total=estimate)
    r = requests.get(
        f"{SERVER_URI}/games/user/{opts.user}", params=params, headers=headers, stream=True
    )

    for game in r.iter_lines():
        t.update()
        print(game.decode("utf-8"), file=opts.outfile)

    t.close()


def estimate_games(user):
    """Finds the total number of games for a user."""
    r = requests.get(f"{SERVER_URI}/user/{user}").json()
    return r["count"]["all"]


def parse_opts():
    parser = argparse.ArgumentParser(
        description="Download all games for a lichess user"
    )
    parser.add_argument("user", help="The user name to download games for")
    parser.add_argument("--token", help="An OAuth2 token (speeds up downloads)")
    parser.add_argument(
        "--outfile",
        type=argparse.FileType("w"),
        help="Where to put the data",
        default="-",
    )
    parser.add_argument("--max", type=int, help="Max number of games to download")
    return parser.parse_args()


def main():
    opts = parse_opts()
    if opts.max:
        n = opts.max
    else:
        n = estimate_games(opts.user)

    print(f"Found {n} games, beginning download...", file=sys.stderr)
    download_games(n, opts)


if __name__ == "__main__":
    main()
