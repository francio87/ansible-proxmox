from pathlib import Path

import yaml


PLAYBOOK = Path(__file__).parents[1] / "setup.yml"


def _tasks(playbook):
    document = yaml.safe_load(playbook.read_text())
    play = document[0]
    return play.get("pre_tasks", []) + play.get("tasks", [])


def _task(name):
    return next(task for task in _tasks(PLAYBOOK) if task.get("name") == name)


def test_installed_version_probe_is_read_only_and_non_fatal():
    task = _task("Read installed cv4pve-autosnap version")

    assert task["ansible.builtin.command"]["argv"][-1] == "--version"
    assert task["changed_when"] is False
    assert task["failed_when"] is False
    assert task["check_mode"] is False


def test_release_download_path_is_gated_by_installed_version():
    gated_tasks = {
        "Query cv4pve-autosnap release",
        "Download cv4pve-autosnap release",
        "Extract cv4pve-autosnap release",
        "Install cv4pve-autosnap binary in local bin",
    }

    for name in gated_tasks:
        assert _task(name)["when"] == "cv4pve_autosnap_update_needed"


def test_only_single_persistent_binary_path_is_documented():
    readme = (PLAYBOOK.parent / "README.md").read_text()

    assert "/usr/local/bin/cv4pve-autosnap" in readme
    assert "/usr/local/libexec" not in readme
