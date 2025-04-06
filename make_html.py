import os
import re
from collections import defaultdict

# Path to your merged_videos folder (adjust if needed)
video_dir = '/l/users/gus.xia/fathinah/expotion/predicted_output/expotion/merged_videos'

# Groups will be stored in a dictionary where:
#   key: group prefix (everything up to and including "clip<number>_")
#   value: dict mapping suffix -> filename
groups = defaultdict(dict)

# Set to collect all unique suffixes (for potential table ordering)
all_suffixes = set()

# Regex to extract group key and suffix.
# For example:
# "4.mp4_ProudPeacock_2025-02-28T12-21-34_clip2_face_only.mp4"
# group key -> "4.mp4_ProudPeacock_2025-02-28T12-21-34_clip2_"
# suffix   -> "face_only"
pattern = re.compile(r"^(.*clip\d+_)(.+)\.mp4$")

# Iterate over all mp4 files in the folder
for filename in os.listdir(video_dir):
    if filename.endswith(".mp4"):
        match = pattern.match(filename)
        if match:
            group_key = match.group(1)
            suffix = match.group(2)
            groups[group_key][suffix] = filename
            all_suffixes.add(suffix)

# Define the set of group keys that should go into the second table.
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

# Split groups into two dictionaries
groups_first = {}   # Groups not in the second table list
groups_second = {}  # Groups in the second table list

for group_key, mapping in groups.items():
    if group_key in second_table_groups:
        groups_second[group_key] = mapping
    else:
        groups_first[group_key] = mapping

# For the first table, we want to display only these five columns (data keys)
first_table_columns = [
    "vidmuse_video",
    "baseline_musicgen_video",
    "synch_5fps_video",
    "face_synch"
]

# Header mapping for the first table
first_table_header_mapping = {
    "vidmuse_video": "VidMuse",
    "baseline_musicgen_video": "MusicGen",
    "synch_5fps_video": "Ours(Motion)",
    "face_synch": "Ours(Face+Motion)"
}

# For the second table, we want a fixed order of six columns (data keys)
second_table_columns = [
    "face_only",
    "face_synch",
    "raft_5fps_video",
    "raft_nocap_video",
    "synch_5fps_video",
    "synch_nocap_all_5fps_video"
]

# Header mapping for the second table
second_table_header_mapping = {
    "face_only": "Face Only",
    "face_synch": "Face+Motion",
    "raft_5fps_video": "Motion(R)",
    "raft_nocap_video": "Motion(R) NC",
    "synch_5fps_video": "Motion(S)",
    "synch_nocap_all_5fps_video": "Motion (S) NC"
}

def generate_table_html_no_group(groups_dict, column_order, header_mapping=None):
    """
    Generate HTML for a table without a group column.
    Each row corresponds to one group, and each cell in the row is based on the fixed column order.
    Optionally uses header_mapping to display friendly column names.
    """
    html = '<table>\n'
    html += '  <thead>\n'
    html += '    <tr>\n'
    for col in column_order:
        header = header_mapping[col] if header_mapping and col in header_mapping else col
        html += f'      <th>{header}</th>\n'
    html += '    </tr>\n'
    html += '  </thead>\n'
    html += '  <tbody>\n'
    for group_key, suffix_dict in groups_dict.items():
        html += '    <tr>\n'
        for col in column_order:
            if col in suffix_dict:
                # Construct relative path (assumes merged_videos folder is alongside the HTML)
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
    html += '  </tbody>\n'
    html += '</table>\n'
    return html

# Generate the first table using the fixed five columns and header mapping (no group name)
html_table_first = generate_table_html_no_group(groups_first, first_table_columns, first_table_header_mapping)

# Generate the second table using the fixed six columns and header mapping (no group name)
html_table_second = generate_table_html_no_group(groups_second, second_table_columns, second_table_header_mapping)

# Combine the two tables into a full HTML page with emoticons and table titles.
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
""".format(table1=html_table_first, table2=html_table_second)

# Write the full HTML to a file
with open("videos_tables.html", "w") as f:
    f.write(full_html)

print("HTML with two tables generated and saved as videos_tables.html")
