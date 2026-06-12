# Miro Sticky Counter v1.2

Count sticky notes by color across frames on a Miro board, with optional per-frame breakdowns.

## How it works

1. Reads a **legend frame** on your board to map sticky colors → labels
2. Fetches sticky notes from the **target frames** you configure
3. Outputs counts per color/label, plus optional per-frame detail

## Usage

### Web app (no coding required)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`. Fill in your Miro token, board ID, and frame settings, then click **Count stickies**.

To avoid re-entering credentials on every reload, add a `.env` file:

```
MIRO_TOKEN=your_token_here
MIRO_BOARD=your_board_id_here   # optional
```

When deployed to **Streamlit Community Cloud**, set these same keys in the app's **Secrets** panel (Settings → Secrets) instead of a `.env` file.

### CLI

```bash
pip install -r requirements.txt
MIRO_TOKEN=your_token python count_stickies.py --board <board_id>
```

Or put your token in a `.env` file:

```
MIRO_TOKEN=your_token_here
```

Then run:

```bash
python count_stickies.py --board <board_id>
```

## Configuration (`settings.json`)

Both the web app and CLI read `settings.json` for default frame settings.

```json
{
  "legend_frame": "Légende",
  "frames": ["Doing", "Merge", "Done", "HOTFIX Done .*"],
  "frames_details": ["Doing", "HOTFIX Done .*"]
}
```

| Field | Description |
|---|---|
| `legend_frame` | Name (or regex) of the frame holding your color legend |
| `frames` | Frame names or regex patterns to count stickies across |
| `frames_details` | Subset of frames to also show individually |

Frame names support Python regex (e.g. `HOTFIX Done .*` matches any frame starting with that prefix).

### Filtering a detail group by Miro tag

A detail group entry starting with `#` filters that group to stickies carrying the named Miro tag. Multiple `#tag` entries combine with **OR**, and tag matching is case-insensitive.

In the web app's **Detail frame groups** field:

```
Doing
HOTFIX Done .*
#Bug
#Urgent
```

The CLI reads the same from `frames_details` in `settings.json`, where a group is a list:

```json
{
  "frames_details": [
    ["Doing", "HOTFIX Done .*", "#Bug", "#Urgent"]
  ]
}
```

Both count only stickies tagged `Bug` or `Urgent` within those frames. A group containing only `#tag` entries (no frame) filters across all target frames. Unknown tags are warned about and ignored. The top "All" summary is never filtered.

## Getting your Miro token

1. Go to [miro.com/app/settings/user-profile/apps](https://miro.com/app/settings/user-profile/apps)
2. Create a Developer App or generate a Personal Access Token
3. Make sure the token has **board:read** scope

## Getting your board ID

The board ID is in the URL when you open your board:

```
https://miro.com/app/board/<board_id>/
```

## Language support

The web app supports **English** and **French**. A language selector appears at the top of the page and your choice is remembered in the browser.

All UI strings live in `translations.py` — edit that file to update wording or add a new language.

## Project structure

```
├── miro.py             # Shared API logic (used by both interfaces)
├── app.py              # Streamlit web app
├── translations.py     # EN/FR UI strings
├── count_stickies.py   # Command-line interface
├── settings.json       # Default frame configuration
└── requirements.txt
```
