# Plagiarism Checker Plus for JavaScript and TypeScript

Official client for the [Plagiarism Checker Plus API](https://plagiarismcheckerplus.com/integrations/api). Works in Node.js 18+ and any runtime with `fetch`. No dependencies. Ships ESM, CommonJS and TypeScript types.

The API needs a paid plan. A key on the free plan returns `403 plan_required`.

```sh
npm install plagiarism-checker-plus
```

```js
import PlagiarismCheckerPlus, { PlagiarismCheckerPlusError, ErrorCodes } from "plagiarism-checker-plus";

const client = new PlagiarismCheckerPlus({ apiKey: process.env.PCP_API_KEY });

try {
  const { id } = await client.createScan(essayText, ["plagiarism", "ai_detect"], "essay-draft-1");
  const scan = await client.waitForScan(id);

  console.log("Matched:", scan.results.plagiarism?.score, "%");
  for (const source of scan.results.plagiarism?.sources ?? []) console.log(source.url);

  // A likelihood, not proof that the text was written by AI.
  console.log("AI likelihood:", scan.results.aiDetection?.score, "%");
} catch (error) {
  if (error instanceof PlagiarismCheckerPlusError && error.code === ErrorCodes.TEXT_TOO_SHORT) {
    console.error("Send at least 30 words for plagiarism, 50 for AI detection.");
  } else {
    throw error;
  }
}
```

CommonJS: `const { PlagiarismCheckerPlus } = require("plagiarism-checker-plus");`

## Methods

| Method | API call |
|---|---|
| `createScan(text, tools, name?)` | `POST /scans` |
| `getScan(id, { includeText })` | `GET /scans/{id}` |
| `listScans({ page, limit })` | `GET /scans` |
| `getAccount()` | `GET /account` |
| `waitForScan(id, { timeout, interval, maxInterval })` | Polls `GET /scans/{id}` until `completed` or `failed` |

`waitForScan` starts at 2 seconds between polls, grows by 1.5× up to 10 seconds, waits for `Retry-After` on `429`, and throws `ScanTimeoutError` after 5 minutes by default.

Failed calls throw `PlagiarismCheckerPlusError` with `status`, `code` (such as `plan_required`, `text_too_short`, `doc_too_long`, `insufficient_words`) and `retryAfter`.

Each tool is billed at the full word count. The rate limit is 60 requests a minute per key.

MIT licensed. Copyright (c) 2026 Plagiarism Checker Plus.
