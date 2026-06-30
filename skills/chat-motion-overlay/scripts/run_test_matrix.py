#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the chat-motion-overlay test matrix.")
    parser.add_argument("--skill-root", required=True, help="Path to the skill root")
    parser.add_argument("--work-dir", required=True, help="Directory for generated test artifacts")
    parser.add_argument("--node-modules", required=True, help="Resolved node_modules directory with remotion/react/typescript")
    parser.add_argument("--render", action="store_true", help="Render representative still frames with Remotion")
    return parser.parse_args()


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True)


def main() -> None:
    args = parse_args()
    skill_root = Path(args.skill_root).resolve()
    work_dir = Path(args.work_dir).resolve()
    node_modules = Path(args.node_modules).resolve()
    build_script = skill_root / "scripts" / "build_chat_overlay_spec.py"
    bundle_script = skill_root / "scripts" / "prepare_chat_overlay_bundle.py"
    transcript = skill_root / "assets" / "examples" / "chat-transcript.txt"
    avatar_dir = skill_root / "assets" / "avatar-library"

    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    sample_upload_left = str((avatar_dir / "female-bunny-pink.png").resolve())
    sample_upload_right = str((avatar_dir / "male-penguin-blue.png").resolve())
    missing_upload_right = str((avatar_dir / "missing-avatar-does-not-exist.png").resolve())

    cases = [
        {
            "name": "default_wechat_phone_preset_hidden",
            "config": {
                "container": "wechat",
                "avatarMode": "preset",
                "deviceFrame": "iphone-dynamic-island",
                "nicknameMode": "hidden",
                "deliveryFormat": "mov",
                "showTimestamp": True,
                "avatarAssignments": {
                    "leftPreset": "female-bunny-pink",
                    "rightPreset": "female-cat-orange",
                    "leftUploadPath": None,
                    "rightUploadPath": None,
                },
            },
            "render": True,
            "expect_fail": False,
        },
        {
            "name": "plain_bubbles_no_frame_first_message",
            "config": {
                "container": "none",
                "avatarMode": "preset",
                "deviceFrame": "none",
                "nicknameMode": "first-message-only",
                "deliveryFormat": "remotion",
                "showTimestamp": False,
                "avatarAssignments": {
                    "leftPreset": "female-bunny-pink",
                    "rightPreset": "female-cat-orange",
                    "leftUploadPath": None,
                    "rightUploadPath": None,
                },
            },
            "render": True,
            "expect_fail": False,
        },
        {
            "name": "telegram_no_frame_always",
            "config": {
                "container": "telegram",
                "avatarMode": "preset",
                "deviceFrame": "none",
                "nicknameMode": "always",
                "deliveryFormat": "webm",
                "showTimestamp": True,
                "avatarAssignments": {
                    "leftPreset": "female-fox-yellow",
                    "rightPreset": "male-bear-mint",
                    "leftUploadPath": None,
                    "rightUploadPath": None,
                },
            },
            "render": True,
            "expect_fail": False,
        },
        {
            "name": "messenger_phone_hidden",
            "config": {
                "container": "messenger",
                "avatarMode": "preset",
                "deviceFrame": "iphone-dynamic-island",
                "nicknameMode": "hidden",
                "deliveryFormat": "mov",
                "showTimestamp": True,
                "avatarAssignments": {
                    "leftPreset": "male-koala-lilac",
                    "rightPreset": "male-penguin-blue",
                    "leftUploadPath": None,
                    "rightUploadPath": None,
                },
            },
            "render": True,
            "expect_fail": False,
        },
        {
            "name": "upload_phone_always",
            "config": {
                "container": "wechat",
                "avatarMode": "upload",
                "deviceFrame": "iphone-dynamic-island",
                "nicknameMode": "always",
                "deliveryFormat": "mov",
                "showTimestamp": True,
                "avatarAssignments": {
                    "leftPreset": "female-bunny-pink",
                    "rightPreset": "female-cat-orange",
                    "leftUploadPath": sample_upload_left,
                    "rightUploadPath": sample_upload_right,
                },
            },
            "render": True,
            "expect_fail": False,
        },
        {
            "name": "mixed_wechat_phone_first_message",
            "config": {
                "container": "wechat",
                "avatarMode": "mixed",
                "deviceFrame": "iphone-dynamic-island",
                "nicknameMode": "first-message-only",
                "deliveryFormat": "hyperframe",
                "showTimestamp": True,
                "avatarAssignments": {
                    "leftPreset": "female-bunny-pink",
                    "rightPreset": "male-penguin-blue",
                    "leftUploadPath": sample_upload_left,
                    "rightUploadPath": None,
                },
            },
            "render": True,
            "expect_fail": False,
        },
        {
            "name": "json_spec_only",
            "config": {
                "container": "wechat",
                "avatarMode": "preset",
                "deviceFrame": "iphone-dynamic-island",
                "nicknameMode": "hidden",
                "deliveryFormat": "json",
                "showTimestamp": True,
                "avatarAssignments": {
                    "leftPreset": "female-bunny-pink",
                    "rightPreset": "female-cat-orange",
                    "leftUploadPath": None,
                    "rightUploadPath": None,
                },
            },
            "render": False,
            "expect_fail": False,
        },
        {
            "name": "invalid_upload_missing_side",
            "config": {
                "container": "wechat",
                "avatarMode": "upload",
                "deviceFrame": "iphone-dynamic-island",
                "nicknameMode": "always",
                "deliveryFormat": "mov",
                "showTimestamp": True,
                "avatarAssignments": {
                    "leftPreset": "female-bunny-pink",
                    "rightPreset": "female-cat-orange",
                    "leftUploadPath": sample_upload_left,
                    "rightUploadPath": None,
                },
            },
            "render": False,
            "expect_fail": True,
            "expected_error": "avatarMode=upload requires both leftUploadPath and rightUploadPath",
        },
        {
            "name": "invalid_mixed_without_upload",
            "config": {
                "container": "wechat",
                "avatarMode": "mixed",
                "deviceFrame": "iphone-dynamic-island",
                "nicknameMode": "always",
                "deliveryFormat": "mov",
                "showTimestamp": True,
                "avatarAssignments": {
                    "leftPreset": "female-bunny-pink",
                    "rightPreset": "female-cat-orange",
                    "leftUploadPath": None,
                    "rightUploadPath": None,
                },
            },
            "render": False,
            "expect_fail": True,
            "expected_error": "avatarMode=mixed requires at least one upload path",
        },
        {
            "name": "invalid_upload_missing_file",
            "config": {
                "container": "wechat",
                "avatarMode": "upload",
                "deviceFrame": "iphone-dynamic-island",
                "nicknameMode": "always",
                "deliveryFormat": "mov",
                "showTimestamp": True,
                "avatarAssignments": {
                    "leftPreset": "female-bunny-pink",
                    "rightPreset": "female-cat-orange",
                    "leftUploadPath": sample_upload_left,
                    "rightUploadPath": missing_upload_right,
                },
            },
            "render": False,
            "expect_fail": True,
            "fail_phase": "prepare_bundle",
            "expected_error": "Configured rightUploadPath does not exist",
        },
    ]

    results = []
    tsc_bin = node_modules / ".bin" / "tsc"
    remotion_bin = node_modules / ".bin" / "remotion"

    for case in cases:
        case_dir = work_dir / case["name"]
        case_dir.mkdir(parents=True, exist_ok=True)
        config_path = case_dir / "config.json"
        spec_path = case_dir / "spec.json"
        bundle_dir = case_dir / "bundle"
        write_json(config_path, case["config"])

        build_proc = run(
            [sys.executable, str(build_script), "--input", str(transcript), "--config", str(config_path), "--output", str(spec_path)],
            cwd=skill_root,
        )

        if case["expect_fail"]:
            fail_phase = case.get("fail_phase", "validation")
            if fail_phase == "validation":
                combined = (build_proc.stdout or "") + (build_proc.stderr or "")
                ok = build_proc.returncode != 0 and case["expected_error"] in combined
                results.append({"case": case["name"], "status": "passed" if ok else "failed", "phase": "validation", "details": combined.strip()})
                continue

            if build_proc.returncode != 0:
                results.append({"case": case["name"], "status": "failed", "phase": "build_spec", "details": build_proc.stderr.strip() or build_proc.stdout.strip()})
                continue

            bundle_proc = run(
                [
                    sys.executable,
                    str(bundle_script),
                    "--transcript",
                    str(transcript),
                    "--config",
                    str(config_path),
                    "--output-dir",
                    str(bundle_dir),
                    "--force",
                ],
                cwd=skill_root,
            )
            combined = (bundle_proc.stdout or "") + (bundle_proc.stderr or "")
            ok = bundle_proc.returncode != 0 and case["expected_error"] in combined
            results.append({"case": case["name"], "status": "passed" if ok else "failed", "phase": "prepare_bundle", "details": combined.strip()})
            continue

        if build_proc.returncode != 0:
            results.append({"case": case["name"], "status": "failed", "phase": "build_spec", "details": build_proc.stderr.strip()})
            continue

        bundle_proc = run(
            [
                sys.executable,
                str(bundle_script),
                "--transcript",
                str(transcript),
                "--config",
                str(config_path),
                "--output-dir",
                str(bundle_dir),
                "--force",
            ],
            cwd=skill_root,
        )
        if bundle_proc.returncode != 0:
            results.append({"case": case["name"], "status": "failed", "phase": "prepare_bundle", "details": bundle_proc.stderr.strip()})
            continue

        generated_spec = (bundle_dir / "src" / "chatSpec.ts").read_text(encoding="utf-8")
        if "UploadPath" in generated_spec or "/Users/" in generated_spec:
            results.append(
                {
                    "case": case["name"],
                    "status": "failed",
                    "phase": "bundle_sanitization",
                    "details": "Generated chatSpec.ts leaked local upload-path data.",
                }
            )
            continue

        symlink_path = bundle_dir / "node_modules"
        if symlink_path.exists() or symlink_path.is_symlink():
            symlink_path.unlink()
        symlink_path.symlink_to(node_modules)

        tsc_proc = run([str(tsc_bin), "--noEmit", "-p", str(bundle_dir / "tsconfig.json")], cwd=bundle_dir)
        if tsc_proc.returncode != 0:
            results.append({"case": case["name"], "status": "failed", "phase": "tsc", "details": tsc_proc.stderr.strip() or tsc_proc.stdout.strip()})
            continue

        if args.render and case["render"]:
            preview_path = case_dir / "preview.png"
            render_proc = run(
                [str(remotion_bin), "still", "src/index.ts", "ChatMotionOverlay", str(preview_path), "--scale=0.15", "--frame=120"],
                cwd=bundle_dir,
            )
            if render_proc.returncode != 0:
                results.append({"case": case["name"], "status": "failed", "phase": "render", "details": render_proc.stderr.strip() or render_proc.stdout.strip()})
                continue

        results.append({"case": case["name"], "status": "passed", "phase": "complete", "details": ""})

    summary = {
        "passed": sum(1 for item in results if item["status"] == "passed"),
        "failed": sum(1 for item in results if item["status"] == "failed"),
        "results": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
