package com.plagiarismcheckerplus.sdk;

/** A non-2xx response. {@link #getErrorCode()} is the API's code, such as plan_required. */
public class ApiException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    public static final String PLAN_REQUIRED = "plan_required";
    public static final String TEXT_TOO_SHORT = "text_too_short";
    public static final String DOC_TOO_LONG = "doc_too_long";
    public static final String INSUFFICIENT_WORDS = "insufficient_words";

    private final int status;
    private final String errorCode;
    private final Double retryAfterSeconds;
    private final transient Object body;

    public ApiException(String message, int status, String errorCode, Double retryAfterSeconds, Object body) {
        super(message);
        this.status = status;
        this.errorCode = errorCode;
        this.retryAfterSeconds = retryAfterSeconds;
        this.body = body;
    }

    public int getStatus() { return status; }

    public String getErrorCode() { return errorCode; }

    /** Seconds from Retry-After, or null if not sent. */
    public Double getRetryAfterSeconds() { return retryAfterSeconds; }

    public Object getBody() { return body; }
}
