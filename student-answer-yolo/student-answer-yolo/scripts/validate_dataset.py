"""Validate the YOLO dataset for training issues."""
import os
import glob
from collections import Counter
from PIL import Image

DATASET_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset")

def validate():
    issues = []
    
    for split in ["train", "val", "test"]:
        img_dir = os.path.join(DATASET_ROOT, "images", split)
        lbl_dir = os.path.join(DATASET_ROOT, "labels", split)
        
        if not os.path.isdir(img_dir):
            print(f"[SKIP] {img_dir} does not exist")
            continue
            
        images = {os.path.splitext(f)[0]: f for f in os.listdir(img_dir) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))}
        
        labels = {}
        if os.path.isdir(lbl_dir):
            labels = {os.path.splitext(f)[0]: f for f in os.listdir(lbl_dir) 
                      if f.endswith('.txt')}
        
        print(f"\n{'='*60}")
        print(f"  SPLIT: {split}")
        print(f"  Images: {len(images)}, Labels: {len(labels)}")
        print(f"{'='*60}")

        missing_labels = set(images.keys()) - set(labels.keys())
        if missing_labels:
            print(f"  [WARN] {len(missing_labels)} images WITHOUT labels:")
            for m in sorted(missing_labels)[:5]:
                print(f"    - {m}")
        
        extra_labels = set(labels.keys()) - set(images.keys())
        if extra_labels:
            print(f"  [WARN] {len(extra_labels)} labels WITHOUT images:")
            for e in sorted(extra_labels)[:5]:
                print(f"    - {e}")
        
        line_counts = []
        class_ids = Counter()
        bad_labels = []
        bbox_sizes = []
        
        for name, lbl_file in sorted(labels.items()):
            lbl_path = os.path.join(lbl_dir, lbl_file)
            with open(lbl_path, 'r') as f:
                lines = [l.strip() for l in f.readlines() if l.strip()]
            
            line_counts.append(len(lines))
            
            for line in lines:
                parts = line.split()
                if len(parts) != 5:
                    bad_labels.append((name, line))
                    continue
                
                try:
                    cls_id = int(parts[0])
                    x_center, y_center, width, height = map(float, parts[1:])
                    class_ids[cls_id] += 1
                    bbox_sizes.append((width, height))
                    
                    if not (0 <= x_center <= 1 and 0 <= y_center <= 1):
                        bad_labels.append((name, f"OOB center: {x_center:.4f}, {y_center:.4f}"))
                    if not (0 < width <= 1 and 0 < height <= 1):
                        bad_labels.append((name, f"Bad size: {width:.4f}x{height:.4f}"))
                except ValueError:
                    bad_labels.append((name, line))
        
        if line_counts:
            print(f"\n  Label statistics:")
            print(f"    Min annotations/image: {min(line_counts)}")
            print(f"    Max annotations/image: {max(line_counts)}")
            print(f"    Avg annotations/image: {sum(line_counts)/len(line_counts):.1f}")
            print(f"    Total annotations: {sum(line_counts)}")
        
        if class_ids:
            print(f"\n  Class distribution:")
            for cls, count in sorted(class_ids.items()):
                print(f"    Class {cls}: {count} annotations")
        
        if bad_labels:
            print(f"\n  [ERROR] {len(bad_labels)} bad label entries:")
            for name, detail in bad_labels[:10]:
                print(f"    - {name}: {detail}")
        
        if bbox_sizes:
            widths = [w for w, h in bbox_sizes]
            heights = [h for w, h in bbox_sizes]
            print(f"\n  BBox size stats (normalized):")
            print(f"    Width:  min={min(widths):.5f}, max={max(widths):.5f}, avg={sum(widths)/len(widths):.5f}")
            print(f"    Height: min={min(heights):.5f}, max={max(heights):.5f}, avg={sum(heights)/len(heights):.5f}")
            
            tiny = sum(1 for w, h in bbox_sizes if w < 0.01 or h < 0.01)
            if tiny:
                print(f"    [WARN] {tiny} boxes are VERY TINY (< 1% of image)")
        
        if images:
            print(f"\n  Checking image dimensions (first 10)...")
            img_sizes = Counter()
            for name in sorted(images.keys())[:10]:
                img_path = os.path.join(img_dir, images[name])
                try:
                    with Image.open(img_path) as im:
                        img_sizes[im.size] += 1
                except Exception as e:
                    print(f"    [ERROR] Can't open {name}: {e}")
            
            for size, count in img_sizes.most_common():
                print(f"    {size[0]}x{size[1]}: {count} images")

    data_yaml = os.path.join(os.path.dirname(DATASET_ROOT), "data.yaml")
    if os.path.exists(data_yaml):
        print(f"\n{'='*60}")
        print(f"  DATA.YAML CONTENTS:")
        print(f"{'='*60}")
        with open(data_yaml) as f:
            print(f.read())

if __name__ == "__main__":
    validate()
