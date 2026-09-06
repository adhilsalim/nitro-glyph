#!/usr/bin/env python3

from __future__ import annotations

import argparse
import configparser
import glob
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_CONFIG = Path(__file__).with_name("release.ini")
PROJECT_VERSION_PATTERN = re.compile(r'^version\s*=\s*["\']([^"\']+)["\']', re.MULTILINE)


def load_config(config_path: Path) -> configparser.SectionProxy:
    parser = configparser.ConfigParser()
    if not config_path.exists():
        raise FileNotFoundError(
            f"Missing config file: {config_path}. Copy release.ini.example to release.ini first."
        )

    parser.read(config_path)
    if "release" not in parser:
        raise KeyError("Config file must contain a [release] section")

    return parser["release"]


def read_project_version(project_dir: Path) -> str:
    pyproject_path = project_dir / "pyproject.toml"
    if not pyproject_path.exists():
        raise FileNotFoundError(f"Missing pyproject.toml: {pyproject_path}")

    pyproject_text = pyproject_path.read_text(encoding="utf-8")
    match = PROJECT_VERSION_PATTERN.search(pyproject_text)
    if match is None:
        raise ValueError(f"Could not find project version in {pyproject_path}")

    return match.group(1)


def run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def clean_dist(project_dir: Path) -> Path:
    dist_dir = project_dir / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    return dist_dir


def prompt_yes_no(message: str, default: bool = False) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    response = input(f"{message} {suffix} ").strip().lower()
    if not response:
        return default
    return response in {"y", "yes"}


def prompt_exact(message: str, expected: str) -> bool:
    return input(f"{message} ").strip() == expected


def show_info(title: str, lines: list[str]) -> None:
    print(f"\n== {title} ==")
    for line in lines:
        print(line)


def build_package(project_dir: Path, yes: bool) -> list[Path]:
    version = read_project_version(project_dir)
    dist_dir = clean_dist(project_dir)

    show_info(
        "Build summary",
        [
            f"Project directory: {project_dir}",
            f"Version: {version}",
            f"Removing old artifacts from: {dist_dir}",
        ],
    )

    if not yes and not prompt_yes_no("Remove old dist artifacts and build the package?"):
        raise RuntimeError("Build cancelled by user")

    run([sys.executable, "-m", "build"], cwd=project_dir)

    dist_files = sorted(glob.glob(str(dist_dir / "*")))
    if not dist_files:
        raise FileNotFoundError(f"No distribution files found in {dist_dir}")

    run([sys.executable, "-m", "twine", "check", *dist_files], cwd=project_dir)

    show_info(
        "Build complete",
        [
            f"Created version: {version}",
            "Artifacts:",
            *[f"- {Path(path).name}" for path in dist_files],
        ],
    )

    return [Path(path) for path in dist_files]


def deploy_package(project_dir: Path, yes: bool, token: str, username: str) -> int:
    version = read_project_version(project_dir)
    dist_dir = project_dir / "dist"
    dist_files = sorted(glob.glob(str(dist_dir / "*")))

    if not dist_files:
        raise FileNotFoundError(
            f"No distribution files found in {dist_dir}. Run the build command first or let deploy rebuild."
        )

    show_info(
        "Deploy summary",
        [
            "Target: PyPI",
            f"Project directory: {project_dir}",
            f"Version: {version}",
            "Files to upload:",
            *[f"- {Path(path).name}" for path in dist_files],
        ],
    )

    if not yes and not prompt_exact(f"Type the version to continue ({version}):", version):
        raise RuntimeError("Deployment cancelled because the version confirmation did not match")

    if not yes and not prompt_yes_no("Upload these files to PyPI?"):
        raise RuntimeError("Deployment cancelled by user")

    upload_command = [
        sys.executable,
        "-m",
        "twine",
        "upload",
        "--repository-url",
        "https://upload.pypi.org/legacy/",
        "--username",
        username,
        "--password",
        token,
        *dist_files,
    ]

    run(upload_command, cwd=project_dir)

    show_info(
        "Deploy complete",
        [
            f"Published version: {version}",
            "You can now install it with:",
            "pip install nitroglyph",
        ],
    )

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build or deploy nitroglyph")
    subparsers = parser.add_subparsers(dest="command", required=True)

    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to release.ini",
    )
    common_parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompts",
    )

    subparsers.add_parser("build", parents=[common_parser], help="Build and validate the package")
    subparsers.add_parser("deploy", parents=[common_parser], help="Build, validate, and upload to PyPI")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    config = load_config(args.config)
    project_dir = Path(config.get("project_dir", Path(__file__).parent)).resolve()
    token = os.environ.get("PYPI_TOKEN") or config.get("token", fallback="").strip()
    username = config.get("username", fallback="__token__")

    if args.command == "build":
        build_package(project_dir, args.yes)
        return 0

    if not token:
        raise RuntimeError("Missing PyPI token. Set PYPI_TOKEN or add token=... to release.ini")

    build_package(project_dir, args.yes)
    return deploy_package(project_dir, args.yes, token, username)


if __name__ == "__main__":
    raise SystemExit(main())