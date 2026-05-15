TRANSLATIONS = {
    "en": {
        "page_title": "Miro Sticky Counter",
        "app_title": "Miro Sticky Counter v1.1",
        "sidebar_connection": "Connection",
        "token_label": "Miro API token",
        "token_help": "Personal access token from miro.com/app/settings/user-profile/apps",
        "board_id_label": "Board ID",
        "board_id_help": "The ID in the board URL: miro.com/app/board/<board_id>/",
        "sidebar_settings": "Settings",
        "legend_frame_label": "Legend frame name",
        "legend_frame_help": "Exact name (or regex) of the frame that contains your color legend",
        "target_frames_label": "Target frames (one per line)",
        "target_frames_help": "Frame names or regex patterns to count stickies in",
        "detail_groups_label": "Detail frame groups (blank line separates groups)",
        "detail_groups_help": "Each group of patterns (separated by a blank line) is combined into one breakdown",
        "ignored_label": "Ignored types (one per line)",
        "ignored_help": "Type labels to exclude from all counts (e.g. Bug). Case-insensitive.",
        "run_button": "Count stickies",
        "how_it_works": """### How it works

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

6. Click **Count stickies** — results appear on a table format.
""",
        "spinner_frames": "Fetching frames…",
        "spinner_legend": "Reading legend from '{name}'…",
        "spinner_frame": "Reading '{name}'…",
        "error_api": "Could not reach Miro API: {e}",
        "warning_legend": "Legend frame '{name}' not found — showing raw colors.",
        "error_no_match": "No frames matched: {names}",
        "section_all": "All",
        "section_by_group": "By group",
        "col_type": "Type",
        "col_count": "Count",
        "total_label": "TOTAL",
        "stickies_suffix": "stickies",
    },
    "fr": {
        "page_title": "Compteur de stickies Miro",
        "app_title": "Compteur de stickies Miro v1.1",
        "sidebar_connection": "Connexion",
        "token_label": "Token API Miro",
        "token_help": "Token d'accès personnel depuis miro.com/app/settings/user-profile/apps",
        "board_id_label": "ID du tableau",
        "board_id_help": "L'ID dans l'URL du tableau : miro.com/app/board/<board_id>/",
        "sidebar_settings": "Paramètres",
        "legend_frame_label": "Nom du cadre (frame) de légende",
        "legend_frame_help": "Nom exact (ou regex) du cadre contenant votre légende de couleurs",
        "target_frames_label": "Cadres cibles (un par ligne)",
        "target_frames_help": "Noms de cadres ou expressions régulières pour compter les stickies",
        "detail_groups_label": "Groupes de détail de cadres (ligne vide entre les groupes)",
        "detail_groups_help": "Chaque groupe de patterns (séparé par une ligne vide) est combiné en un seul rapport",
        "ignored_label": "Types ignorés (un par ligne)",
        "ignored_help": "Labels à exclure de tous les comptes (ex. Bug). Sans distinction majuscules/minuscules.",
        "run_button": "Compter les stickies",
        "how_it_works": """### Comment ça marche

1. **Collez votre token API Miro** dans la barre latérale — obtenez-le sur [miro.com → Paramètres → Vos apps](https://miro.com/app/settings/user-profile/apps)
2. **Collez l'ID de votre tableau** — c'est le dernier segment de l'URL du tableau :
   `miro.com/app/board/`**`uXjVLYxwyqI=`**`/`
3. **Configurez votre cadre de légende** — un cadre sur votre tableau où chaque sticky note associe une couleur à un label.
   Le texte du sticky doit commencer par le label, optionnellement suivi de `:` et d'une description :

   | Couleur du sticky | Texte du sticky | → Label |
   |---|---|---|
   | 🟡 jaune | `Bug : quelque chose de cassé` | **Bug** |
   | 🟢 vert clair | `Fonctionnalité` | **Fonctionnalité** |
   | 🔵 bleu clair | `Dette technique : nettoyage` | **Dette technique** |

4. **Listez les cadres cibles** — un par ligne, supporte les regex :
   ```
   En cours
   Terminé
   HOTFIX Terminé .*
   ```
5. **Listez les groupes de détail** *(optionnel)* — cadres à détailler après le résumé.
   Séparez les groupes par une ligne vide ; les patterns d'un groupe sont combinés :
   ```
   Terminé
   HOTFIX Terminé .*

   En cours
   ```
   → Groupe 1 : `Terminé` + tous les cadres `HOTFIX Terminé *` combinés
   → Groupe 2 : `En cours` seul

6. Cliquez sur **Compter les stickies** — les résultats apparaissent sous la forme d'un tableau.
""",
        "spinner_frames": "Récupération des cadres…",
        "spinner_legend": "Lecture de la légende depuis '{name}'…",
        "spinner_frame": "Lecture de '{name}'…",
        "error_api": "Impossible d'accéder à l'API Miro : {e}",
        "warning_legend": "Cadre de légende '{name}' introuvable — affichage des couleurs brutes.",
        "error_no_match": "Aucun cadre trouvé : {names}",
        "section_all": "Tout",
        "section_by_group": "Par groupe",
        "col_type": "Type",
        "col_count": "Nombre",
        "total_label": "TOTAL",
        "stickies_suffix": "stickies",
    },
}
