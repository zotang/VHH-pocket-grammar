# VHH Pocket Grammar

Topology-first VHH profile assets for small-molecule pocket design and inspection.

This repository contains a public v4 profile set with five pocket grammar modes:

| Key | Mode | Oligomeric state | RFantibody |
| --- | --- | --- | --- |
| `deep_cavity` | Capped buried cavity | Monomer | Supported |
| `lateral_groove` | Side-open groove | Monomer | Supported |
| `tunnel_cdr1_cdr3_fr1` | Roofed under-CDR1 tunnel | Monomer | Supported |
| `tunnel_cdr1_cdr2_fr3` | Inter-sheet edge-slit tunnel | Monomer | Supported |
| `dimeric_groove` | Symmetric inter-protomer clamp | Homodimer | Not supported |

The profile YAML files are machine-readable contracts. They define pocket topology, residue selections, ligand reference handling, stage policies, contact grammar, workflow hints, and filter grammar. PDB files under `profiles/` provide the cleaned frameworks and holo/apo references named by the manifest.

## Repository layout

```text
profiles/
  builtin_vhh_profiles_manifest_v4.yml
  *_v4.yml
  *.pdb
scripts/
  inspect_profiles.py
examples/
  sample_query.yml
  sample_result.json
```

## Install

Use Python 3.9 or newer.

```bash
python -m pip install -r requirements.txt
```

The only runtime dependency for the inspection script is PyYAML.

## Use the profiles

Load `profiles/builtin_vhh_profiles_manifest_v4.yml` first. Each manifest entry points to one profile YAML plus its framework and reference PDB files.

```python
from pathlib import Path
import yaml

root = Path("profiles")
manifest = yaml.safe_load((root / "builtin_vhh_profiles_manifest_v4.yml").read_text())

for entry in manifest["profiles"]:
    profile = yaml.safe_load((root / entry["profile_yaml"]).read_text())
    print(entry["built_in_key"], profile["mode_subtype"], entry["framework_pdb"])
```

Residue selections in these YAML files are stored in `pdb_author` numbering. Generate IMGT or Chothia maps from the cleaned framework PDB when a downstream tool needs another numbering scheme.

## Inspection program

`scripts/inspect_profiles.py` reads the manifest, joins each entry to its profile YAML, verifies referenced files, and emits either JSON or a compact table.

List all profiles as a table:

```bash
python scripts/inspect_profiles.py --profiles-dir profiles --format table
```

Run the sample query and write JSON:

```bash
python scripts/inspect_profiles.py \
  --profiles-dir profiles \
  --query examples/sample_query.yml \
  --format json
```

## Sample data

`examples/sample_query.yml` selects two profile keys and requests the most common integration fields:

```yaml
profile_keys:
  - deep_cavity
  - lateral_groove
fields:
  - built_in_key
  - display_name
  - mode_subtype
  - oligomeric_state
  - ligand_resname
  - topology_class
  - framework_pdb
  - holo_reference_pdb
```

## Sample result

Expected output for the sample query is stored at `examples/sample_result.json`.

```bash
python scripts/inspect_profiles.py --profiles-dir profiles --query examples/sample_query.yml --format json
```

The output contains one object per selected profile, including the ligand residue name, topology class, and referenced PDB assets.

## Profile asset notes

- `profiles/builtin_vhh_profiles_manifest_v4.yml` is the entry point for programmatic use.
- `*_framework_*.pdb` files are cleaned framework scaffolds.
- `*_holo_ref_*.pdb` files provide holo reference geometry and ligand conformer context.
- `*_original_*.pdb` files preserve original apo/holo references for traceability.
- `dimeric_groove` is a homodimeric interface profile and is intentionally RFantibody-disabled.

## Citation and provenance

The file names identify the exemplar PDB structures used by each profile, including 7TJC, 1I3U/1I3V, 3QXV/3QXW, 8FTG, and the fipronil VHH reference set.
