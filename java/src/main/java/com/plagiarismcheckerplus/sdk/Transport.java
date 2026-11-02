package com.plagiarismcheckerplus.sdk;

import java.io.IOException;
import java.util.Map;

/** Sends one HTTP request. Swap in your own for proxies or tests. */
@FunctionalInterface
public interface Transport {
    Response send(String method, String url, Map<String, String> headers, String body) throws IOException, InterruptedException;

    /** One HTTP response. */
    final class Response {
        public final int status;
        public final Map<String, String> headers;
        public final String body;

        public Response(int status, Map<String, String> headers, String body) {
            this.status = status;
            this.headers = headers;
            this.body = body;
        }

        public String header(String name) {
            for (Map.Entry<String, String> e : headers.entrySet()) {
                if (e.getKey().equalsIgnoreCase(name)) return e.getValue();
            }
            return null;
        }
    }
}
