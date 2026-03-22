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