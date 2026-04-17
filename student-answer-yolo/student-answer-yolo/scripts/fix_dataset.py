"""
Fix all training issues found in the YOLO dataset:
1. Fix class IDs (15 -> 0) in 22 contaminated label files
2. Remove classes.txt garbage file
3. Delete stale .cache files
4. Remove orphaned label (20260309_210922.txt from train labels)
"""
import os
import shutil

DATASET = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dataset")

def fix_labels():
    """Fix class ID 15 -> 0 in all label files."""
    label_dir = os.path.join(DATASET, "labels", "train")
    fixed_count = 0
    
    for fname in sorted(os.listdir(label_dir)):
        if not fname.endswith('.txt') or fname == 'classes.txt':
            continue
        
        path = os.path.join(label_dir, fname)
        with open(path, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        file_changed = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            parts = stripped.split()
            if len(parts) == 5 and parts[0] != '0':
                parts[0] = '0'
                new_lines.append(' '.join(parts) + '\n')
                file_changed = True
            else:
                new_lines.append(stripped + '\n')
        
        if file_changed:
            with open(path, 'w') as f:
                f.writelines(new_lines)
            fixed_count += 1
            print(f"  [FIXED] {fname} - class IDs corrected to 0")
    
    print(f"\n  Total files fixed: {fixed_count}")
    return fixed_count


def remove_garbage_files():
    """Remove classes.txt and orphaned files."""
    removed = 0
    
    # Remove classes.txt from labels/train
    classes_txt = os.path.join(DATASET, "labels", "train", "classes.txt")
    if os.path.exists(classes_txt):
        os.remove(classes_txt)
        print(f"  [REMOVED] classes.txt from labels/train")
        removed += 1
    
    # Remove orphaned label (20260309_210922.txt in train labels but no matching image)
    orphan = os.path.join(DATASET, "labels", "train", "20260309_210922.txt")
    if os.path.exists(orphan):
        # Check if the image exists in train
        img_exists = any(
            os.path.exists(os.path.join(DATASET, "images", "train", f"20260309_210922.{ext}"))
            for ext in ['jpg', 'jpeg', 'png']
        )
        if not img_exists:
            os.remove(orphan)
            print(f"  [REMOVED] 20260309_210922.txt (orphaned label, no matching image)")
            removed += 1
    
    return removed


def delete_cache_files():
    """Delete .cache files so YOLO re-reads corrected data."""
    deleted = 0
    for root, dirs, files in os.walk(DATASET):
        for f in files:
            if f.endswith('.cache'):
                cache_path = os.path.join(root, f)
                os.remove(cache_path)
                print(f"  [DELETED] {os.path.relpath(cache_path, DATASET)}")
                deleted += 1
    return deleted


def main():
    print("=" * 60)
    print("  YOLO DATASET FIX SCRIPT")
    print("=" * 60)
    
    print("\n[1/3] Fixing class IDs in label files...")
    fix_labels()
    
    print("\n[2/3] Removing garbage files...")
    remove_garbage_files()
    
    print("\n[3/3] Deleting stale cache files...")
    delete_cache_files()
    
    print("\n" + "=" * 60)
    print("  ALL FIXES APPLIED!")
    print("  Next step: Retrain the model with 'python scripts/train.py'")
    print("=" * 60)


if __name__ == "__main__":
    main()
