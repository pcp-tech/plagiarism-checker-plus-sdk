# Plagiarism Checker Plus for Go

Official client for the [Plagiarism Checker Plus API](https://plagiarismcheckerplus.com/integrations/api). Go 1.21+, standard library only.

The API needs a paid plan. A key on the free plan returns `403 plan_required`.

```sh
go get github.com/pcp-tech/plagiarism-checker-plus-sdk/go
```

```go
package main

import (
	"context"
	"errors"
	"fmt"
	"log"
	"os"

	pcp "github.com/pcp-tech/plagiarism-checker-plus-sdk/go"
)

func main() {
	ctx := context.Background()
	client := pcp.NewClient(os.Getenv("PCP_API_KEY"))

	created, err := client.CreateScan(ctx, essayText, []string{pcp.ToolPlagiarism, pcp.ToolAIDetect}, "essay-draft-1")
	var apiErr *pcp.Error
	if errors.As(err, &apiErr) && apiErr.Code == pcp.CodeTextTooShort {
		log.Fatal("Send at least 30 words for plagiarism, 50 for AI detection.")
	} else if err != nil {
		log.Fatal(err)
	}

	scan, err := client.WaitForScan(ctx, created.ID, pcp.WaitOptions{})
	if err != nil {
		log.Fatal(err)
	}
	if scan.Results == nil {
		log.Fatalf("scan ended with status %s", scan.Status)
	}
	if p := scan.Results.Plagiarism; p != nil {
		fmt.Printf("Matched: %.1f%%\n", p.Score)
		for _, s := range p.Sources {
			fmt.Println(s.URL)
		}
	}
	// A likelihood, not proof that the text was written by AI.
	if a := scan.Results.AIDetection; a != nil {
		fmt.Printf("AI likelihood: %.1f%%\n", a.Score)
	}
}
```

## Methods

| Method | API call |
|---|---|
| `CreateScan(ctx, text, tools, name)` | `POST /scans` |
| `GetScan(ctx, id, includeText)` | `GET /scans/{id}` |
| `ListScans(ctx, page, limit)` | `GET /scans` |
| `GetAccount(ctx)` | `GET /account` |
| `WaitForScan(ctx, id, WaitOptions{})` | Polls until `completed` or `failed` |

`WaitForScan` starts at 2 seconds, grows by 1.5× up to 10 seconds, waits for `Retry-After` on `429`, and returns `ErrScanTimeout` after 5 minutes by default.

Failed calls return `*pcp.Error` with `Status`, `Code` (such as `plan_required`, `text_too_short`, `doc_too_long`, `insufficient_words`) and `RetryAfter`.

Run the tests with `go test ./...`.

MIT licensed. Copyright (c) 2026 Plagiarism Checker Plus.
