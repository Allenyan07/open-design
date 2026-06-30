#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SIDE_MAP = {"left": "left", "right": "right", "左": "left", "右": "right"}
PRESET_KEYS = [
    "female-bunny-pink",
    "female-cat-orange",
    "female-fox-yellow",
    "male-bear-mint",
    "male-penguin-blue",
    "male-koala-lilac",
]

ALLOWED_CONTAINERS = {"none", "wechat", "telegram", "messenger"}
ALLOWED_AVATAR_MODES = {"preset", "upload", "mixed"}
ALLOWED_DEVICE_FRAMES = {"none", "iphone-dynamic-island"}
ALLOWED_NICKNAME_MODES = {"hidden", "first-message-only", "always"}
ALLOWED_DELIVERY_FORMATS = {"mov", "webm", "json", "remotion", "hyperframe", "preview"}
DELIVERY_TO_OUTPUT = {
    "mov": "mov-alpha",
    "webm": "webm-alpha",
    "json": "json-spec",
    "remotion": "remotion-component",
    "hyperframe": "hyperframe-ready",
    "preview": "preview-only",
}

DEFAULT_CONFIG = {
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
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a configurable chat motion overlay scene spec.")
    parser.add_argument("--input", required=True, help="Path to transcript text file")
    parser.add_argument("--config", help="Path to scene config JSON")
    parser.add_argument("--output", help="Path to output JSON file")
    return parser.parse_args()


def parse_transcript(path: Path) -> dict:
    metadata = {"title": "聊天记录", "time": "今天", "start": 15, "gap": 18, "hold": 36}
    raw_messages: list[dict] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        meta_match = re.match(r"^(title|time|start|gap|hold)\s*[:：]\s*(.+)$", line, flags=re.IGNORECASE)
        if meta_match:
            key = meta_match.group(1).strip().lower()
            value = meta_match.group(2).strip()
            metadata[key] = int(value) if key in {"start", "gap", "hold"} else value
            continue
        raw_messages.append(parse_message_line(line))
    return {"metadata": metadata, "messages": raw_messages}


def parse_message_line(line: str) -> dict:
    parts = [part.strip() for part in line.split("|")] if "|" in line else []
    if not parts:
        match = re.match(r"^([^:：]{1,30})[:：]\s*(.+)$", line)
        if not match:
            raise ValueError(f"Cannot parse line: {line}")
        parts = [match.group(1).strip(), match.group(2).strip()]
    result = {"speaker": parts[0], "side": None, "avatar": None, "text": "", "highlight": False}
    if len(parts) == 2:
        result["text"] = parts[1]
        return result
    if len(parts) == 3:
        if is_flag(parts[2]):
            result["text"] = parts[1]
            result["highlight"] = True
            return result
        if is_side(parts[1]):
            result["side"] = SIDE_MAP[parts[1]]
            result["text"] = parts[2]
            return result
        result["text"] = parts[1]
        result["avatar"] = parts[2]
        return result
    if len(parts) >= 4 and is_side(parts[1]):
        result["side"] = SIDE_MAP[parts[1]]
        result["avatar"] = parts[2]
        result["text"] = parts[3]
        result["highlight"] = len(parts) > 4 and is_flag(parts[4])
        return result
    raise ValueError(f"Unsupported message line shape: {line}")


def is_side(value: str) -> bool:
    return value in SIDE_MAP


def is_flag(value: str) -> bool:
    return value.strip().lower() == "highlight"


def load_config(path: str | None) -> dict:
    config = json.loads(json.dumps(DEFAULT_CONFIG))
    if not path:
        validate_config(config)
        return config
    user = json.loads(Path(path).read_text(encoding="utf-8"))
    config.update({k: v for k, v in user.items() if k != "avatarAssignments"})
    if "avatarAssignments" in user:
        config["avatarAssignments"].update(user["avatarAssignments"])
    validate_config(config)
    return config


def validate_config(config: dict) -> None:
    if config["container"] not in ALLOWED_CONTAINERS:
        raise ValueError(f"Unsupported container: {config['container']}")
    if config["avatarMode"] not in ALLOWED_AVATAR_MODES:
        raise ValueError(f"Unsupported avatarMode: {config['avatarMode']}")
    if config["deviceFrame"] not in ALLOWED_DEVICE_FRAMES:
        raise ValueError(f"Unsupported deviceFrame: {config['deviceFrame']}")
    if config["nicknameMode"] not in ALLOWED_NICKNAME_MODES:
        raise ValueError(f"Unsupported nicknameMode: {config['nicknameMode']}")
    if config["deliveryFormat"] not in ALLOWED_DELIVERY_FORMATS:
        raise ValueError(f"Unsupported deliveryFormat: {config['deliveryFormat']}")

    assignments = config["avatarAssignments"]
    for side in ("left", "right"):
        preset_key = assignments.get(f"{side}Preset")
        if preset_key and preset_key not in PRESET_KEYS:
            raise ValueError(f"Unsupported {side}Preset: {preset_key}")

    if config["avatarMode"] == "upload":
        if not assignments.get("leftUploadPath") or not assignments.get("rightUploadPath"):
            raise ValueError("avatarMode=upload requires both leftUploadPath and rightUploadPath")
    if config["avatarMode"] == "mixed":
        if not assignments.get("leftUploadPath") and not assignments.get("rightUploadPath"):
            raise ValueError("avatarMode=mixed requires at least one upload path")


def auto_avatar_for_side(side: str, config: dict) -> str:
    return config["avatarAssignments"]["leftPreset"] if side == "left" else config["avatarAssignments"]["rightPreset"]


def build_spec(parsed: dict, config: dict) -> dict:
    meta = parsed["metadata"]
    participants = {}
    order = []
    messages = []
    start = int(meta["start"])
    gap = int(meta["gap"])
    for index, message in enumerate(parsed["messages"]):
        speaker = message["speaker"]
        if speaker not in participants:
            order.append(speaker)
            inferred_side = "left" if len(order) == 1 else "right" if len(order) == 2 else "left"
            side = message["side"] or inferred_side
            participants[speaker] = {
                "id": slugify(speaker),
                "name": speaker,
                "side": side,
                "avatarKey": message["avatar"] or auto_avatar_for_side(side, config),
            }
        participant = participants[speaker]
        side = message["side"] or participant["side"]
        avatar_key = message["avatar"] or participant["avatarKey"]
        messages.append(
            {
                "id": f"msg-{index + 1}",
                "speaker": speaker,
                "text": message["text"].strip(),
                "side": side,
                "avatarKey": avatar_key,
                "appearAt": start + index * gap,
                "highlight": bool(message["highlight"]),
            }
        )
    duration = start + max(len(messages) - 1, 0) * gap + int(meta["hold"])
    runtime_output = DELIVERY_TO_OUTPUT[config["deliveryFormat"]]
    return {
        "title": meta["title"],
        "timestamp": meta["time"],
        "durationInFrames": duration,
        "timing": {"start": start, "gap": gap, "hold": int(meta["hold"])},
        "sceneConfig": {**config, "output": runtime_output},
        "participants": list(participants.values()),
        "messages": messages,
    }


def slugify(text: str) -> str:
    lowered = text.strip().lower()
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "-", lowered).strip("-") or "speaker"


def main() -> None:
    args = parse_args()
    parsed = parse_transcript(Path(args.input))
    config = load_config(args.config)
    spec = build_spec(parsed, config)
    output = json.dumps(spec, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
