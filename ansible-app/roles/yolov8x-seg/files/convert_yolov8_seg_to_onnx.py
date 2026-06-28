from ultralytics import YOLO

print("Loading YOLOv8-seg model...")
model = YOLO("yolov8x-seg.pt")

print("Exporting to ONNX...")
model.export(
    format="onnx",
    opset=12,
    dynamic=True,
    imgsz=1024,
    simplify=False
)

print("Done: yolov8x-seg.onnx")
