#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from build_chat_overlay_spec import build_spec, load_config, parse_transcript


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a renderable Remotion chat overlay bundle.")
    parser.add_argument("--transcript", required=True, help="Path to transcript text file")
    parser.add_argument("--config", help="Path to scene config JSON")
    parser.add_argument("--output-dir", required=True, help="Directory to create the Remotion bundle in")
    parser.add_argument("--force", action="store_true", help="Overwrite the output directory if it exists")
    return parser.parse_args()


def script_dir() -> Path:
    return Path(__file__).resolve().parent


def skill_root() -> Path:
    return script_dir().parent


def template_dir() -> Path:
    return skill_root() / "assets" / "remotion-template"


def avatar_library_dir() -> Path:
    return skill_root() / "assets" / "avatar-library"


def copy_template(output_dir: Path, force: bool) -> None:
    if output_dir.exists():
        if not force:
            raise SystemExit(f"Output directory already exists: {output_dir}. Use --force to overwrite.")
        shutil.rmtree(output_dir)
    shutil.copytree(template_dir(), output_dir)


def write_chat_spec_ts(spec: dict, output_dir: Path) -> None:
    target = output_dir / "src" / "chatSpec.ts"
    content = "export const chatSpec = " + json.dumps(spec, ensure_ascii=False, indent=2) + " as const;\n"
    target.write_text(content, encoding="utf-8")


def remove_local_upload_paths(spec: dict) -> None:
    assignments = spec["sceneConfig"]["avatarAssignments"]
    for side in ("left", "right"):
        assignments.pop(f"{side}UploadPath", None)


def copy_avatar_assets(spec: dict, output_dir: Path) -> None:
    public_dir = output_dir / "public"
    public_dir.mkdir(parents=True, exist_ok=True)
    for preset_file in avatar_library_dir().glob("*.png"):
        shutil.copy2(preset_file, public_dir / preset_file.name)
    assignments = spec["sceneConfig"]["avatarAssignments"]
    for side in ("left", "right"):
        upload_path = assignments.get(f"{side}UploadPath")
        if upload_path:
            source = Path(upload_path).expanduser().resolve()
            if not source.exists():
                raise SystemExit(
                    f"Configured {side}UploadPath does not exist: {source}. "
                    "Fix the upload avatar path before preparing the bundle."
                )
            target_name = f"{side}-upload{source.suffix.lower()}"
            shutil.copy2(source, public_dir / target_name)
            assignments[f"{side}UploadAsset"] = target_name
    remove_local_upload_paths(spec)
    write_chat_spec_ts(spec, output_dir)


def main() -> None:
    args = parse_args()
    parsed = parse_transcript(Path(args.transcript))
    config = load_config(args.config)
    spec = build_spec(parsed, config)
    out_dir = Path(args.output_dir).resolve()
    copy_template(out_dir, args.force)
    write_chat_spec_ts(spec, out_dir)
    copy_avatar_assets(spec, out_dir)
    print(f"Prepared Remotion bundle at {out_dir}")


if __name__ == "__main__":
    main()
