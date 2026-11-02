package plagiarismcheckerplus

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

type reply struct {
	status  int
	headers map[string]string
	body    string
}

func server(t *testing.T, replies []reply, seen *[]*http.Request, bodies *[]string) *Client {
	t.Helper()
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		raw, _ := io.ReadAll(r.Body)
		*seen = append(*seen, r)
		*bodies = append(*bodies, string(raw))
		next := replies[0]
		replies = replies[1:]
		for k, v := range next.headers {
			w.Header().Set(k, v)
		}
		w.WriteHeader(next.status)
		_, _ = w.Write([]byte(next.body))
	}))
	t.Cleanup(srv.Close)
	c := NewClient("pcp_test")
	c.BaseURL = srv.URL
	return c
}

func TestCreateScan(t *testing.T) {
	var seen []*http.Request
	var bodies []string
	c := server(t, []reply{{202, nil, `{"id":"s1","status":"processing"}`}}, &seen, &bodies)
	out, err := c.CreateScan(context.Background(), "text", []string{ToolPlagiarism}, "draft")
	if err != nil || out.ID != "s1" {
		t.Fatalf("got %v, %v", out, err)
	}
	if seen[0].Method != http.MethodPost || seen[0].URL.Path != "/scans" {
		t.Fatalf("bad request %s %s", seen[0].Method, seen[0].URL.Path)
	}
	if seen[0].Header.Get("Authorization") != "Bearer pcp_test" {
		t.Fatal("missing bearer token")
	}
	var body map[string]any
	_ = json.Unmarshal([]byte(bodies[0]), &body)
	if body["text"] != "text" || body["name"] != "draft" {
		t.Fatalf("bad body %v", body)
	}
}

func TestQueryParameters(t *testing.T) {
	var seen []*http.Request
	var bodies []string
	c := server(t, []reply{{200, nil, `{"id":"s1"}`}, {200, nil, `{"data":[]}`}}, &seen, &bodies)
	if _, err := c.GetScan(context.Background(), "s1", true); err != nil {
		t.Fatal(err)
	}
	if _, err := c.ListScans(context.Background(), 2, 5); err != nil {
		t.Fatal(err)
	}
	if seen[0].URL.RawQuery != "include_text=true" || !strings.HasSuffix(seen[0].URL.Path, "/scans/s1") {
		t.Fatalf("bad getScan url %s", seen[0].URL)
	}
	if seen[1].URL.RawQuery != "limit=5&page=2" {
		t.Fatalf("bad listScans query %s", seen[1].URL.RawQuery)
	}
}

func TestErrorCode(t *testing.T) {
	var seen []*http.Request
	var bodies []string
	c := server(t, []reply{{403, nil, `{"error":{"code":"plan_required","message":"Paid plan needed"}}`}}, &seen, &bodies)
	_, err := c.GetAccount(context.Background())
	var apiErr *Error
	if !errors.As(err, &apiErr) || apiErr.Status != 403 || apiErr.Code != CodePlanRequired {
		t.Fatalf("got %v", err)
	}
}

func TestWaitHonoursRetryAfter(t *testing.T) {
	var seen []*http.Request
	var bodies []string
	c := server(t, []reply{
		{200, nil, `{"id":"s1","status":"processing"}`},
		{429, map[string]string{"Retry-After": "3"}, `{"error":{"code":"rate_limited","message":"Slow down"}}`},
		{200, nil, `{"id":"s1","status":"completed"}`},
	}, &seen, &bodies)
	var waits []time.Duration
	c.Sleep = func(_ context.Context, d time.Duration) error { waits = append(waits, d); return nil }
	scan, err := c.WaitForScan(context.Background(), "s1", WaitOptions{Interval: time.Second})
	if err != nil || scan.Status != "completed" {
		t.Fatalf("got %v, %v", scan, err)
	}
	if len(waits) != 2 || waits[0] != time.Second || waits[1] != 3*time.Second {
		t.Fatalf("bad waits %v", waits)
	}
}

func TestWaitTimesOut(t *testing.T) {
	var seen []*http.Request
	var bodies []string
	c := server(t, []reply{{200, nil, `{"id":"s1","status":"processing"}`}}, &seen, &bodies)
	c.Sleep = func(context.Context, time.Duration) error { return nil }
	_, err := c.WaitForScan(context.Background(), "s1", WaitOptions{Timeout: 10 * time.Millisecond, Interval: time.Second})
	if !errors.Is(err, ErrScanTimeout) {
		t.Fatalf("got %v", err)
	}
}
