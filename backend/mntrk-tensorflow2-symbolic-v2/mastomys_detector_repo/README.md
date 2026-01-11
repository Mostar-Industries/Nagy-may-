# 🐭 Mastomys Rodent Detection with YOLOv8

This repository contains all necessary files to train and deploy a YOLOv8 model for detecting **Mastomys natalensis**, a key vector of Lassa Fever.

---

## 📦 Contents

- `mastomys_yolov8_detector.ipynb` – Kaggle-ready notebook for full training and deployment
- `README.md` – This guide
- `data.yaml` – Sample config for YOLO training (upload your own if using a new dataset)

---

## 🧪 How to Use on Kaggle

### Step 1: Upload Dataset
Upload a YOLOv8-formatted dataset to **Kaggle Datasets**, including:

```
mastomys-yolo-dataset/
├── images/
│   ├── train/
│   ├── val/
├── labels/
│   ├── train/
│   ├── val/
└── data.yaml
```

> Your `data.yaml` should point to correct paths for train/val sets and class names.

---

### Step 2: Open the Notebook
1. Go to [Kaggle Notebooks](https://www.kaggle.com/code)
2. Click “**New Notebook**”
3. Attach your uploaded dataset from the right panel
4. Upload this notebook: `mastomys_yolov8_detector.ipynb`
5. Run all cells (make sure GPU is enabled under “Accelerator” settings)

---

### Step 3: Export the Model (Optional)
The notebook exports the trained model to:
- ONNX
- TorchScript
- OpenVINO

You can download them from `runs/detect/train/weights/`.

---

## 🧠 Tips
- For faster training, use `yolov8n.pt` or `yolov8s.pt`
- You can increase epochs or image size for better accuracy
- Export to ONNX if deploying to real-time systems or mobile

--- 

Built with ⚡ by MoStar Grid.
