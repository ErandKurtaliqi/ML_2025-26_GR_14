import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { GradingService } from './services/grading.service';
import { 
  AnswerKey, 
  GradingResult, 
  AppState,
  FullPipelineResult,
  YoloDetectionResponse,
  OcrResponse,
  ComparisonResponse
} from './models/grading.models';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="app" [class.dark-mode]="false">
      <!-- Header -->
      <header class="header">
        <div class="header-glow"></div>
        <div class="container header-content">
          <div class="logo-section">
            <div class="logo-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 11l3 3L22 4"/>
                <path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/>
              </svg>
            </div>
            <div>
              <h1 class="logo">Exam Grading System</h1>
              <p class="tagline">AI-Powered Answer Detection & Evaluation</p>
            </div>
          </div>
          <div class="header-right">
            <div class="status-pill" [class.online]="true">
              <span class="status-dot"></span>
              System Online
            </div>
          </div>
        </div>
      </header>

      <main class="main">
        <div class="container">
          <!-- Progress Steps -->
          <div class="steps-wrapper">
            <div class="steps">
              <div class="step" [class.active]="currentStep >= 1" [class.done]="currentStep > 1" (click)="currentStep > 1 ? currentStep = 1 : null">
                <div class="step-icon">
                  <svg *ngIf="currentStep <= 1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6"/></svg>
                  <svg *ngIf="currentStep > 1" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>
                </div>
                <div class="step-text">
                  <span class="step-label">Step 1</span>
                  <span class="step-title">Answer Key</span>
                </div>
              </div>
              <div class="step-connector" [class.active]="currentStep > 1">
                <div class="connector-fill"></div>
              </div>
              <div class="step" [class.active]="currentStep >= 2" [class.done]="currentStep > 2" (click)="currentStep > 2 ? currentStep = 2 : null">
                <div class="step-icon">
                  <svg *ngIf="currentStep <= 2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
                  <svg *ngIf="currentStep > 2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>
                </div>
                <div class="step-text">
                  <span class="step-label">Step 2</span>
                  <span class="step-title">Upload Exams</span>
                </div>
              </div>
              <div class="step-connector" [class.active]="currentStep > 2">
                <div class="connector-fill"></div>
              </div>
              <div class="step" [class.active]="currentStep >= 3">
                <div class="step-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>
                </div>
                <div class="step-text">
                  <span class="step-label">Step 3</span>
                  <span class="step-title">Results</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 1: Answer Key -->
          <section class="card animate-in" *ngIf="currentStep === 1">
            <div class="card-glow"></div>
            <div class="card-header">
              <div class="card-title-group">
                <div class="card-icon blue">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/></svg>
                </div>
                <div>
                  <h2>Upload or Build Answer Key</h2>
                  <p>Import CSV or manually select answers for all 20 questions</p>
                </div>
              </div>
            </div>

            <div class="template-banner">
              <div class="template-left">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
                <div>
                  <strong>Need a template?</strong>
                  <span>Download a sample CSV to see the expected format</span>
                </div>
              </div>
              <button class="btn btn-ghost" (click)="downloadTemplate()">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><path d="M7 10l5 5 5-5M12 15V3"/></svg>
                Download Template
              </button>
            </div>

            <div class="manual-key-card">
              <div class="manual-key-header">
                <strong>Manual Answer Key</strong>
                <span>Select A/B/C/D for each question</span>
              </div>

              <div class="manual-key-grid">
                <div class="manual-key-row" *ngFor="let q of questionNumbers">
                  <div class="manual-key-q">Q{{ q }}</div>
                  <div class="manual-key-options">
                    <button
                      *ngFor="let opt of answerOptions"
                      type="button"
                      class="manual-opt"
                      [class.active]="manualAnswers[q] === opt"
                      (click)="setManualAnswer(q, opt)">
                      {{ opt }}
                    </button>
                  </div>
                </div>
              </div>

              <div class="manual-key-actions">
                <button class="btn btn-ghost" type="button" (click)="clearManualAnswers()">Clear Manual Key</button>
                <button class="btn btn-outline" type="button" (click)="saveManualAnswerKey()" [disabled]="!isManualKeyComplete() || state === 'uploading'">
                  Use Manual Key
                </button>
              </div>
            </div>

            <div class="drop-zone" 
                 [class.dragover]="isDragging"
                 [class.uploaded]="currentAnswerKey"
                 (dragover)="onDragOver($event)"
                 (dragleave)="onDragLeave($event)"
                 (drop)="onDropAnswerKey($event)"
                 (click)="answerKeyInput.click()">
              <input type="file" #answerKeyInput accept=".csv,.txt" (change)="onAnswerKeySelected($event)" hidden>
              
              <div *ngIf="!currentAnswerKey" class="drop-zone-idle">
                <div class="drop-icon-wrap">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><path d="M17 8l-5-5-5 5M12 3v12"/></svg>
                </div>
                <p class="drop-title">Drag & drop your CSV file here</p>
                <p class="drop-sub">or click to browse files</p>
              </div>

              <div *ngIf="currentAnswerKey" class="drop-zone-success">
                <div class="success-icon-wrap">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg>
                </div>
                <div class="success-info">
                  <strong>{{ currentAnswerKey.name }}</strong>
                  <span>{{ getAnswerCount(currentAnswerKey) }} answers loaded successfully</span>
                </div>
              </div>
            </div>

            <div class="card-actions" *ngIf="currentAnswerKey">
              <button class="btn btn-ghost" (click)="answerKeyInput.click()">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 4v6h6M23 20v-6h-6"/><path d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 013.51 15"/></svg>
                Replace File
              </button>
              <button class="btn btn-primary" (click)="goToNextStep()">
                Continue
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
              </button>
            </div>
          </section>

          <!-- Step 2: Upload Exams -->
          <section class="card animate-in" *ngIf="currentStep === 2">
            <div class="card-glow"></div>
            <div class="card-header">
              <div class="card-title-group">
                <div class="card-icon violet">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
                </div>
                <div>
                  <h2>Upload Exam Images</h2>
                  <p>Upload scanned answer sheets for AI-powered grading</p>
                </div>
              </div>
              <button class="btn btn-ghost" (click)="currentStep = 1">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
                Back
              </button>
            </div>

            <div class="active-key-badge" *ngIf="currentAnswerKey">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
              <span>Using: <strong>{{ currentAnswerKey.name }}</strong> ({{ getAnswerCount(currentAnswerKey) }} questions)</span>
            </div>

            <div class="threshold-card">
              <div class="threshold-copy">
                <strong>Passing Threshold</strong>
                <span>Students with a score greater than this value pass.</span>
              </div>
              <label class="threshold-control">
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="1"
                  [(ngModel)]="passThreshold"
                  (ngModelChange)="normalizePassThreshold()"
                  aria-label="Passing threshold percentage">
                <span>%</span>
              </label>
            </div>

            <div class="drop-zone large" 
                 [class.dragover]="isDragging"
                 (dragover)="onDragOver($event)"
                 (dragleave)="onDragLeave($event)"
                 (drop)="onDropExams($event)"
                 (click)="examInput.click()">
              <input type="file" #examInput accept="image/*" multiple (change)="onExamsSelected($event)" hidden>
              <div class="drop-zone-idle">
                <div class="drop-icon-wrap">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
                </div>
                <p class="drop-title">Drag & drop exam images here</p>
                <p class="drop-sub">or click to browse &bull; JPG, PNG, TIFF supported</p>
              </div>
            </div>

            <div class="file-list" *ngIf="selectedExamFiles.length > 0">
              <div class="file-list-header">
                <span class="file-count">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M13 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V9z"/><path d="M13 2v7h7"/></svg>
                  {{ selectedExamFiles.length }} file{{ selectedExamFiles.length > 1 ? 's' : '' }} selected
                </span>
                <button class="btn btn-ghost danger" (click)="clearFiles()">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                  Clear All
                </button>
              </div>
              <div class="file-items-scroll">
                <div class="file-row" *ngFor="let file of selectedExamFiles; let i = index">
                  <div class="file-thumb">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
                  </div>
                  <span class="file-name">{{ file.name }}</span>
                  <span class="file-size">{{ formatFileSize(file.size) }}</span>
                  <button class="btn-remove" (click)="removeFile(i)" title="Remove">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
                  </button>
                </div>
              </div>
            </div>

            <div class="card-actions" *ngIf="selectedExamFiles.length > 0">
              <span class="time-estimate">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
                Est. ~{{ selectedExamFiles.length * 3 }}s
              </span>
              <button class="btn btn-primary btn-lg" (click)="startGrading()" [disabled]="state === 'grading'">
                <span *ngIf="state !== 'grading'">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>
                  Start Grading
                </span>
                <span *ngIf="state === 'grading'" class="loading-state">
                  <span class="spinner"></span>
                  Processing {{ selectedExamFiles.length }} exam{{ selectedExamFiles.length > 1 ? 's' : '' }}...
                </span>
              </button>
            </div>
          </section>

          <!-- Step 3: Results -->
          <section class="card results-card animate-in" *ngIf="currentStep === 3">
            <div class="card-glow"></div>
            <div class="card-header">
              <div class="card-title-group">
                <div class="card-icon green">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>
                </div>
                <div>
                  <h2>Grading Results</h2>
                  <p>{{ getSuccessCount() }} of {{ results.length }} exams processed successfully</p>
                </div>
              </div>
              <div class="header-actions">
                <button class="btn btn-ghost" (click)="resetAndStartNew()">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 4v6h6M23 20v-6h-6"/><path d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 013.51 15"/></svg>
                  Grade More
                </button>
                <button class="btn btn-ghost danger" (click)="clearOutputs()">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                  Clear Outputs
                </button>
                <div class="export-dropdown">
                  <button class="btn btn-outline" (click)="showExportMenu = !showExportMenu">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><path d="M7 10l5 5 5-5M12 15V3"/></svg>
                    Export
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:14px;height:14px"><path d="M6 9l6 6 6-6"/></svg>
                  </button>
                  <div class="export-menu" *ngIf="showExportMenu">
                    <button (click)="exportYoloCsv(); showExportMenu = false">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
                      YOLO Detections CSV
                    </button>
                    <button (click)="exportOcrNetCsv(); showExportMenu = false">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><path d="M22 6l-10 7L2 6"/></svg>
                      Student ID CSV
                    </button>
                    <button (click)="exportComparisonCsv(); showExportMenu = false">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/></svg>
                      Full Comparison CSV
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Stats Cards -->
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-icon blue">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 4h2a2 2 0 012 2v14a2 2 0 01-2 2H6a2 2 0 01-2-2V6a2 2 0 012-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/></svg>
                </div>
                <div class="stat-data">
                  <span class="stat-number">{{ getSuccessCount() }}</span>
                  <span class="stat-label">Processed</span>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon violet">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>
                </div>
                <div class="stat-data">
                  <span class="stat-number">{{ getAverageScore() | number:'1.1-1' }}%</span>
                  <span class="stat-label">Average Score</span>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon green">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 6l-9.5 9.5-5-5L1 18"/><path d="M17 6h6v6"/></svg>
                </div>
                <div class="stat-data">
                  <span class="stat-number high">{{ getHighestScore() | number:'1.0-0' }}%</span>
                  <span class="stat-label">Highest</span>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon red">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 18l-9.5-9.5-5 5L1 6"/><path d="M17 18h6v-6"/></svg>
                </div>
                <div class="stat-data">
                  <span class="stat-number low">{{ getLowestScore() | number:'1.0-0' }}%</span>
                  <span class="stat-label">Lowest</span>
                </div>
              </div>
            </div>

            <!-- Results Table -->
            <div class="table-wrap">
              <table class="data-table">
                <thead>
                  <tr>
                    <th class="col-sticky">Student ID</th>
                    <th *ngFor="let q of questionNumbers" class="col-q">Q{{ q }}</th>
                    <th class="col-score">Score</th>
                    <th class="col-status">Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr *ngFor="let result of results" (click)="selectedResult = result" [class.selected]="selectedResult === result">
                    <td class="col-sticky">
                      <span class="student-id">{{ result.studentId || 'Unknown' }}</span>
                    </td>
                    <td *ngFor="let q of questionNumbers" 
                        class="col-q"
                        [class.correct]="getQuestionStatus(result, q) === 'CORRECT'"
                        [class.wrong]="getQuestionStatus(result, q) === 'WRONG'"
                        [class.blank]="getQuestionStatus(result, q) === 'BLANK' || !getStudentAnswer(result, q)">
                      {{ getStudentAnswer(result, q) || '-' }}
                    </td>
                    <td class="col-score">
                      <div class="score-pill"
                           [class.high]="result.scorePercentage >= 70"
                           [class.medium]="result.scorePercentage >= 50 && result.scorePercentage < 70"
                           [class.low]="result.scorePercentage < 50">
                        {{ result.correctCount }}/{{ result.totalQuestions }}
                        <span class="score-pct">{{ result.scorePercentage | number:'1.0-0' }}%</span>
                      </div>
                    </td>
                    <td class="col-status">
                      <span class="pass-tag" [class.pass]="hasPassed(result)" [class.fail]="!hasPassed(result)">
                        {{ hasPassed(result) ? 'PASS' : 'FAIL' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Detail Panel -->
            <div class="detail-panel" *ngIf="selectedResult">
              <div class="detail-header">
                <div class="detail-title">
                  <div class="detail-avatar">{{ (selectedResult.studentId || '?')[0] }}</div>
                  <div>
                    <h4>{{ selectedResult.studentId || 'Unknown Student' }}</h4>
                    <span class="detail-file">{{ selectedResult.fileName }}</span>
                  </div>
                </div>
                <span class="pass-tag large" [class.pass]="hasPassed(selectedResult)" [class.fail]="!hasPassed(selectedResult)">
                  {{ hasPassed(selectedResult) ? 'PASS' : 'FAIL' }}
                </span>
                <button class="btn-close" (click)="selectedResult = null">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
                </button>
              </div>

              <!-- API Responses (Debug) -->
              <div class="api-panels" *ngIf="debugResults[selectedResult.fileName || '']">
                <div class="api-panel">
                  <div class="api-panel-header yolo">
                    <div class="api-step-badge">1</div>
                    <h5>YOLO Detection</h5>
                    <span class="api-pill" [class.ok]="debugResults[selectedResult.fileName || '']?.yoloResponse?.success"
                          [class.fail]="!debugResults[selectedResult.fileName || '']?.yoloResponse?.success">
                      {{ debugResults[selectedResult.fileName || '']?.yoloResponse?.success ? 'SUCCESS' : 'FAILED' }}
                    </span>
                  </div>
                  <div class="api-panel-body">
                    <div class="api-meta">
                      <span>Method: <strong>{{ debugResults[selectedResult.fileName || '']?.yoloResponse?.method || 'N/A' }}</strong></span>
                      <span>Detections: <strong>{{ debugResults[selectedResult.fileName || '']?.yoloResponse?.totalDetections || 0 }}</strong></span>
                    </div>
                    <div class="chip-grid">
                      <div *ngFor="let item of getYoloAnswersArray(selectedResult.fileName || '')" class="chip yolo">
                        <span class="chip-q">Q{{ item.q }}</span>
                        <span class="chip-a">{{ item.a }}</span>
                      </div>
                    </div>
                    <details class="json-toggle">
                      <summary>View Raw JSON</summary>
                      <pre>{{ debugResults[selectedResult.fileName || '']?.yoloResponse | json }}</pre>
                    </details>
                  </div>
                </div>

                <div class="api-panel">
                  <div class="api-panel-header ocr">
                    <div class="api-step-badge">2</div>
                    <h5>Student ID Model</h5>
                    <span class="api-pill" [class.ok]="debugResults[selectedResult.fileName || '']?.ocrResponse?.success"
                          [class.fail]="!debugResults[selectedResult.fileName || '']?.ocrResponse?.success">
                      {{ debugResults[selectedResult.fileName || '']?.ocrResponse?.success ? 'SUCCESS' : 'FAILED' }}
                    </span>
                  </div>
                  <div class="api-panel-body">
                    <div class="ocr-display">
                      <span class="ocr-label">Extracted Number</span>
                      <span class="ocr-number">{{ getStudentIdFromOcr(debugResults[selectedResult.fileName || '']?.ocrResponse) || '-' }}</span>
                    </div>
                    <div class="api-meta">
                      <span>Confidence: <strong>{{ (debugResults[selectedResult.fileName || '']?.ocrResponse?.confidence || 0) | number:'1.1-1' }}%</strong></span>
                      <span *ngIf="getRawOcrText(debugResults[selectedResult.fileName || '']?.ocrResponse)">
                        Raw: <strong>{{ getRawOcrText(debugResults[selectedResult.fileName || '']?.ocrResponse) }}</strong>
                      </span>
                      <span *ngIf="getOcrError(debugResults[selectedResult.fileName || '']?.ocrResponse)">
                        Error: <strong>{{ getOcrError(debugResults[selectedResult.fileName || '']?.ocrResponse) }}</strong>
                      </span>
                    </div>
                    <details class="json-toggle">
                      <summary>View Raw JSON</summary>
                      <pre>{{ debugResults[selectedResult.fileName || '']?.ocrResponse | json }}</pre>
                    </details>
                  </div>
                </div>

                <div class="api-panel">
                  <div class="api-panel-header compare">
                    <div class="api-step-badge">3</div>
                    <h5>Answer Comparison</h5>
                    <span class="api-pill" [class.ok]="debugResults[selectedResult.fileName || '']?.comparisonResponse?.success"
                          [class.fail]="!debugResults[selectedResult.fileName || '']?.comparisonResponse?.success">
                      {{ debugResults[selectedResult.fileName || '']?.comparisonResponse?.success ? 'SUCCESS' : 'FAILED' }}
                    </span>
                  </div>
                  <div class="api-panel-body">
                    <div class="compare-stats">
                      <div class="cmp-stat correct">
                        <span class="cmp-num">{{ debugResults[selectedResult.fileName || '']?.comparisonResponse?.correctCount || 0 }}</span>
                        <span class="cmp-lbl">Correct</span>
                      </div>
                      <div class="cmp-stat wrong">
                        <span class="cmp-num">{{ (debugResults[selectedResult.fileName || '']?.comparisonResponse?.totalQuestions || 0) - (debugResults[selectedResult.fileName || '']?.comparisonResponse?.correctCount || 0) }}</span>
                        <span class="cmp-lbl">Wrong</span>
                      </div>
                      <div class="cmp-stat score">
                        <span class="cmp-num">{{ debugResults[selectedResult.fileName || '']?.comparisonResponse?.scorePercentage || 0 }}%</span>
                        <span class="cmp-lbl">Score</span>
                      </div>
                    </div>
                    <details class="json-toggle">
                      <summary>View Raw JSON</summary>
                      <pre>{{ debugResults[selectedResult.fileName || '']?.comparisonResponse | json }}</pre>
                    </details>
                  </div>
                </div>
              </div>
              
              <!-- Detailed Question Table -->
              <div class="question-table-wrap">
                <table class="question-table">
                  <thead>
                    <tr>
                      <th>Q#</th>
                      <th>YOLO Detected</th>
                      <th>Correct (CSV)</th>
                      <th>Match</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr *ngFor="let qr of selectedResult.questionResults"
                        [class.row-correct]="qr.isCorrect"
                        [class.row-wrong]="!qr.isCorrect && qr.studentAnswer"
                        [class.row-blank]="!qr.studentAnswer">
                      <td class="q-num">{{ qr.questionNumber }}</td>
                      <td class="td-yolo">
                        <span class="answer-bubble yolo">{{ qr.studentAnswer || '-' }}</span>
                      </td>
                      <td class="td-correct">
                        <span class="answer-bubble correct">{{ qr.correctAnswer || '-' }}</span>
                      </td>
                      <td class="td-match">
                        <span class="match-tag" [class.yes]="qr.isCorrect" [class.no]="!qr.isCorrect">
                          {{ qr.isCorrect ? 'CORRECT' : 'WRONG' }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Score Summary -->
              <div class="score-summary">
                <div class="score-item">
                  <span class="score-item-label">Total Questions</span>
                  <span class="score-item-value">{{ selectedResult.totalQuestions }}</span>
                </div>
                <div class="score-item">
                  <span class="score-item-label">Correct</span>
                  <span class="score-item-value correct">{{ selectedResult.correctCount }}</span>
                </div>
                <div class="score-item">
                  <span class="score-item-label">Wrong</span>
                  <span class="score-item-value wrong">{{ selectedResult.totalQuestions - selectedResult.correctCount }}</span>
                </div>
                <div class="score-item highlight">
                  <span class="score-item-label">Final Score</span>
                  <span class="score-item-value">{{ selectedResult.scorePercentage }}%</span>
                </div>
              </div>

              <details class="json-toggle">
                <summary>View Full API Response</summary>
                <pre>{{ selectedResult | json }}</pre>
              </details>
            </div>
          </section>
        </div>
      </main>

      <!-- Toast -->
      <div class="toast-bar" *ngIf="errorMessage" (click)="errorMessage = ''">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M15 9l-6 6M9 9l6 6"/></svg>
        <span>{{ errorMessage }}</span>
        <button>Dismiss</button>
      </div>

      <!-- Footer -->
      <footer class="footer">
        <div class="container footer-content">
          <span>Exam Grading System</span>
          <span class="footer-sep">&bull;</span>
          <span>Powered by YOLO, Tesseract & .NET</span>
        </div>
      </footer>
    </div>
  `,
  styles: [`
    :host {
      --primary: #3b82f6;
      --primary-dark: #2563eb;
      --primary-light: #93c5fd;
      --violet: #8b5cf6;
      --violet-dark: #7c3aed;
      --success: #10b981;
      --success-dark: #059669;
      --danger: #ef4444;
      --danger-dark: #dc2626;
      --warning: #f59e0b;
      --gray-50: #f8fafc;
      --gray-100: #f1f5f9;
      --gray-200: #e2e8f0;
      --gray-300: #cbd5e1;
      --gray-400: #94a3b8;
      --gray-500: #64748b;
      --gray-600: #475569;
      --gray-700: #334155;
      --gray-800: #1e293b;
      --gray-900: #0f172a;
      --radius: 12px;
      --radius-sm: 8px;
      --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
      --shadow: 0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -2px rgba(0,0,0,0.05);
      --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -4px rgba(0,0,0,0.05);
      --shadow-xl: 0 20px 25px -5px rgba(0,0,0,0.08), 0 8px 10px -6px rgba(0,0,0,0.04);
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    .app {
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 50%, #f0fdf4 100%);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      color: var(--gray-800);
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 24px;
      width: 100%;
    }

    /* ═══════ HEADER ═══════ */
    .header {
      position: relative;
      background: linear-gradient(135deg, var(--gray-900) 0%, #1a1a3e 50%, #0f172a 100%);
      padding: 18px 0;
      overflow: hidden;
    }

    .header-glow {
      position: absolute;
      top: -50%;
      left: 30%;
      width: 40%;
      height: 200%;
      background: radial-gradient(ellipse, rgba(99,102,241,0.15) 0%, transparent 70%);
      pointer-events: none;
    }

    .header-content {
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: relative;
      z-index: 1;
    }

    .logo-section {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .logo-icon {
      width: 44px;
      height: 44px;
      background: linear-gradient(135deg, var(--primary) 0%, var(--violet) 100%);
      border-radius: var(--radius);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      box-shadow: 0 4px 15px rgba(99,102,241,0.4);
      svg { width: 24px; height: 24px; }
    }

    .logo {
      font-size: 1.2rem;
      font-weight: 700;
      color: white;
      letter-spacing: -0.02em;
    }

    .tagline {
      font-size: 0.78rem;
      color: rgba(255,255,255,0.5);
      font-weight: 400;
    }

    .status-pill {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      background: rgba(255,255,255,0.08);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 50px;
      font-size: 0.78rem;
      color: rgba(255,255,255,0.7);
      font-weight: 500;
    }

    .status-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--success);
      box-shadow: 0 0 8px var(--success);
      animation: pulse-dot 2s ease-in-out infinite;
    }

    @keyframes pulse-dot {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }

    /* ═══════ MAIN ═══════ */
    .main { flex: 1; padding: 36px 0 48px; }

    /* ═══════ STEPS ═══════ */
    .steps-wrapper { margin-bottom: 36px; }

    .steps {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0;
    }

    .step {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 16px;
      border-radius: var(--radius);
      cursor: default;
      transition: all 0.3s ease;
    }

    .step-icon {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: var(--gray-200);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
      svg { width: 20px; height: 20px; color: var(--gray-400); }
    }

    .step-text {
      display: flex;
      flex-direction: column;
    }

    .step-label {
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--gray-400);
    }

    .step-title {
      font-size: 0.88rem;
      font-weight: 600;
      color: var(--gray-400);
    }

    .step.active {
      .step-icon {
        background: linear-gradient(135deg, var(--primary) 0%, var(--violet) 100%);
        box-shadow: 0 4px 12px rgba(99,102,241,0.3);
        svg { color: white; }
      }
      .step-label { color: var(--primary); }
      .step-title { color: var(--gray-800); }
    }

    .step.done {
      cursor: pointer;
      .step-icon {
        background: linear-gradient(135deg, var(--success) 0%, #34d399 100%);
        box-shadow: 0 4px 12px rgba(16,185,129,0.3);
        svg { color: white; }
      }
      .step-label { color: var(--success); }
      .step-title { color: var(--gray-700); }
    }

    .step-connector {
      width: 60px;
      height: 3px;
      background: var(--gray-200);
      border-radius: 2px;
      margin: 0 4px;
      overflow: hidden;
    }

    .step-connector .connector-fill {
      width: 0%;
      height: 100%;
      background: linear-gradient(90deg, var(--success), #34d399);
      border-radius: 2px;
      transition: width 0.5s ease;
    }

    .step-connector.active .connector-fill { width: 100%; }

    /* ═══════ CARD ═══════ */
    .card {
      position: relative;
      background: rgba(255,255,255,0.85);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(255,255,255,0.6);
      border-radius: 16px;
      padding: 28px;
      margin-bottom: 24px;
      box-shadow: var(--shadow-lg);
      overflow: hidden;
    }

    .card-glow {
      position: absolute;
      top: -80px;
      right: -80px;
      width: 200px;
      height: 200px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(99,102,241,0.06) 0%, transparent 70%);
      pointer-events: none;
    }

    .animate-in {
      animation: fadeSlideIn 0.4s ease-out;
    }

    @keyframes fadeSlideIn {
      from { opacity: 0; transform: translateY(12px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 24px;
    }

    .card-title-group {
      display: flex;
      align-items: flex-start;
      gap: 16px;

      h2 {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--gray-900);
        letter-spacing: -0.02em;
        margin-bottom: 4px;
      }

      p {
        font-size: 0.88rem;
        color: var(--gray-500);
      }
    }

    .card-icon {
      width: 44px;
      height: 44px;
      border-radius: var(--radius);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      svg { width: 22px; height: 22px; color: white; }

      &.blue { background: linear-gradient(135deg, var(--primary), #6366f1); box-shadow: 0 4px 12px rgba(59,130,246,0.25); }
      &.violet { background: linear-gradient(135deg, var(--violet), #a855f7); box-shadow: 0 4px 12px rgba(139,92,246,0.25); }
      &.green { background: linear-gradient(135deg, var(--success), #34d399); box-shadow: 0 4px 12px rgba(16,185,129,0.25); }
    }

    .card-actions {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 24px;
      padding-top: 20px;
      border-top: 1px solid var(--gray-200);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    /* ═══════ BUTTONS ═══════ */
    .btn {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 10px 18px;
      font-size: 0.88rem;
      font-weight: 600;
      font-family: inherit;
      border-radius: var(--radius-sm);
      border: none;
      cursor: pointer;
      transition: all 0.2s ease;
      svg { width: 18px; height: 18px; flex-shrink: 0; }
      &:disabled { opacity: 0.5; cursor: not-allowed; }
    }

    .btn-primary {
      background: linear-gradient(135deg, var(--primary) 0%, var(--violet) 100%);
      color: white;
      box-shadow: 0 4px 14px rgba(99,102,241,0.35);
      &:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(99,102,241,0.4); }
    }

    .btn-lg { padding: 12px 24px; font-size: 0.95rem; }

    .btn-outline {
      background: white;
      color: var(--gray-700);
      border: 1px solid var(--gray-300);
      &:hover { background: var(--gray-50); border-color: var(--gray-400); }
    }

    .btn-ghost {
      background: none;
      color: var(--gray-600);
      padding: 8px 14px;
      &:hover { color: var(--gray-900); background: var(--gray-100); border-radius: var(--radius-sm); }
      &.danger { color: var(--danger); &:hover { background: rgba(239,68,68,0.08); } }
    }

    .btn-close {
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: none;
      border: none;
      border-radius: 50%;
      cursor: pointer;
      color: var(--gray-400);
      transition: all 0.2s;
      svg { width: 18px; height: 18px; }
      &:hover { background: var(--gray-100); color: var(--gray-700); }
    }

    .btn-remove {
      width: 28px;
      height: 28px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: none;
      border: none;
      border-radius: 50%;
      cursor: pointer;
      color: var(--gray-400);
      transition: all 0.2s;
      svg { width: 14px; height: 14px; }
      &:hover { background: rgba(239,68,68,0.1); color: var(--danger); }
    }

    /* ═══════ TEMPLATE BANNER ═══════ */
    .template-banner {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 18px;
      background: linear-gradient(135deg, rgba(59,130,246,0.05), rgba(139,92,246,0.05));
      border: 1px solid rgba(99,102,241,0.12);
      border-radius: var(--radius);
      margin-bottom: 20px;
    }

    .template-left {
      display: flex;
      align-items: center;
      gap: 12px;
      svg { width: 20px; height: 20px; color: var(--primary); flex-shrink: 0; }
      strong { display: block; color: var(--gray-800); font-size: 0.88rem; }
      span { font-size: 0.8rem; color: var(--gray-500); }
    }

    .manual-key-card {
      margin-bottom: 20px;
      border: 1px solid rgba(99,102,241,0.18);
      border-radius: var(--radius);
      background: rgba(99,102,241,0.04);
      padding: 14px;
    }

    .manual-key-header {
      display: flex;
      flex-direction: column;
      gap: 2px;
      margin-bottom: 10px;
      strong { color: var(--gray-800); font-size: 0.92rem; }
      span { color: var(--gray-500); font-size: 0.8rem; }
    }

    .manual-key-grid {
      max-height: 280px;
      overflow-y: auto;
      display: grid;
      gap: 8px;
      padding-right: 4px;
    }

    .manual-key-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #fff;
      border: 1px solid var(--gray-200);
      border-radius: 10px;
      padding: 8px 10px;
    }

    .manual-key-q {
      min-width: 44px;
      font-weight: 700;
      color: var(--gray-700);
      font-size: 0.86rem;
    }

    .manual-key-options {
      width: 220px;
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 6px;
    }

    .manual-opt {
      border: 1px solid var(--gray-300);
      border-radius: 8px;
      background: #fff;
      color: var(--gray-700);
      font-weight: 700;
      font-size: 0.82rem;
      padding: 6px 0;
      cursor: pointer;
      transition: all 0.15s ease;
    }

    .manual-opt:hover {
      border-color: var(--primary);
      color: var(--primary);
    }

    .manual-opt.active {
      background: var(--primary);
      border-color: var(--primary);
      color: #fff;
      box-shadow: 0 4px 10px rgba(79,70,229,0.22);
    }

    .manual-key-actions {
      margin-top: 12px;
      display: flex;
      justify-content: flex-end;
      gap: 8px;
    }

    /* ═══════ DROP ZONE ═══════ */
    .drop-zone {
      border: 2px dashed var(--gray-300);
      border-radius: var(--radius);
      padding: 48px 24px;
      text-align: center;
      cursor: pointer;
      transition: all 0.25s ease;
      background: rgba(255,255,255,0.5);

      &:hover, &.dragover {
        border-color: var(--primary);
        background: rgba(59,130,246,0.04);
        box-shadow: 0 0 0 4px rgba(59,130,246,0.08);
      }

      &.uploaded {
        border-style: solid;
        border-color: var(--success);
        background: rgba(16,185,129,0.04);
        box-shadow: 0 0 0 4px rgba(16,185,129,0.08);
      }

      &.large { padding: 64px 24px; }
    }

    .drop-zone-idle {
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .drop-icon-wrap {
      width: 64px;
      height: 64px;
      border-radius: 50%;
      background: linear-gradient(135deg, rgba(59,130,246,0.08), rgba(139,92,246,0.08));
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 16px;
      svg { width: 28px; height: 28px; color: var(--primary); }
    }

    .drop-title {
      font-size: 1rem;
      font-weight: 600;
      color: var(--gray-700);
      margin-bottom: 4px;
    }

    .drop-sub {
      font-size: 0.85rem;
      color: var(--gray-400);
    }

    .drop-zone-success {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 16px;
    }

    .success-icon-wrap {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--success), #34d399);
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(16,185,129,0.3);
      svg { width: 24px; height: 24px; color: white; }
    }

    .success-info {
      text-align: left;
      strong { display: block; color: var(--gray-900); font-size: 1rem; }
      span { font-size: 0.85rem; color: var(--success); font-weight: 500; }
    }

    /* ═══════ ACTIVE KEY BADGE ═══════ */
    .active-key-badge {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 8px 16px;
      background: rgba(16,185,129,0.08);
      border: 1px solid rgba(16,185,129,0.15);
      border-radius: 50px;
      font-size: 0.85rem;
      color: var(--gray-700);
      margin-bottom: 20px;
      svg { width: 16px; height: 16px; color: var(--success); }
      strong { color: var(--gray-900); }
    }

    /* ═══════ FILE LIST ═══════ */
    .file-list {
      margin-top: 20px;
      border: 1px solid var(--gray-200);
      border-radius: var(--radius);
      overflow: hidden;
    }

    .file-list-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      background: var(--gray-50);
      border-bottom: 1px solid var(--gray-200);
    }

    .file-count {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--gray-600);
      svg { width: 16px; height: 16px; }
    }

    .file-items-scroll {
      max-height: 220px;
      overflow-y: auto;
    }

    .file-row {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 16px;
      border-bottom: 1px solid var(--gray-100);
      transition: background 0.15s;
      &:last-child { border-bottom: none; }
      &:hover { background: var(--gray-50); }
    }

    .file-thumb {
      width: 32px;
      height: 32px;
      border-radius: 6px;
      background: rgba(139,92,246,0.08);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      svg { width: 16px; height: 16px; color: var(--violet); }
    }

    .file-name {
      flex: 1;
      font-size: 0.88rem;
      font-weight: 500;
      color: var(--gray-800);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .file-size {
      font-size: 0.78rem;
      color: var(--gray-400);
      font-weight: 500;
    }

    /* ═══════ OPTIONS BAR ═══════ */
    .options-bar {
      margin-top: 20px;
      padding: 14px 18px;
      background: var(--gray-50);
      border: 1px solid var(--gray-200);
      border-radius: var(--radius);
    }

    .mode-note {
      display: flex;
      justify-content: flex-end;
      color: var(--gray-500);
      font-size: 0.84rem;
    }

    .switch-label {
      display: flex;
      align-items: center;
      gap: 14px;
      cursor: pointer;
      font-size: 0.88rem;
      color: var(--gray-700);
      em { font-style: normal; color: var(--gray-400); font-size: 0.82rem; }
    }

    .switch-track {
      width: 44px;
      height: 24px;
      border-radius: 12px;
      background: var(--gray-300);
      position: relative;
      transition: background 0.25s;
      flex-shrink: 0;
      &.on { background: linear-gradient(135deg, var(--primary), var(--violet)); }
    }

    .switch-thumb {
      position: absolute;
      top: 2px;
      left: 2px;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: white;
      box-shadow: 0 1px 3px rgba(0,0,0,0.2);
      transition: transform 0.25s;
      .on & { transform: translateX(20px); }
    }

    .time-estimate {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.85rem;
      color: var(--gray-500);
      svg { width: 16px; height: 16px; }
    }

    .loading-state {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .spinner {
      width: 18px;
      height: 18px;
      border: 2.5px solid rgba(255,255,255,0.3);
      border-top-color: white;
      border-radius: 50%;
      animation: spin 0.7s linear infinite;
    }

    @keyframes spin { to { transform: rotate(360deg); } }

    /* ═══════ STATS GRID ═══════ */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 28px;
    }

    .stat-card {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 18px;
      background: white;
      border: 1px solid var(--gray-200);
      border-radius: var(--radius);
      box-shadow: var(--shadow-sm);
      transition: transform 0.2s, box-shadow 0.2s;
      &:hover { transform: translateY(-2px); box-shadow: var(--shadow); }
    }

    .stat-icon {
      width: 42px;
      height: 42px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      svg { width: 20px; height: 20px; color: white; }
      &.blue { background: linear-gradient(135deg, var(--primary), #6366f1); }
      &.violet { background: linear-gradient(135deg, var(--violet), #a855f7); }
      &.green { background: linear-gradient(135deg, var(--success), #34d399); }
      &.red { background: linear-gradient(135deg, var(--danger), #f87171); }
    }

    .stat-data { display: flex; flex-direction: column; }

    .stat-number {
      font-size: 1.4rem;
      font-weight: 800;
      color: var(--gray-900);
      letter-spacing: -0.02em;
      &.high { color: var(--success); }
      &.low { color: var(--danger); }
    }

    .stat-label {
      font-size: 0.78rem;
      color: var(--gray-500);
      font-weight: 500;
      margin-top: 1px;
    }

    /* ═══════ DATA TABLE ═══════ */
    .table-wrap {
      overflow-x: auto;
      border: 1px solid var(--gray-200);
      border-radius: var(--radius);
      box-shadow: var(--shadow-sm);
    }

    .data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;

      th, td {
        padding: 12px 10px;
        text-align: center;
        border-bottom: 1px solid var(--gray-100);
      }

      thead th {
        background: var(--gray-900);
        color: rgba(255,255,255,0.9);
        font-weight: 600;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        position: sticky;
        top: 0;
        z-index: 2;
      }

      .col-sticky {
        text-align: left;
        min-width: 120px;
        position: sticky;
        left: 0;
        z-index: 1;
        background: white;
      }

      thead .col-sticky { background: var(--gray-900); z-index: 3; }

      .col-q {
        min-width: 38px;
        font-weight: 600;
        &.correct { background: rgba(16,185,129,0.1); color: var(--success-dark); }
        &.wrong { background: rgba(239,68,68,0.08); color: var(--danger); }
        &.blank { color: var(--gray-300); }
      }

      .col-score { min-width: 100px; }

      tbody tr {
        cursor: pointer;
        transition: background 0.15s;
        &:hover td { background: rgba(99,102,241,0.04); }
        &:hover .col-sticky { background: rgba(99,102,241,0.04); }
        &.selected td { background: rgba(99,102,241,0.08); }
        &.selected .col-sticky { background: rgba(99,102,241,0.08); }
      }
    }

    .student-id { font-weight: 600; color: var(--gray-800); }

    .threshold-card {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      padding: 16px 18px;
      margin-bottom: 20px;
      border: 1px solid var(--gray-200);
      border-radius: var(--radius);
      background: var(--gray-50);
    }

    .threshold-copy {
      display: flex;
      flex-direction: column;
      gap: 3px;
      strong { color: var(--gray-900); font-size: 0.95rem; }
      span { color: var(--gray-500); font-size: 0.84rem; }
    }

    .threshold-control {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border: 1px solid var(--gray-300);
      border-radius: var(--radius-sm);
      background: white;
      color: var(--gray-600);
      font-weight: 700;
      input {
        width: 70px;
        border: none;
        outline: none;
        font: inherit;
        color: var(--gray-900);
        text-align: right;
        background: transparent;
      }
    }

    .score-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 12px;
      border-radius: 50px;
      font-weight: 700;
      font-size: 0.82rem;
      &.high { background: rgba(16,185,129,0.12); color: var(--success-dark); }
      &.medium { background: rgba(245,158,11,0.12); color: #b45309; }
      &.low { background: rgba(239,68,68,0.12); color: var(--danger-dark); }
    }

    .score-pct {
      font-weight: 500;
      opacity: 0.7;
      font-size: 0.75rem;
    }

    .col-status { min-width: 90px; }

    .pass-tag {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 58px;
      padding: 5px 10px;
      border-radius: 999px;
      font-weight: 800;
      font-size: 0.72rem;
      letter-spacing: 0.04em;
      &.pass { background: rgba(16,185,129,0.12); color: var(--success-dark); }
      &.fail { background: rgba(239,68,68,0.1); color: var(--danger-dark); }
      &.large { min-width: 72px; padding: 7px 14px; font-size: 0.78rem; }
    }

    /* ═══════ DETAIL PANEL ═══════ */
    .detail-panel {
      margin-top: 24px;
      padding: 24px;
      background: white;
      border-radius: var(--radius);
      border: 1px solid var(--gray-200);
      box-shadow: var(--shadow);
      animation: fadeSlideIn 0.3s ease;
    }

    .detail-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--gray-200);
    }

    .detail-title {
      display: flex;
      align-items: center;
      gap: 14px;
      h4 { font-size: 1.05rem; font-weight: 700; color: var(--gray-900); }
    }

    .detail-file { font-size: 0.82rem; color: var(--gray-500); }

    .detail-avatar {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--primary), var(--violet));
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: 700;
      font-size: 1.1rem;
    }

    /* ═══════ API PANELS ═══════ */
    .api-panels {
      display: flex;
      flex-direction: column;
      gap: 14px;
      margin-bottom: 24px;
    }

    .api-panel {
      border: 1px solid var(--gray-200);
      border-radius: var(--radius);
      overflow: hidden;
    }

    .api-panel-header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 16px;
      background: var(--gray-50);
      border-bottom: 1px solid var(--gray-200);

      &.yolo { border-left: 4px solid var(--primary); }
      &.ocr { border-left: 4px solid var(--violet); }
      &.compare { border-left: 4px solid var(--success); }

      h5 { flex: 1; font-size: 0.9rem; font-weight: 700; color: var(--gray-800); }
    }

    .api-step-badge {
      width: 24px;
      height: 24px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--gray-700);
      color: white;
      border-radius: 50%;
      font-size: 0.72rem;
      font-weight: 700;
    }

    .api-pill {
      padding: 3px 10px;
      border-radius: 50px;
      font-size: 0.72rem;
      font-weight: 700;
      letter-spacing: 0.02em;
      &.ok { background: rgba(16,185,129,0.12); color: var(--success-dark); }
      &.fail { background: rgba(239,68,68,0.12); color: var(--danger); }
    }

    .api-panel-body { padding: 16px; }

    .api-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 20px;
      margin-bottom: 14px;
      font-size: 0.82rem;
      color: var(--gray-500);
      strong { color: var(--gray-800); }
    }

    .chip-grid {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }

    .chip {
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 5px 10px;
      border-radius: 6px;
      font-size: 0.82rem;
      &.yolo {
        background: rgba(59,130,246,0.08);
        border: 1px solid rgba(59,130,246,0.15);
      }
    }

    .chip-q { color: var(--gray-500); font-size: 0.72rem; font-weight: 600; }
    .chip-a { font-weight: 800; color: var(--primary); }

    .ocr-display {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      gap: 4px;
      margin-bottom: 14px;
      padding: 14px 20px;
      background: linear-gradient(135deg, rgba(139,92,246,0.06), rgba(139,92,246,0.02));
      border: 1px solid rgba(139,92,246,0.15);
      border-radius: var(--radius);
    }

    .ocr-label { font-size: 0.78rem; color: var(--gray-500); font-weight: 500; }

    .ocr-number {
      font-size: 2rem;
      font-weight: 800;
      color: var(--violet);
      letter-spacing: 4px;
      font-variant-numeric: tabular-nums;
    }

    .compare-stats {
      display: flex;
      gap: 20px;
      padding: 14px 20px;
      background: var(--gray-50);
      border-radius: var(--radius);
    }

    .cmp-stat {
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .cmp-num {
      font-size: 1.6rem;
      font-weight: 800;
      .correct & { color: var(--success); }
      .wrong & { color: var(--danger); }
      .score & { color: var(--primary); }
    }

    .cmp-lbl { font-size: 0.72rem; color: var(--gray-500); font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em; }

    .json-toggle {
      margin-top: 10px;
      summary {
        cursor: pointer;
        font-size: 0.78rem;
        color: var(--gray-400);
        font-weight: 500;
        padding: 6px 0;
        &:hover { color: var(--gray-600); }
      }
      pre {
        margin-top: 8px;
        padding: 14px;
        background: var(--gray-900);
        color: #7dd3fc;
        border-radius: var(--radius-sm);
        font-size: 0.72rem;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        overflow-x: auto;
        max-height: 240px;
        overflow-y: auto;
        line-height: 1.6;
      }
    }

    /* ═══════ QUESTION TABLE ═══════ */
    .question-table-wrap {
      overflow-x: auto;
      margin-bottom: 20px;
      border: 1px solid var(--gray-200);
      border-radius: var(--radius);
    }

    .question-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;

      th, td {
        padding: 13px 18px;
        text-align: center;
        border-bottom: 1px solid var(--gray-100);
      }

      th {
        background: var(--gray-50);
        font-weight: 700;
        color: var(--gray-600);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
      }

      .q-num { font-weight: 700; color: var(--gray-400); width: 50px; }

      .answer-bubble {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        border-radius: 50%;
        font-weight: 700;
        font-size: 0.95rem;
        &.yolo { background: rgba(59,130,246,0.1); color: var(--primary); }
        &.correct { background: rgba(16,185,129,0.1); color: var(--success-dark); }
      }

      .match-tag {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 50px;
        font-weight: 700;
        font-size: 0.75rem;
        letter-spacing: 0.02em;
        &.yes { background: rgba(16,185,129,0.12); color: var(--success-dark); }
        &.no { background: rgba(239,68,68,0.1); color: var(--danger); }
      }

      tr.row-correct { background: rgba(16,185,129,0.03); }
      tr.row-wrong { background: rgba(239,68,68,0.03); }
      tr.row-blank {
        .answer-bubble.yolo { background: var(--gray-100); color: var(--gray-400); }
      }
    }

    /* ═══════ SCORE SUMMARY ═══════ */
    .score-summary {
      display: flex;
      gap: 0;
      border: 1px solid var(--gray-200);
      border-radius: var(--radius);
      overflow: hidden;
      margin-bottom: 16px;
    }

    .score-item {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 16px;
      background: var(--gray-50);
      border-right: 1px solid var(--gray-200);
      &:last-child { border-right: none; }
      &.highlight { background: linear-gradient(135deg, rgba(99,102,241,0.06), rgba(139,92,246,0.06)); }
    }

    .score-item-label {
      font-size: 0.78rem;
      color: var(--gray-500);
      font-weight: 500;
      margin-bottom: 4px;
    }

    .score-item-value {
      font-size: 1.4rem;
      font-weight: 800;
      color: var(--gray-800);
      &.correct { color: var(--success); }
      &.wrong { color: var(--danger); }
    }

    /* ═══════ EXPORT DROPDOWN ═══════ */
    .export-dropdown { position: relative; }

    .export-menu {
      position: absolute;
      top: calc(100% + 6px);
      right: 0;
      background: white;
      border: 1px solid var(--gray-200);
      border-radius: var(--radius);
      box-shadow: var(--shadow-xl);
      min-width: 220px;
      z-index: 50;
      padding: 6px;
      animation: fadeSlideIn 0.15s ease;

      button {
        display: flex;
        align-items: center;
        gap: 10px;
        width: 100%;
        padding: 10px 14px;
        background: none;
        border: none;
        font-size: 0.85rem;
        font-family: inherit;
        color: var(--gray-700);
        cursor: pointer;
        border-radius: var(--radius-sm);
        transition: background 0.15s;
        font-weight: 500;
        svg { width: 16px; height: 16px; color: var(--gray-400); }
        &:hover { background: var(--gray-50); }
      }
    }

    /* ═══════ TOAST ═══════ */
    .toast-bar {
      position: fixed;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 14px 20px;
      background: linear-gradient(135deg, var(--danger), var(--danger-dark));
      color: white;
      border-radius: var(--radius);
      box-shadow: 0 8px 30px rgba(239,68,68,0.3);
      cursor: pointer;
      z-index: 100;
      animation: slideUp 0.3s ease;

      svg { width: 20px; height: 20px; flex-shrink: 0; }
      span { font-weight: 500; font-size: 0.9rem; }
      button {
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.82rem;
        cursor: pointer;
        font-family: inherit;
        font-weight: 600;
        &:hover { background: rgba(255,255,255,0.3); }
      }
    }

    @keyframes slideUp {
      from { transform: translateX(-50%) translateY(20px); opacity: 0; }
      to { transform: translateX(-50%) translateY(0); opacity: 1; }
    }

    /* ═══════ FOOTER ═══════ */
    .footer {
      padding: 18px 0;
      border-top: 1px solid var(--gray-200);
      background: rgba(255,255,255,0.5);
    }

    .footer-content {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      font-size: 0.82rem;
      color: var(--gray-400);
      font-weight: 500;
    }

    .footer-sep { color: var(--gray-300); }

    /* ═══════ RESPONSIVE ═══════ */
    @media (max-width: 768px) {
      .stats-grid { grid-template-columns: repeat(2, 1fr); }
      .card-header { flex-direction: column; gap: 12px; }
      .header-actions { width: 100%; justify-content: flex-end; }
      .step-text { display: none; }
      .score-summary { flex-wrap: wrap; }
      .score-item { min-width: 50%; }
    }
  `]
})
export class AppComponent implements OnInit {
  currentStep = 1;
  state: AppState = 'idle';
  isDragging = false;
  errorMessage = '';
  debugMode = true;
  showExportMenu = false;
  passThreshold = 40;

  currentAnswerKey: AnswerKey | null = null;
  selectedExamFiles: File[] = [];
  results: GradingResult[] = [];
  selectedResult: GradingResult | null = null;
  
  debugResults: { [fileName: string]: FullPipelineResult } = {};

  questionNumbers = Array.from({ length: 20 }, (_, i) => i + 1);
  answerOptions = ['A', 'B', 'C', 'D'];
  manualAnswers: { [key: number]: string } = {};

  constructor(private gradingService: GradingService) {}

  ngOnInit() {
    // Keep step 1 by default; answer key must be uploaded or entered manually.
  }

  loadCurrentAnswerKey() {
    this.gradingService.getCurrentAnswerKey().subscribe({
      next: (key) => {
        this.currentAnswerKey = key;
        if (key) this.currentStep = 2;
      },
      error: () => {}
    });
  }

  goToNextStep() {
    this.currentStep = 2;
  }

  downloadTemplate() {
    const template = `Question,Answer
1,A
2,B
3,C
4,D
5,A
6,B
7,C
8,D
9,A
10,B
11,C
12,D
13,A
14,B
15,C
16,D
17,A
18,B
19,C
20,D`;

    const blob = new Blob([template], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'answer_key_template.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDragging = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    this.isDragging = false;
  }

  onDropAnswerKey(event: DragEvent) {
    event.preventDefault();
    this.isDragging = false;
    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.uploadAnswerKey(files[0]);
    }
  }

  onAnswerKeySelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.uploadAnswerKey(input.files[0]);
    }
    input.value = '';
  }

  uploadAnswerKey(file: File) {
    this.state = 'uploading';
    this.errorMessage = '';

    this.gradingService.uploadAnswerKey(file).subscribe({
      next: (response) => {
        if (response.success) {
          this.currentAnswerKey = {
            id: response.id!,
            name: response.name!,
            answers: response.answers!,
            createdAt: new Date().toISOString()
          };
        } else {
          this.errorMessage = response.errorMessage || 'Failed to upload';
        }
        this.state = 'idle';
      },
      error: (err) => {
        this.errorMessage = err.message;
        this.state = 'idle';
      }
    });
  }

  setManualAnswer(questionNumber: number, option: string) {
    this.manualAnswers[questionNumber] = option;
  }

  clearManualAnswers() {
    this.manualAnswers = {};
  }

  isManualKeyComplete(): boolean {
    return this.questionNumbers.every((q) => !!this.manualAnswers[q]);
  }

  saveManualAnswerKey() {
    if (!this.isManualKeyComplete()) {
      this.errorMessage = 'Please select answers for all 20 questions.';
      return;
    }

    const rows = ['Question,Answer'];
    for (const q of this.questionNumbers) {
      rows.push(`${q},${this.manualAnswers[q]}`);
    }

    const csv = rows.join('\n');
    const file = new File(
      [csv],
      `manual_answer_key_${new Date().toISOString().slice(0, 10)}.csv`,
      { type: 'text/csv' }
    );
    this.uploadAnswerKey(file);
  }

  onDropExams(event: DragEvent) {
    event.preventDefault();
    this.isDragging = false;
    const files = event.dataTransfer?.files;
    if (files) {
      this.addExamFiles(Array.from(files));
    }
  }

  onExamsSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      this.addExamFiles(Array.from(input.files));
    }
    input.value = '';
  }

  addExamFiles(files: File[]) {
    const imageFiles = files.filter(f => f.type.startsWith('image/'));
    this.selectedExamFiles = [...this.selectedExamFiles, ...imageFiles];
  }

  removeFile(index: number) {
    this.selectedExamFiles.splice(index, 1);
  }

  clearFiles() {
    this.selectedExamFiles = [];
  }

  formatFileSize(bytes: number): string {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  }

  startGrading() {
    if (this.selectedExamFiles.length === 0) return;

    this.normalizePassThreshold();
    this.state = 'grading';
    this.errorMessage = '';
    this.debugResults = {};
    this.startDebugGrading();
  }

  startDebugGrading() {
    const files = [...this.selectedExamFiles];
    this.results = [];
    let processed = 0;

    files.forEach(file => {
      this.gradingService.fullPipeline(file).subscribe({
        next: (pipelineResult) => {
          this.debugResults[file.name] = pipelineResult;
          const studentId = this.getStudentIdFromOcr(pipelineResult.ocrResponse);
          
          const gradingResult: GradingResult = {
            success: pipelineResult.success,
            studentId,
            fileName: file.name,
            detectedAnswers: pipelineResult.yoloResponse?.answers || {},
            questionResults: (pipelineResult.comparisonResponse?.comparisons || []).map(c => ({
              questionNumber: c.questionNumber,
              studentAnswer: c.detectedAnswer,
              correctAnswer: c.correctAnswer,
              isCorrect: c.isMatch,
              status: c.isMatch ? 'CORRECT' as const : (c.detectedAnswer === '-' ? 'BLANK' as const : 'WRONG' as const)
            })),
            correctCount: pipelineResult.comparisonResponse?.correctCount || 0,
            totalQuestions: pipelineResult.comparisonResponse?.totalQuestions || 0,
            scorePercentage: pipelineResult.comparisonResponse?.scorePercentage || 0,
            processedAt: new Date().toISOString()
          };

          this.results.push(gradingResult);
          processed++;

          if (processed === files.length) {
            this.state = 'complete';
            this.currentStep = 3;
          }
        },
        error: (err) => {
          processed++;
          this.results.push({
            success: false,
            fileName: file.name,
            errorMessage: err.message,
            detectedAnswers: {},
            questionResults: [],
            correctCount: 0,
            totalQuestions: 0,
            scorePercentage: 0,
            processedAt: new Date().toISOString()
          });

          if (processed === files.length) {
            this.state = 'complete';
            this.currentStep = 3;
          }
        }
      });
    });
  }

  getAnswerCount(key: AnswerKey): number {
    return Object.keys(key.answers).length;
  }

  getSuccessCount(): number {
    return this.results.filter(r => r.success).length;
  }

  getAverageScore(): number {
    const successful = this.results.filter(r => r.success);
    if (successful.length === 0) return 0;
    return successful.reduce((sum, r) => sum + r.scorePercentage, 0) / successful.length;
  }

  getHighestScore(): number {
    const successful = this.results.filter(r => r.success);
    if (successful.length === 0) return 0;
    return Math.max(...successful.map(r => r.scorePercentage));
  }

  getLowestScore(): number {
    const successful = this.results.filter(r => r.success);
    if (successful.length === 0) return 0;
    return Math.min(...successful.map(r => r.scorePercentage));
  }

  normalizePassThreshold() {
    const parsed = Number(this.passThreshold);
    if (!Number.isFinite(parsed)) {
      this.passThreshold = 40;
      return;
    }
    this.passThreshold = Math.max(0, Math.min(100, Math.round(parsed)));
  }

  hasPassed(result: GradingResult): boolean {
    return result.success && result.scorePercentage > this.passThreshold;
  }

  getStudentIdFromOcr(ocr?: OcrResponse): string | undefined {
    if (!ocr) return undefined;
    return ocr.extractedNumber || ocr.extracted_number || undefined;
  }

  getOcrError(ocr?: OcrResponse): string {
    if (!ocr) return '';
    return ocr.errorMessage || ocr.error_message || '';
  }

  getRawOcrText(ocr?: OcrResponse): string {
    if (!ocr) return '';
    return ocr.rawOcrText || ocr.raw_ocr_text || '';
  }

  getStudentAnswer(result: GradingResult, questionNumber: number): string {
    const qr = result.questionResults.find(q => q.questionNumber === questionNumber);
    return qr?.studentAnswer || '';
  }

  getQuestionStatus(result: GradingResult, questionNumber: number): string {
    const qr = result.questionResults.find(q => q.questionNumber === questionNumber);
    return qr?.status || '';
  }

  getCorrectAnswer(result: GradingResult, questionNumber: number): string {
    const qr = result.questionResults.find(q => q.questionNumber === questionNumber);
    return qr?.correctAnswer || '';
  }

  getYoloAnswersArray(fileName: string): { q: number; a: string }[] {
    const pipelineResult = this.debugResults[fileName];
    if (!pipelineResult?.yoloResponse?.answers) return [];
    
    return Object.entries(pipelineResult.yoloResponse.answers)
      .map(([q, a]) => ({ q: parseInt(q, 10), a }))
      .sort((x, y) => x.q - y.q);
  }

  private csvEscape(value: string | number | boolean | undefined | null): string {
    const s = value === undefined || value === null ? '' : String(value);
    if (/[",\r\n]/.test(s)) {
      return '"' + s.replace(/"/g, '""') + '"';
    }
    return s;
  }

  private downloadCsv(filename: string, rows: string[][]) {
    const lines = rows.map((row) => row.map((c) => this.csvEscape(c)).join(','));
    const csv = lines.join('\n');
    const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  private yoloAnswersForResult(result: GradingResult): { [key: number]: string } {
    const fn = result.fileName || '';
    const fromDebug = this.debugResults[fn]?.yoloResponse?.answers;
    if (fromDebug && Object.keys(fromDebug).length > 0) {
      return { ...fromDebug };
    }
    if (result.detectedAnswers && Object.keys(result.detectedAnswers).length > 0) {
      return { ...result.detectedAnswers };
    }
    const map: { [key: number]: string } = {};
    for (const qr of result.questionResults) {
      const a = qr.studentAnswer;
      if (a && a !== '-') {
        map[qr.questionNumber] = a;
      }
    }
    return map;
  }

  exportYoloCsv() {
    const qHeaders = this.questionNumbers.map((q) => `Q${q}`);
    const headers = [
      'File_Name',
      'YOLO_Success',
      'Method',
      'Total_Detections',
      ...qHeaders,
      ...this.questionNumbers.flatMap((q) => [`Q${q}_Confidence`])
    ];

    const rows: string[][] = [headers];

    for (const result of this.results) {
      const fn = result.fileName || '';
      const yolo = this.debugResults[fn]?.yoloResponse;
      const answers = this.yoloAnswersForResult(result);
      const confByQ = new Map<number, number>();
      if (yolo?.detectedAnswers?.length) {
        for (const d of yolo.detectedAnswers) {
          confByQ.set(d.question, d.confidence);
        }
      }

      const row: (string | number)[] = [
        fn,
        yolo ? (yolo.success ? 'TRUE' : 'FALSE') : result.success ? 'TRUE' : 'FALSE',
        yolo?.method ?? '',
        yolo?.totalDetections ?? Object.keys(answers).length
      ];

      for (const q of this.questionNumbers) {
        row.push(answers[q] ?? '');
      }
      for (const q of this.questionNumbers) {
        const c = confByQ.get(q);
        row.push(c !== undefined ? Math.round(c * 1000) / 1000 : '');
      }

      rows.push(row.map(String));
    }

    this.downloadCsv(`export_yolo_${new Date().toISOString().slice(0, 10)}.csv`, rows);
  }

  exportOcrNetCsv() {
    const headers = [
      'File_Name',
      'Extracted_Number',
      'Student_ID_Success',
      'Confidence',
      'Raw_Text',
      'Error_Message'
    ];
    const rows: string[][] = [headers];

    for (const result of this.results) {
      const fn = result.fileName || '';
      const ocr = this.debugResults[fn]?.ocrResponse;
      rows.push([
        fn,
        this.getStudentIdFromOcr(ocr) ?? result.studentId ?? '',
        ocr ? (ocr.success ? 'TRUE' : 'FALSE') : result.studentId ? 'TRUE' : 'FALSE',
        ocr?.confidence !== undefined ? String(ocr.confidence) : '',
        this.getRawOcrText(ocr),
        this.getOcrError(ocr) || result.errorMessage || ''
      ]);
    }

    this.downloadCsv(`export_dotnet_number_${new Date().toISOString().slice(0, 10)}.csv`, rows);
  }

  exportComparisonCsv() {
    const rows: string[][] = [];

    for (const result of this.results) {
      if (rows.length === 0) {
        rows.push(['ROW_TYPE', 'File_Name', 'Student_ID', 'Score_Percentage', 'Passing_Threshold', 'Status', ...this.questionNumbers.map((q) => `Q${q}`)]);
      }

      const status = this.hasPassed(result) ? 'PASS' : 'FAIL';
      const score = String(result.scorePercentage);
      const threshold = String(this.passThreshold);
      const keyRow: string[] = ['KEY', result.fileName || '', result.studentId || 'Unknown', score, threshold, status];
      const answersRow: string[] = ['ANSWERS', result.fileName || '', result.studentId || 'Unknown', score, threshold, status];
      const statusRow: string[] = ['RESULT', result.fileName || '', result.studentId || 'Unknown', score, threshold, status];

      for (const q of this.questionNumbers) {
        const qr = result.questionResults.find((qres) => qres.questionNumber === q);
        keyRow.push((qr?.correctAnswer || '-').toUpperCase());
        answersRow.push((qr?.studentAnswer || '-').toUpperCase());
        statusRow.push(qr ? (qr.isCorrect ? 'CORRECT' : 'INCORRECT') : 'INCORRECT');
      }

      rows.push(keyRow, answersRow, statusRow, []);
    }

    this.downloadCsv(`export_comparison_${new Date().toISOString().slice(0, 10)}.csv`, rows);
  }

  clearOutputs() {
    this.results = [];
    this.selectedResult = null;
    this.debugResults = {};
    this.showExportMenu = false;
    this.state = 'idle';
    this.currentStep = 2;
  }

  resetAndStartNew() {
    this.selectedExamFiles = [];
    this.results = [];
    this.selectedResult = null;
    this.debugResults = {};
    this.currentStep = 2;
    this.state = 'idle';
  }
}

