export type Tool = "plagiarism" | "ai_detect";
export type ScanStatus = "pending" | "processing" | "completed" | "failed";

export interface ScanSummary {
  id: string;
  name: string | null;
  status: ScanStatus;
  /** Words in the submitted text. */
  wordCount: number;
  /** Words billed: wordCount × number of tools. */
  wordsCharged: number;
  tools: Tool[];
  createdAt: string;
  completedAt: string | null;
}

export interface PlagiarismSource {
  url: string;
  domain: string;
  matchPercentage: number;
  /** The passage from your text that matched. */
  matchedText: string;
  /** Surrounding text from the source page. */
  excerpt: string | null;
}

export interface AiSentence {
  text: string;
  /** 0–1 likelihood the sentence is AI-generated. A likelihood, not proof. */
  probability: number;
  offset: number;
  length: number;
}

export interface ScanDetail extends ScanSummary {
  /** Only present when includeText is true. */
  text?: string;
  progress?: { percent: number; tools: { tool: string; status: string; percent: number }[] };
  /** Populated as each tool finishes; null until then. */
  results?: {
    plagiarism?: { score: number; uniqueSources: number; sources: PlagiarismSource[] } | null;
    aiDetection?: { score: number; summary: string | null; sentences: AiSentence[] } | null;
  };
}

export interface CreateScanResponse {
  id: string;
  status: string;
  wordCount: number;
  wordsCharged: number;
  tools: string[];
}

export interface ScanList {
  data: ScanSummary[];
  pagination: { page: number; limit: number; total: number; totalPages: number };
}

export interface Account {
  id: string;
  email: string;
  plan: string;
  words: { monthlyLimit: number; monthlyUsed: number; monthlyRemaining: number; bonusBalance: number };
  limits: { maxDocumentWords: number | null };
  monthlyResetAt: string | null;
}

export interface ClientOptions {
  apiKey: string;
  baseUrl?: string;
  fetch?: typeof fetch;
}

export interface WaitOptions {
  /** Total time to wait in ms. Default 300000. */
  timeout?: number;
  /** First poll delay in ms. Default 2000. */
  interval?: number;
  /** Largest poll delay in ms. Default 10000. */
  maxInterval?: number;
  includeText?: boolean;
  sleep?: (ms: number) => Promise<void>;
}

export declare const DEFAULT_BASE_URL: string;
export declare const ErrorCodes: {
  readonly PLAN_REQUIRED: "plan_required";
  readonly TEXT_TOO_SHORT: "text_too_short";
  readonly DOC_TOO_LONG: "doc_too_long";
  readonly INSUFFICIENT_WORDS: "insufficient_words";
};

export declare class PlagiarismCheckerPlusError extends Error {
  status: number;
  /** The API's error code, e.g. "plan_required". */
  code: string | null;
  /** Seconds from Retry-After, if sent. */
  retryAfter: number | null;
  body: unknown;
}

export declare class ScanTimeoutError extends Error {
  scanId: string;
}

export declare function parseRetryAfter(value: string | null | undefined): number | null;

export declare class PlagiarismCheckerPlus {
  constructor(options: ClientOptions);
  createScan(text: string, tools: Tool[], name?: string): Promise<CreateScanResponse>;
  getScan(id: string, options?: { includeText?: boolean }): Promise<ScanDetail>;
  listScans(options?: { page?: number; limit?: number }): Promise<ScanList>;
  getAccount(): Promise<Account>;
  waitForScan(id: string, options?: WaitOptions): Promise<ScanDetail>;
}

export default PlagiarismCheckerPlus;
