import re
from collections import defaultdict

import requests

MIRO_API = "https://api.miro.com/v2"


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


def get_frames(board_id: str, token: str) -> list[dict]:
    frames, cursor = [], None
    while True:
        params = {"type": "frame", "limit": 50}
        if cursor:
            params["cursor"] = cursor
        resp = requests.get(f"{MIRO_API}/boards/{board_id}/items", headers=_headers(token), params=params)
        resp.raise_for_status()
        data = resp.json()
        frames.extend(data.get("data", []))
        cursor = data.get("cursor")
        if not cursor:
            break
    return frames


def get_stickies(board_id: str, frame_id: str, token: str) -> list[dict]:
    stickies, cursor = [], None
    while True:
        params = {"type": "sticky_note", "limit": 50, "parent_item_id": frame_id}
        if cursor:
            params["cursor"] = cursor
        resp = requests.get(f"{MIRO_API}/boards/{board_id}/items", headers=_headers(token), params=params)
        resp.raise_for_status()
        data = resp.json()
        stickies.extend(data.get("data", []))
        cursor = data.get("cursor")
        if not cursor:
            break
    return stickies


def build_legend(stickies: list[dict]) -> dict[str, str]:
    legend = {}
    for s in stickies:
        color = s.get("style", {}).get("fillColor", "")
        text = re.sub(r"<[^>]+>", "", s.get("data", {}).get("content", "")).strip()
        label = text.split(":", 1)[0].strip() if ":" in text else text
        if color and label:
            legend[color] = label
    return legend


def count_by_color(stickies: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for s in stickies:
        color = s.get("style", {}).get("fillColor", "unknown")
        counts[color] += 1
    return dict(sorted(counts.items()))


def frame_title_map(frames: list[dict]) -> dict[str, str]:
    return {
        f["data"]["title"]: f["id"]
        for f in frames
        if f.get("data", {}).get("title")
    }


def match_frames(pattern: str, title_map: dict[str, str]) -> dict[str, str]:
    return {t: i for t, i in title_map.items() if re.fullmatch(pattern, t)}
