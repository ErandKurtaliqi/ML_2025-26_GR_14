from ultralytics import YOLO

# 1. Load the pretrained model
model = YOLO("yolov8n.pt")

# 2. Train with optimized hyperparameters for tiny "X" mark detection
#
# KEY CHANGES from previous training:
#   - imgsz=1024  (was 640) — marks are only ~5.5% x 1.5% of image, need more pixels
#   - epochs=150  (was 50)  — more training time for convergence on tiny objects
#   - degrees=15  — rotation augmentation for angled sheets
#   - perspective=0.001 — camera tilt augmentation
#   - mixup=0.1   — regularization for better generalization
#   - patience=30 — early stopping to prevent overfitting
#   - single_cls=True — we only have 1 class, this simplifies the task
#
model.train(
    data="data.yaml",
    epochs=150,               # More epochs for better convergence
    imgsz=1024,               # CRITICAL: marks are ~56x16px at 1024 vs ~35x10px at 640
    batch=-1,                 # Auto-batch (uses max memory available)
    project="runs",
    name="student_answer_v2",
    exist_ok=True,
    patience=30,              # Early stopping — stops if no improvement for 30 epochs
    single_cls=True,          # Only 1 class (marked_box) — simplifies the model's job

    # --- AUGMENTATIONS ---
    degrees=15.0,             # Rotation: handles tilted/rotated scanned sheets
    perspective=0.001,        # Perspective warp: handles camera angle variations
    hsv_v=0.4,                # Brightness jitter: handles different lighting
    hsv_s=0.7,                # Saturation jitter: helps with faint pencil/ink
    scale=0.3,                # Zoom scale (reduced from 0.5 — 0.5 is too aggressive for tiny marks)
    mosaic=1.0,               # Mosaic augmentation: combines 4 images
    mixup=0.1,                # Mixup: mild regularization
    close_mosaic=20,          # Disable mosaic in last 20 epochs for fine-tuning
    flipud=0.0,               # NO vertical flip (answer sheets have fixed orientation)
    fliplr=0.0,               # NO horizontal flip (A/B/C/D order matters for position)
    erasing=0.0,              # NO random erasing (could erase the tiny marks we need!)
)

print("\n" + "=" * 60)
print("  Training complete!")
print("  Best model: runs/student_answer_v2/weights/best.pt")
print("=" * 60)