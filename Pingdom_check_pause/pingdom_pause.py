#!/usr/bin/env python3
"""
pingdom_checks.py

Pause or resume Pingdom checks by matching substrings in their names (OR logic).

Examples:
  # Pause all checks whose names contain any of: "api", "checkout"
  PINGDOM_API_TOKEN=xxxxx python pingdom_checks.py pause api checkout

  # Resume checks matching "staging" (dry run first)
  PINGDOM_API_TOKEN=xxxxx python pingdom_checks.py resume --dry-run staging

  # Use a custom env var name for the token
  PDM_TOKEN=xxxxx python pingdom_checks.py pause --token-env PDM_TOKEN prod
"""
import argparse
import os
import sys
import requests
from typing import List, Dict

BASE_URL = "https://api.pingdom.com/api/3.1"
TIMEOUT = 20

def get_token(env_name: str) -> str:
    token = os.getenv(env_name)
    if not token:
        sys.exit(f"ERROR: Missing API token. Set {env_name}=<your-token> in the environment.")
    return token

def fetch_all_checks(session: requests.Session) -> List[Dict]:
    url = f"{BASE_URL}/checks"
    r = session.get(url, timeout=TIMEOUT)
    if r.status_code == 401:
        sys.exit("ERROR: Unauthorized. Check your API token and account permissions.")
    r.raise_for_status()
    data = r.json()
    # Expecting {"checks":[{"id":123,"name":"..."} , ... ]}
    checks = data.get("checks", [])
    return checks

def filter_checks(checks: List[Dict], patterns: List[str]) -> List[Dict]:
    pats = [p.lower() for p in patterns]
    matched = []
    for c in checks:
        name = (c.get("name") or "").lower()
        if any(p in name for p in pats):
            matched.append(c)
    return matched

def bulk_pause_or_resume(session: requests.Session, check_ids: List[int], pause: bool) -> Dict:
    """
    Uses bulk endpoint:
      PUT /checks
      Form data: paused=true|false&checkids=comma,separated,ids
    """
    url = f"{BASE_URL}/checks"
    payload = {
        "paused": "true" if pause else "false",
    }
    if check_ids:
        payload["checkids"] = ",".join(str(i) for i in check_ids)
    r = session.put(url, data=payload, timeout=TIMEOUT)
    if r.status_code == 401:
        sys.exit("ERROR: Unauthorized. Check your API token and account permissions.")
    if r.status_code == 404:
        sys.exit("ERROR: Endpoint not found. Verify API base URL and version.")
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        msg = r.text.strip()
        sys.exit(f"ERROR: API request failed ({r.status_code}). {msg or e}")
    return r.json() if r.headers.get("Content-Type", "").startswith("application/json") else {}

def main():
    parser = argparse.ArgumentParser(
        description="Pause or resume Pingdom checks by matching name substrings (OR logic)."
    )
    sub = parser.add_subparsers(dest="action", required=True)

    for action in ("pause", "resume"):
        p = sub.add_parser(action, help=f"{action.capitalize()} matching checks")
        p.add_argument("patterns", nargs="*", help="One or more substrings to match against check names (OR logic).")
        p.add_argument("--token-env", default="PINGDOM_API_TOKEN",
                       help="Environment variable that holds your Pingdom API token (default: PINGDOM_API_TOKEN)")
        p.add_argument("--dry-run", action="store_true", help="Show what would be changed, without calling the API.")
        p.add_argument("--case-sensitive", action="store_true", help="Match case-sensitively (default: case-insensitive)")

    args = parser.parse_args()

    if not args.patterns:
        sys.exit("No patterns provided. Pass one or more strings to match (e.g., `pause api checkout`).")

    token = get_token(args.token_env)

    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        # Bulk pause uses form-encoded body in API 3.1
        "Content-Type": "application/x-www-form-urlencoded",
    })

    # 1) Fetch checks
    checks = fetch_all_checks(session)

    # 2) Filter by OR of substrings
    if args.case_sensitive:
        pats = args.patterns
        matched = [c for c in checks if any(p in (c.get("name") or "") for p in pats)]
    else:
        matched = filter_checks(checks, args.patterns)

    if not matched:
        sys.exit("No checks matched the provided patterns. Nothing to do.")

    # Prepare output list
    matched_ids = [int(c["id"]) for c in matched if "id" in c]
    matched_names = [c.get("name", f"id:{c.get('id')}") for c in matched]

    # 3) Dry run?
    if args.dry_run:
        verb = "PAUSE" if args.action == "pause" else "RESUME"
        print(f"[DRY RUN] Would {verb} {len(matched_ids)} checks:")
        for name, cid in zip(matched_names, matched_ids):
            print(f"  - {name} (id={cid})")
        sys.exit(0)

    # 4) Apply change (bulk)
    pause_flag = args.action == "pause"
    _ = bulk_pause_or_resume(session, matched_ids, pause=pause_flag)

    # 5) Report
    change_word = "Paused" if pause_flag else "Resumed"
    print(f"{change_word} {len(matched_ids)} checks:")
    for name, cid in zip(matched_names, matched_ids):
        print(f"  - {name} (id={cid})")

if __name__ == "__main__":
    main()
