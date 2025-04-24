#!/usr/bin/env python3
import argparse
from typing import Any
from typing import IO
from typing import Sequence

import ruamel.yaml


def move_key_to_end(given_dict: dict[str, Any], keyname: str) -> None:
    value = given_dict.pop(keyname)
    given_dict[keyname] = value


def check_source_entry(source: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons = []
    if "helm" not in source:
        return True, []
    retval = True
    source_keys = list(source.keys())
    if source_keys[-1] != "helm":
        reasons.append("helm is not the last key")
        move_key_to_end(source, "helm")
        retval = False

    helm_keys = list(source.get("helm", {}).keys())

    move_values = False

    if "values" in helm_keys and "valuesObject" in helm_keys:
        if "values" not in helm_keys[-2:] or "valuesObject" not in helm_keys[-2:]:
            reasons.append("in helm section 'values' and 'valuesObject' are not the last keys")
            move_values = True

    for keyname in ["values", "valuesObject"]:
        if keyname in helm_keys and helm_keys[-1] != keyname:
            reasons.append(f"in helm section '{keyname}' is not the last key")
            move_values = True

    if move_values:
        retval = False
        helm_section: dict[str, Any] = source.get("helm", {})
        for keyname in ["values", "valuesObject"]:
            if keyname in helm_keys:
                move_key_to_end(helm_section, keyname)

    return retval, reasons


def check_file(filename: str, yaml: ruamel.yaml.YAML, args: argparse.Namespace) -> bool:  # type: ignore
    fp: IO[bytes] = open(filename, "rb+")
    try:
        manifest = yaml.load(fp.read())
    except ruamel.yaml.YAMLError as exc:  # type: ignore
        print(exc)
        return False

    if not isinstance(manifest, dict):
        print(f"Warning: YAML manifest not parsed as dict/map ({type(manifest)}) [SKIP]")
        return True

    if manifest.get("kind") != "Application":
        if args.verbose:
            print(f"{filename}: is not an ArgoCD Application manifest [SKIP]")
        return True
    if manifest.get("apiVersion") != "argoproj.io/v1alpha1":
        if args.verbose:
            print(f"{filename}: api version not handled [SKIP]")
        return True
    retval = True
    spec_keys = list(manifest.get("spec", {}).keys())
    if spec_keys[-1] not in ["source", "sources"]:
        print(f"{filename}: source is not the last key in spec")
        retval = False
        for keyname in ["source", "sources"]:
            if keyname in spec_keys:
                move_key_to_end(manifest["spec"], keyname)

    for keyname in ["source", "sources"]:
        if keyname in spec_keys:
            if keyname == "source":
                status, reasons = check_source_entry(manifest["spec"][keyname])
                if not status:
                    print(f"{filename}: in source, {'; '.join(reasons)}")
                    retval = False
            elif keyname == "sources":
                for i in range(len(manifest["spec"][keyname])):
                    status, reasons = check_source_entry(manifest["spec"][keyname][i])
                    if not status:
                        print(f"{filename}: in source #{i}, {'; '.join(reasons)}")
                        retval = False

    if not retval:
        fp.seek(0)
        yaml.dump(manifest, fp)
        fp.truncate()

    return retval


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
    )
    args = parser.parse_args(argv)

    retval = 0
    yaml = ruamel.yaml.YAML()  # type: ignore
    for filename in args.filenames:
        try:
            if not check_file(filename, yaml, args):
                retval = 1
        except Exception as e:
            print(f"error parsing {filename}")
            raise e
    return retval


if __name__ == "__main__":
    raise SystemExit(main())
