<div align="center">

<!-- Logo: direct SVG from Commons. If it does not load (firewall, rate limits), download the file from the Commons link below, save as docs/images/university-of-prishtina-logo.png in this repo, and point src to that path. -->
<img src="https://upload.wikimedia.org/wikipedia/commons/e/e1/University_of_Prishtina_logo.svg" width="150" height="150" alt="University of Prishtina logo" />

# University of Prishtina

## Faculty of Electrical and Computer Engineering

**Study Program:** Computer and Software Engineering – Master  
**Course:** Machine Learning  
**Group:** 14  

### Project topic

**Training and Application of the YOLO Model for Automatic Detection and Evaluation of Entrance Exams at FIEK**

[Official logo file (Wikimedia Commons)](https://commons.wikimedia.org/wiki/File:University_of_Prishtina_logo.svg)

</div>

---

## Table of contents

- [Disclaimer](#disclaimer)
- [Project overview](#project-overview)
- [Motivation](#motivation-of-the-project)
- [Phase 1](#phase-1) — dataset, pipeline, evaluation concept
- [Phase 2](#phase-2) — architecture, exam grading app, YOLO training & integration
- [Phase 3](#phase-3) - retrained 5-digit code detection, faster processing, CSV priority lists
- [Training process (YOLO)](#training-process-yolo) — labeling, metrics, OCR workflow
- [Future improvements](#future-improvements)
- [Conclusion](#conclusion)
- [Credits](#credits)

---

# Disclaimer

This project material is prepared strictly for internal academic project purposes.

Publishing, reposting, redistributing, or using any part of this material online or in any other external context is not permitted without prior written approval from the project team and course supervisor.

---

# Project Overview

This project focuses on the design and implementation of an **automated system for detecting and evaluating entrance exam tests** using **Artificial Intelligence and Computer Vision techniques**.

The system is based on the **YOLO (You Only Look Once)** deep learning model, which is widely used for **real-time object detection**.

The main objective of this project is to create a system capable of automatically analyzing **exam sheets** and extracting relevant information from them, including:

- Candidate identification code
- The position of each answer field
- Selected answers marked by the candidate
- Correct answers
- Final score calculation

By automating this process, the system can significantly **reduce the time required to evaluate entrance exams**, while also **increasing accuracy and consistency**.

---

# Motivation of the Project

Entrance exams often involve a large number of candidates. Evaluating these tests manually requires significant time and effort from academic staff.

Manual grading may also introduce potential issues such as:

- Human errors during correction
- Inconsistent evaluation
- Fatigue during large-scale exam processing
- Slow result generation

The goal of this project is to develop an **AI-based automated grading system** that can assist institutions by providing:

- Faster evaluation
- Consistent grading
- Reduced manual workload
- Reliable automated results

---

The project is organized into three main phases:

- **Phase 1 – Current System Implementation**
- **Phase 2 – YOLO Model Training and Improvement**
- **Phase 3 - Retraining, Processing Optimization, and CSV Priority Allocation**
  
---

# Phase 1

# Dataset Creation

A **custom dataset** was created specifically for training the YOLO model used in this project.

The dataset contains approximately **100 exam sheet samples**, representing different ways candidates may fill out their tests, and includes around 2,000 annotated questions.

To simulate realistic exam conditions, these test sheets were **distributed among randomly selected individuals**, who were asked to complete them as if they were taking an actual entrance exam.

This approach was chosen in order to ensure that the dataset contains **natural variations in human behavior and writing styles**, which is essential for training a robust machine learning model.

---

# Data Diversity and Realistic Scenarios

The dataset was intentionally designed to include a wide range of realistic scenarios.

Some of the cases included in the dataset are:

- Fully completed exam sheets
- Partially completed exam sheets
- Questions intentionally **left unanswered**
- Cases where **multiple answers were marked**
- Answers filled **very lightly**
- Answers filled **very strongly**
- Incomplete markings
- Slightly misaligned markings
- Deviations from the expected filling pattern
- Crossed-out answers
- Cases where candidates **changed their answers**

Additionally, the dataset includes examples where:

- The answer circle is only partially filled
- The candidate marked outside the expected area
- The candidate left blank responses
- The candidate selected incorrect answers intentionally

These variations were intentionally included to make the dataset **more robust and closer to real-world exam situations**.

---

# Image Acquisition

All test sheets were converted into **image format**, since YOLO models operate on visual data.

Images were collected using:

- Document scanners
- Smartphone cameras
- Standard digital cameras

Different image capture conditions were intentionally used, including:

- Slight rotation of the paper
- Minor perspective distortions
- Different lighting conditions
- Shadows created during scanning or photographing

This diversity helps the model learn to perform well under **real-world conditions**, where input images are rarely perfectly aligned.

---

# Data Validation and Quality Assurance

Before being included in the dataset, each image underwent a **manual verification process**.

The following aspects were checked carefully:

- Image clarity and sharpness
- Visibility of candidate codes
- Visibility of answer areas
- Proper positioning of the exam sheet
- Absence of extreme distortions
- Proper resolution and image quality

After the first verification stage, a **second manual review process** was conducted to ensure that:

- No corrupted images were included
- Annotation errors were avoided
- Dataset structure remained consistent

This two-step verification process ensures that the dataset maintains **high quality and reliability**.

High-quality datasets are extremely important for machine learning models because poor data quality can significantly reduce model performance.

---

# Data Annotation Process

After collecting and verifying the images, the next step was **data annotation**.

Annotation involves labeling specific parts of each image so that the model can learn to detect them.

The following objects were annotated:

- Candidate code area
- Answer bubble locations
- Question areas
- Marked answers

Each annotation was saved using the **YOLO annotation format**, which includes:

- Object class
- Bounding box coordinates
- Image reference

These annotations are essential because they allow the YOLO model to **learn how to detect objects within exam sheet images**.

---

# Dataset Structure

The dataset used in this project follows a structured format commonly used in YOLO training pipelines.

The dataset contains:

- Training images
- Validation images
- Corresponding annotation files

Example structure:
<img width="302" height="259" alt="image" src="https://github.com/user-attachments/assets/5ddf6633-57cc-4750-bcd3-742f40fe1a51" />
---

# Model Training Pipeline

The YOLO model training process follows several steps:

## 1 Dataset Preparation
The collected dataset is cleaned, verified, and structured.

## 2 Data Splitting
The dataset is divided into:

- Training set
- Validation set

This helps the model learn while also allowing performance evaluation.

## 3 Model Configuration
The YOLO configuration files are adjusted to match:

- Number of classes
- Dataset structure
- Training parameters

## 4 Model Training
The model is trained on the dataset using deep learning techniques.

During training, the model learns to:

- Detect answer bubbles
- Identify candidate codes
- Recognize marked answers
- Distinguish filled vs empty responses

## 5 Model Evaluation
After training, the model is evaluated using validation data.

Key performance metrics may include:

- Precision
- Recall
- mAP (Mean Average Precision)

---

# Automated Exam Evaluation

Once the model is trained, the system will be able to process new exam sheet images automatically.

The process includes:

1. Uploading the exam sheet image
2. Running YOLO object detection
3. Detecting candidate code and answers
4. Comparing detected answers with the correct answer key
5. Calculating the final score

---

# Expected Output

The system will generate the final result in the following format:

Example output:

210453 - 17


This allows fast evaluation of large numbers of exam sheets.

---

# Advantages of the System

The proposed system provides several advantages:

- Faster evaluation of entrance exams
- Reduced manual correction workload
- Increased grading accuracy
- Consistent evaluation results
- Scalable solution for large exam datasets
- Reduced human error
- Automated processing of exam sheets

---

# Technologies Used

This project uses the following technologies:

- Python, FastAPI (`yolo-api/`)
- ASP.NET Core (`ML ASP.net service/ExamNumberReader/`)
- Angular (`frontend/`)
- YOLO (You Only Look Once)
- OCR (Tesseract / ONNX for student ID)
- Computer Vision, Image Processing, Deep Learning, Machine Learning

---

# Phase 2

This section provides an in-depth academic discussion regarding dataset robustness, model generalization, and system scalability.

The dataset used in this project has been carefully engineered to simulate real-world exam conditions. One of the most important aspects of machine learning systems is the ability to generalize beyond the training data. In this context, generalization refers to the model’s capability to perform accurately on unseen data.

In practical scenarios, exam sheets are rarely captured under ideal conditions. Therefore, introducing noise, distortions, and irregularities into the dataset significantly improves the robustness of the trained model. These include variations in illumination, slight rotations, perspective transformations, and differences in marking intensity.

Furthermore, the YOLO model architecture allows for real-time object detection, making it suitable for applications where performance and speed are critical. The bounding-box detection approach enables the model to localize relevant features efficiently.

From a system architecture perspective, separating the machine learning logic into a Python API ensures modularity. The .NET backend acts as a communication layer, while Angular provides a user-friendly interface. This separation of concerns ensures maintainability and scalability.

Another important aspect is the evaluation of the system. Metrics such as precision, recall, and mean average precision (mAP) are used to assess the model’s performance. High precision ensures that detected answers are correct, while high recall ensures that most relevant answers are detected.

---

## Current Architecture

The current project structure is divided into the following main parts:

- **Dataset/** – contains exam sheet images and related project material
- **ML ASP.NET service / ExamNumberReader/** – main backend service in ASP.NET Core
- **frontend/** – Angular frontend application
- **yolo-api/** – Python service responsible for detection-related logic

# Exam Grading System

Automatic test evaluation system using YOLO for answer detection and .NET for student ID recognition.

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   Angular Frontend  │────▶│    .NET API         │────▶│   YOLO API          │
│   (Port 4200)       │     │    (Port 5000)      │     │   (Port 8001)       │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
         │                           │                           │
         │                           │                           │
         ▼                           ▼                           ▼
    Upload CSV            Extract Student ID           Detect Marked
    Answer Key            (Tesseract + ONNX)           Answers (YOLO)
```

## Components

### 1. YOLO API (`yolo-api/`)
FastAPI service for detecting marked answers on exam sheets.

**Endpoints:**
- `GET /health` - Health check
- `POST /detect` - Detect answers from single image
- `POST /detect/batch` - Detect answers from multiple images

### 2. .NET API (`ML ASP.net service/`)
ASP.NET Core API for exam processing and grading.

**Endpoints:**
- `POST /api/grading/answer-key` - Upload CSV answer key
- `GET /api/grading/answer-key/current` - Get current answer key
- `POST /api/grading/grade` - Grade single exam
- `POST /api/grading/grade/batch` - Grade multiple exams
- `POST /api/grading/export/csv` - Export results to CSV
- `POST /api/grading/export/excel` - Export results to Excel
- `POST /api/image/extract-number` - Extract 5-digit student ID

### 3. Angular Frontend (`frontend/`)
Modern web interface for exam grading.

**Features:**
- Step-by-step wizard interface
- Drag & drop file upload
- Real-time grading results
- Results table with color-coded answers
- CSV/Excel export

## Quick Start

### Prerequisites
- Python 3.10+
- .NET 9.0 SDK
- Node.js 18+
- YOLO trained model (`best.pt`)
- Tesseract OCR data files

### 1. Start YOLO API

```bash
cd yolo-api
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python run.py
```

The API will be available at `http://localhost:8001`

### 2. Start .NET API

```bash
cd "ML ASP.net service\ExamNumberReader"
dotnet run
```

The API will be available at `http://localhost:5000`

### 3. Start Angular Frontend

```bash
cd frontend
npm install
npm start
```

Open `http://localhost:4200` in your browser

## CSV Answer Key Format

Create a CSV file with question numbers and correct answers:

```csv
1,A
2,B
3,C
4,D
5,A
...
20,B
```

Or simply list answers in order (one per line):

```
A
B
C
D
A
...
```

## Configuration

### YOLO API
Environment variables:
- `YOLO_MODEL_PATH` - Path to trained YOLO model (default: auto-detected)
- `API_HOST` - Host to bind (default: 0.0.0.0)
- `API_PORT` - Port to bind (default: 8001)

### .NET API
`appsettings.json`:
```json
{
  "YoloApi": {
    "BaseUrl": "http://localhost:8001"
  }
}
```

### Angular Frontend
`environment.ts`:
```typescript
export const environment = {
  apiUrl: 'http://localhost:5000/api'
};
```

## Model Training

The YOLO model was trained to detect marked checkboxes. Training scripts are in `student-answer-yolo/student-answer-yolo/scripts/`:

- `train.py` - Train the YOLO model
- `predict.py` - Test predictions
- `grade_students.py` - Complete grading pipeline

### Training run: `student_answer_v2`

Ultralytics YOLO writes validation plots and batch visualizations under `student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/`. The figures below summarize how the detector behaves on the validation set after training (curves are typically shown **per class** and/or **aggregated** depending on YOLO version and settings).

These assets live in [`student_answer_v2`](https://github.com/ErandKurtaliqi/ML_2025-26_GR_14/tree/main/student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2). Images below use **paths relative to the repo root** so GitHub can render them the same way as other files in the tree.

**Why the preview can look “broken”**

1. **Cursor / VS Code “Markdown Preview”** loads `![...](path)` from **your disk**. If the `.png` / `.jpg` files are not in that folder locally (only on GitHub), the preview shows an empty or broken icon. **Fix:** run `git pull`, or copy the images into `student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/`, or open the README on **github.com** after you push—there the images match the repository files.
2. **Do not use** `https://github.com/.../blob/main/...png` inside `![alt](...)`. That URL is an **HTML page**, not the image bytes. For hotlinking outside GitHub you would use `https://raw.githubusercontent.com/<user>/<repo>/<branch>/...` instead; GitHub’s own README still works best with **relative** paths.
3. **Private repository:** anonymous `raw.githubusercontent.com` links often **404** in a preview; relative paths in the README are resolved by GitHub with your session and usually render correctly on the website.

#### Box F1 curve (`BoxF1_curve.png`)

The **F1 score** combines precision and recall into one number. This plot shows **F1 versus confidence threshold**, so you can see at which operating point the detector best balances false positives and false negatives when turning raw boxes into “marked vs empty” decisions.

![Box F1 curve](student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/BoxF1_curve.png)  
*[View file on GitHub](https://github.com/ErandKurtaliqi/ML_2025-26_GR_14/blob/main/student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/BoxF1_curve.png)*

#### Precision–Recall curve (`BoxPR_curve.png`)

The **PR curve** plots precision against recall across thresholds. A curve that stays **high and toward the upper-right** indicates strong ranking of true boxes; the area under this curve is related to **Average Precision (AP)** for the box-detection task.

![Box PR curve](student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/BoxPR_curve.png)  
*[View file on GitHub](https://github.com/ErandKurtaliqi/ML_2025-26_GR_14/blob/main/student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/BoxPR_curve.png)*

#### Precision vs confidence (`BoxP_curve.png`)

This graph shows how **precision changes as the confidence cutoff is raised**. Higher thresholds usually increase precision (fewer weak detections kept) but may drop recall if correct boxes are filtered out.

![Box precision vs confidence](student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/BoxP_curve.png)  
*[View file on GitHub](https://github.com/ErandKurtaliqi/ML_2025-26_GR_14/blob/main/student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/BoxP_curve.png)*

#### Recall vs confidence (`BoxR_curve.png`)

This graph shows how **recall changes with the confidence threshold**. Lower thresholds keep more detections, which often helps recall but can introduce more false positives—use it together with the precision plot to choose a threshold.

![Box recall vs confidence](student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/BoxR_curve.png)  
*[View file on GitHub](https://github.com/ErandKurtaliqi/ML_2025-26_GR_14/blob/main/student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/BoxR_curve.png)*

#### Confusion matrix (`confusion_matrix.png`)

The **confusion matrix** counts predictions versus ground-truth classes (e.g., `empty_box` vs `marked_box`). Off-diagonal cells show which classes are confused with each other and guide targeted fixes (annotation quality, class balance, or augmentation).

![Confusion matrix](student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/confusion_matrix.png)  
*[View file on GitHub](https://github.com/ErandKurtaliqi/ML_2025-26_GR_14/blob/main/student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/confusion_matrix.png)*

#### Normalized confusion matrix (`confusion_matrix_normalized.png`)

The same information as the confusion matrix, but **normalized per true class** (rows or columns depending on the tool), so you can compare error rates **between classes** even when class counts differ.

![Normalized confusion matrix](student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/confusion_matrix_normalized.png)  
*[View file on GitHub](https://github.com/ErandKurtaliqi/ML_2025-26_GR_14/blob/main/student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/confusion_matrix_normalized.png)*

#### Label distribution (`labels.jpg`)

Ultralytics generates a **label overview** (class frequency, box sizes, and positions in image coordinates). It helps verify **annotation balance** and whether boxes are concentrated in certain regions of the sheet, which affects learning and evaluation.

![Label distribution](student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/labels.jpg)  
*[View file on GitHub](https://github.com/ErandKurtaliqi/ML_2025-26_GR_14/blob/main/student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/labels.jpg)*

#### Training results summary (`results.png`)

`results.png` is a **multi-panel summary** of the run: training and validation losses, and core detection metrics (such as precision, recall, and mAP) **over epochs**. It is the fastest way to spot overfitting (train improves while validation stalls) or unstable training.

![Training results summary](student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/results.png)  
*[View file on GitHub](https://github.com/ErandKurtaliqi/ML_2025-26_GR_14/blob/main/student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/results.png)*

#### Training batch sample (`train_batch780.jpg`)

A **mosaic of training batches** (often heavily augmented) at a given step—here batch **780**. It confirms that augmentations look reasonable (geometry, color, mosaic layout) and that labels still align with transformed images.

![Training batch example](student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/train_batch780.jpg)  
*[View file on GitHub](https://github.com/ErandKurtaliqi/ML_2025-26_GR_14/blob/main/student-answer-yolo/student-answer-yolo/runs/detect/runs/student_answer_v2/train_batch780.jpg)*

## Project Structure

```
ML-Web/
├── frontend/                    # Angular web application
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   └── models/
│   │   └── styles.scss
│   └── package.json
├── ML ASP.net service/          # .NET Core API
│   └── ExamNumberReader/
│       ├── Controllers/
│       ├── Services/
│       ├── Models/
│       └── Program.cs
├── yolo-api/                    # FastAPI YOLO service
│   ├── app/
│   │   ├── main.py
│   │   ├── detection_service.py
│   │   └── models.py
│   └── requirements.txt
└── student-answer-yolo/         # YOLO training & scripts
    └── student-answer-yolo/
        ├── scripts/
        ├── dataset/
        ├── runs/
        └── data.yaml
```

## API Documentation

### Swagger UI
- .NET API: http://localhost:5000
- YOLO API: http://localhost:8001/docs

## Troubleshooting

### YOLO model not loading
Ensure the model file exists at the configured path. Check logs for the actual path being used.

### OCR not working
Make sure Tesseract data files are in the `tessdata` folder and the MNIST ONNX model is in the `models` folder.

### CORS errors
Both APIs are configured to allow all origins. If you still see CORS errors, check the browser console for more details for debug.

## License

This project is for educational purposes.

---

## Overview of Phase 2

Phase 2 represents the **core machine learning stage** of the project, where the system transitions from basic architectural design and preprocessing logic into a fully functional **intelligent detection pipeline**.

The primary focus of this phase is the **training, validation, and optimization of a YOLO-based object detection model**, designed specifically for analyzing exam sheets.

Unlike Phase 1, which focuses on system structure and data flow, this phase emphasizes:

- Model accuracy  
- Detection reliability  
- Real-world robustness  
- Scalability for production environments  

The trained model aims to detect and interpret key elements of exam sheets, including:

- Candidate code area  
- Answer bubbles  
- Marked answers  
- Question-related regions  

---

## Machine Learning Approach

The project leverages the power of **YOLO (You Only Look Once)**, a state-of-the-art real-time object detection algorithm.

YOLO is chosen because of its:

- High detection speed  
- Strong accuracy for object localization  
- Ability to detect multiple classes in a single pass  
- Suitability for real-time systems  

The model processes exam sheet images and produces:

- Bounding boxes  
- Class labels  
- Confidence scores  

These outputs are then used for further processing, including **answer recognition and grading logic**.

---

## Main activities of Phase 2

Dataset size, diversity, capture conditions, annotation policy (YOLO format), and quality checks are documented **once** in [Phase 1](#phase-1) (*Dataset Creation* through *Data Annotation Process*). Training runs, validation plots, and exported weights appear under [Model training](#model-training) and [Training process (YOLO)](#training-process-yolo). The live grading stack (`yolo-api/`, .NET, Angular) is described in [Exam Grading System](#exam-grading-system).

---

## Expected Goal of Phase 2

At the completion of this phase, the system should include a **fully trained and optimized YOLO model** capable of:

- Accurately detecting all relevant exam elements  
- Handling real-world variations in marking  
- Supporting automated grading workflows  

This will significantly improve:

- Accuracy  
- Reliability  
- Efficiency  

---

# Training Process (YOLO)

## Image Description

This image represents a sample from the dataset used to train the **YOLO model** for detecting student answers in multiple-choice tests.

The test originates from the **Faculty of Electrical and Computer Engineering** and is used as an entrance exam at the **Bachelor level**.

The image contains:

- A **grid of answer options (A, B, C, D)** for each question  
- Approximately **20 multiple-choice questions**  
- Some boxes are **marked by the student (with X)**  
---

## Labeling Process (LabelImg)

The dataset was created using the tool:

**LabelImg**

Each answer option (box) is manually annotated using **bounding boxes**.

### Classes Used

- **`marked_box`** → box selected by the student  
- **`empty_box`** → unselected (empty) box  

### Methodology

- For every answer option (A, B, C, D) in each question:
  - a **bounding box** is created
- Each bounding box is classified as:
  - marked  
  - empty  

In the image:

- Green rectangles represent labeled bounding boxes  
- The right-side panel shows all labels (`marked_box`, `empty_box`)

---

## Annotation Format (YOLO Format)

Each image has a corresponding `.txt` file in YOLO format:

```
<class_id> <x_center> <y_center> <width> <height>
```
<img width="1600" height="861" alt="IMG-20260322-WA0000" src="https://github.com/user-attachments/assets/2241dc25-3b6d-4f28-8752-798777158461" />

### Explanation:

- **class_id = 0** → `empty_box`  
- **class_id = 1** → `marked_box`  

- Coordinates are:
  - **normalized (0–1)**
  - relative to image dimensions

---

## Training Objective

The YOLO model is trained to:

- Detect every answer box in the test  
- Classify whether it is:
  - marked
  - or empty  
- Enable **automatic answer evaluation**  
- Automate the test correction process  

---

## Model Prediction (Inference)

This image shows the output of the trained **YOLO model** during the **prediction (inference) phase**.

After training, the model is used to analyze unseen test images and automatically detect and classify answer boxes.

---

## What is shown in the image

- A real student test from **FIEK (Bachelor level)**
- The trained YOLO model applied on the image
- Blue bounding boxes around detected answer options
- Each box is labeled with:
  - predicted class (`empty_box` or `marked_box`)
  - confidence score (e.g., 0.75, 0.82)

---

## Model Behavior

During inference, the YOLO model:

- Detects all answer boxes in the test
- Classifies each box as:
  - **`empty_box`** → not selected
  - **`marked_box`** → selected by the student
- Assigns a **confidence score** to each prediction

Example label:
```
empty_box 0.81
```

This means:
- the model predicts the box is empty
- with 81% confidence

---

## Prediction Script

The prediction is executed using a custom script:

```
python scripts/predict.py
```

This script:

- Loads the trained YOLO model
- Runs inference on test images
- Draws bounding boxes and labels
- Saves the output in:

```
runs/detect/predict/
```

---

## Output Interpretation

- Blue rectangles → detected answer boxes  
- Labels → predicted class + confidence  
- High confidence → more reliable prediction  

This output is used for:

- Identifying selected answers  
- Calculating test scores automatically  
- Fully automating the evaluation process  

---
<img width="1294" height="805" alt="IMG-20260322-WA0001" src="https://github.com/user-attachments/assets/49ac038a-75d6-4785-8b71-294efcb5a2f8" />

## Importance in the Project

This step demonstrates the **real-world application** of the trained model:

> Automatically reading and evaluating student test sheets without human intervention.

It validates that the model can:

- Generalize to new test images  
- Detect and classify answers correctly  
- Support automated grading systems  

---

---

## Role in the Project

This dataset is part of the project:

> **Automated Test Evaluation using Computer Vision (YOLO)**

The goal is to:

- Eliminate manual grading  
- Improve evaluation accuracy  
- Automatically process student test sheets at **FECE (Bachelor level)**  

---

## Precision and Detection Accuracy

This image highlights a detailed view of the labeling process and is particularly useful for understanding the **precision requirements** of the YOLO model.

<img width="1500" height="906" alt="IMG-20260322-WA0005" src="https://github.com/user-attachments/assets/328f3a84-906a-445e-b962-4c6e44176845" />

---

## Why Precision Matters

In this project, precision is critical because:

- Each question has **multiple answer options (A, B, C, D)**
- Only **one box should be marked per question**
- Even a small detection error can lead to:
  - incorrect answer interpretation
  - wrong final score

---

## Definition of Precision

**Precision** measures how many of the detected boxes are actually correct.

```
Precision = True Positives / (True Positives + False Positives)
```

- **True Positive (TP)** → correctly detected marked box  
- **False Positive (FP)** → model detects a box as marked when it is actually empty  

---

## Challenges in This Dataset

From the image, we can observe several challenges:

### 1. Close Proximity of Boxes
- Answer boxes are very close to each other  
- The model must avoid detecting multiple boxes as one  

### 2. Similar Visual Patterns
- Empty and marked boxes have similar structure  
- The only difference is the presence of an **X mark**

### 3. Handwritten Variations
- The "X" marks are handwritten  
- They vary in:
  - thickness
  - angle
  - position  

This increases the difficulty of classification.

---

## Potential Errors

Without high precision, the model may:

- Detect an **empty box as marked** (False Positive)
- Detect **multiple answers for one question**
- Miss a marked box entirely (False Negative)

---

## Improving Precision

To achieve high precision, the following strategies were applied:

- **Accurate bounding box labeling** using LabelImg  
- Clean dataset with correct annotations  
- Data augmentation (rotation, brightness, noise)  
- Fine-tuning YOLO model parameters  
- Validation on unseen data  

---

## Expected Outcome

A well-trained model should:

- Detect only the **correct answer boxes**
- Avoid false detections  
- Maintain high confidence scores for correct predictions  

> High precision ensures that the automated grading system is reliable and trustworthy.

---

## Identification Code

### Identification Code (ID): Each digit of the 5-digit code (e.g., 00216) is labeled individually as a specific class (digit_0, digit_1, etc.). This allows the model to recognize and read each student's unique ID.

### Table Structure: Localizing the answer table to enable the accurate mapping of rows (1-20) to columns (a, b, c, d).

## Main Classes

digit_0 - digit_9: Individual digits of the 5-digit identification code.

<img width="1600" height="863" alt="IMG-20260328-WA0000" src="https://github.com/user-attachments/assets/1054b964-022e-41d9-b675-127c65b7697d" />

---

## Model Training Output Description
For this second phase of the dataset, the trained model generates the following results based on images like this one, applying advanced localization and recognition techniques.

### Code (ID) Detection and Recognition
This model goes beyond just detecting individual digits; it identifies the entire code region and reads it as a single entity:

### Main Bounding Box: Identifies the large blue frame that encompasses the area where the full code is expected to be written.

### Digit Segmentation: Segments and detects each digit individually using smaller yellow boxes.

### Text Recognition (OCR): Combines the detected digits into a single 5-digit code. For example, in this image, the model accurately reads the code 12780 and outputs this information (e.g., in a JSON or CSV file) as a single string value instead of five separate digits.

### Full Answer Table Detection
Unlike detecting individual boxes, this model localizes the entire structure of the table:

### Table Bounding Box: Defines a large green frame that encompasses the entire answer table.

### Matrix Mapping: This allows for precise software-level mapping of every box (e.g., "Row 1, Column c") without needing to treat every single box as a separate class. This significantly increases efficiency and accuracy for mass data extraction.

### Final Structured Output
The final output from the model for such an image can be a JSON file structured as follows:

Code: "12780"

Response_Matrix_Location: [xmin, ymin, xmax, ymax]

Answer_1: "c"

Answer_2: "c"

...

Answer_20: "c"

--<img width="883" height="543" alt="Screenshot 2026-04-19 095416" src="https://github.com/user-attachments/assets/94dea6ef-70f6-41a1-80a2-35a3ee6d86c6" />

---

## Optimization: Automated Code Extraction & OCR
To maximize processing speed and ensure high-level accuracy, we have implemented an optimized workflow for identifying the student’s 5-digit identification code. Instead of processing the entire document, the system focuses directly on the handwritten input.

### Automated Cropping Process
The system utilizes a specialized preprocessing script that automatically crops the specific region where the student writes their code.

<img width="1251" height="539" alt="IMG-20260329-WA0008" src="https://github.com/user-attachments/assets/5e618467-1e89-46b2-a7a5-721bb8880e0f" />

### Targeted Focus: By isolating this area from the rest of the document, we eliminate background noise and potential interference from other text or table lines.

### Performance Boost: This automated cropping significantly reduces the computational load on the model, allowing for near-instantaneous processing of large batches of exam papers.

### Advanced OCR Integration
Once the region is isolated, the system applies Optical Character Recognition (OCR) to bridge the gap between handwritten ink and digital data.

<img width="1239" height="532" alt="IMG-20260329-WA0009" src="https://github.com/user-attachments/assets/2222eb7b-5935-4d9a-ac53-acf79da2cb4e" />

### Format Conversion: The OCR engine analyzes the handwritten strokes within the cropped image and converts them directly into a clean digital string.

<img width="745" height="383" alt="IMG-20260329-WA0006" src="https://github.com/user-attachments/assets/6dfb96e4-c052-4a1d-8181-5c79532c489d" />

<img width="811" height="379" alt="IMG-20260329-WA0004" src="https://github.com/user-attachments/assets/678cf5fb-6c18-4c81-b961-d73968c77964" />

<img width="1122" height="524" alt="IMG-20260329-WA0003" src="https://github.com/user-attachments/assets/52d038ba-5ba0-408d-a118-fa12364154d6" />

### Data Integrity: This method ensures that the unique 5-digit code (e.g., 12780) is captured exactly as written, facilitating a seamless transition from a physical paper to a structured database entry (JSON/CSV).

### Key Benefits
Speed: Drastically reduces the time required for student identification.

Accuracy: Minimizes human error by automating the transcription of handwriting.

Scalability: Designed to handle thousands of exam entries efficiently, making it an ideal solution for large-scale academic institutions.

---

## Full Pipeline

1. Capture test images (scan / photo)  
2. Manual labeling using **LabelImg**  
3. Dataset organization (`train`, `val`)  
4. YOLO model training  
5. Inference (detection & classification)  
6. Automatic result calculation  
---

## Challenges Faced

During this phase, several challenges were identified:

- Variability in answer marking styles  
- Poor image quality in some samples  
- Overlapping or unclear markings  
- Dataset size limitations  
- Balancing precision vs recall  

These challenges are addressed through:

- Data augmentation  
- Improved annotation quality  
- Model tuning  

---

# Future improvements

Planned future enhancements include:

- Expanding the dataset significantly  
- Improving model accuracy through tuning  
- Comparing different YOLO versions (YOLOv5, YOLOv8, etc.)  
- Experimenting with different architectures  
- Supporting additional exam formats  
- Deploying on scalable cloud infrastructure  
- Deeper integration with the web platform  

Phase 2 is a **critical milestone** in the project, transforming it from a conceptual system into an **intelligent, automated solution**.

The successful implementation of this phase lays the foundation for:

- Fully automated exam grading  
- Real-time processing capabilities  
- Scalable deployment in educational environments  

---

# Phase 3

Phase 3 focuses on improving the final system performance after the initial YOLO implementation and integration were completed. In this phase, the main goal was to make the identification process faster, more reliable, and more useful for the admission workflow after exam evaluation.

The work in this phase includes:

- Retraining the YOLO model for improved **5-digit student code detection**
- Using **LabelImg** for annotation and dataset preparation
- Reducing test processing time through a more efficient detection workflow
- Implementing CSV-based priority lists for student direction allocation
- Separating students by minority and non-minority groups for each study direction

---

## Retraining the 5-Digit Code Detection Model

During the previous phase, the system was able to detect and process exam sheets using YOLO. However, the detection of the student's **5-digit identification code** required further optimization because this code is one of the most important parts of the automated evaluation process.

For this reason, the code detection component was retrained with a more focused dataset and improved annotations. The retraining process was designed to help the model detect the 5-digit code area more accurately and reduce unnecessary processing around parts of the test that are not relevant for student identification.

This improvement is important because the 5-digit code connects the scanned exam paper with the correct student record. If the code is detected faster and more accurately, the entire grading and result generation process becomes more reliable.

---

## LabelImg Annotation Tool

For the retraining process, **LabelImg** was used as the main annotation tool.

LabelImg is a graphical image annotation tool that allows users to manually draw bounding boxes around objects in images and assign class labels to them. It is commonly used in object detection projects because it can export annotations in the **YOLO format**, which is directly compatible with YOLO training pipelines.

In this project, LabelImg was used to label the regions related to the **5-digit student code**. This made it possible to create a more accurate training dataset for the model and helped YOLO learn the exact position and structure of the code field on the exam sheet.

LabelImg was useful for YOLO because:

- It supports bounding box annotation
- It exports labels in YOLO-compatible format
- It helps maintain consistent class labeling
- It allows manual verification of each annotated image
- It improves dataset quality before retraining

By using LabelImg, the retrained model received cleaner and more focused annotations, which directly contributed to better detection performance.

---

## Processing Time Improvement

Before the retraining and optimization in Phase 3, the processing time for a test was approximately **1 minute and 13 seconds**.

After improving the retraining workflow and focusing the model more efficiently on the required detection area, the processing time was reduced to approximately **17 seconds** per test.

This improvement was achieved because the retrained model became more efficient at detecting the relevant code area and required less unnecessary processing. As a result, the system can evaluate test images faster while still maintaining reliable detection accuracy.

The reduction from **1 minute and 13 seconds** to **17 seconds** is significant for real-world usage, especially when the system needs to process a large number of entrance exam sheets.

---

## CSV Priority List Implementation

In addition to model improvement, Phase 3 also includes the implementation of a **CSV file-based priority system** for student direction allocation.

Each student may have a list of preferred study directions. If a student cannot be accepted into the first selected direction, the system checks the next available options based on the student's priority list. This allows the allocation process to be more organized and closer to the real admission process.

The CSV file contains information such as:

- Student identification code
- Student priority list
- Preferred study directions
- Available alternatives if the first direction is not possible
- Allocation status based on available places

The system uses the CSV file to determine which direction a student should be assigned to, while also considering the number of available places in each direction.

---

## Allocation Based on Available Places

The allocation logic takes into account that each study direction has a limited number of available places. Some of these places may also be reserved for minority groups, depending on the admission rules.

For this reason, the system separates the allocation process into:

- Minority group places
- Non-minority group places

This means that the student is not only evaluated based on score and preferences, but also according to the available capacity for the relevant group.

If the student cannot be placed in the first preferred direction, the system continues checking the next options from the CSV priority list until an available direction is found.

---

## CSV Output per Study Direction

For each study direction, the system generates or displays CSV-based results that separate students into the correct admission groups.

The output for every direction includes:

- Students allocated through the minority group quota
- Students allocated through the non-minority group quota
- Students who could not be assigned to that direction
- Alternative options based on the student's priority list

This CSV structure makes the result easier to review, filter, and validate. It also helps the admission process remain transparent because each student allocation can be traced back to the student's score, priority list, available places, and group category.

Through this implementation, Phase 3 extends the project from exam detection and grading into a more complete admission support system.

---

# Conclusion

This project demonstrates how **modern computer vision techniques** can be applied to solve real-world problems in educational institutions.

By leveraging **YOLO object detection and machine learning**, it is possible to develop an automated system capable of evaluating entrance exams efficiently and accurately. In conclusion, this project combines multiple disciplines including software engineering and system integration to deliver a practical and scalable solution.

Such systems can significantly improve the **efficiency, reliability, and scalability of exam evaluation processes**.

---

# Credits

**Dataset source:** Custom dataset created for this project.

### Professors

Prof. Dr. Lele Ahmedi  
Prof. Asst. Dr. Mërgim H. Hoti  

### Students

Altin Pajaziti  
Ardi Bërdyna  
Erand Kurtaliqi  

**Date:** February 2026
