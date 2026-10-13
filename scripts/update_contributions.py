#!/usr/bin/env python3
"""Refresh curated engineering projects using public GitHub PR details."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import html
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

START_MARKER = "<!-- OPEN-SOURCE:START -->"
END_MARKER = "<!-- OPEN-SOURCE:END -->"
REFRESH_DAYS = 42
PR_URL = re.compile(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/pull/([1-9][0-9]*)/?")
LOGO_PATH = re.compile(r"assets/projects/[a-z0-9]+(?:-[a-z0-9]+)*\.png")


class UpdateError(Exception):
    """A failed refresh must not replace the last successful output."""


class GitHubClient:
    def __init__(self, token: str | None = None):
        self.token = token
        self.deadline = time.monotonic() + 210

    def pull_request(self, repo, number):
        return self._get(f"/repos/{repo}/pulls/{number}")

    def _get(self, path, params=None):
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "profile-contribution-updater",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        url = "https://api.github.com" + path
        if params:
            url += "?" + urlencode(params)
        request = Request(url, headers=headers)
        for attempt in range(3):
            if time.monotonic() + 20 >= self.deadline:
                raise UpdateError("Refresh exceeded its request budget; previous output retained.")
            wait = 2 ** (attempt + 1)
            try:
                with urlopen(request, timeout=20) as response:
                    result = json.load(response)
                if not isinstance(result, dict):
                    raise UpdateError("GitHub returned an unexpected JSON response.")
                return result
            except HTTPError as exc:
                message = f"GitHub HTTP {exc.code}"
                try:
                    detail = json.loads(exc.read()).get("message", "")
                    message += ": " + str(detail)
                except (ValueError, AttributeError):
                    pass
                limited = exc.code == 429 or (
                    exc.code == 403 and (
                        exc.headers.get("Retry-After")
                        or exc.headers.get("X-RateLimit-Remaining") == "0"
                        or "rate limit" in message.lower()
                    )
                )
                if not limited and exc.code not in (500, 502, 503, 504):
                    raise UpdateError(message) from exc
                try:
                    if exc.headers.get("Retry-After"):
                        wait = max(wait, float(exc.headers["Retry-After"]))
                    elif limited and exc.headers.get("X-RateLimit-Reset"):
                        wait = max(wait, float(exc.headers["X-RateLimit-Reset"]) - time.time() + 1)
                except ValueError:
                    raise UpdateError(message + "; invalid retry header.") from exc
                if attempt == 2 or wait > 60 or time.monotonic() + wait + 20 >= self.deadline:
                    raise UpdateError(message + "; retry on the next run.") from exc
            except (URLError, TimeoutError, OSError) as exc:
                if attempt == 2:
                    raise UpdateError(f"GitHub connection failed: {exc}") from exc
            except (ValueError, UnicodeError) as exc:
                raise UpdateError("GitHub returned invalid JSON; previous output retained.") from exc
            time.sleep(wait)
        raise UpdateError("GitHub request failed.")


def _canonical_url(url):
    if not isinstance(url, str):
        raise UpdateError("PR links must be GitHub pull-request URLs.")
    match = PR_URL.fullmatch(url)
    if not match:
        raise UpdateError(f"Invalid GitHub PR URL: {url}")
    return f"https://github.com/{match[1]}/pull/{int(match[2])}"


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise UpdateError(f"{field} must be nonempty plain text.")
    return value


def validate_config(config):
    if not isinstance(config, dict) or config.get("schema_version") != 2:
        raise UpdateError("This updater requires contributions.json schema_version 2.")
    username = config.get("username")
    if not isinstance(username, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", username):
        raise UpdateError("Config must contain a valid GitHub username.")
    _text(config.get("introduction"), "introduction")
    projects = config.get("projects")
    if not isinstance(projects, list) or not projects:
        raise UpdateError("projects must be a nonempty ordered list.")
    repos = set()
    for project in projects:
        if not isinstance(project, dict):
            raise UpdateError("Each project must be an object.")
        repo = project.get("repository")
        if not isinstance(repo, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
            raise UpdateError("Each project needs a full owner/repository name.")
        if repo.lower() in repos or repo.split("/")[0].lower() == username.lower():
            raise UpdateError("Projects must be unique external repositories.")
        repos.add(repo.lower())
        for field in ("name", "title", "area", "summary"):
            _text(project.get(field), field)
        if type(project.get("expanded")) is not bool:
            raise UpdateError("expanded must be true or false.")
        if "logo" in project:
            logo = project["logo"]
            if not isinstance(logo, dict):
                raise UpdateError("logo must contain a local PNG src and nonempty alt text.")
            source = logo.get("src")
            if not isinstance(source, str) or not LOGO_PATH.fullmatch(source):
                raise UpdateError("logo.src must be a local PNG path under assets/projects/.")
            _text(logo.get("alt"), "logo.alt")
        chains = project.get("chains")
        if not isinstance(chains, list) or not chains:
            raise UpdateError("Each project needs at least one evidence chain.")
        for chain in chains:
            if not isinstance(chain, dict) or chain.get("kind") not in ("dependency", "stages", "independent"):
                raise UpdateError("Chain kind must be dependency, stages, or independent.")
            _text(chain.get("title"), "chain title")
            _text(chain.get("analysis"), "chain analysis")
            steps = chain.get("steps")
            if not isinstance(steps, list) or not steps:
                raise UpdateError("Each chain needs an ordered steps list.")
            for step in steps:
                if not isinstance(step, dict):
                    raise UpdateError("Each step must be an object.")
                _text(step.get("label"), "step label")
                urls = step.get("prs")
                if not isinstance(urls, list) or not urls:
                    raise UpdateError("Each step needs at least one selected PR URL.")
                for url in urls:
                    canonical = _canonical_url(url)
                    match = PR_URL.fullmatch(canonical)
                    if match[1].lower() != repo.lower():
                        raise UpdateError("A project chain must reference PRs from that repository.")


def selected_pr_urls(config):
    validate_config(config)
    urls = {}
    for project in config["projects"]:
        for chain in project["chains"]:
            for step in chain["steps"]:
                for url in step["prs"]:
                    canonical = _canonical_url(url)
                    urls.setdefault(canonical.lower(), canonical)
    return list(urls.values())


def _normalize_pr(item, username, expected_url=None):
    if not isinstance(item, dict):
        raise UpdateError("Invalid PR detail response.")
    url = _canonical_url(item.get("html_url"))
    match = PR_URL.fullmatch(url)
    repo, number = match[1], int(match[2])
    if expected_url and url.lower() != _canonical_url(expected_url).lower():
        raise UpdateError("GitHub returned a different PR than requested.")
    if type(item.get("number")) is not int or item["number"] != number:
        raise UpdateError("PR number does not match its URL.")
    user = item.get("user")
    if not isinstance(user, dict) or not isinstance(user.get("login"), str) or user["login"].lower() != username.lower():
        raise UpdateError("Selected PR must be authored by the configured user.")
    if repo.split("/")[0].lower() == username.lower():
        raise UpdateError("Selected PR must belong to an external repository.")
    # Legacy public Search items remain useful as offline development fixtures.
    if isinstance(item.get("pull_request"), dict):
        request = item["pull_request"]
        repository_url = item.get("repository_url", "")
        if not isinstance(repository_url, str) or repository_url.lower() != ("https://api.github.com/repos/" + repo).lower():
            raise UpdateError("Invalid legacy Search repository.")
    else:
        request = item
        base = item.get("base")
        repository = base.get("repo") if isinstance(base, dict) else None
        if not isinstance(repository, dict) or repository.get("private") is not False:
            raise UpdateError("Only public repository PR details are accepted.")
        full_name = repository.get("full_name")
        if not isinstance(full_name, str) or full_name.lower() != repo.lower():
            raise UpdateError("PR base repository does not match the project.")
    title = _text(item.get("title"), "PR title")
    state = item.get("state")
    if state not in ("open", "closed") or "merged_at" not in request:
        raise UpdateError("PR detail must include state and merged_at.")
    merged_at = request["merged_at"]
    if merged_at is not None and (not isinstance(merged_at, str) or not merged_at):
        raise UpdateError("Invalid merged_at value.")
    draft = item.get("draft", False)
    if type(draft) is not bool:
        raise UpdateError("PR draft flag must be boolean.")
    if merged_at and state != "closed":
        raise UpdateError("A merged PR must be closed.")
    status = "merged" if merged_at else "closed" if state == "closed" else "draft" if draft else "open"
    return dict(repo=repo, number=number, url=url, title=title, status=status, draft=draft)


def collect_selected_prs(client, config):
    items = []
    for url in selected_pr_urls(config):
        match = PR_URL.fullmatch(url)
        item = client.pull_request(match[1], int(match[2]))
        _normalize_pr(item, config["username"], url)
        items.append(item)
    return items


def build_snapshot(items, config):
    validate_config(config)
    if not isinstance(items, list):
        raise UpdateError("Offline PR input must be an array.")
    lookup = {}
    for item in items:
        if not isinstance(item, dict):
            raise UpdateError("Invalid PR input.")
        key = _canonical_url(item.get("html_url")).lower()
        if key in lookup and lookup[key] != item:
            raise UpdateError("Conflicting duplicate PR responses.")
        lookup[key] = item
    metadata = {}
    for url in selected_pr_urls(config):
        item = lookup.get(url.lower())
        if item is None:
            raise UpdateError(f"Selected PR metadata is missing: {url}")
        metadata[url.lower()] = _normalize_pr(item, config["username"], url)
    projects = []
    for project in config["projects"]:
        result = {field: project[field] for field in ("repository", "name", "title", "area", "summary", "expanded")}
        if "logo" in project:
            result["logo"] = {field: project["logo"][field] for field in ("src", "alt")}
        result["chains"] = []
        for chain in project["chains"]:
            result_chain = {field: chain[field] for field in ("title", "kind", "analysis")}
            result_chain["steps"] = [
                dict(label=step["label"], prs=[dict(metadata[_canonical_url(url).lower()]) for url in step["prs"]])
                for step in chain["steps"]
            ]
            result["chains"].append(result_chain)
        projects.append(result)
    return dict(username=config["username"], introduction=config["introduction"], projects=projects)


def markdown_text(value):
    text = " ".join(str(value).split())
    text = html.escape(text, quote=False)
    return "".join("\\" + char if char in ("\\" + chr(96) + "*_{}[]()|!#") else char for char in text)


def _link_title(value):
    # Entity-encode quote and escape characters before entering a Markdown title.
    return html.escape(" ".join(value.split()), quote=True).replace("\\", "&#92;")


def _visible_project(project):
    """Filter display evidence without changing the saved metadata or config."""
    chains = []
    project_filtered = False
    for chain in project["chains"]:
        steps = []
        chain_filtered = False
        for step in chain["steps"]:
            prs = [pr for pr in step["prs"] if pr["status"] != "closed"]
            step_filtered = len(prs) != len(step["prs"])
            chain_filtered = chain_filtered or step_filtered
            if prs:
                steps.append(dict(label="Selected PRs" if step_filtered else step["label"], prs=prs))
        project_filtered = project_filtered or chain_filtered
        if steps:
            visible = dict(chain, steps=steps)
            if chain_filtered:
                # A missing prerequisite does not establish a new dependency.
                # Shared prose may describe removed work, so show evidence only.
                visible.update(title="Selected PRs", analysis="", kind="independent")
            chains.append(visible)
    if not chains:
        return None
    visible = dict(project, chains=chains)
    if project_filtered:
        # Do not retain aggregate claims that may rely on a removed PR.
        visible.update(title="", summary="")
    return visible


def _render_project(project):
    details = "<details open>" if project["expanded"] else "<details>"
    prefix = "- "
    if "logo" in project:
        logo = project["logo"]
        href = html.escape("https://github.com/" + project["repository"], quote=True)
        source = html.escape(logo["src"], quote=True)
        alt = html.escape(logo["alt"], quote=True)
        prefix += f'<a href="{href}"><img src="{source}" alt="{alt}" width="64" height="36" align="middle"></a> '
    heading = f"{prefix}**[{markdown_text(project['name'])}](https://github.com/{project['repository']})**"
    if project["title"]:
        heading += " · " + markdown_text(project["title"])
    lines = [heading, ""]
    if project["summary"]:
        lines += ["  " + markdown_text(project["summary"]), ""]
    lines += ["  " + details, "", "  <summary>Technical details and selected PRs</summary>", ""]
    for chain in project["chains"]:
        description = f"  - **{markdown_text(chain['title'])}.**"
        if chain["analysis"]:
            description += " " + markdown_text(chain["analysis"])
        lines += [description, ""]
        steps = []
        for step in chain["steps"]:
            links = []
            for pr in step["prs"]:
                links.append(f"[#{pr['number']}]({pr['url']} \"{_link_title(pr['title'])}\") ({pr['status'].capitalize()})")
            evidence = " + ".join(links)
            if len(links) > 1:
                evidence = "(" + evidence + ")"
            steps.append(markdown_text(step["label"]) + " " + evidence)
        separator = " → " if chain["kind"] == "dependency" else " · "
        lines += ["    " + separator.join(steps), ""]
    lines += ["  </details>", ""]
    return lines


def render_section(snapshot, verified_on):
    lines = [markdown_text(snapshot["introduction"]), ""]
    groups = {}
    for project in snapshot["projects"]:
        projects = groups.setdefault(project["area"], [])
        visible = _visible_project(project)
        if visible is not None:
            projects.append(visible)
    for area, projects in groups.items():
        if not projects:
            continue
        lines += ["### " + markdown_text(area), ""]
        for project in projects:
            lines.extend(_render_project(project))
    lines.append(f"<sub>Selected public contributions · PR status verified {verified_on}.</sub>")
    return "\n".join(lines).strip()


def replace_section(readme, section):
    if readme.count(START_MARKER) != 1 or readme.count(END_MARKER) != 1:
        raise UpdateError("README must contain exactly one OPEN-SOURCE marker pair.")
    start = readme.index(START_MARKER) + len(START_MARKER)
    end = readme.index(END_MARKER)
    if end < start:
        raise UpdateError("README markers are in the wrong order.")
    newline = "\r\n" if "\r\n" in readme else "\n"
    section = section.strip().replace("\r\n", "\n").replace("\n", newline)
    return readme[:start] + newline * 2 + section + newline * 2 + readme[end:]


def _write_outputs(outputs):
    staged = []
    changed = []
    try:
        for path, content in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            previous = path.read_bytes() if path.exists() else None
            if previous == content:
                continue
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".contributions-", delete=False) as handle:
                staged.append((path, Path(handle.name), previous))
                handle.write(content)
            os.chmod(handle.name, 0o644)
        for path, temporary, previous in staged:
            os.replace(temporary, path)
            changed.append((path, previous))
    except OSError as exc:
        for path, previous in reversed(changed):
            if previous is None:
                path.unlink(missing_ok=True)
            else:
                with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
                    handle.write(previous)
                os.replace(handle.name, path)
        raise UpdateError(f"Could not save contribution output: {exc}") from exc
    finally:
        for _, temporary, _ in staged:
            temporary.unlink(missing_ok=True)


def update(root, items, config, today, dry_run=False):
    root = Path(root)
    readme_path = root / "README.md"
    readme = readme_path.read_bytes().decode("utf-8")
    replace_section(readme, "")
    snapshot = build_snapshot(items, config)
    state_path = root / "assets/contributions-data.json"
    verified_on = today.isoformat()
    if state_path.exists():
        try:
            previous = json.loads(state_path.read_text(encoding="utf-8"))
            previous_day = date.fromisoformat(previous["verified_on"])
        except (ValueError, KeyError, TypeError) as exc:
            raise UpdateError("Invalid saved snapshot; previous output retained.") from exc
        if previous_day > today:
            raise UpdateError("Saved snapshot date is ahead of the current UTC date.")
        if previous.get("schema_version") == 2 and previous.get("data") == snapshot and (today - previous_day).days < REFRESH_DAYS:
            verified_on = previous["verified_on"]
    state = dict(schema_version=2, verified_on=verified_on, data=snapshot)
    outputs = {
        readme_path: replace_section(readme, render_section(snapshot, verified_on)).encode("utf-8"),
        state_path: (json.dumps(state, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    }
    changed = [path for path, content in outputs.items() if not path.exists() or path.read_bytes() != content]
    if changed and not dry_run:
        _write_outputs(outputs)
    verb = "Would update" if dry_run else "Updated"
    print(f"{verb} {len(changed)} file(s)." if changed else "No selected PR or editorial changes; no files written.")
    return bool(changed)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--dry-run", action="store_true", help="Check and render in memory without writing files.")
    parser.add_argument("--input-json", type=Path, help="Read selected PR details (or legacy Search items) without API calls.")
    args = parser.parse_args(argv)
    try:
        config = json.loads((args.root / "contributions.json").read_text(encoding="utf-8"))
        validate_config(config)
        replace_section((args.root / "README.md").read_bytes().decode("utf-8"), "")
        today = datetime.now(timezone.utc).date()
        if args.input_json:
            source = json.loads(args.input_json.read_text(encoding="utf-8"))
            if isinstance(source, dict):
                if source.get("incomplete_results") is not False or not isinstance(source.get("items"), list):
                    raise UpdateError("Offline Search response is incomplete or invalid.")
                items = source["items"]
            elif isinstance(source, list):
                items = source
            else:
                raise UpdateError("Offline input must be a PR detail array or legacy Search response.")
        else:
            items = collect_selected_prs(GitHubClient(os.environ.get("GITHUB_TOKEN")), config)
        update(args.root, items, config, today, args.dry_run)
        return 0
    except (UpdateError, OSError, ValueError) as exc:
        print(f"Contribution refresh failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
