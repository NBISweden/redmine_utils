#!/usr/bin/env python3
"""
Fetch assignee names for Redmine issue IDs listed in a text file (one ID per line).
Outputs tab-separated: id <TAB> assignee

Usage:
    python get_assignees.py -c config.yaml issue_ids.txt

Requires a config.yaml with fields:
    url: "https://your-redmine-instance"
    api_key: "your_api_key"
"""

import sys
import argparse
import requests
import yaml
import pdb

def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)


def get_assignee(base_url, api_key, issue_id):
    """Return the assignee name for a given issue ID, or None if unassigned."""
    url = f"{base_url.rstrip('/')}/issues/{issue_id}.json"
    resp = requests.get(url, headers={"X-Redmine-API-Key": api_key}, timeout=15)
    resp.raise_for_status()
    issue = resp.json().get("issue", {})
    assigned_to = issue.get("assigned_to")
    pi_email = [ field for field in issue['custom_fields'] if field['name']=="PI e-mail" ][0]['value']
    if pi_email:
        pi_email = pi_email.strip().lower()
    else:
        pi_email = [ field for field in issue['custom_fields'] if field['name']=="Principal Investigator" ][0]['value'].strip().lower()
    if assigned_to:
        return [ assigned_to.get("name"), pi_email]
    return [None, pi_email]


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Redmine assignee names for a list of issue IDs."
    )
    parser.add_argument(
        "-c", "--config",
        required=True,
        metavar="CONFIG",
        help="Path to config.yaml with Redmine URL and API key.",
    )
    parser.add_argument(
        "ids_file",
        metavar="IDS_FILE",
        help="Text file with one issue ID per line.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_url = config["url"]
    api_key = config["api_key"]

    with open(args.ids_file) as f:
        issue_ids = [line.strip() for line in f if line.strip()]

    pi_assignee = {}
    print("id\tassignee\tpi_email")

    for issue_id in sorted(issue_ids):
        try:
            assignee, pi_email = get_assignee(base_url, api_key, issue_id)
            print(f"{issue_id}\t{assignee or '(unassigned)'}\t{pi_email}")
            if assignee:
                pi_assignee[pi_email] = assignee
        except requests.HTTPError as e:
            print(f"{issue_id}\tERROR: {e}", file=sys.stderr)
            print(f"{issue_id}\tERROR")
        except Exception as e:
            print(f"{issue_id}\tERROR: {e}", file=sys.stderr)
            print(f"{issue_id}\tERROR")


    print("\n\n\nPIs with any assignee:")
    print("pi\tassignee")
    for pi_email, assignee in sorted(pi_assignee.items()):
        print(f"{pi_email}\t{assignee}")

if __name__ == "__main__":
    main()
