package com.plagiarismcheckerplus.sdk;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.DoubleConsumer;

/**
 * Client for the Plagiarism Checker Plus public API. Responses are returned
 * as {@code Map<String, Object>} that mirror the API's JSON.
 */
public final class PlagiarismCheckerPlus {
    public static final String DEFAULT_BASE_URL = "https://app.plagiarismcheckerplus.com/api/public/v1";
    public static final String VERSION = "1.0.0";

    private final String apiKey;
    private final String baseUrl;
    private final Transport transport;
    private DoubleConsumer sleeper = PlagiarismCheckerPlus::sleepSeconds;

    public PlagiarismCheckerPlus(String apiKey) {
        this(apiKey, DEFAULT_BASE_URL, defaultTransport(Duration.ofSeconds(30)));
    }

    public PlagiarismCheckerPlus(String apiKey, String baseUrl, Transport transport) {
        if (apiKey == null || apiKey.isEmpty()) throw new IllegalArgumentException("apiKey is required");
        this.apiKey = apiKey;
        this.baseUrl = baseUrl.replaceAll("/+$", "");
        this.transport = transport;
    }

    /** Replace how waitForScan sleeps (seconds). Useful in tests. */
    public PlagiarismCheckerPlus withSleeper(DoubleConsumer sleeper) {
        this.sleeper = sleeper;
        return this;
    }

    /** Submit text. tools: any of "plagiarism" and "ai_detect". name may be null. */
    public Map<String, Object> createScan(String text, List<String> tools, String name) {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("text", text);
        body.put("tools", tools);
        if (name != null) body.put("name", name);
        return request("POST", "/scans", null, body);
    }

    public Map<String, Object> getScan(String id, boolean includeText) {
        return request("GET", "/scans/" + encode(id), includeText ? "include_text=true" : null, null);
    }

    /** List scans, newest first. Null page or limit uses the API default. */
    public Map<String, Object> listScans(Integer page, Integer limit) {
        StringBuilder q = new StringBuilder();
        if (page != null) q.append("page=").append(page);
        if (limit != null) q.append(q.length() > 0 ? "&" : "").append("limit=").append(limit);
        return request("GET", "/scans", q.length() > 0 ? q.toString() : null, null);
    }

    public Map<String, Object> getAccount() {
        return request("GET", "/account", null, null);
    }

    public Map<String, Object> waitForScan(String id) {
        return waitForScan(id, 300, 2, 10, false);
    }

    /** Poll until the scan is completed or failed, honouring Retry-After on 429. Times in seconds. */
    public Map<String, Object> waitForScan(String id, double timeout, double interval, double maxInterval, boolean includeText) {
        long deadline = System.nanoTime() + (long) (timeout * 1e9);
        double delay = interval;
        while (true) {
            double wait = delay;
            try {
                Map<String, Object> scan = getScan(id, includeText);
                Object status = scan.get("status");
                if ("completed".equals(status) || "failed".equals(status)) return scan;
                delay = Math.min(delay * 1.5, maxInterval);
            } catch (ApiException e) {
                if (e.getStatus() != 429) throw e;
                if (e.getRetryAfterSeconds() != null) wait = e.getRetryAfterSeconds();
            }
            if (System.nanoTime() + (long) (wait * 1e9) > deadline) {
                throw new ScanTimeoutException("Scan " + id + " did not finish within " + timeout + " seconds");
            }
            sleeper.accept(wait);
        }
    }

    /** Seconds from a Retry-After header (delta-seconds or HTTP date), or null. */
    public static Double parseRetryAfter(String value) {
        if (value == null || value.isEmpty()) return null;
        try {
            return Math.max(0, Double.parseDouble(value));
        } catch (NumberFormatException ignored) {
            // Not delta-seconds; try an HTTP date.
        }
        try {
            ZonedDateTime when = ZonedDateTime.parse(value, DateTimeFormatter.RFC_1123_DATE_TIME);
            return Math.max(0, (when.toInstant().toEpochMilli() - System.currentTimeMillis()) / 1000.0);
        } catch (RuntimeException e) {
            return null;
        }
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> request(String method, String path, String query, Map<String, Object> body) {
        String url = baseUrl + path + (query != null ? "?" + query : "");
        Map<String, String> headers = new LinkedHashMap<>();
        headers.put("Authorization", "Bearer " + apiKey);
        headers.put("Accept", "application/json");
        headers.put("User-Agent", "plagiarism-checker-plus-java/" + VERSION);
        String payload = null;
        if (body != null) {
            headers.put("Content-Type", "application/json");
            payload = Json.stringify(body);
        }
        Transport.Response response;
        try {
            response = transport.send(method, url, headers, payload);
        } catch (IOException e) {
            throw new ApiException("Request failed: " + e.getMessage(), 0, null, null, null);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new ApiException("Request interrupted", 0, null, null, null);
        }
        Object data = null;
        if (response.body != null && !response.body.isEmpty()) {
            try {
                data = Json.parse(response.body);
            } catch (RuntimeException ignored) {
                data = null;
            }
        }
        if (response.status < 200 || response.status >= 300) {
            Map<String, Object> error = Map.of();
            if (data instanceof Map && ((Map<String, Object>) data).get("error") instanceof Map) {
                error = (Map<String, Object>) ((Map<String, Object>) data).get("error");
            }
            Object message = error.get("message");
            Object code = error.get("code");
            throw new ApiException(
                    message != null ? message.toString() : "HTTP " + response.status,
                    response.status,
                    code != null ? code.toString() : null,
                    parseRetryAfter(response.header("Retry-After")),
                    data);
        }
        return data instanceof Map ? (Map<String, Object>) data : new LinkedHashMap<>();
    }

    private static String encode(String value) {
        return URLEncoder.encode(value, StandardCharsets.UTF_8).replace("+", "%20");
    }

    private static void sleepSeconds(double seconds) {
        try {
            Thread.sleep((long) (seconds * 1000));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new ApiException("Interrupted while waiting", 0, null, null, null);
        }
    }

    /** Default transport using java.net.http. */
    public static Transport defaultTransport(Duration timeout) {
        HttpClient client = HttpClient.newBuilder().connectTimeout(timeout).build();
        return (method, url, headers, body) -> {
            HttpRequest.Builder builder = HttpRequest.newBuilder(URI.create(url)).timeout(timeout)
                    .method(method, body == null
                            ? HttpRequest.BodyPublishers.noBody()
                            : HttpRequest.BodyPublishers.ofString(body, StandardCharsets.UTF_8));
            headers.forEach(builder::header);
            HttpResponse<String> response = client.send(builder.build(), HttpResponse.BodyHandlers.ofString());
            Map<String, String> out = new LinkedHashMap<>();
            response.headers().map().forEach((k, v) -> out.put(k, String.join(", ", v)));
            return new Transport.Response(response.statusCode(), out, response.body());
        };
    }
}
