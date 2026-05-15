# Miro Sticky Counter v1.0

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

## Getting your Miro token

1. Go to [miro.com/app/settings/user-profile/apps](https://miro.com/app/settings/user-profile/apps)
2. Create a Developer App or generate a Personal Access Token
3. Make sure the token has **board:read** scope

## Getting your board ID

The board ID is in the URL when you open your board:

```
https://miro.com/app/board/<board_id>/
```

## Project structure

```
├── miro.py             # Shared API logic (used by both interfaces)
├── app.py              # Streamlit web app
├── count_stickies.py   # Command-line interface
├── settings.json       # Default frame configuration
└── requirements.txt
```
