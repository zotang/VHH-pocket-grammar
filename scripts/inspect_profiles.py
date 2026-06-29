#!/usr/bin/env python3
"""Inspect the VHH pocket grammar profile manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    print("PyYAML is required. Install with: python -m pip install -r requirements.txt", file=sys.stderr)
    raise SystemExit(2)


DEFAULT_FIELDS = [
    "built_in_key",
    "display_name",
    "mode_subtype",
    "oligomeric_state",
    "supports_rfantibody",
    "ligand_resname",
    "topology_class",
    "topology_subtype",
    "framework_pdb",
    "holo_reference_pdb",
]


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} did not contain a YAML mapping")
    return data


def collect_profiles(profiles_dir: Path, manifest_name: str) -> list[dict[str, Any]]:
    manifest_path = profiles_dir / manifest_name
    manifest = load_yaml(manifest_path)
    rows: list[dict[str, Any]] = []

    for entry in manifest.get("profiles", []):
        profile_path = profiles_dir / entry["profile_yaml"]
        profile = load_yaml(profile_path)
        topology = profile.get("topology") or {}
        ligand = profile.get("ligand") or {}

        referenced_files = [
            entry.get("profile_yaml"),
            entry.get("framework_pdb"),
            entry.get("holo_reference_pdb"),
            entry.get("auxiliary_apo_framework_pdb"),
        ]
        missing_files = [
            name for name in referenced_files if name and not (profiles_dir / name).exists()
        ]

        rows.append(
            {
                "built_in_key": entry.get("built_in_key"),
                "display_name": entry.get("display_name"),
                "profile_yaml": entry.get("profile_yaml"),
                "mode_subtype": entry.get("mode_subtype") or profile.get("mode_subtype"),
                "mode_family": profile.get("mode_family"),
                "oligomeric_state": entry.get("oligomeric_state") or profile.get("oligomeric_state"),
                "supports_rfantibody": entry.get("supports_rfantibody"),
                "ligand_resname": ligand.get("resname"),
                "protein_chain_ids": profile.get("protein_chain_ids", []),
                "topology_class": topology.get("topology_class"),
                "topology_subtype": topology.get("topology_subtype"),
                "framework_pdb": entry.get("framework_pdb"),
                "holo_reference_pdb": entry.get("holo_reference_pdb"),
                "missing_files": missing_files,
            }
        )

    return rows


def load_query(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return load_yaml(path)


def filter_rows(rows: list[dict[str, Any]], query: dict[str, Any]) -> list[dict[str, Any]]:
    keys = query.get("profile_keys")
    if keys:
        wanted = set(keys)
        rows = [row for row in rows if row["built_in_key"] in wanted]

    fields = query.get("fields") or DEFAULT_FIELDS
    filtered = [{field: row.get(field) for field in fields} for row in rows]

    if query.get("include_missing_files"):
        for source, target in zip(rows, filtered):
            target["missing_files"] = source["missing_files"]

    return filtered


def emit_table(rows: list[dict[str, Any]]) -> None:
    fields = ["built_in_key", "mode_subtype", "oligomeric_state", "ligand_resname", "framework_pdb"]
    widths = {
        field: max(len(field), *(len(str(row.get(field, ""))) for row in rows))
        for field in fields
    }
    print("  ".join(field.ljust(widths[field]) for field in fields))
    print("  ".join("-" * widths[field] for field in fields))
    for row in rows:
        print("  ".join(str(row.get(field, "")).ljust(widths[field]) for field in fields))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles-dir", default="profiles", type=Path)
    parser.add_argument("--manifest", default="builtin_vhh_profiles_manifest_v4.yml")
    parser.add_argument("--query", type=Path)
    parser.add_argument("--format", choices=["json", "table"], default="json")
    args = parser.parse_args(argv)

    rows = collect_profiles(args.profiles_dir, args.manifest)
    query = load_query(args.query)
    rows = filter_rows(rows, query)

    if args.format == "table":
        emit_table(rows)
    else:
        print(json.dumps(rows, indent=2, sort_keys=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
