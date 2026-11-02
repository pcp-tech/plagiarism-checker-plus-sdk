package com.plagiarismcheckerplus.sdk;

/** Thrown by {@link PlagiarismCheckerPlus#waitForScan} when the timeout passes. */
public class ScanTimeoutException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    public ScanTimeoutException(String message) {
        super(message);
    }
}
