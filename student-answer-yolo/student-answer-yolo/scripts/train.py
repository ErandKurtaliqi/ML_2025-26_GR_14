from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="data.yaml",
    epochs=150,               
    imgsz=1024,              
    batch=-1,                
    project="runs",
    name="student_answer_v2",
    exist_ok=True,
    patience=30,              
    single_cls=True,          
    degrees=15.0,            
    perspective=0.001,        
    hsv_v=0.4,                
    hsv_s=0.7,                
    scale=0.3,               
    mosaic=1.0,               
    mixup=0.1,                
    close_mosaic=20,          
    flipud=0.0,               
    fliplr=0.0,               
    erasing=0.0,              
)

print("\n" + "=" * 60)
print("  Training complete!")
print("  Best model: runs/student_answer_v2/weights/best.pt")
print("=" * 60)