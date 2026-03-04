<div align="center">

<img src="dataset/assets/logo_up.png" alt="University of Prishtina" width="150"/>

# University of Prishtina

## Faculty of Electrical and Computer Engineering

**Study Program:** Computer and Software Engineering – Master  
**Course:** Machine Learning  
**Group:** 14  

# Project Topic

## Training and Application of the YOLO Model for Automatic Detection and Evaluation of Entrance Exams at FIEK

</div>

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

# Dataset Creation

A **custom dataset** was created specifically for training the YOLO model used in this project.

The dataset contains approximately **100 exam sheet samples**, representing different ways in which candidates may fill out their tests.

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
-- QETU KEMI ME VENDOS FOTO NGA STRUKTURA E RENDITJEVE TE FILES


Each image has a corresponding `.txt` file that contains the object annotations.

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

# Conclusion

This project demonstrates how **modern computer vision techniques** can be applied to solve real-world problems in educational institutions.

By leveraging **YOLO object detection and machine learning**, it is possible to develop an automated system capable of evaluating entrance exams efficiently and accurately.

Such systems can significantly improve the **efficiency, reliability, and scalability of exam evaluation processes**.

---

**Dataset Source:** Custom Dataset Created for This Project  

### Professors
Prof. Dr. Lele Ahmeti  
Prof. Dr. Mërgim Hoti  

**Date:** February 2026