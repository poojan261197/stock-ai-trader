from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request


def request_json(url: str, method: str = "GET", payload: dict | None = None) -> dict | list | float | bool:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Small client for the realtime trading agent API.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8005", help="API base URL")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health", help="Fetch service health")
    subparsers.add_parser("status", help="Fetch service metadata")

    trade_parser = subparsers.add_parser("trade", help="Submit a single trade data point")
    trade_parser.add_argument("--close", type=float, required=True, help="Close price")
    trade_parser.add_argument("--volume", type=float, required=True, help="Trade volume")

    reset_parser = subparsers.add_parser("reset", help="Reset account balance")
    reset_parser.add_argument("--money", type=float, default=None, help="New balance; omit to reset to default")

    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    try:
        if args.command == "health":
            result = request_json(f"{base_url}/health")
        elif args.command == "status":
            result = request_json(f"{base_url}/metadata")
        elif args.command == "trade":
            result = request_json(
                f"{base_url}/trade",
                method="POST",
                payload={"data": [args.close, args.volume]},
            )
        else:
            result = request_json(
                f"{base_url}/reset",
                method="POST",
                payload={"money": args.money},
            )
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(body)
        return exc.code
    except urllib.error.URLError as exc:
        print(f"Request failed: {exc.reason}")
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
