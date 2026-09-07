"""
plot_redmine_time.py

Fetch all logged time for a Redmine user and produce two plots saved as a PNG:
  1. Time distribution across all projects (pie + bar chart)
  2. Time distribution across issues within a specific project (horizontal bar chart)

Usage:
    python plot_redmine_time.py -c config.yaml -u "Jane Doe" -p "My Project"

    # With explicit date range:
    python plot_redmine_time.py -c config.yaml -u "Jane Doe" -p "My Project" \
        -s 2024-01-01 -e 2024-12-31 -o time_report.png

Dates default to the past 365 days when omitted.

The script expects the redmine_utils repo to be on PYTHONPATH, or for
lib/Redmine_apis.py to sit next to this script (or in ./lib/).

Setup:
    pip install requests matplotlib pyyaml
"""

import argparse
import sys
import datetime
from pathlib import Path
from collections import defaultdict

import yaml
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# ---------------------------------------------------------------------------
# Locate and import Redmine_apis
# ---------------------------------------------------------------------------
def _find_and_import_redmine_apis():
    """Try a few common locations for lib/Redmine_apis.py."""
    search_dirs = [
        Path(__file__).parent,
        Path(__file__).parent / "lib",
        Path.cwd(),
        Path.cwd() / "lib",
    ]
    for d in search_dirs:
        if (d / "Redmine_apis.py").exists():
            sys.path.insert(0, str(d.parent if d.name == "lib" else d))
            break

    try:
        from lib.Redmine_apis import Redmine_server_api
    except ModuleNotFoundError:
        try:
            from Redmine_apis import Redmine_server_api  # type: ignore
        except ModuleNotFoundError:
            sys.exit(
                "ERROR: Could not import Redmine_apis. "
                "Make sure lib/Redmine_apis.py is accessible or add the "
                "redmine_utils repo to PYTHONPATH."
            )
    return Redmine_server_api


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------
def aggregate_by_project(time_entries):
    """Return {project_name: total_hours} sorted descending."""
    totals = defaultdict(float)
    for entry in time_entries:
        totals[entry["project"]["name"]] += entry["hours"]
    return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))


def aggregate_by_issue(time_entries, target_project_id):
    """
    Return a list of dicts for issues belonging to target_project_id.
    Each dict: {issue_id, subject, hours}
    """
    totals = defaultdict(lambda: {"subject": "", "hours": 0.0})
    for entry in time_entries:
        if entry["project"]["id"] != target_project_id:
            continue
        iid = entry["issue"]["id"] if "issue" in entry else f"(no issue – {entry['project']['name']})"
        totals[iid]["hours"] += entry["hours"]

    result = [{"issue_id": k, **v} for k, v in totals.items()]
    result.sort(key=lambda x: x["hours"], reverse=True)
    return result


def enrich_issue_subjects(api, issue_rows):
    """Add 'subject' to each row by fetching issue details (uses cache)."""
    for row in issue_rows:
        iid = row["issue_id"]
        if isinstance(iid, int):
            try:
                row["subject"] = api.fetch_issue(iid).get("subject", f"Issue #{iid}")
            except Exception:
                row["subject"] = f"Issue #{iid}"
        else:
            row["subject"] = str(iid)
    return issue_rows


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
COLORS = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3",
    "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD",
]


def _wrap(label, max_len=28):
    """Truncate long labels with an ellipsis."""
    return label if len(label) <= max_len else label[: max_len - 1] + "…"


