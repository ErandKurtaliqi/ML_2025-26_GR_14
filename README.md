<div align="center">

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/University_of_Prishtina_logo.svg/1200px-University_of_Prishtina_logo.svg.png" width="150" alt="University Logo" />

# University of Prishtina

## Faculty of Electrical and Computer Engineering

**Study Program:** Computer and Software Engineering – Master  
**Course:** Machine Learning  
**Group:** 14  

# Project Topic

## Training and Application of the YOLO Model for Automatic Detection and Evaluation of Entrance Exams at FIEK

</div>

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

The project is organized into tree main phases:

- **Phase 1 – Current System Implementation**
- **Phase 2 – YOLO Model Training and Improvement**
- **Phase 3 – Improvement in model**
  
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

- Python
- YOLO (You Only Look Once)
- Computer Vision
- Image Processing
- Deep Learning
- Machine Learning

---

# Future Improvements

Future improvements may include:

- Increasing the dataset size
- Improving model accuracy
- Integrating the system with a web platform
- Supporting different exam formats
- Real-time exam sheet analysis
- Integration with university exam systems

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

---

## Backend – ASP.NET Core Service

The ASP.NET Core backend is responsible for the main business logic of the system.

Its responsibilities include:

- Receiving exam sheet images
- Managing grading logic
- Calling OCR and detection services
- Comparing detected answers with the answer key
- Exporting results
- Exposing API endpoints for the frontend

The backend includes:

- **Controllers** for API endpoints
- **Models** for data structures
- **Services** for grading, OCR, export, and answer key processing

---

## Python Detection API

A dedicated Python API is included in the system architecture to support machine learning and detection logic.

This module contains:

- Configuration files
- Detection service logic
- Model-related code
- Python entry points for execution

The Python service is designed to be modular, so it can later be extended with a trained YOLO model in Phase 2.

---

## Frontend – Angular Application

The frontend provides the user interface of the system.

Its main responsibilities are:

- Uploading exam sheet images
- Sending requests to the backend
- Displaying extracted results
- Presenting grading information in a user-friendly format

This layer ensures easier interaction with the automated grading system.

---

## Current Workflow

The current system workflow is as follows:

1. The user uploads an exam sheet image
2. The frontend sends the image to the backend
3. The backend processes the request
4. OCR / detection logic is executed
5. The candidate code is extracted
6. Answers are detected and interpreted
7. The answers are compared with the correct answer key
8. The final score is calculated
9. The result is returned to the frontend

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

## Main Activities of Phase 2

The second phase consists of multiple structured steps:

### 1. Dataset Preparation
- Collecting real exam sheets
- Ensuring diversity in format and marking styles
- Organizing images into structured datasets

### 2. Image Verification
- Checking image quality
- Removing corrupted or unusable samples
- Standardizing image formats and resolutions

### 3. Data Annotation
- Labeling all relevant regions using bounding boxes
- Ensuring annotation consistency
- Exporting labels in YOLO format

### 4. Dataset Splitting
- Training set (≈70–80%)
- Validation set (≈10–20%)
- Test set (≈10%)

### 5. YOLO Configuration
- Defining class labels
- Configuring model architecture
- Setting training parameters (epochs, batch size, learning rate)

### 6. Model Training
- Training the YOLO model on annotated data
- Monitoring loss and accuracy metrics
- Adjusting hyperparameters when necessary

### 7. Model Validation
- Evaluating model on validation dataset
- Detecting overfitting or underfitting
- Fine-tuning model performance

### 8. Performance Evaluation
- Measuring:
  - Precision  
  - Recall  
  - mAP (mean Average Precision)  
- Analyzing detection errors

### 9. System Integration
- Integrating the trained model into backend (Python / API)
- Connecting results with ASP.NET Core logic
- Preparing outputs for Angular frontend

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

> A more detailed technical breakdown will be included in future README updates.

---

## Dataset

A custom dataset was created specifically for this project to simulate real exam scenarios.

### Dataset Characteristics

- ~100 exam sheet samples  
- Multiple marking styles and conditions  

### Included Scenarios

- Fully completed sheets  
- Partially completed sheets  
- Blank answers  
- Multiple marked answers  
- Light and strong markings  
- Crossed-out answers  
- Changed responses  
- Slight misalignment of markings  

### Image Sources

Images were collected using:

- Document scanners  
- Smartphone cameras  
- Standard digital cameras  

This diversity ensures the model learns to handle **real-world noise and variability**.

---

## Data Annotation

Annotation is a critical part of this phase.

### Annotated Elements

- Candidate code area  
- Answer bubble locations  
- Marked answers  
- Question regions  

### Annotation Format

All annotations follow the **YOLO format**, where each object is defined by:
<class_id> <x_center> <y_center> <width> <height>


### Challenges in Annotation

- Ensuring consistency across samples  
- Handling ambiguous markings  
- Labeling overlapping regions  

---

## Technologies Used

This project integrates multiple technologies across different layers:

### Backend
- ASP.NET Core (API & business logic)

### Frontend
- Angular (UI and visualization)

### AI / Processing
- Python  
- YOLO  
- OCR (for candidate code extraction)  

### Core Domains
- Machine Learning  
- Computer Vision  
- Image Processing  

---

## Advantages of the Proposed System

The system provides several key benefits:

- Faster exam evaluation  
- Reduced manual workload  
- Increased grading consistency  
- High scalability  
- Reduced human error  
- Automated result generation  

Additionally, the system enables **standardized evaluation**, which is difficult to achieve manually.

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

## Future Improvements

Planned future enhancements include:

- 📂 Expanding the dataset significantly  
- 🎯 Improving model accuracy through tuning  
- 🔄 Comparing different YOLO versions (YOLOv5, YOLOv8, etc.)  
- 🧪 Experimenting with different architectures  
- 📝 Supporting additional exam formats  
- ☁️ Deploying on scalable cloud infrastructure  
- 🔗 Deeper integration with the web platform  

Phase 2 is a **critical milestone** in the project, transforming it from a conceptual system into an **intelligent, automated solution**.

The successful implementation of this phase lays the foundation for:

- Fully automated exam grading  
- Real-time processing capabilities  
- Scalable deployment in educational environments  

---

# Conclusion

This project demonstrates how **modern computer vision techniques** can be applied to solve real-world problems in educational institutions.

By leveraging **YOLO object detection and machine learning**, it is possible to develop an automated system capable of evaluating entrance exams efficiently and accurately. In conclusion, this project combines multiple disciplines including software engineering and system integration to deliver a practical and scalable solution.

Such systems can significantly improve the **efficiency, reliability, and scalability of exam evaluation processes**.

---
**Dataset Source:** Custom Dataset Created for This Project  

### Professors
Prof. Dr. Lele Ahmeti  
Prof. Dr. Mërgim Hoti  

### Students
Altin Pajaziti  
Ardi Bërdyna  
Erand Kurtaliqi  


**Date:** February 2026
