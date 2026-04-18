# from pathlib import Path

# label_dirs = [
#     Path("dataset/labels/train"),
#     Path("dataset/labels/val"),
#     Path("dataset/labels/test"),
# ]

# mapping = {
#     "15": "0",  # empty_box
#     "16": "1",  # marked_box
#     "16.0": "1",
#     "15.0": "0",
#     "17": "1",  # në rast se diku i ke 16/17
# }

# for label_dir in label_dirs:
#     for txt_file in label_dir.glob("*.txt"):
#         lines = txt_file.read_text(encoding="utf-8").splitlines()
#         fixed_lines = []

#         for line in lines:
#             parts = line.strip().split()
#             if not parts:
#                 continue

#             if parts[0] in mapping:
#                 parts[0] = mapping[parts[0]]

#             fixed_lines.append(" ".join(parts))

#         txt_file.write_text("\n".join(fixed_lines) + "\n", encoding="utf-8")

# print("Labels fixed successfully.")


# from pathlib import Path

# label_dirs = [
#     Path("dataset/labels/train"),
#     Path("dataset/labels/val"),
#     Path("dataset/labels/test"),
# ]

# mapping = {
#     "15": "1",  # marked_box
#     "16": "0",  # empty_box
# }

# for label_dir in label_dirs:
#     for txt_file in label_dir.glob("*.txt"):
#         lines = txt_file.read_text(encoding="utf-8").splitlines()
#         fixed_lines = []

#         for line in lines:
#             parts = line.strip().split()
#             if not parts:
#                 continue

#             if parts[0] in mapping:
#                 parts[0] = mapping[parts[0]]

#             fixed_lines.append(" ".join(parts))

#         txt_file.write_text("\n".join(fixed_lines) + "\n", encoding="utf-8")

# print("Labels fixed correctly.")

from pathlib import Path

label_dirs = [
    Path("dataset/labels/train"),
    Path("dataset/labels/val"),
    Path("dataset/labels/test"),
]

for label_dir in label_dirs:
    for txt_file in label_dir.glob("*.txt"):
        lines = txt_file.read_text(encoding="utf-8").splitlines()
        fixed_lines = []

        for line in lines:
            parts = line.strip().split()
            if not parts:
                continue

            parts[0] = "0"   # vetëm marked_box

            fixed_lines.append(" ".join(parts))

        txt_file.write_text("\n".join(fixed_lines) + "\n", encoding="utf-8")

print("All labels converted to class 0 (marked_box).")