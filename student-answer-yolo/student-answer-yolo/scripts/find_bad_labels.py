"""Find all label files with class ID != 0."""
import os

LABEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset", "labels", "train")

for fname in sorted(os.listdir(LABEL_DIR)):
    if not fname.endswith('.txt') or fname == 'classes.txt':
        continue
    path = os.path.join(LABEL_DIR, fname)
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]
    
    bad_classes = []
    for i, line in enumerate(lines):
        parts = line.split()
        if len(parts) == 5:
            cls_id = int(parts[0])
            if cls_id != 0:
                bad_classes.append((i+1, cls_id, line))
    
    if bad_classes:
        print(f"\n--- {fname} ({len(lines)} total lines) ---")
        for line_num, cls_id, content in bad_classes:
            print(f"  Line {line_num}: class={cls_id}  -> {content}")
        print(f"  Bad lines: {len(bad_classes)}/{len(lines)}")
