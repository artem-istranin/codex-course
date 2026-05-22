from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote
from xml.etree import ElementTree


HUNK_RE = re.compile(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--coverage-file", required=True)
    parser.add_argument("--source-prefix", required=True)
    parser.add_argument("--base-sha", default="")
    parser.add_argument("--head-sha", default="")
    return parser.parse_args()


def format_percent(value: float | None) -> str:
    if value is None:
        return "N/A"
    if value == 100 or value == 0:
        return f"{value:.0f}%"
    return f"{value:.1f}%"


def badge_color(value: float | None) -> str:
    if value is None:
        return "lightgrey"
    if value >= 90:
        return "brightgreen"
    if value >= 80:
        return "green"
    if value >= 70:
        return "yellowgreen"
    if value >= 60:
        return "yellow"
    if value >= 50:
        return "orange"
    return "red"


def badge(label: str, value: float | None) -> str:
    message = format_percent(value)
    url = "https://img.shields.io/badge/{label}-{message}-{color}".format(
        label=quote(label, safe=""),
        message=quote(message, safe=""),
        color=badge_color(value),
    )
    return f"![{label}]({url})"


def coverage_lines(
    coverage_file: Path,
    source_prefix: str,
) -> tuple[float, dict[str, dict[int, bool]]]:
    root = ElementTree.parse(coverage_file).getroot()
    branch_rate = float(root.attrib["branch-rate"]) * 100
    prefix = source_prefix.strip("/")
    lines_by_file: dict[str, dict[int, bool]] = {}

    for class_node in root.findall(".//class"):
        filename = class_node.attrib["filename"].strip("/")
        repo_path = f"{prefix}/{filename}" if prefix else filename
        file_lines: dict[int, bool] = {}

        for line in class_node.findall("./lines/line"):
            number = int(line.attrib["number"])
            file_lines[number] = int(line.attrib.get("hits", "0")) > 0

        lines_by_file[repo_path] = file_lines

    return branch_rate, lines_by_file


def changed_lines(base_sha: str, head_sha: str, source_prefix: str) -> dict[str, set[int]]:
    if not base_sha or not head_sha:
        return {}

    command = [
        "git",
        "diff",
        "--unified=0",
        f"{base_sha}...{head_sha}",
        "--",
        source_prefix,
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    changed: dict[str, set[int]] = {}
    current_file = ""
    current_line: int | None = None

    for diff_line in result.stdout.splitlines():
        if diff_line.startswith("+++ "):
            path = diff_line[4:].strip()
            current_file = "" if path == "/dev/null" else path.removeprefix("b/")
            current_line = None
            continue

        match = HUNK_RE.match(diff_line)
        if match:
            current_line = int(match.group(1))
            continue

        if current_line is None or not current_file:
            continue

        if diff_line.startswith("+") and not diff_line.startswith("+++"):
            changed.setdefault(current_file, set()).add(current_line)
            current_line += 1
        elif diff_line.startswith("-") and not diff_line.startswith("---"):
            continue
        else:
            current_line += 1

    return changed


def diff_coverage_percent(
    changed: dict[str, set[int]],
    lines_by_file: dict[str, dict[int, bool]],
) -> float | None:
    covered = 0
    total = 0

    for filename, line_numbers in changed.items():
        covered_lines = lines_by_file.get(filename)
        if covered_lines is None:
            continue

        for line_number in line_numbers:
            if line_number not in covered_lines:
                continue
            total += 1
            if covered_lines[line_number]:
                covered += 1

    if total == 0:
        return None
    return covered / total * 100


def set_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with Path(output_path).open("a", encoding="utf-8") as output:
        output.write(f"{name}<<EOF\n{value}\nEOF\n")


def append_summary(markdown: str) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with Path(summary_path).open("a", encoding="utf-8") as summary:
        summary.write(f"{markdown}\n")


def main() -> int:
    args = parse_args()
    coverage_file = Path(args.coverage_file)
    if not coverage_file.is_file():
        print(f"Coverage XML not found: {coverage_file}", file=sys.stderr)
        return 1

    branch_coverage, lines_by_file = coverage_lines(coverage_file, args.source_prefix)
    changed = changed_lines(args.base_sha, args.head_sha, args.source_prefix)
    pr_coverage = diff_coverage_percent(changed, lines_by_file)

    markdown = f"{badge('Coverage', branch_coverage)} {badge('PR coverage', pr_coverage)}"
    append_summary(markdown)
    set_output("coverage", format_percent(branch_coverage))
    set_output("pr-coverage", format_percent(pr_coverage))
    set_output("markdown", markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
