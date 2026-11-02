"use strict";

// Client for the Plagiarism Checker Plus public API (openapi.json at the repo root).

const DEFAULT_BASE_URL = "https://app.plagiarismcheckerplus.com/api/public/v1";
const VERSION = "1.0.0";

const ErrorCodes = Object.freeze({
  PLAN_REQUIRED: "plan_required",
  TEXT_TOO_SHORT: "text_too_short",
  DOC_TOO_LONG: "doc_too_long",
  INSUFFICIENT_WORDS: "insufficient_words",
});

class PlagiarismCheckerPlusError extends Error {
  constructor(message, { status = 0, code = null, retryAfter = null, body = null } = {}) {
    super(message);
    this.name = "PlagiarismCheckerPlusError";
    this.status = status;
    this.code = code;
    this.retryAfter = retryAfter;
    this.body = body;
  }
}

class ScanTimeoutError extends Error {
  constructor(scanId, timeoutMs) {
    super(`Scan ${scanId} did not finish within ${timeoutMs} ms`);
    this.name = "ScanTimeoutError";
    this.scanId = scanId;
  }
}

/** Seconds from a Retry-After header (delta-seconds or HTTP date), or null. */
function parseRetryAfter(value) {
  if (value == null || value === "") return null;
  const seconds = Number(value);
  if (Number.isFinite(seconds)) return Math.max(0, seconds);
  const date = Date.parse(value);
  return Number.isNaN(date) ? null : Math.max(0, (date - Date.now()) / 1000);
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

class PlagiarismCheckerPlus {
  /**
   * @param {object} options
   * @param {string} options.apiKey Your API key (pcp_...).
   * @param {string} [options.baseUrl]
   * @param {typeof fetch} [options.fetch] Custom fetch, for tests or proxies.
   */
  constructor({ apiKey, baseUrl = DEFAULT_BASE_URL, fetch: fetchImpl } = {}) {
    if (!apiKey) throw new TypeError("apiKey is required");
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.replace(/\/+$/, "");
    this.fetch = fetchImpl || globalThis.fetch;
    if (typeof this.fetch !== "function") throw new TypeError("fetch is not available; pass options.fetch");
  }

  async request(method, path, { query, body } = {}) {
    const url = new URL(this.baseUrl + path);
    for (const [key, value] of Object.entries(query || {})) {
      if (value !== undefined && value !== null) url.searchParams.set(key, String(value));
    }
    const headers = {
      Authorization: `Bearer ${this.apiKey}`,
      Accept: "application/json",
      "User-Agent": `plagiarism-checker-plus-js/${VERSION}`,
    };
    if (body !== undefined) headers["Content-Type"] = "application/json";
    const response = await this.fetch(url.toString(), {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
    const raw = await response.text();
    let data = null;
    if (raw) {
      try {
        data = JSON.parse(raw);
      } catch {
        data = null;
      }
    }
    if (!response.ok) {
      const error = (data && data.error) || {};
      throw new PlagiarismCheckerPlusError(error.message || `HTTP ${response.status}`, {
        status: response.status,
        code: error.code || null,
        retryAfter: parseRetryAfter(response.headers.get("retry-after")),
        body: data,
      });
    }
    return data;
  }

  /** Submit text. tools: array of "plagiarism" and/or "ai_detect". Returns 202 body. */
  createScan(text, tools, name) {
    const body = { text, tools };
    if (name !== undefined) body.name = name;
    return this.request("POST", "/scans", { body });
  }

  /** Read a scan and its results. */
  getScan(id, { includeText = false } = {}) {
    return this.request("GET", `/scans/${encodeURIComponent(id)}`, {
      query: includeText ? { include_text: "true" } : undefined,
    });
  }

  /** List scans, newest first. */
  listScans({ page, limit } = {}) {
    return this.request("GET", "/scans", { query: { page, limit } });
  }

  /** Plan and remaining words. */
  getAccount() {
    return this.request("GET", "/account");
  }

  /**
   * Poll until the scan is completed or failed. Waits interval ms, growing by
   * 1.5x up to maxInterval; on 429 waits for Retry-After instead.
   */
  async waitForScan(id, { timeout = 300_000, interval = 2_000, maxInterval = 10_000, includeText = false, sleep: sleepFn = sleep } = {}) {
    const deadline = Date.now() + timeout;
    let delay = interval;
    for (;;) {
      let wait = delay;
      try {
        const scan = await this.getScan(id, { includeText });
        if (scan.status === "completed" || scan.status === "failed") return scan;
        delay = Math.min(Math.round(delay * 1.5), maxInterval);
      } catch (error) {
        if (!(error instanceof PlagiarismCheckerPlusError) || error.status !== 429) throw error;
        wait = error.retryAfter != null ? error.retryAfter * 1000 : delay;
      }
      if (Date.now() + wait > deadline) throw new ScanTimeoutError(id, timeout);
      await sleepFn(wait);
    }
  }
}

module.exports = {
  PlagiarismCheckerPlus,
  PlagiarismCheckerPlusError,
  ScanTimeoutError,
  ErrorCodes,
  DEFAULT_BASE_URL,
  parseRetryAfter,
};
