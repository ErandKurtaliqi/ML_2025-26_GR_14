export interface AnswerKey {
  id: string;
  name: string;
  answers: { [key: number]: string };
  createdAt: string;
}

export interface AnswerKeyResponse {
  success: boolean;
  id?: string;
  name?: string;
  answerCount?: number;
  answers?: { [key: number]: string };
  errorMessage?: string;
}

export interface QuestionResult {
  questionNumber: number;
  studentAnswer?: string;
  correctAnswer?: string;
  isCorrect: boolean;
  status: 'CORRECT' | 'WRONG' | 'BLANK';
}

export interface GradingResult {
  success: boolean;
  studentId?: string;
  fileName?: string;
  detectedAnswers: { [key: number]: string };
  questionResults: QuestionResult[];
  correctCount: number;
  totalQuestions: number;
  scorePercentage: number;
  errorMessage?: string;
  processedAt: string;
}

export interface BatchGradingResult {
  results: GradingResult[];
  totalProcessed: number;
  successCount: number;
  failedCount: number;
  averageScore: number;
  answerKeyId?: string;
}

export type AppState = 'idle' | 'uploading' | 'grading' | 'complete' | 'error';

// Debug API Models
export interface YoloDetectionResponse {
  success: boolean;
  answers: { [key: number]: string };
  detectedAnswers: DetectedAnswer[];
  totalDetections: number;
  method: string;
  errorMessage?: string;
}

export interface DetectedAnswer {
  question: number;
  answer: string;
  confidence: number;
}

export interface OcrResponse {
  success: boolean;
  extractedNumber?: string;
  extracted_number?: string;
  rawOcrText?: string;
  raw_ocr_text?: string;
  confidence: number;
  errorMessage?: string;
  error_message?: string;
  fileName?: string;
  file_name?: string;
}

export interface QuestionComparison {
  questionNumber: number;
  detectedAnswer: string;
  correctAnswer: string;
  isMatch: boolean;
}

export interface ComparisonResponse {
  success: boolean;
  errorMessage?: string;
  comparisons: QuestionComparison[];
  totalQuestions: number;
  correctCount: number;
  scorePercentage: number;
}

export interface FullPipelineResult {
  success: boolean;
  errorMessage?: string;
  fileName?: string;
  yoloResponse?: YoloDetectionResponse;
  ocrResponse?: OcrResponse;
  comparisonResponse?: ComparisonResponse;
}
