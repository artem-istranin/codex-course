from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


COMMENT_MARKER = "<!-- wheel-winner-coverage-report -->"


def main() -> int:
    workspace = Path(os.environ["GITHUB_WORKSPACE"])
    coverage_file = workspace / os.environ["COVERAGE_FILE"]
    source_prefix = os.environ["SOURCE_PREFIX"].strip("/")

    coverage = parse_coverage(coverage_file)
    overall = percent(float(coverage["branch_rate"]) * 100)

    event = load_json(Path(os.environ["GITHUB_EVENT_PATH"]))
    pr_number = event.get("pull_request", {}).get("number")
    pr_coverage = "N/A"

    if pr_number:
        added_lines = fetch_added_lines(int(pr_number), source_prefix)
        pr_coverage = percent(diff_coverage(coverage["lines"], added_lines))

    body = f"{badge('Coverage', overall)} {badge('PR coverage', pr_coverage)}"
    write_summary(body)

    if pr_number:
        try:
            upsert_pr_comment(int(pr_number), f"{COMMENT_MARKER}\n{body}")
        except urllib.error.HTTPError as error:
            if error.code != 403:
                raise
            print("Skipping PR comment because the workflow token cannot write comments.", file=sys.stderr)

    return 0


def parse_coverage(path: Path) -> dict[str, object]:
    root = ET.parse(path).getroot()
    line_hits: dict[tuple[str, int], int] = {}

    for class_node in root.findall(".//class"):
        filename = class_node.attrib["filename"]
        for line_node in class_node.findall("./lines/line"):
            number = int(line_node.attrib["number"])
            hits = int(line_node.attrib.get("hits", "0"))
            line_hits[(filename, number)] = hits

    return {
        "branch_rate": root.attrib.get("branch-rate", "0"),
        "lines": line_hits,
    }


def fetch_added_lines(pr_number: int, source_prefix: str) -> dict[str, set[int]]:
    files: dict[str, set[int]] = {}
    page = 1

    while True:
        response = github_api(
            f"/repos/{os.environ['GITHUB_REPOSITORY']}/pulls/{pr_number}/files"
            f"?per_page=100&page={page}"
        )
        if not response:
            break

        for changed_file in response:
            filename = changed_file["filename"]
            if not filename.startswith(f"{source_prefix}/"):
                continue

            patch = changed_file.get("patch", "")
            added = parse_added_patch_lines(patch)
            if added:
                files[to_coverage_filename(filename, source_prefix)] = added

        page += 1

    return files


def parse_added_patch_lines(patch: str) -> set[int]:
    added: set[int] = set()
    new_line = 0

    for line in patch.splitlines():
        hunk = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
        if hunk:
            new_line = int(hunk.group(1))
            continue

        if line.startswith("+") and not line.startswith("+++"):
            added.add(new_line)
            new_line += 1
        elif line.startswith("-") and not line.startswith("---"):
            continue
        elif line.startswith("\\"):
            continue
        else:
            new_line += 1

    return added


def to_coverage_filename(repo_filename: str, source_prefix: str) -> str:
    source_prefix = source_prefix.strip("/")
    if repo_filename.startswith(f"{source_prefix}/"):
        return repo_filename.removeprefix(f"{source_prefix}/")
    return repo_filename


def diff_coverage(
    line_hits: dict[tuple[str, int], int],
    added_lines: dict[str, set[int]],
) -> float:
    covered = 0
    total = 0

    for filename, lines in added_lines.items():
        for line in lines:
            hits = line_hits.get((filename, line))
            if hits is None:
                continue
            total += 1
            if hits > 0:
                covered += 1

    if total == 0:
        return 100.0

    return covered / total * 100


def percent(value: float) -> str:
    return f"{value:.2f}%"


def badge(label: str, value: str) -> str:
    color = badge_color(value)
    encoded_label = label.replace(" ", "%20")
    encoded_value = value.replace("%", "%25")
    return f"![{label}](https://img.shields.io/badge/{encoded_label}-{encoded_value}-{color})"


def badge_color(value: str) -> str:
    if value == "N/A":
        return "lightgrey"

    number = float(value.rstrip("%"))
    if number >= 90:
        return "brightgreen"
    if number >= 75:
        return "yellow"
    return "red"


def write_summary(body: str) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    Path(summary_path).write_text(f"{body}\n", encoding="utf-8")


def upsert_pr_comment(pr_number: int, body: str) -> None:
    comments = github_api(
        f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{pr_number}/comments"
        "?per_page=100"
    )

    for comment in comments:
        if COMMENT_MARKER in comment.get("body", ""):
            github_api(comment["url"], method="PATCH", data={"body": body})
            return

    github_api(
        f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{pr_number}/comments",
        method="POST",
        data={"body": body},
    )


def github_api(path_or_url: str, method: str = "GET", data: dict[str, str] | None = None):
    if path_or_url.startswith("https://"):
        url = path_or_url
    else:
        url = f"{os.environ.get('GITHUB_API_URL', 'https://api.github.com')}{path_or_url}"

    body = None
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request) as response:
            if response.status == 204:
                return None
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        print(error.read().decode("utf-8"), file=sys.stderr)
        raise


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
