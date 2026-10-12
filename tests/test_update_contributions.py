"""Network-free acceptance tests for the curated, repository-first README updater.

Run from the delivery directory with: python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import copy
from contextlib import redirect_stderr
from datetime import date, timedelta
import importlib.util
import io
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "update_contributions.py"
SPEC = importlib.util.spec_from_file_location("update_contributions", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
updater = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = updater
SPEC.loader.exec_module(updater)

USERNAME = "fusheng-ji"
TODAY = date(2026, 10, 8)


def pr(number, repo="example/project", *, state="open", merged=False, draft=False,
       author=USERNAME, private=False, title=None):
    return {
        "id": int.from_bytes(f"{repo}:{number}".encode(), "big"),
        "number": number,
        "title": title or f"Improve project behavior {number}",
        "state": state,
        "draft": draft,
        "merged_at": "2026-02-01T12:00:00Z" if merged else None,
        "user": {"login": author},
        "base": {"repo": {"full_name": repo, "private": private}},
        "html_url": f"https://github.com/{repo}/pull/{number}",
        "updated_at": "2026-10-01T12:00:00Z",
    }


def fixtures():
    return [
        pr(1, state="closed", merged=True), pr(2), pr(3, state="closed"),
        pr(4, "another/library", draft=True), pr(5, "another/library"),
    ]


def config():
    return {
        "schema_version": 2,
        "username": USERNAME,
        "introduction": "Selected work on reliable GPU kernels, video generation, and model integration.",
        "projects": [
            {
                "repository": "example/project",
                "name": "Example Project",
                "title": "Example Project — GPU inference",
                "area": "Video generation",
                "summary": "An editor-written account of the work and its purpose.",
                "expanded": True,
                "chains": [
                    {
                        "title": "Kernel integration",
                        "kind": "dependency",
                        "analysis": "The integration builds on a validated kernel implementation.",
                        "steps": [
                            {"label": "Kernel baseline", "prs": ["https://github.com/example/project/pull/1"]},
                            {"label": "Integration", "prs": ["https://github.com/example/project/pull/2"]},
                        ],
                    },
                    {
                        "title": "Separate maintenance",
                        "kind": "independent",
                        "analysis": "Independent compatibility work.",
                        "steps": [{"label": "Compatibility", "prs": ["https://github.com/example/project/pull/3"]}],
                    },
                ],
            },
            {
                "repository": "another/library",
                "name": "Another Library",
                "title": "Another Library — model compatibility",
                "area": "Model integration",
                "summary": "Compatibility work developed in separate stages.",
                "expanded": False,
                "chains": [
                    {
                        "title": "Staged support",
                        "kind": "stages",
                        "analysis": "These stages describe the work without claiming a code dependency.",
                        "steps": [
                            {"label": "Initial support", "prs": ["https://github.com/another/library/pull/4"]},
                            {"label": "Validation", "prs": ["https://github.com/another/library/pull/5"]},
                        ],
                    },
                ],
            },
        ],
    }


def legacy_item(item):
    result = copy.deepcopy(item)
    result["repository_url"] = "https://api.github.com/repos/" + item["base"]["repo"]["full_name"]
    result["pull_request"] = {"merged_at": result.pop("merged_at")}
    result.pop("base")
    return result


class FakeSelectedClient:
    def __init__(self, items):
        self.items = {
            (item["base"]["repo"]["full_name"].lower(), item["number"]): copy.deepcopy(item)
            for item in items
        }
        self.calls = []

    def pull_request(self, repo, number):
        self.calls.append((repo, number))
        key = (repo.lower(), number)
        if key not in self.items:
            raise updater.UpdateError("A PR outside the curated selection was requested")
        return copy.deepcopy(self.items[key])


class CollectionTests(unittest.TestCase):
    def test_selected_urls_follow_editorial_config_order(self):
        self.assertEqual(updater.selected_pr_urls(config()), [item["html_url"] for item in fixtures()])

    def test_repeated_urls_fetch_once_in_first_occurrence_order(self):
        settings = config()
        settings["projects"][0]["chains"][1]["steps"][0]["prs"].append("https://github.com/EXAMPLE/Project/pull/1/")
        client = FakeSelectedClient(fixtures())
        result = updater.collect_selected_prs(client, settings)
        self.assertEqual([item["html_url"] for item in result], [item["html_url"] for item in fixtures()])
        self.assertEqual(client.calls, [
            ("example/project", 1), ("example/project", 2), ("example/project", 3),
            ("another/library", 4), ("another/library", 5),
        ])

    def test_fetches_only_selected_prs_without_search(self):
        client = FakeSelectedClient(fixtures() + [pr(1000, "unselected/repository")])
        self.assertEqual(len(updater.collect_selected_prs(client, config())), 5)
        self.assertEqual(len(client.calls), 5)
        self.assertNotIn(("unselected/repository", 1000), client.calls)

    def test_selected_request_failure_is_not_silently_omitted(self):
        with self.assertRaises(updater.UpdateError):
            updater.collect_selected_prs(FakeSelectedClient(fixtures()[:-1]), config())


class ConfigTests(unittest.TestCase):
    def test_null_username_is_rejected(self):
        invalid = config()
        invalid["username"] = None
        with self.assertRaises(updater.UpdateError):
            updater.validate_config(invalid)

    def test_invalid_chain_kind_is_rejected(self):
        invalid = config()
        invalid["projects"][0]["chains"][0]["kind"] = "latest"
        with self.assertRaises(updater.UpdateError):
            updater.validate_config(invalid)

    def test_pr_from_different_project_cannot_appear_in_a_project_chain(self):
        invalid = config()
        invalid["projects"][0]["chains"][0]["steps"][0]["prs"] = ["https://github.com/another/library/pull/4"]
        with self.assertRaises(updater.UpdateError):
            updater.validate_config(invalid)

    def test_own_repository_is_not_an_external_contribution(self):
        invalid = config()
        invalid["projects"][0]["repository"] = "fusheng-ji/personal-site"
        invalid["projects"][0]["chains"] = []
        with self.assertRaises(updater.UpdateError):
            updater.validate_config(invalid)

    def test_non_github_pr_url_is_rejected(self):
        invalid = config()
        invalid["projects"][0]["chains"][0]["steps"][0]["prs"] = ["https://example.com/project/pull/1"]
        with self.assertRaises(updater.UpdateError):
            updater.validate_config(invalid)

    def test_optional_logo_accepts_local_png_slug_paths(self):
        for source in ("assets/projects/gsplat.png", "assets/projects/example-project.png"):
            settings = config()
            settings["projects"][0]["logo"] = {"src": source, "alt": "Example Project logo"}
            with self.subTest(source=source):
                updater.validate_config(settings)

    def test_logo_rejects_remote_paths_traversal_svg_invalid_slugs_and_nonstring_sources(self):
        sources = [
            "https://example.com/logo.png", "//example.com/logo.png",
            "assets/projects/../logo.png", "/assets/projects/example.png",
            "assets/projects/example.svg", "assets/projects/Example.png",
            "assets/projects/example_project.png", "assets/projects/example--project.png",
            "assets/projects/example.png?theme=dark", None, 123, {}, [],
        ]
        for source in sources:
            settings = config()
            settings["projects"][0]["logo"] = {"src": source, "alt": "Example Project logo"}
            with self.subTest(source=source), self.assertRaises(updater.UpdateError):
                updater.validate_config(settings)

    def test_logo_requires_an_object_with_nonempty_string_alt(self):
        invalid_logos = [
            None, [], "assets/projects/example-project.png",
            {"src": "assets/projects/example-project.png"},
            {"src": "assets/projects/example-project.png", "alt": None},
            {"src": "assets/projects/example-project.png", "alt": 123},
            {"src": "assets/projects/example-project.png", "alt": ""},
            {"src": "assets/projects/example-project.png", "alt": "   "},
        ]
        for logo in invalid_logos:
            settings = config()
            settings["projects"][0]["logo"] = logo
            with self.subTest(logo=logo), self.assertRaises(updater.UpdateError):
                updater.validate_config(settings)


class SnapshotTests(unittest.TestCase):
    def all_prs(self, snapshot):
        return [
            item for project in snapshot["projects"] for chain in project["chains"]
            for step in chain["steps"] for item in step["prs"]
        ]

    def test_preserves_project_order_and_editor_authored_descriptions(self):
        settings = config()
        snapshot = updater.build_snapshot(fixtures(), settings)
        self.assertEqual(snapshot["username"], settings["username"])
        self.assertEqual(snapshot["introduction"], settings["introduction"])
        for actual, expected in zip(snapshot["projects"], settings["projects"]):
            for field in ("repository", "name", "title", "area", "summary", "expanded"):
                self.assertEqual(actual[field], expected[field])
            for actual_chain, expected_chain in zip(actual["chains"], expected["chains"]):
                for field in ("title", "kind", "analysis"):
                    self.assertEqual(actual_chain[field], expected_chain[field])
                self.assertEqual([step["label"] for step in actual_chain["steps"]], [step["label"] for step in expected_chain["steps"]])

    def test_optional_logo_is_preserved_and_absent_logo_stays_absent(self):
        settings = config()
        settings["projects"][0]["logo"] = {"src": "assets/projects/example-project.png", "alt": "Example Project logo"}
        snapshot = updater.build_snapshot(fixtures(), settings)
        self.assertEqual(snapshot["projects"][0]["logo"], settings["projects"][0]["logo"])
        self.assertNotIn("logo", snapshot["projects"][1])

    def test_legacy_projects_without_logo_keep_their_existing_snapshot_shape(self):
        snapshot = updater.build_snapshot(fixtures(), config())
        self.assertTrue(all("logo" not in project for project in snapshot["projects"]))

    def test_snapshot_distinguishes_merged_open_draft_and_unmerged_closed(self):
        selected = self.all_prs(updater.build_snapshot(fixtures(), config()))
        self.assertEqual([item["status"] for item in selected], ["merged", "open", "closed", "draft", "open"])
        self.assertEqual([item["draft"] for item in selected], [False, False, False, True, False])
        self.assertEqual([item["url"] for item in selected], [item["html_url"] for item in fixtures()])

    def test_merged_takes_priority_over_an_obsolete_draft_flag(self):
        items = fixtures()
        items[0]["draft"] = True
        self.assertEqual(self.all_prs(updater.build_snapshot(items, config()))[0]["status"], "merged")

    def test_input_order_and_updated_at_never_reorder_the_selection(self):
        expected = updater.build_snapshot(fixtures(), config())
        reversed_items = list(reversed(fixtures()))
        for index, item in enumerate(reversed_items):
            item["updated_at"] = f"2026-10-0{index + 1}T23:59:59Z"
        self.assertEqual(updater.build_snapshot(reversed_items, config()), expected)

    def test_legacy_search_items_can_seed_an_offline_snapshot(self):
        self.assertEqual(updater.build_snapshot([legacy_item(item) for item in fixtures()], config()), updater.build_snapshot(fixtures(), config()))

    def test_wrong_author_private_repository_or_mismatched_repository_is_rejected(self):
        for change in ("author", "private", "repository"):
            items = fixtures()
            if change == "author":
                items[0]["user"]["login"] = "someone-else"
            elif change == "private":
                items[0]["base"]["repo"]["private"] = True
            else:
                items[0]["base"]["repo"]["full_name"] = "unrelated/project"
            with self.subTest(change=change), self.assertRaises(updater.UpdateError):
                updater.build_snapshot(items, config())

    def test_missing_selected_pr_fails_instead_of_removing_editorial_content(self):
        with self.assertRaises(updater.UpdateError):
            updater.build_snapshot(fixtures()[:-1], config())

    def test_legacy_closed_item_without_merge_metadata_is_rejected(self):
        items = [legacy_item(item) for item in fixtures()]
        items[0]["pull_request"].pop("merged_at")
        with self.assertRaises(updater.UpdateError):
            updater.build_snapshot(items, config())


class RenderingTests(unittest.TestCase):
    def interleaved_areas(self):
        settings = config()
        third = copy.deepcopy(settings["projects"][0])
        third.update({
            "repository": "third/tool", "name": "Third Tool", "title": "Independent validation",
            "summary": "A separate validation contribution in the first area.", "expanded": False,
            "chains": [{
                "title": "Contract validation", "kind": "independent",
                "analysis": "Validation checks a distinct numerical contract.",
                "steps": [{"label": "Validation", "prs": ["https://github.com/third/tool/pull/6"]}],
            }],
        })
        settings["projects"].append(third)
        return settings, fixtures() + [pr(6, "third/tool")]

    def test_project_bullets_have_visible_summaries_and_independent_details_under_area_headings(self):
        settings = config()
        section = updater.render_section(updater.build_snapshot(fixtures(), settings), TODAY.isoformat())
        self.assertIn(settings["introduction"], section)
        bullets = [f"- **[{project['name']}](https://github.com/{project['repository']})** · {project['title']}" for project in settings["projects"]]
        self.assertEqual([line for line in section.splitlines() if line.startswith("- **")], bullets)
        self.assertEqual(len(re.findall(r"<details\b[^>]*>", section)), len(settings["projects"]))
        self.assertEqual(section.count("<summary>Technical details and selected PRs</summary>"), len(settings["projects"]))
        for index, project in enumerate(settings["projects"]):
            with self.subTest(repository=project["repository"]):
                start = section.index(bullets[index])
                end = section.index(bullets[index + 1]) if index + 1 < len(bullets) else len(section)
                block = section[start:end]
                opening = re.search(r"<details\b[^>]*>", block)
                self.assertIsNotNone(opening)
                self.assertLess(block.index(project["summary"]), opening.start())
                self.assertIn("\n  " + project["summary"], block[:opening.start()])
                details = block[opening.end():block.index("</details>")]
                self.assertLess(section.index("### " + project["area"]), start)
                self.assertNotIn("*" + project["area"] + "*", details)
                for chain in project["chains"]:
                    self.assertIn(chain["title"], details)
                    self.assertIn(chain["analysis"], details)
                    self.assertNotIn(chain["analysis"], block[:opening.start()])
                    for step in chain["steps"]:
                        self.assertIn(step["label"], details)
                        for url in step["prs"]:
                            self.assertIn(url, details)
                            self.assertNotIn(url, block[:opening.start()])
        self.assertNotIn("<picture>", section)
        self.assertNotIn("Merged / Submitted", section)
        self.assertNotIn("Further engineering contributions", section)

    def test_logo_is_a_clickable_64_by_36_image_before_the_existing_project_link(self):
        settings = config()
        settings["projects"][0]["logo"] = {"src": "assets/projects/example-project.png", "alt": "Example Project logo"}
        section = updater.render_section(updater.build_snapshot(fixtures(), settings), TODAY.isoformat())
        expected = (
            '- <a href="https://github.com/example/project"><img src="assets/projects/example-project.png" '
            'alt="Example Project logo" width="64" height="36" align="middle"></a> '
            '**[Example Project](https://github.com/example/project)** · Example Project — GPU inference'
        )
        self.assertIn(expected, section.splitlines())
        self.assertIn('- **[Another Library](https://github.com/another/library)** · Another Library — model compatibility', section.splitlines())
        self.assertEqual(section.count("<img "), 1)

    def test_logo_alt_is_escaped_without_creating_html_attributes(self):
        settings = config()
        alt = 'Project " onerror="alert(1) <logo> & \'quoted\''
        settings["projects"][0]["logo"] = {"src": "assets/projects/example-project.png", "alt": alt}
        section = updater.render_section(updater.build_snapshot(fixtures(), settings), TODAY.isoformat())

        class ImageParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.images = []
                self.anchors = []

            def handle_starttag(self, tag, attrs):
                if tag == "img":
                    self.images.append(dict(attrs))
                elif tag == "a":
                    self.anchors.append(dict(attrs))

        parser = ImageParser()
        parser.feed(section)
        self.assertEqual(len(parser.images), 1)
        self.assertEqual(parser.images[0], {
            "src": "assets/projects/example-project.png", "alt": alt,
            "width": "64", "height": "36", "align": "middle",
        })
        self.assertEqual(parser.anchors[0], {"href": "https://github.com/example/project"})
        self.assertIn("&quot;", section)
        self.assertIn("&lt;logo&gt;", section)
        self.assertNotIn("<logo>", section)

    def test_projects_without_logos_retain_plain_markdown_bullets(self):
        settings = config()
        section = updater.render_section(updater.build_snapshot(fixtures(), settings), TODAY.isoformat())
        expected = [f"- **[{project['name']}](https://github.com/{project['repository']})** · {project['title']}" for project in settings["projects"]]
        self.assertEqual([line for line in section.splitlines() if line.startswith("- ")], expected)
        self.assertNotIn("<img", section)
        self.assertNotIn("<a href=", section)

    def test_interleaved_areas_group_once_in_first_appearance_order_and_keep_project_order(self):
        settings, items = self.interleaved_areas()
        section = updater.render_section(updater.build_snapshot(items, settings), TODAY.isoformat())
        first_area = settings["projects"][0]["area"]
        second_area = settings["projects"][1]["area"]
        self.assertEqual([line for line in section.splitlines() if line.startswith("### ")], ["### " + first_area, "### " + second_area])
        expected_projects = [settings["projects"][0], settings["projects"][2], settings["projects"][1]]
        expected_bullets = [f"- **[{project['name']}](https://github.com/{project['repository']})** · {project['title']}" for project in expected_projects]
        self.assertEqual([line for line in section.splitlines() if line.startswith("- **")], expected_bullets)
        self.assertLess(section.index(expected_bullets[1]), section.index("### " + second_area))
        self.assertEqual(section.count("### " + first_area), 1)

    def test_expanded_flags_do_not_change_area_grouping_or_project_order(self):
        settings, items = self.interleaved_areas()
        for project, expanded in zip(settings["projects"], (False, True, True)):
            project["expanded"] = expanded
        mixed = updater.render_section(updater.build_snapshot(items, settings), TODAY.isoformat())
        self.assertEqual(re.findall(r"<details\b[^>]*>", mixed), ["<details>", "<details open>", "<details open>"])
        for project in settings["projects"]:
            project["expanded"] = False
        closed = updater.render_section(updater.build_snapshot(items, settings), TODAY.isoformat())
        self.assertEqual(mixed.replace("<details open>", "<details>"), closed)

    def test_area_heading_escapes_markdown_and_html_characters(self):
        settings = config()
        settings["projects"][0]["area"] = "GPU [kernels] & <tools> *training*"
        section = updater.render_section(updater.build_snapshot(fixtures(), settings), TODAY.isoformat())
        expected = "### GPU \\[kernels\\] &amp; &lt;tools&gt; \\*training\\*"
        self.assertIn(expected, section.splitlines())
        self.assertNotIn("<tools>", section)
        self.assertNotIn("### GPU [kernels]", section)

    def test_mixed_expanded_flags_control_each_fold_without_reordering_projects(self):
        settings = config()
        settings["projects"][0]["expanded"] = False
        settings["projects"][1]["expanded"] = True
        section = updater.render_section(updater.build_snapshot(fixtures(), settings), TODAY.isoformat())
        openings = re.findall(r"<details\b[^>]*>", section)
        self.assertEqual(openings, ["<details>", "<details open>"])
        self.assertLess(section.index(settings["projects"][0]["title"]), section.index(settings["projects"][1]["title"]))

    def test_all_false_expanded_flags_produce_default_closed_project_folds(self):
        settings = config()
        for project in settings["projects"]:
            project["expanded"] = False
        section = updater.render_section(updater.build_snapshot(fixtures(), settings), TODAY.isoformat())
        self.assertEqual(re.findall(r"<details\b[^>]*>", section), ["<details>"] * len(settings["projects"]))

    def test_only_dependency_chains_use_arrows_and_parallel_prs_use_plus(self):
        settings = config()
        settings["projects"][0]["chains"][1]["steps"].append({"label": "Independent validation", "prs": ["https://github.com/example/project/pull/2"]})
        settings["projects"][0]["chains"][0]["steps"][0]["prs"].append("https://github.com/example/project/pull/3")
        section = updater.render_section(updater.build_snapshot(fixtures(), settings), TODAY.isoformat())
        self.assertIn(" → ", section)
        self.assertIn(" + ", section)
        self.assertIn(" · ", section)
        self.assertEqual(section.count(" → "), 1)

    def test_each_chain_analysis_and_pr_continuation_share_one_inner_bullet(self):
        settings = config()
        section = updater.render_section(updater.build_snapshot(fixtures(), settings), TODAY.isoformat())
        bodies = re.findall(r"<details\b[^>]*>(.*?)</details>", section, re.DOTALL)
        self.assertEqual(len(bodies), len(settings["projects"]))
        for project, body in zip(settings["projects"], bodies):
            positions = list(re.finditer(r"(?m)^  - \*\*", body))
            self.assertEqual(len(positions), len(project["chains"]))
            self.assertNotRegex(body, r"(?m)^    - ")
            for index, chain in enumerate(project["chains"]):
                with self.subTest(repository=project["repository"], chain=chain["title"]):
                    end = positions[index + 1].start() if index + 1 < len(positions) else len(body)
                    item = body[positions[index].start():end]
                    expected_analysis = "  - **" + chain["title"] + ".** " + chain["analysis"]
                    self.assertEqual(item.splitlines()[0], expected_analysis)
                    continuations = [line for line in item.splitlines() if line.startswith("    " + chain["steps"][0]["label"] + " ")]
                    self.assertEqual(len(continuations), 1)
                    links = continuations[0]
                    for step in chain["steps"]:
                        self.assertIn(step["label"], links)
                        for url in step["prs"]:
                            self.assertIn(url, links)
                    for other in project["chains"]:
                        if other is not chain:
                            self.assertNotIn("**" + other["title"] + ".**", item)

    def test_inner_chain_bullet_preserves_markdown_and_html_escaping(self):
        settings = config()
        chain = settings["projects"][0]["chains"][0]
        chain["title"] = "Cache [shape] & <state> *checks*"
        chain["analysis"] = 'Validate <contract> & [inputs] before "reuse".'
        section = updater.render_section(updater.build_snapshot(fixtures(), settings), TODAY.isoformat())
        expected = '  - **Cache \\[shape\\] &amp; &lt;state&gt; \\*checks\\*.** Validate &lt;contract&gt; &amp; \\[inputs\\] before "reuse".'
        self.assertIn(expected, section.splitlines())
        self.assertNotIn("<state>", section)
        self.assertNotIn("<contract>", section)
        self.assertTrue(any(line.startswith("    Kernel baseline ") for line in section.splitlines()))

    def test_api_title_is_preserved_in_snapshot_and_escaped_in_tooltip(self):
        items = fixtures()
        title = 'Fix <script>alert(1)</script> & [link] " onmouseover="alert(1)'
        items[0]["title"] = title
        snapshot = updater.build_snapshot(items, config())
        self.assertEqual(snapshot["projects"][0]["chains"][0]["steps"][0]["prs"][0]["title"], title)
        section = updater.render_section(snapshot, TODAY.isoformat())
        self.assertNotIn("<script>", section)
        self.assertNotIn(' onmouseover="', section)
        self.assertIn("&lt;script&gt;", section)
        self.assertIn(items[0]["html_url"], section)

    def test_all_four_statuses_and_pr_links_are_retained_inside_project_details(self):
        section = updater.render_section(updater.build_snapshot(fixtures(), config()), TODAY.isoformat())
        details = "\n".join(re.findall(r"<details\b[^>]*>(.*?)</details>", section, re.DOTALL))
        for status in ("Merged", "Open", "Draft", "Closed"):
            self.assertIn(status, details)
        for item in fixtures():
            self.assertIn(item["html_url"], details)


class ReplacementTests(unittest.TestCase):
    def test_only_marked_region_changes(self):
        prefix = "# Profile\n\nA manually maintained introduction.\n"
        suffix = "\n## Research\n\nKeep everything below here.\n"
        readme = f"{prefix}{updater.START_MARKER}\nold section\n{updater.END_MARKER}{suffix}"
        updated = updater.replace_section(readme, "new section")
        self.assertTrue(updated.startswith(prefix + updater.START_MARKER))
        self.assertTrue(updated.endswith(updater.END_MARKER + suffix))
        self.assertIn("new section", updated)
        self.assertNotIn("old section", updated)

    def test_missing_duplicate_or_reversed_markers_are_rejected(self):
        invalid = [
            "# No markers", updater.START_MARKER, updater.END_MARKER,
            updater.END_MARKER + updater.START_MARKER,
            updater.START_MARKER + updater.START_MARKER + updater.END_MARKER,
            updater.START_MARKER + updater.END_MARKER + updater.END_MARKER,
            updater.START_MARKER + updater.END_MARKER + updater.START_MARKER + updater.END_MARKER,
        ]
        for readme in invalid:
            with self.subTest(readme=readme), self.assertRaises(updater.UpdateError):
                updater.replace_section(readme, "new section")


class NetworkTests(unittest.TestCase):
    @staticmethod
    def http_error(code, headers=None):
        return HTTPError("https://api.github.com/repos/example/project/pulls/1", code, "Failure", headers or {}, io.BytesIO(b'{"message":"API failure"}'))

    def test_transient_server_error_is_retried_and_request_has_a_timeout(self):
        response = io.BytesIO(json.dumps(pr(1)).encode("utf-8"))
        with patch.object(updater, "urlopen", side_effect=[self.http_error(503), response]) as request, patch.object(updater.time, "sleep") as sleep:
            result = updater.GitHubClient().pull_request("example/project", 1)
        self.assertEqual(result["number"], 1)
        self.assertEqual(request.call_count, 2)
        self.assertEqual(request.call_args.kwargs["timeout"], 20)
        self.assertIn("/repos/example/project/pulls/1", request.call_args.args[0].full_url)
        sleep.assert_called_once_with(2)

    def test_connection_failure_has_three_attempts_and_bounded_backoff(self):
        with patch.object(updater, "urlopen", side_effect=URLError("offline")) as request, patch.object(updater.time, "sleep") as sleep:
            with self.assertRaises(updater.UpdateError):
                updater.GitHubClient().pull_request("example/project", 1)
        self.assertEqual(request.call_count, 3)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [2, 4])

    def test_permission_failure_is_not_retried(self):
        with patch.object(updater, "urlopen", side_effect=self.http_error(403)) as request, patch.object(updater.time, "sleep") as sleep:
            with self.assertRaises(updater.UpdateError):
                updater.GitHubClient().pull_request("example/project", 1)
        request.assert_called_once()
        sleep.assert_not_called()

    def test_rate_limit_requesting_long_wait_is_left_for_next_run(self):
        with patch.object(updater, "urlopen", side_effect=self.http_error(429, {"Retry-After": "61"})) as request, patch.object(updater.time, "sleep") as sleep:
            with self.assertRaises(updater.UpdateError):
                updater.GitHubClient().pull_request("example/project", 1)
        request.assert_called_once()
        sleep.assert_not_called()

    def test_invalid_json_fails_without_retrying(self):
        with patch.object(updater, "urlopen", return_value=io.BytesIO(b"not JSON")) as request, patch.object(updater.time, "sleep") as sleep:
            with self.assertRaises(updater.UpdateError):
                updater.GitHubClient().pull_request("example/project", 1)
        request.assert_called_once()
        sleep.assert_not_called()

    def test_request_budget_stops_before_starting_another_request(self):
        client = updater.GitHubClient()
        with patch.object(updater.time, "monotonic", return_value=client.deadline - 19), patch.object(updater, "urlopen") as request:
            with self.assertRaises(updater.UpdateError):
                client.pull_request("example/project", 1)
        request.assert_not_called()


class UpdateTests(unittest.TestCase):
    def setUp(self):
        output_patch = patch.object(sys, "stdout", new=io.StringIO())
        output_patch.start()
        self.addCleanup(output_patch.stop)
        self.directory = tempfile.TemporaryDirectory(prefix="contributions-tests-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.original_readme = f"# My Profile\n\nBefore.\n{updater.START_MARKER}\nold section\n{updater.END_MARKER}\n\nAfter.\n"
        (self.root / "README.md").write_text(self.original_readme, encoding="utf-8")
        self.items = fixtures()
        self.config = config()

    def files(self):
        return {path.relative_to(self.root).as_posix(): path.read_bytes() for path in self.root.rglob("*") if path.is_file()}

    def mtimes(self):
        return {path.relative_to(self.root).as_posix(): path.stat().st_mtime_ns for path in self.root.rglob("*") if path.is_file()}

    def test_first_run_writes_only_snapshot_and_readme(self):
        self.assertTrue(updater.update(self.root, self.items, self.config, TODAY))
        output = self.files()
        self.assertEqual(set(output), {"README.md", "assets/contributions-data.json"})
        snapshot = json.loads(output["assets/contributions-data.json"])
        self.assertEqual(snapshot["schema_version"], 2)
        self.assertEqual(snapshot["verified_on"], TODAY.isoformat())
        self.assertEqual(len(snapshot["data"]["projects"]), 2)
        self.assertTrue(output["README.md"].startswith(b"# My Profile\n\nBefore.\n"))
        self.assertTrue(output["README.md"].endswith(b"\n\nAfter.\n"))

    def test_windows_crlf_readme_preserves_prefix_suffix_and_generated_line_endings(self):
        prefix = "# Profile — 文博\r\n\r\nBefore:  two spaces.  \r\n".encode("utf-8")
        suffix = "\r\n\r\n## Research\r\n\r\nAfter: retain trailing spaces.  \r\n".encode("utf-8")
        original = prefix + updater.START_MARKER.encode() + b"\r\nold section\r\n" + updater.END_MARKER.encode() + suffix
        readme_path = self.root / "README.md"
        readme_path.write_bytes(original)
        self.assertTrue(updater.update(self.root, self.items, self.config, TODAY))
        result = readme_path.read_bytes()
        self.assertTrue(result.startswith(prefix + updater.START_MARKER.encode()))
        self.assertTrue(result.endswith(updater.END_MARKER.encode() + suffix))
        self.assertNotRegex(result, rb"(?<!\r)\n")
        self.assertNotIn(b"old section", result)
        self.assertFalse(updater.update(self.root, self.items, self.config, TODAY))
        self.assertEqual(readme_path.read_bytes(), result)

    def test_repeat_weekly_and_updated_at_only_changes_are_noops(self):
        updater.update(self.root, self.items, self.config, TODAY)
        before, mtimes = self.files(), self.mtimes()
        changed_metadata = list(reversed(copy.deepcopy(self.items)))
        for item in changed_metadata:
            item["updated_at"] = "2026-10-08T00:00:00Z"
        self.assertFalse(updater.update(self.root, changed_metadata, self.config, TODAY + timedelta(days=7)))
        self.assertEqual(self.files(), before)
        self.assertEqual(self.mtimes(), mtimes)

    def test_refresh_occurs_at_42_days_but_not_at_41(self):
        updater.update(self.root, self.items, self.config, TODAY)
        before = self.files()
        self.assertFalse(updater.update(self.root, self.items, self.config, TODAY + timedelta(days=41)))
        self.assertEqual(self.files(), before)
        refreshed = TODAY + timedelta(days=42)
        self.assertTrue(updater.update(self.root, self.items, self.config, refreshed))
        data = json.loads((self.root / "assets/contributions-data.json").read_text(encoding="utf-8"))
        self.assertEqual(data["verified_on"], refreshed.isoformat())
        self.assertFalse(updater.update(self.root, self.items, self.config, refreshed))

    def test_status_title_and_editorial_changes_trigger_refresh(self):
        updater.update(self.root, self.items, self.config, TODAY)
        changed = copy.deepcopy(self.items)
        changed[1]["state"] = "closed"
        changed[1]["merged_at"] = "2026-10-09T00:00:00Z"
        self.assertTrue(updater.update(self.root, changed, self.config, TODAY + timedelta(days=1)))
        changed[0]["title"] = "A corrected pull request title"
        self.assertTrue(updater.update(self.root, changed, self.config, TODAY + timedelta(days=2)))
        changed_config = copy.deepcopy(self.config)
        changed_config["projects"][0]["summary"] = "Updated editorial summary."
        self.assertTrue(updater.update(self.root, changed, changed_config, TODAY + timedelta(days=3)))
        self.assertIn("Updated editorial summary.", (self.root / "README.md").read_text(encoding="utf-8"))

    def test_v1_snapshot_is_regenerated_as_v2(self):
        state_path = self.root / "assets/contributions-data.json"
        state_path.parent.mkdir()
        state_path.write_text(json.dumps({"schema_version": 1, "verified_on": TODAY.isoformat(), "data": {"counts": {"merged": 99}}}), encoding="utf-8")
        self.assertTrue(updater.update(self.root, self.items, self.config, TODAY))
        state = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["schema_version"], 2)
        self.assertNotIn("counts", state["data"])

    def test_bad_markers_leave_existing_generated_files_untouched(self):
        updater.update(self.root, self.items, self.config, TODAY)
        (self.root / "README.md").write_text("# Accidentally removed markers\n", encoding="utf-8")
        before = self.files()
        with self.assertRaises(updater.UpdateError):
            updater.update(self.root, self.items, self.config, TODAY + timedelta(days=1))
        self.assertEqual(self.files(), before)

    def test_missing_selected_pr_leaves_existing_files_untouched(self):
        updater.update(self.root, self.items, self.config, TODAY)
        before = self.files()
        with self.assertRaises(updater.UpdateError):
            updater.update(self.root, self.items[:-1], self.config, TODAY)
        self.assertEqual(self.files(), before)

    def test_dry_run_proposes_changes_without_creating_or_editing_files(self):
        before = self.files()
        self.assertTrue(updater.update(self.root, self.items, self.config, TODAY, dry_run=True))
        self.assertEqual(self.files(), before)
        updater.update(self.root, self.items, self.config, TODAY)
        before = self.files()
        changed = copy.deepcopy(self.items)
        changed[0]["title"] = "A revised title"
        self.assertTrue(updater.update(self.root, changed, self.config, TODAY, dry_run=True))
        self.assertEqual(self.files(), before)

    def test_cli_api_failure_reports_error_without_modifying_previous_files(self):
        updater.update(self.root, self.items, self.config, TODAY)
        (self.root / "contributions.json").write_text(json.dumps(self.config), encoding="utf-8")
        before = self.files()
        stderr = io.StringIO()

        class FailingClient:
            def pull_request(self, repo, number):
                raise updater.UpdateError("GitHub API unavailable")

        with patch.object(updater, "GitHubClient", return_value=FailingClient()), redirect_stderr(stderr):
            result = updater.main(["--root", str(self.root)])
        self.assertEqual(result, 1)
        self.assertIn("GitHub API unavailable", stderr.getvalue())
        self.assertEqual(self.files(), before)

    def test_cli_offline_raw_array_legacy_array_and_items_envelope_are_accepted(self):
        (self.root / "contributions.json").write_text(json.dumps(self.config), encoding="utf-8")
        input_path = self.root / "input.json"
        sources = [
            self.items,
            [legacy_item(item) for item in self.items],
            {"items": self.items, "total_count": len(self.items), "incomplete_results": False},
        ]
        for source in sources:
            with self.subTest(input_shape=type(source).__name__):
                input_path.write_text(json.dumps(source), encoding="utf-8")
                self.assertEqual(updater.main(["--root", str(self.root), "--input-json", str(input_path)]), 0)
        state = json.loads((self.root / "assets/contributions-data.json").read_text(encoding="utf-8"))
        self.assertEqual(state["data"], updater.build_snapshot(self.items, self.config))

    def test_incomplete_offline_search_response_leaves_previous_files_untouched(self):
        updater.update(self.root, self.items, self.config, TODAY)
        (self.root / "contributions.json").write_text(json.dumps(self.config), encoding="utf-8")
        input_path = self.root / "input.json"
        input_path.write_text(json.dumps({"items": self.items, "incomplete_results": True}), encoding="utf-8")
        before = self.files()
        with redirect_stderr(io.StringIO()):
            self.assertEqual(updater.main(["--root", str(self.root), "--input-json", str(input_path)]), 1)
        self.assertEqual(self.files(), before)

    def test_failed_atomic_save_rolls_back_previous_output(self):
        updater.update(self.root, self.items, self.config, TODAY)
        before = self.files()
        changed = copy.deepcopy(self.items)
        changed[0]["title"] = "A new title"
        original_replace = updater.os.replace
        attempts = 0

        def fail_second_replace(source, destination):
            nonlocal attempts
            attempts += 1
            if attempts == 2:
                raise OSError("simulated filesystem error")
            return original_replace(source, destination)

        with patch.object(updater.os, "replace", side_effect=fail_second_replace):
            with self.assertRaises(updater.UpdateError):
                updater.update(self.root, changed, self.config, TODAY + timedelta(days=1))
        self.assertEqual(self.files(), before)


if __name__ == "__main__":
    unittest.main()
