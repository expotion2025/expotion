import os
import re
import csv
from collections import defaultdict

# ---------------------------
# Load captions from CSV file
# ---------------------------
# The CSV file is expected to have two columns:
#   Column 0: filename (e.g., "4.mp4_ProudPeacock_2025-02-27T13-01-50_clip2")
#   Column 1: caption text
captions = {}
csv_path = "../../test.csv"  # Adjust the path if needed

with open(csv_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        # Split only on the first comma
        parts = line.split(",", 1)
        if len(parts) == 2:
            key = parts[0].strip()  # filename without extension
            caption_text = parts[1].strip()
            captions[key] = caption_text

# -----------------------------------------
# Build groups from the merged_videos folder
# -----------------------------------------
video_dir = '/l/users/gus.xia/fathinah/expotion/predicted_output/expotion/merged_videos'

# Groups will be stored in a dictionary where:
#   key: group prefix (everything up to and including "clip<number>_")
#   value: dict mapping suffix -> filename
groups = defaultdict(dict)
all_suffixes = set()

# Regex to extract group key and suffix.
# Example: For "4.mp4_ProudPeacock_2025-02-27T13-01-50_clip2_face_only.mp4":
#   group key -> "4.mp4_ProudPeacock_2025-02-27T13-01-50_clip2_"
#   suffix   -> "face_only"
pattern = re.compile(r"^(.*clip\d+_)(.+)\.mp4$")

for filename in os.listdir(video_dir):
    if filename.endswith(".mp4"):
        match = pattern.match(filename)
        if match:
            group_key = match.group(1)
            suffix = match.group(2)
            groups[group_key][suffix] = filename
            all_suffixes.add(suffix)

# ---------------------------------------------
# Split groups into two dictionaries (by group key)
# ---------------------------------------------
second_table_groups = {
    "161.mp4_DelightfulOwl_2025-03-06T18-06-02_clip3_",
    "46.mp4_DelightfulOwl_2025-03-06T19-27-32_clip3_",
    "540.mp4_DelightfulOwl_2025-03-06T19-11-18_clip3_",
    "61.mp4_DelightfulOwl_2025-03-06T18-09-39_clip3_",
    "20.mp4_ProudPeacock_2025-02-26T09-54-39_clip10_",
    "106.mp4_NiceWolf_2025-03-11T12-46-02_clip1_",
    "54.mp4_EnergeticMonkey_2025-03-01T10-26-38_clip18_",
    "56.mp4_EagerRabbit_2025-03-01T05-12-36_clip2_"
}

groups_first = {}   # Groups not in the second table list
groups_second = {}  # Groups in the second table list

for group_key, mapping in groups.items():
    if group_key in second_table_groups:
        groups_second[group_key] = mapping
    else:
        groups_first[group_key] = mapping

# ---------------------------------------------
# Table definitions and header mappings
# ---------------------------------------------
# First table: Fixed columns and header mapping.
first_table_columns = [
    "vidmuse_video",
    "baseline_musicgen_video",
    "synch_5fps_video",
    "face_synch"
]

first_table_header_mapping = {
    "vidmuse_video": "VidMuse",
    "baseline_musicgen_video": "MusicGen",
    "synch_5fps_video": "Ours(Motion)",
    "face_synch": "Ours(Face+Motion)"
}

# Second table: Fixed columns and header mapping.
second_table_columns = [
    "face_only",
    "face_synch",
    "synch_5fps_video",
    "raft_5fps_video",
    "raft_nocap_video",
    "synch_nocap_all_5fps_video"
]

second_table_header_mapping = {
    "face_only": "Face Only",
    "face_synch": "Face+Motion🏆",
    "synch_5fps_video": "Motion(S)🏆",
    "raft_5fps_video": "Motion(R)",
    "raft_nocap_video": "Motion(R) NC",
    "synch_nocap_all_5fps_video": "Motion (S) NC"
}

# ------------------------------------------------------------
# Function to generate HTML for a table without a group column.
# Now the caption is added in a row below each group's video row.
# If table_class is provided, it is added to the <table> tag.
# If split_nc is True, the caption row will merge only the first (total_columns - split_nc_count) cells,
# and then add separate cells with "N/A" for the remaining columns.
# ------------------------------------------------------------
def generate_table_html_no_group(groups_dict, column_order, header_mapping=None, captions_dict=None, split_nc=False, split_nc_count=0, table_class=""):
    class_attr = f' class="{table_class}"' if table_class else ""
    html = f'<table{class_attr}>\n'
    html += '  <thead>\n'
    html += '    <tr>\n'
    for col in column_order:
        header = header_mapping[col] if header_mapping and col in header_mapping else col
        html += f'      <th>{header}</th>\n'
    html += '    </tr>\n'
    html += '  </thead>\n'
    html += '  <tbody>\n'
    # For each group, create two rows: one for videos, one for the caption.
    for group_key, suffix_dict in groups_dict.items():
        # First row: video cells.
        html += '    <tr>\n'
        for col in column_order:
            if col in suffix_dict:
                video_path = f"merged_videos/{suffix_dict[col]}"
                html += '      <td>\n'
                html += '        <video width="320" controls>\n'
                html += f'          <source src="{video_path}" type="video/mp4">\n'
                html += '          Your browser does not support the video tag.\n'
                html += '        </video>\n'
                html += '      </td>\n'
            else:
                html += '      <td></td>\n'
        html += '    </tr>\n'
        # Second row: caption.
        lookup_key = group_key.rstrip('_')
        caption_text = captions_dict.get(lookup_key, "") if captions_dict else ""
        if split_nc:
            total_cols = len(column_order)
            merged_cols = total_cols - split_nc_count
            html += f'    <tr><td colspan="{merged_cols}" style="text-align:left;font-style:italic;color:#555;">{caption_text}</td>'
            for _ in range(split_nc_count):
                html += '<td>Music with catchy melody</td>'
            html += '</tr>\n'
        else:
            colspan = len(column_order)
            html += f'    <tr><td colspan="{colspan}" style="text-align:left;font-style:italic;color:#555;">{caption_text}</td></tr>\n'
    html += '  </tbody>\n'
    html += '</table>\n'
    return html

# ------------------------------------------------------------
# Generate both tables.
# For the first table, use the default merged caption row.
html_table_first = generate_table_html_no_group(groups_first, first_table_columns, first_table_header_mapping, captions)

# For the second table, split the caption row so that the last 2 columns are not merged,
# and assign a table class to enable fixed layout.
html_table_second = generate_table_html_no_group(groups_second, second_table_columns, second_table_header_mapping, captions, split_nc=True, split_nc_count=2, table_class="table2")

# ------------------------------------------------------------
# Escape any curly braces in the generated table HTML to avoid format() errors.
safe_table1 = html_table_first.replace("{", "{{").replace("}", "}}")
safe_table2 = html_table_second.replace("{", "{{").replace("}", "}}")

# ------------------------------------------------------------
# Combine the two tables into a full HTML page with styling and notes.
# ------------------------------------------------------------
full_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Video Tables</title>
  <style>
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 2rem;
    }}
    /* Fixed layout for table2 to ensure consistent column widths */
    table.table2 {{
      table-layout: fixed;
    }}
    table.table2 th, table.table2 td {{
      width: calc(100% / 6);
    }}
    th, td {{
      padding: 0.5rem;
      border: 1px solid #ccc;
      text-align: center;
    }}
    video {{
      max-width: 100%;
      height: auto;
    }}
    body {{
      font-family: Arial, sans-serif;
      margin: 2rem;
    }}
    h1 {{
      color: #333;
    }}
    p.note {{
      font-style: italic;
      color: #555;
    }}
  </style>
</head>
<body>
  <h1>🎬 Baselines VS Ours</h1>
  {table1}
  <h1>🎶 Generated Music on Different Visual Extractors</h1>
  {table2}
  <p class="note">💡 Note: "Motion(R)" means Motion with RAFT, "Motion(S)" means Motion with Synchformer, and "NC" means no caption (generic caption).</p>
</body>
</html>
""".format(table1=safe_table1, table2=safe_table2)

# Write the full HTML to a file (e.g., index.html)
with open("index.html", "w") as f:
    f.write(full_html)

print("HTML with two tables (with modified caption rows in second table) generated and saved as index.html")