def plot_all(project_totals, issue_rows, project_name, output_path, user_label,
             start_date, end_date):
    """
    Build a three-panel figure:
      - Top-left:  Pie chart of time per project
      - Top-right: Horizontal bar chart of time per project
      - Bottom:    Horizontal bar chart of time per issue in target project
    """
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor("#F8F9FA")

    fig.suptitle(
        f"Redmine time report  ·  {user_label}  ·  {start_date} → {end_date}",
        fontsize=14, fontweight="bold", y=0.98,
    )

    gs = fig.add_gridspec(2, 2, hspace=0.45, wspace=0.35,
                          top=0.93, bottom=0.06, left=0.07, right=0.97)
    ax_pie  = fig.add_subplot(gs[0, 0])
    ax_proj = fig.add_subplot(gs[0, 1])
    ax_iss  = fig.add_subplot(gs[1, :])

    total_hours = sum(project_totals.values())
    proj_labels = list(project_totals.keys())
    proj_hours  = list(project_totals.values())
    colors = (COLORS * ((len(proj_labels) // len(COLORS)) + 1))[: len(proj_labels)]

    # --- Pie chart ---
    wedges, _, autotexts = ax_pie.pie(
        proj_hours,
        labels=None,
        colors=colors,
        autopct=lambda p: f"{p:.1f}%" if p > 3 else "",
        startangle=140,
        wedgeprops={"linewidth": 0.8, "edgecolor": "white"},
        pctdistance=0.78,
    )
    for at in autotexts:
        at.set_fontsize(7)
    ax_pie.set_title(f"By project  ({total_hours:.1f} h total)", fontsize=10, pad=8)
    ax_pie.legend(
        wedges,
        [_wrap(l) for l in proj_labels],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.04),
        fontsize=6.5,
        ncol=2,
        frameon=False,
    )

    # --- Horizontal bar: projects ---
    bars = ax_proj.barh(
        [_wrap(l) for l in reversed(proj_labels)],
        list(reversed(proj_hours)),
        color=list(reversed(colors)),
        edgecolor="white",
        linewidth=0.6,
    )
    ax_proj.set_xlabel("Hours", fontsize=8)
    ax_proj.set_title("Hours per project", fontsize=10)
    ax_proj.tick_params(axis="y", labelsize=7)
    ax_proj.tick_params(axis="x", labelsize=7)
    ax_proj.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=6))
    ax_proj.set_facecolor("#F0F2F5")
    ax_proj.grid(axis="x", color="white", linewidth=0.8)
    ax_proj.spines[["top", "right"]].set_visible(False)
    for bar in bars:
        w = bar.get_width()
        ax_proj.text(w + 0.3, bar.get_y() + bar.get_height() / 2,
                     f"{w:.1f}", va="center", ha="left", fontsize=6.5)

    # --- Horizontal bar: issues ---
    if issue_rows:
        iss_labels = [_wrap(f"#{r['issue_id']}  {r['subject']}", 45) for r in issue_rows]
        iss_hours  = [r["hours"] for r in issue_rows]
        iss_colors = (COLORS * ((len(iss_labels) // len(COLORS)) + 1))[: len(iss_labels)]

        iss_bars = ax_iss.barh(
            list(reversed(iss_labels)),
            list(reversed(iss_hours)),
            color=list(reversed(iss_colors)),
            edgecolor="white",
            linewidth=0.6,
        )
        ax_iss.set_xlabel("Hours", fontsize=8)
        ax_iss.set_title(f"Hours per issue  ·  project: {project_name}", fontsize=10)
        ax_iss.tick_params(axis="y", labelsize=7)
        ax_iss.tick_params(axis="x", labelsize=7)
        ax_iss.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=8))
        ax_iss.set_facecolor("#F0F2F5")
        ax_iss.grid(axis="x", color="white", linewidth=0.8)
        ax_iss.spines[["top", "right"]].set_visible(False)
        for bar in iss_bars:
            w = bar.get_width()
            ax_iss.text(w + 0.15, bar.get_y() + bar.get_height() / 2,
                        f"{w:.1f}", va="center", ha="left", fontsize=6.5)
    else:
        ax_iss.text(0.5, 0.5, f"No time entries found for project: {project_name}",
                    ha="center", va="center", transform=ax_iss.transAxes,
                    fontsize=10, color="gray")
        ax_iss.set_title(f"Hours per issue  ·  project: {project_name}", fontsize=10)
        ax_iss.axis("off")

    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved to: {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args():
    today         = datetime.date.today()
    default_end   = today.isoformat()
    default_start = (today - datetime.timedelta(days=365)).isoformat()

    p = argparse.ArgumentParser(
        description="Plot Redmine time distribution for a user.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("-c", "--config",  required=True,
                   help="Path to config.yaml")
    p.add_argument("-u", "--user",    required=True,
                   help="Redmine user display name (e.g. 'Jane Doe')")
    p.add_argument("-p", "--project", required=True,
                   help="Project name for the per-issue breakdown")
    p.add_argument("-s", "--start",   default=default_start,
                   help="Start date YYYY-MM-DD")
    p.add_argument("-e", "--end",     default=default_end,
                   help="End date YYYY-MM-DD")
    p.add_argument("-o", "--output",  default=f"time-report_{p.parse_args().user.replace(' ', '-')}_{p.parse_args().start}_to_{p.parse_args().end}.png",
                   help="Output PNG file path")
    return p.parse_args()


def main():
    args = parse_args()

    with open(args.config) as fh:
        config = yaml.safe_load(fh)

    Redmine_server_api = _find_and_import_redmine_apis()
    api = Redmine_server_api(config)

    # Resolve project name → ID
    project_id = api.find_project_id_from_name(args.project)
    if project_id is None:
        sys.exit(f"ERROR: Project '{args.project}' not found.")

    # Fetch time entries by user name (resolution handled inside the API class)
    print(f"Fetching time entries for '{args.user}' ({args.start} → {args.end}) …")
    time_entries = api.fetch_time_entries_by_user_name(args.user, args.start, args.end)
    if not time_entries:
        sys.exit("No time entries found — check the user name, date range, and permissions.")
    print(f"  → {len(time_entries)} entries found.")

    # Aggregate
    project_totals = aggregate_by_project(time_entries)

    print(f"Aggregating issues for project '{args.project}' …")
    issue_rows = aggregate_by_issue(time_entries, project_id)
    issue_rows = enrich_issue_subjects(api, issue_rows)
    print(f"  → {len(issue_rows)} issues with logged time.")

    plot_all(
        project_totals=project_totals,
        issue_rows=issue_rows,
        project_name=args.project,
        output_path=args.output,
        user_label=args.user,
        start_date=args.start,
        end_date=args.end,
    )


if __name__ == "__main__":
    main()
