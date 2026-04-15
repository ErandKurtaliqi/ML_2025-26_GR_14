import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';
import { 
  AnswerKey, 
  AnswerKeyResponse, 
  GradingResult, 
  BatchGradingResult,
  YoloDetectionResponse,
  OcrResponse,
  ComparisonResponse,
  FullPipelineResult
} from '../models/grading.models';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class GradingService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  uploadAnswerKey(file: File, name?: string): Observable<AnswerKeyResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    let url = `${this.apiUrl}/grading/answer-key`;
    if (name) {
      url += `?name=${encodeURIComponent(name)}`;
    }
    
    return this.http.post<AnswerKeyResponse>(url, formData).pipe(
      catchError(this.handleError)
    );
  }

  getCurrentAnswerKey(): Observable<AnswerKey> {
    return this.http.get<AnswerKey>(`${this.apiUrl}/grading/answer-key/current`).pipe(
      catchError(this.handleError)
    );
  }

  getAllAnswerKeys(): Observable<AnswerKey[]> {
    return this.http.get<AnswerKey[]>(`${this.apiUrl}/grading/answer-key`).pipe(
      catchError(this.handleError)
    );
  }

  activateAnswerKey(id: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/grading/answer-key/${id}/activate`, {}).pipe(
      catchError(this.handleError)
    );
  }

  deleteAnswerKey(id: string): Observable<any> {
    return this.http.delete(`${this.apiUrl}/grading/answer-key/${id}`).pipe(
      catchError(this.handleError)
    );
  }

  gradeExam(file: File, answerKeyId?: string): Observable<GradingResult> {
    const formData = new FormData();
    formData.append('file', file);
    
    let url = `${this.apiUrl}/grading/grade`;
    if (answerKeyId) {
      url += `?answerKeyId=${answerKeyId}`;
    }
    
    return this.http.post<GradingResult>(url, formData).pipe(
      catchError(this.handleError)
    );
  }

  gradeExamsBatch(files: File[], answerKeyId?: string): Observable<BatchGradingResult> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    
    let url = `${this.apiUrl}/grading/grade/batch`;
    if (answerKeyId) {
      url += `?answerKeyId=${answerKeyId}`;
    }
    
    return this.http.post<BatchGradingResult>(url, formData).pipe(
      catchError(this.handleError)
    );
  }

  exportToCsv(results: GradingResult[]): Observable<Blob> {
    return this.http.post(`${this.apiUrl}/grading/export/csv`, { results }, {
      responseType: 'blob'
    }).pipe(
      catchError(this.handleError)
    );
  }

  exportToExcel(results: GradingResult[]): Observable<Blob> {
    return this.http.post(`${this.apiUrl}/grading/export/excel`, { results }, {
      responseType: 'blob'
    }).pipe(
      catchError(this.handleError)
    );
  }

  // Debug API Methods - Individual Steps
  
  yoloDetect(file: File): Observable<YoloDetectionResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<YoloDetectionResponse>(`${this.apiUrl}/debug/yolo-detect`, formData).pipe(
      catchError(this.handleError)
    );
  }

  ocrExtract(file: File): Observable<OcrResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<OcrResponse>(`${this.apiUrl}/debug/ocr-extract`, formData).pipe(
      catchError(this.handleError)
    );
  }

  compareAnswers(detectedAnswers: { [key: number]: string }, answerKeyId?: string): Observable<ComparisonResponse> {
    const body = { 
      detectedAnswers,
      answerKeyId 
    };
    return this.http.post<ComparisonResponse>(`${this.apiUrl}/debug/compare`, body).pipe(
      catchError(this.handleError)
    );
  }

  fullPipeline(file: File, answerKeyId?: string): Observable<FullPipelineResult> {
    const formData = new FormData();
    formData.append('file', file);
    
    let url = `${this.apiUrl}/debug/full-pipeline`;
    if (answerKeyId) {
      url += `?answerKeyId=${answerKeyId}`;
    }
    
    return this.http.post<FullPipelineResult>(url, formData).pipe(
      catchError(this.handleError)
    );
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An error occurred';
    
    if (error.error instanceof ErrorEvent) {
      errorMessage = error.error.message;
    } else if (error.error?.errorMessage) {
      errorMessage = error.error.errorMessage;
    } else if (error.error?.message) {
      errorMessage = error.error.message;
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    return throwError(() => new Error(errorMessage));
  }
}
