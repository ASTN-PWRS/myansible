# YOLOv8-seg CLI — 使い方まとめ

この CLI は以下に対応しています：

- **ONNX 推論（既存モデル / 学習モデル）**
- **PyTorch 学習（best.pt 生成）**
- **学習後の best.pt → best.onnx 自動変換**
- **複数 ONNX モデルを同時にかけて結果を統合**
- **除外テンプレートによるフィルタリング**

---

## 1. 推論（Inference）

### 1-1. 既存モデル（公式 yolov8x-seg.onnx）で推論

```bash
yolov8_seg_cli --image input.png
```

### 1-2. 学習モデル（best.onnx）で推論

```
yolov8_seg_cli \
  --image input.png \
  --model /opt/models/yolov8-custom/mylogo/weights/best.onnx
```

### 1-3. 推論結果をファイルに保存

```
yolov8_seg_cli --image input.png --output result.json
```

### 1-4. 標準入力から画像を渡す

```
cat input.png | yolov8_seg_cli
```


## 2. 複数モデルを同時にかけて結果を統合

```
yolov8_seg_cli \
  --image input.png \
  --multi-model /opt/models/YOLOv8/yolov8x-seg.onnx,/opt/models/yolov8-custom/mylogo/weights/best.onnx
```

出力結果の例：

{
  "results": [
    {"box": [10,20,100,200], "model": "/opt/models/YOLOv8/yolov8x-seg.onnx"},
    {"box": [30,40,120,220], "model": "/opt/models/yolov8-custom/mylogo/weights/best.onnx"}
  ]
}

## 3. 学習（Training）


### 3-1. 最小構成（project 自動設定）

```
yolov8_seg_cli --train \
  --train-model yolov8s.pt \
  --data /opt/datasets/mylogo/custom.yaml

```

保存先：


/opt/models/yolov8-custom/exp/weights/best.pt
/opt/models/yolov8-custom/exp/weights/best.onnx


### 3-2. name を指定して学習

yolov8_seg_cli --train \
  --train-model yolov8s.pt \
  --data /opt/datasets/mylogo/custom.yaml \
  --name mylogo


保存先：


/opt/models/yolov8-custom/mylogo/weights/best.pt
/opt/models/yolov8-custom/mylogo/weights/best.onnx


4. 除外テンプレートの例

例：除外したいロゴ画像
exclude-template.png

{
  "min_area_ratio": 0.15,
  "ratio_tolerance": 0.02
}


5. 学習用 custom.yaml の例

train: /opt/datasets/mylogo/train/images
val: /opt/datasets/mylogo/val/images

names:
  0: logo
  1: dog
  2: cat


7. まとめ

| 機能 | 説明 |
| --- | --- |
| ONNX 推論 | ``--model`` で切り替え |
| PyTorch 学習 | ``--train`` |
| best.pt → best.onnx | 自動変換 |
| 複数モデル同時推論 | ``--multi-model`` |
| 除外テンプレート | ``--exclude-template`` |


