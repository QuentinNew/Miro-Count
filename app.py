import json
import re

import streamlit as st
from streamlit_local_storage import LocalStorage

from miro import build_legend, count_by_color, frame_title_map, get_frames, get_stickies, match_frames

st.set_page_config(page_title="Miro Sticky Counter", page_icon="🗒️", layout="centered")
st.title("Miro Sticky Counter v1.0")

_ls = LocalStorage()
_saved_token = _ls.getItem("miro_token") or ""
_saved_board = _ls.getItem("miro_board") or ""
_saved_legend = _ls.getItem("miro_legend_frame") or ""
_saved_frames = _ls.getItem("miro_frames") or ""
_saved_details = _ls.getItem("miro_details") or ""

# Fall back to settings.json only when nothing is saved in browser yet
if not any([_saved_legend, _saved_frames, _saved_details]):
    try:
        with open("settings.json") as f:
            _file = json.load(f)
        _saved_legend = _file.get("legend_frame", "")
        _saved_frames = "\n".join(_file.get("frames", []))
        _detail_groups_default = _file.get("frames_details", [])
        _saved_details = "\n\n".join(
            "\n".join(g) if isinstance(g, list) else g
            for g in _detail_groups_default
        )
    except FileNotFoundError:
        pass

with st.sidebar:
    st.header("Connection")
    token = st.text_input("Miro API token", value=_saved_token, type="password", help="Personal access token from miro.com/app/settings/user-profile/apps")
    board_id = st.text_input("Board ID", value=_saved_board, help="The ID in the board URL: miro.com/app/board/<board_id>/")

    st.divider()
    st.header("Settings")

    legend_frame = st.text_input(
        "Legend frame name",
        value=_saved_legend,
        help="Exact name (or regex) of the frame that contains your color legend",
    )
    frames_raw = st.text_area(
        "Target frames (one per line)",
        value=_saved_frames,
        help="Frame names or regex patterns to count stickies in",
    )
    details_raw = st.text_area(
        "Detail groups (blank line separates groups)",
        value=_saved_details,
        help="Each group of patterns (separated by a blank line) is combined into one breakdown",
    )

    if token != _saved_token:
        _ls.setItem("miro_token", token)
    if board_id != _saved_board:
        _ls.setItem("miro_board", board_id)
    if legend_frame != _saved_legend:
        _ls.setItem("miro_legend_frame", legend_frame)
    if frames_raw != _saved_frames:
        _ls.setItem("miro_frames", frames_raw)
    if details_raw != _saved_details:
        _ls.setItem("miro_details", details_raw)

    run = st.button("Count stickies", type="primary", disabled=not (token and board_id and legend_frame and frames_raw))



if not run:
    st.markdown("""
### How it works

1. **Paste your Miro API token** in the sidebar — get it from [miro.com → Settings → Your apps](https://miro.com/app/settings/user-profile/apps)
2. **Paste your Board ID** — it's the last segment of your board URL:
   `miro.com/app/board/`**`uXjVLYxwyqI=`**`/`
3. **Set up your legend frame** — a frame on your board where each sticky note maps a color to a label.
   The note text must start with the label, optionally followed by `:` and a description:

   | Sticky color | Sticky text | → Label |
   |---|---|---|
   | 🟡 yellow | `Bug : something broken` | **Bug** |
   | 🟢 light_green | `Feature` | **Feature** |
   | 🔵 light_blue | `Tech debt : cleanup` | **Tech debt** |

4. **List target frames** — one per line, supports regex:
   ```
   Doing
   Done
   HOTFIX Done .*
   ```
5. **List detail groups** *(optional)* — frames to break down after the summary.
   Separate groups with a blank line; patterns within a group are combined:
   ```
   Done
   HOTFIX Done .*

   Doing
   ```
   → Group 1: `Done` + all `HOTFIX Done *` frames combined
   → Group 2: `Doing` alone

6. Click **Count stickies** — results appear with a TSV copy button for pasting into Google Sheets.
""")

if run:
    target_patterns = [p.strip() for p in frames_raw.splitlines() if p.strip()]
    detail_groups: list[list[str]] = []
    for block in re.split(r"\n\s*\n", details_raw.strip()):
        patterns = [p.strip() for p in block.splitlines() if p.strip()]
        if patterns:
            detail_groups.append(patterns)

    try:
        with st.spinner("Fetching frames…"):
            all_frames = get_frames(board_id, token)
    except Exception as e:
        st.error(f"Could not reach Miro API: {e}")
        st.stop()

    titles = frame_title_map(all_frames)

    legend = {}
    legend_hits = match_frames(legend_frame, titles)
    if legend_hits:
        legend_id = next(iter(legend_hits.values()))
        with st.spinner(f"Reading legend from '{next(iter(legend_hits))}'…"):
            legend = build_legend(get_stickies(board_id, legend_id, token))
    else:
        st.warning(f"Legend frame '{legend_frame}' not found — showing raw colors.")

    matched = {}
    missing = []
    for pat in target_patterns:
        hits = match_frames(pat, titles)
        if not hits:
            missing.append(pat)
        matched.update(hits)

    if missing:
        st.error(f"No frames matched: {', '.join(missing)}")
        st.stop()

    resolved_groups = []
    for group_patterns in detail_groups:
        group_names = set()
        for pat in group_patterns:
            group_names.update(match_frames(pat, titles).keys())
        if group_names:
            label = " + ".join(sorted(group_names))
            resolved_groups.append((label, group_names))

    detail_names = {name for _, names in resolved_groups for name in names}

    all_stickies = []
    per_frame_stickies = {}
    for name, fid in matched.items():
        with st.spinner(f"Reading '{name}'…"):
            stickies = get_stickies(board_id, fid, token)
        all_stickies.extend(stickies)
        if name in detail_names:
            per_frame_stickies[name] = stickies

    counts = count_by_color(all_stickies)
    total = sum(counts.values())

    st.subheader("All")
    rows = [{"Type": legend.get(c, c), "Count": n} for c, n in counts.items()]
    rows.append({"Type": "TOTAL", "Count": total})
    st.table(rows)

    if resolved_groups:
        st.subheader("By group")
        for label, group_names in resolved_groups:
            group_stickies = [s for name in group_names for s in per_frame_stickies.get(name, [])]
            group_counts = count_by_color(group_stickies)
            group_total = sum(group_counts.values())
            with st.expander(f"{label} ({group_total} stickies)"):
                group_rows = [{"Type": legend.get(c, c), "Count": n} for c, n in group_counts.items()]
                group_rows.append({"Type": "TOTAL", "Count": group_total})
                st.table(group_rows)
