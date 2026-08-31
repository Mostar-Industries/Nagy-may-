#!/usr/bin/env python3
"""
Skyhawk ML Service - Path Resolution Update Script
Updates yolo_detector.py for better model path handling and refreshes README
"""
from pathlib import Path


def update_yolo_detector():
    """Update YOLO detector model path resolution"""
    print("Updating yolo_detector.py...")

    path = Path('backend/ml_service/models/yolo_detector.py')
    if not path.exists():
        print(f"File not found: {path}")
        return False

    text = path.read_text(encoding='utf-8')

    old = '''        # Model path resolution order:
        # 1. Explicit path passed in
        # 2. Environment variable
        # 3. Default location in weights folder
        if model_path:
            self.model_path = model_path
        else:
            self.model_path = os.getenv(
                "YOLO_MODEL_PATH",
                os.path.join(os.path.dirname(__file__), "weights", "best.pt")
            )'''

    new = '''        # Model path resolution order:
        # 1. Explicit path passed in
        # 2. Environment variable
        # 3. Default location in weights folder
        # 4. Legacy "model/weights" folder (if used)
        candidate_paths = []
        if model_path:
            candidate_paths.append(model_path)
        env_model_path = os.getenv("YOLO_MODEL_PATH")
        if env_model_path:
            candidate_paths.append(env_model_path)

        default_path = os.path.join(os.path.dirname(__file__), "weights", "best.pt")
        legacy_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model", "weights", "best.pt")
        candidate_paths.extend([default_path, legacy_path])

        self.model_path = next(
            (path for path in candidate_paths if path and os.path.exists(path)),
            candidate_paths[0] if candidate_paths else default_path
        )

        if self.model_path == legacy_path:
            logger.warning("[v2] Using legacy model path: %s", legacy_path)'''

    if old not in text:
        print("Expected block not found in yolo_detector.py")
        return False

    path.write_text(text.replace(old, new), encoding='utf-8')
    print("yolo_detector.py updated successfully")
    return True


def update_readme():
    """Rewrite README with clean structure"""
    print("Updating README.md...")

    readme = Path('backend/README.md')

    content = '''# Skyhawk ML Service - Production Integration Guide

## Files Updated

```
ml_service/
|-- __init__.py
|-- app.py                    # FastAPI app with /detect endpoint
|-- Dockerfile                # Production container
|-- requirements.txt          # Python dependencies
|-- models/
|   |-- __init__.py
|   |-- yolo_detector.py      # YOLOv8 inference with production weights
|   `-- weights/
|       `-- best.pt           # <-- DROP YOUR TRAINED MODEL HERE
`-- utils/
    |-- __init__.py
    |-- image_processor.py    # Image preprocessing
    |-- risk_scorer.py        # Lassa fever risk calculation
    |-- clinical_data_loader.py
    `-- sormas_parser.py
```

## Integration Steps

### 1. Add Your Trained Weights
After Kaggle training completes:
```bash
# Copy to: ml_service/models/weights/best.pt
```
If you placed the file under `ml_service/model/weights/`, move it to `ml_service/models/weights/` (the service prefers `models/weights`).

### 2. Local Testing
```bash
cd ml_service
pip install -r requirements.txt
python -m app
# Service runs on http://localhost:5001
```

### 3. Test Detection
```bash
curl -X POST -F "image=@test_image.jpg" http://localhost:5001/detect
```

### 4. Docker Build
```bash
docker build -t skyhawk-ml-service:2.0.0 .
docker run -p 5001:5001 skyhawk-ml-service:2.0.0
```

## Key Updates

1. **yolo_detector.py** - Auto-loads `best.pt` from `models/weights/`, includes Lassa risk weights per species
2. **app.py** - Production FastAPI with enhanced endpoints, MoStar branding
3. **risk_scorer.py** - Lassa-specific risk calculation with endemic region awareness
4. **Dockerfile** - Production-ready with health checks

## Model Performance (v2)
- mAP@50: 72.6%
- Precision: 90.8%
- Recall: 71.4%

---
MoStar Industries | African Flame Initiative | Lassa Shield
'''

    readme.write_text(content, encoding='utf-8')
    print("README.md updated successfully")
    return True


def main():
    """Execute all updates"""
    print("\nSkyhawk ML Service - Path Resolution Update")
    print("=" * 50)

    if not Path('backend').exists():
        print("\nError: 'backend' folder not found")
        print("Please run this script from your project root directory")
        print("(the folder that contains the 'backend' directory)")
        return

    print()
    success = True

    if not update_yolo_detector():
        success = False

    print()

    if not update_readme():
        success = False

    print("\n" + "=" * 50)
    if success:
        print("All updates completed successfully")
        print("\nNext steps:")
        print("  1. Place your trained model at: backend/ml_service/models/weights/best.pt")
        print("  2. Test locally: cd backend/ml_service && python -m app")
        print("  3. Build Docker: docker build -t skyhawk-ml-service:2.0.0 .")
    else:
        print("Some updates failed - check messages above")
    print()


if __name__ == '__main__':
    main()
