import json
import re

import streamlit as st
from streamlit_local_storage import LocalStorage

from miro import build_legend, count_by_color, frame_title_map, get_frames, get_stickies, match_frames
from translations import TRANSLATIONS

st.set_page_config(page_title="Miro Sticky Counter", page_icon="🗒️", layout="centered")

_ls = LocalStorage()
_saved_board = _ls.getItem("miro_board") or ""
_saved_legend = _ls.getItem("miro_legend_frame") or ""
_saved_frames = _ls.getItem("miro_frames") or ""
_saved_details = _ls.getItem("miro_details") or ""
_saved_ignored = _ls.getItem("miro_ignored") or ""
_saved_lang = _ls.getItem("miro_lang") or "en"

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
        _saved_ignored = "\n".join(_file.get("ignored", []))
    except FileNotFoundError:
        pass

_lang_opts = ["en", "fr"]
lang = st.selectbox("🌐 Language", _lang_opts, index=_lang_opts.index(_saved_lang))
if lang != _saved_lang:
    _ls.setItem("miro_lang", lang)
t = TRANSLATIONS[lang]

st.title(t["app_title"])

with st.sidebar:
    st.header(t["sidebar_connection"])
    token = st.text_input(t["token_label"], value="", type="password", help=t["token_help"])
    board_id = st.text_input(t["board_id_label"], value=_saved_board, help=t["board_id_help"])

    st.divider()
    st.header(t["sidebar_settings"])

    legend_frame = st.text_input(t["legend_frame_label"], value=_saved_legend, help=t["legend_frame_help"])
    frames_raw = st.text_area(t["target_frames_label"], value=_saved_frames, help=t["target_frames_help"])
    details_raw = st.text_area(t["detail_groups_label"], value=_saved_details, help=t["detail_groups_help"])
    ignored_raw = st.text_area(t["ignored_label"], value=_saved_ignored, help=t["ignored_help"])

    if board_id != _saved_board:
        _ls.setItem("miro_board", board_id)
    if legend_frame != _saved_legend:
        _ls.setItem("miro_legend_frame", legend_frame)
    if frames_raw != _saved_frames:
        _ls.setItem("miro_frames", frames_raw)
    if details_raw != _saved_details:
        _ls.setItem("miro_details", details_raw)
    if ignored_raw != _saved_ignored:
        _ls.setItem("miro_ignored", ignored_raw)

    run = st.button(t["run_button"], type="primary", disabled=not (token and board_id and legend_frame and frames_raw))

if not run:
    st.markdown(t["how_it_works"])

if run:
    target_patterns = [p.strip() for p in frames_raw.splitlines() if p.strip()]
    detail_groups: list[list[str]] = []
    for block in re.split(r"\n\s*\n", details_raw.strip()):
        patterns = [p.strip() for p in block.splitlines() if p.strip()]
        if patterns:
            detail_groups.append(patterns)

    try:
        with st.spinner(t["spinner_frames"]):
            all_frames = get_frames(board_id, token)
    except Exception as e:
        st.error(t["error_api"].format(e=e))
        st.stop()

    titles = frame_title_map(all_frames)

    legend = {}
    legend_hits = match_frames(legend_frame, titles)
    if legend_hits:
        legend_id = next(iter(legend_hits.values()))
        legend_name = next(iter(legend_hits))
        with st.spinner(t["spinner_legend"].format(name=legend_name)):
            legend = build_legend(get_stickies(board_id, legend_id, token))
    else:
        st.warning(t["warning_legend"].format(name=legend_frame))

    matched = {}
    missing = []
    for pat in target_patterns:
        hits = match_frames(pat, titles)
        if not hits:
            missing.append(pat)
        matched.update(hits)

    if missing:
        st.error(t["error_no_match"].format(names=", ".join(missing)))
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
        with st.spinner(t["spinner_frame"].format(name=name)):
            stickies = get_stickies(board_id, fid, token)
        all_stickies.extend(stickies)
        if name in detail_names:
            per_frame_stickies[name] = stickies

    ignored_labels = {t_str.strip().lower() for t_str in ignored_raw.splitlines() if t_str.strip()}

    def _filter(counts: dict[str, int]) -> dict[str, int]:
        return {c: n for c, n in counts.items() if legend.get(c, c).lower() not in ignored_labels}

    counts = _filter(count_by_color(all_stickies))
    total = sum(counts.values())

    st.subheader(t["section_all"])
    rows = [{t["col_type"]: legend.get(c, c), t["col_count"]: n} for c, n in counts.items()]
    rows.append({t["col_type"]: t["total_label"], t["col_count"]: total})
    st.table(rows)

    if resolved_groups:
        st.subheader(t["section_by_group"])
        for label, group_names in resolved_groups:
            group_stickies = [s for name in group_names for s in per_frame_stickies.get(name, [])]
            group_counts = _filter(count_by_color(group_stickies))
            group_total = sum(group_counts.values())
            with st.expander(f"{label} ({group_total} {t['stickies_suffix']})"):
                group_rows = [{t["col_type"]: legend.get(c, c), t["col_count"]: n} for c, n in group_counts.items()]
                group_rows.append({t["col_type"]: t["total_label"], t["col_count"]: group_total})
                st.table(group_rows)
