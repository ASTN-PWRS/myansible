#!/usr/bin/env python3
import argparse
import sys
import json
import cv2
import numpy as np
import onnxruntime as ort
import tempfile
import os

from ultralytics import YOLO

DEFAULT_MODEL_PATH = "/opt/models/YOLOv8/yolov8x-seg.onnx"


def write_json(obj):
    print(json.dumps(obj, ensure_ascii=False))


def error(msg):
    write_json({"error": msg})
    sys.exit(1)


def read_image_from_stdin():
    data = sys.stdin.buffer.read()
    if not data:
        return None
    arr = np.frombuffer(data, np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def load_exclude_template(path):
    return cv2.imread(path) if path else None


def load_exclude_config(path):
    if not path:
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}


def is_excluded(box, img_shape, template_img, params):
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1
    area = w * h
    H, W = img_shape[:2]

    min_area = params.get("min_area_ratio")
    if min_area and area > W * H * min_area:
        return True

    if template_img is not None:
        th, tw = template_img.shape[:2]
        tr = tw / th
        if abs((w / h) - tr) < params.get("ratio_tolerance", 0.02):
            return True

    return False


def run_yolov8_seg(image_path, model_path):
    try:
        session = ort.InferenceSession(model_path)
    except Exception as e:
        error(f"Failed to load ONNX model: {e}")

    img = cv2.imread(image_path)
    if img is None:
        error(f"Cannot read image: {image_path}")

    H, W = img.shape[:2]

    resized = cv2.resize(img, (1024, 1024))
    x = resized[:, :, ::-1].transpose(2, 0, 1).astype(np.float32) / 255.0
    x = np.expand_dims(x, 0)

    try:
        boxes, masks = session.run(None, {"images": x})
    except Exception as e:
        error(f"ONNX inference failed: {e}")

    results = []
    for i in range(len(boxes)):
        bx = boxes[i]
        mask = masks[i]
        mask = cv2.resize(mask, (W, H))
        mask = (mask > 0.5).astype(np.uint8)
        results.append((bx[:4], mask))

    return results


def run_train(model_path, data_yaml, epochs, imgsz, batch, project, name):
    model = YOLO(model_path)
    model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project=project,
        name=name,
    )

    pt_path = f"{project}/{name}/weights/best.pt"
    onnx_path = f"{project}/{name}/weights/best.onnx"

    # ★ best.pt → best.onnx 自動変換
    try:
        model = YOLO(pt_path)
        model.export(format="onnx", imgsz=imgsz)
    except Exception as e:
        error(f"ONNX export failed: {e}")

    write_json({
        "train": "completed",
        "project": project,
        "name": name,
        "best_pt": pt_path,
        "best_onnx": onnx_path,
    })


def main():
    parser = argparse.ArgumentParser(
        description="YOLOv8-seg CLI — segment image OR train custom model"
    )

    # 推論
    parser.add_argument("--image", help="Path to image file")
    parser.add_argument("--exclude-template", help="Template image for exclusion")
    parser.add_argument("--exclude-config", help="JSON file with exclusion parameters")
    parser.add_argument("--output", help="Write JSON result to file")

    # ★ ONNX モデル切り替え
    parser.add_argument("--model", default=DEFAULT_MODEL_PATH,
                        help="Path to ONNX model")

    # ★ 複数モデル同時推論
    parser.add_argument("--multi-model",
                        help="Comma-separated ONNX model paths for combined inference")

    # 学習モード
    parser.add_argument("--train", action="store_true")
    parser.add_argument("--train-model", help="Base model for training (.pt)")
    parser.add_argument("--data", help="Path to custom.yaml")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    parser.add_argument("--project", default=None)
    parser.add_argument("--name", default="exp")

    args = parser.parse_args()

    # -------------------------
    # 学習モード
    # -------------------------
    if args.train:
        if not args.train_model:
            error("--train-model is required")
        if not args.data:
            error("--data is required")

        project = args.project or "/opt/models/yolov8-custom"

        run_train(
            model_path=args.train_model,
            data_yaml=args.data,
            epochs=args.epochs,
            imgsz=args.imgsz,
            batch=args.batch,
            project=project,
            name=args.name,
        )
        return

    # -------------------------
    # 推論モード
    # -------------------------
    if not args.image and sys.stdin.isatty():
        error("No input image provided")

    img = None
    temp_file = None

    if args.image:
        img = cv2.imread(args.image)
        if img is None:
            error(f"Cannot read image: {args.image}")
    else:
        img = read_image_from_stdin()
        if img is None:
            error("No image provided")

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        cv2.imwrite(temp.name, img)
        temp_file = temp.name

    image_path = args.image if args.image else temp_file

    template_img = load_exclude_template(args.exclude_template)
    exclude_params = load_exclude_config(args.exclude_config)

    results = []

    # ★ 複数モデル同時推論
    if args.multi_model:
        model_paths = args.multi_model.split(",")
        for mp in model_paths:
            seg_results = run_yolov8_seg(image_path, mp)
            for box, mask in seg_results:
                if not is_excluded(box, img.shape, template_img, exclude_params):
                    results.append({"box": list(map(int, box)), "model": mp})
    else:
        seg_results = run_yolov8_seg(image_path, args.model)
        for box, mask in seg_results:
            if not is_excluded(box, img.shape, template_img, exclude_params):
                results.append({"box": list(map(int, box)), "model": args.model})

    output_obj = {"results": results}

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_obj, f, ensure_ascii=False)
    else:
        write_json(output_obj)

    if temp_file:
        os.remove(temp_file)


if __name__ == "__main__":
    main()
