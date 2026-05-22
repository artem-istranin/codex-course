from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


COMMENT_MARKER = "<!-- wheel-winner-coverage-report -->"


def main() -> int:
    coverage_xml = Path(os.environ["COVERAGE_XML"])
    source_prefix = os.environ.get("SOURCE_PREFIX", "").strip("/")
    base_sha = os.environ.get("BASE_SHA", "")
    event = load_json(Path(os.environ["GITHUB_EVENT_PATH"]))
    pr_number = event.get("pull_request", {}).get("number")

    coverage = parse_coverage(coverage_xml, source_prefix)
    overall_branch_coverage = percent(float(coverage["branch_rate"]) * 100)

    pr_coverage = "N/A"
    if pr_number and base_sha:
        changed_lines = fetch_changed_lines(base_sha)
        pr_coverage = percent(diff_coverage(coverage["line_hits"], changed_lines))

    report = (
        f"{badge('Coverage', overall_branch_coverage)} "
        f"{badge('PR coverage', pr_coverage)}\n"
    )
    comment_body = f"{COMMENT_MARKER}\n{report}"

    write_summary(report)
    write_output("coverage", overall_branch_coverage)
    write_output("pr-coverage", pr_coverage)

    if pr_number:
        try:
            upsert_pr_comment(int(pr_number), comment_body)
        except urllib.error.HTTPError as error:
            if error.code in {401, 403}:
                print(
                    "Skipping PR comment because the workflow token cannot write comments.",
                    file=sys.stderr,
                )
            else:
                raise

    return 0


def parse_coverage(path: Path, source_prefix: str) -> dict[str, object]:
    root = ET.parse(path).getroot()
    line_hits: dict[tuple[str, int], tuple[int, int]] = {}

    for class_node in root.findall(".//class"):
        filename = to_repo_filename(class_node.attrib["filename"], source_prefix)
        for line_node in class_node.findall("./lines/line"):
            line_number = int(line_node.attrib["number"])
            hits = int(line_node.attrib.get("hits", "0"))
            line_hits[(filename, line_number)] = coverage_points(line_node, hits)

    return {
        "branch_rate": root.attrib.get("branch-rate", "0"),
        "line_hits": line_hits,
    }


def coverage_points(line_node: ET.Element, hits: int) -> tuple[int, int]:
    if line_node.attrib.get("branch") != "true":
        return (1 if hits else 0, 1)

    match = re.search(r"\((\d+)/(\d+)\)", line_node.attrib.get("condition-coverage", ""))
    if not match:
        return (1 if hits else 0, 1)

    return int(match.group(1)), int(match.group(2))


def fetch_changed_lines(base_sha: str) -> dict[str, set[int]]:
    output = subprocess.check_output(
        ["git", "diff", "--unified=0", f"{base_sha}...HEAD"],
        text=True,
    )
    return parse_added_lines(output)


def parse_added_lines(diff: str) -> dict[str, set[int]]:
    files: dict[str, set[int]] = {}
    current_file = ""
    new_line = 0

    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            current_file = line.removeprefix("+++ b/")
            files.setdefault(current_file, set())
            continue

        match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
        if match:
            new_line = int(match.group(1))
            continue

        if not current_file:
            continue

        if line.startswith("+") and not line.startswith("+++"):
            files[current_file].add(new_line)
            new_line += 1
        elif line.startswith("-") and not line.startswith("---"):
            continue
        elif line.startswith("\\"):
            continue
        else:
            new_line += 1

    return files


def to_repo_filename(filename: str, source_prefix: str) -> str:
    filename = filename.replace("\\", "/")
    if source_prefix and not filename.startswith(f"{source_prefix}/"):
        return f"{source_prefix}/{filename}"
    return filename


def diff_coverage(
    line_hits: dict[tuple[str, int], tuple[int, int]],
    changed_lines: dict[str, set[int]],
) -> float:
    covered = 0
    total = 0

    for filename, lines in changed_lines.items():
        for line_number in lines:
            points = line_hits.get((filename, line_number))
            if not points:
                continue

            covered += points[0]
            total += points[1]

    if total == 0:
        return 100.0

    return covered / total * 100


def percent(value: float) -> str:
    return f"{value:.2f}%"


def badge(label: str, value: str) -> str:
    color = badge_color(value)
    encoded_label = label.replace("-", "--").replace(" ", "%20")
    encoded_value = value.replace("-", "--").replace("%", "%25")
    return f"![{label}](https://img.shields.io/badge/{encoded_label}-{encoded_value}-{color})"


def badge_color(value: str) -> str:
    if value == "N/A":
        return "lightgrey"

    percent_value = float(value.rstrip("%"))
    if percent_value >= 90:
        return "brightgreen"
    if percent_value >= 75:
        return "yellow"
    return "red"


def write_summary(body: str) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    Path(summary_path).write_text(body, encoding="utf-8")


def write_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return

    with Path(output_path).open("a", encoding="utf-8") as output_file:
        output_file.write(f"{name}={value}\n")


def upsert_pr_comment(pr_number: int, body: str) -> None:
    comments = github_api(
        f"/repos/{os.environ['GITHUB_REPOSITORY']}/issues/{pr_number}/comments?per_page=100",
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


def github_api(
    path_or_url: str,
    method: str = "GET",
    data: dict[str, str] | None = None,
) -> object:
    if path_or_url.startswith("https://"):
        url = path_or_url
    else:
        api_url = os.environ.get("GITHUB_API_URL", "https://api.github.com")
        url = f"{api_url}{path_or_url}"

    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, headers=headers, data=body, method=method)
    with urllib.request.urlopen(request) as response:
        if response.status == 204:
            return None

        return json.loads(response.read().decode("utf-8"))


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
