import argparse
import json
import os
import sys

from dotenv import load_dotenv

from miro import build_legend, count_by_color, frame_title_map, get_frames, get_stickies, match_frames

load_dotenv()


def render_plain(counts, total, legend, per_frame=None):
    lines = ["Color counts:"]
    for color, count in counts.items():
        lines.append(f"  {legend.get(color, color):<25} {count}")
    lines.append(f"  {'TOTAL':<25} {total}")
    if per_frame:
        for frame_name, frame_counts in per_frame:
            frame_total = sum(frame_counts.values())
            lines.append(f"\n  {frame_name}")
            for color, count in frame_counts.items():
                lines.append(f"    {legend.get(color, color):<23} {count}")
            lines.append(f"    {'TOTAL':<23} {frame_total}")
    return "\n".join(lines)


def render_markdown(counts, total, legend, per_frame=None):
    lines = ["| Type | Count |", "|------|-------|"]
    for color, count in counts.items():
        lines.append(f"| {legend.get(color, color)} | {count} |")
    lines.append(f"| **TOTAL** | **{total}** |")
    if per_frame:
        for frame_name, frame_counts in per_frame:
            frame_total = sum(frame_counts.values())
            lines.append(f"\n**{frame_name}**\n")
            lines.append("| Type | Count |")
            lines.append("|------|-------|")
            for color, count in frame_counts.items():
                lines.append(f"| {legend.get(color, color)} | {count} |")
            lines.append(f"| **TOTAL** | **{frame_total}** |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Count Miro sticky notes by color.")
    parser.add_argument("--board", required=True, help="Miro board ID")
    args = parser.parse_args()

    token = os.environ.get("MIRO_TOKEN")
    if not token:
        sys.exit("Error: MIRO_TOKEN not set in environment or .env file.")

    with open("settings.json") as f:
        settings = json.load(f)

    legend_frame_name = settings.get("legend_frame", "")
    if not legend_frame_name:
        sys.exit("Error: 'legend_frame' not configured in settings.json.")

    target_frame_names = settings.get("frames", [])
    if not target_frame_names:
        sys.exit("Error: no frames configured in settings.json.")

    detail_frame_patterns = settings.get("frames_details", [])

    print(f"Fetching frames for board {args.board}...")
    all_frames = get_frames(args.board, token)
    titles = frame_title_map(all_frames)

    legend = {}
    legend_hits = match_frames(legend_frame_name, titles)
    if not legend_hits:
        print(f"Warning: legend frame '{legend_frame_name}' not found, showing raw colors.")
    else:
        legend_frame_id = next(iter(legend_hits.values()))
        print(f"  Fetching legend from frame '{next(iter(legend_hits))}'...")
        legend = build_legend(get_stickies(args.board, legend_frame_id, token))

    matched = {}
    unmatched = []
    for pattern in target_frame_names:
        hits = match_frames(pattern, titles)
        if not hits:
            unmatched.append(pattern)
        matched.update(hits)

    if unmatched:
        sys.exit(f"Error: no frames matched pattern(s): {', '.join(unmatched)}")

    resolved_groups = []
    for group in detail_frame_patterns:
        patterns = group if isinstance(group, list) else [group]
        group_names = set()
        for pattern in patterns:
            group_names.update(match_frames(pattern, titles).keys())
        if group_names:
            label = " + ".join(sorted(group_names))
            resolved_groups.append((label, group_names))

    detail_names = {name for _, names in resolved_groups for name in names}

    all_stickies = []
    per_frame_stickies = {}
    for name, frame_id in matched.items():
        print(f"  Fetching sticky notes in frame '{name}'...")
        stickies = get_stickies(args.board, frame_id, token)
        all_stickies.extend(stickies)
        if name in detail_names:
            per_frame_stickies[name] = stickies

    counts = count_by_color(all_stickies)
    total = sum(counts.values())
    per_frame = [
        (label, count_by_color([s for name in names for s in per_frame_stickies.get(name, [])]))
        for label, names in resolved_groups
    ]

    print()
    print(render_plain(counts, total, legend, per_frame or None))


if __name__ == "__main__":
    main()
