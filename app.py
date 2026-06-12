import json
import re

import streamlit as st
from streamlit_local_storage import LocalStorage

from miro import (
    build_legend,
    count_by_color,
    frame_title_map,
    get_frames,
    get_item_ids_by_tag,
    get_stickies,
    get_tags,
    match_frames,
    sticky_text,
)
from translations import TRANSLATIONS

st.set_page_config(page_title="Miro Sticky Counter", page_icon="🗒️", layout="centered")

_ls = LocalStorage()
_saved_board = _ls.getItem("miro_board") or ""
_saved_legend = _ls.getItem("miro_legend_frame") or ""
_saved_frames = _ls.getItem("miro_frames") or ""
_saved_details = _ls.getItem("miro_details") or ""
_saved_ignored = _ls.getItem("miro_ignored") or ""
_saved_drop_empty = _ls.getItem("miro_drop_empty") == "1"
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
    # A form lets Enter (text inputs) / Ctrl+Enter (text areas) submit, i.e.
    # trigger the count from the keyboard. Inside a form, widget values only
    # update on submit, so persistence and validation happen after submit.
    with st.form("settings_form"):
        with st.expander(t["sidebar_connection"], expanded=True):
            token = st.text_input(t["token_label"], value="", type="password", help=t["token_help"])
            board_id = st.text_input(t["board_id_label"], value=_saved_board, help=t["board_id_help"])

        with st.expander(t["section_frames"], expanded=not (_saved_legend and _saved_frames)):
            legend_frame = st.text_input(t["legend_frame_label"], value=_saved_legend, help=t["legend_frame_help"])
            frames_raw = st.text_area(t["target_frames_label"], value=_saved_frames, help=t["target_frames_help"])
            details_raw = st.text_area(t["detail_groups_label"], value=_saved_details, help=t["detail_groups_help"])

        with st.expander(t["section_filters"], expanded=False):
            ignored_raw = st.text_area(t["ignored_label"], value=_saved_ignored, help=t["ignored_help"])
            drop_empty = st.checkbox(t["drop_empty_label"], value=_saved_drop_empty, help=t["drop_empty_help"])

        run = st.form_submit_button(t["run_button"], type="primary")

    if ("1" if drop_empty else "0") != _ls.getItem("miro_drop_empty"):
        _ls.setItem("miro_drop_empty", "1" if drop_empty else "0")
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

if run and not (token and board_id and legend_frame and frames_raw):
    st.error(t["error_missing_fields"])
    run = False

if not run:
    st.markdown(t["how_it_works"])

if run:
    target_patterns = [p.strip() for p in frames_raw.splitlines() if p.strip()]
    # Each detail block splits into frame patterns and #tag filters
    detail_groups: list[dict] = []
    for block in re.split(r"\n\s*\n", details_raw.strip()):
        frame_patterns, tag_names = [], []
        for line in block.splitlines():
            s = line.strip()
            if not s:
                continue
            if s.startswith("#"):
                tag = s[1:].strip()
                if tag:
                    tag_names.append(tag)
            else:
                frame_patterns.append(s)
        if frame_patterns or tag_names:
            detail_groups.append({"frames": frame_patterns, "tags": tag_names})

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

    # (frame_names, tag_names, scope_all) — scope_all means a bare #tag block
    # that filters across all target frames rather than specific ones.
    resolved_groups = []
    for group in detail_groups:
        group_names = set()
        for pat in group["frames"]:
            group_names.update(match_frames(pat, titles).keys())
        scope_all = not group["frames"]
        if group_names or (scope_all and group["tags"]):
            resolved_groups.append((group_names, group["tags"], scope_all))

    detail_names = {name for names, _, _ in resolved_groups for name in names}

    all_stickies = []
    per_frame_stickies = {}
    for name, fid in matched.items():
        with st.spinner(t["spinner_frame"].format(name=name)):
            stickies = get_stickies(board_id, fid, token)
        if drop_empty:
            stickies = [s for s in stickies if sticky_text(s)]
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

    # Lazily fetch board tags only when a #tag filter is actually used.
    need_tags = any(tags for _, tags, _ in resolved_groups)
    board_tags = {}
    tagged_ids_cache: dict[str, set] = {}
    warned_tags: set[str] = set()
    if need_tags:
        with st.spinner(t["spinner_tags"]):
            board_tags = get_tags(board_id, token)

    def _ids_for_tag(name: str):
        tag_id = board_tags.get(name.lower())
        if not tag_id:
            if name not in warned_tags:
                st.warning(t["warning_tag"].format(name=name))
                warned_tags.add(name)
            return None
        if tag_id not in tagged_ids_cache:
            tagged_ids_cache[tag_id] = get_item_ids_by_tag(board_id, tag_id, token)
        return tagged_ids_cache[tag_id]

    if resolved_groups:
        st.subheader(t["section_by_group"])
        for group_names, tag_names, scope_all in resolved_groups:
            if scope_all:
                group_stickies = list(all_stickies)
            else:
                group_stickies = [s for name in group_names for s in per_frame_stickies.get(name, [])]

            if tag_names:
                keep_ids: set = set()
                for tn in tag_names:
                    ids = _ids_for_tag(tn)
                    if ids:
                        keep_ids |= ids
                group_stickies = [s for s in group_stickies if s.get("id") in keep_ids]

            label = " + ".join(sorted(group_names))
            if tag_names:
                tag_str = ", ".join(f"#{tn}" for tn in tag_names)
                label = f"{label} — {tag_str}" if label else tag_str

            group_counts = _filter(count_by_color(group_stickies))
            group_total = sum(group_counts.values())
            with st.expander(f"{label} ({group_total} {t['stickies_suffix']})"):
                group_rows = [{t["col_type"]: legend.get(c, c), t["col_count"]: n} for c, n in group_counts.items()]
                group_rows.append({t["col_type"]: t["total_label"], t["col_count"]: group_total})
                st.table(group_rows)
