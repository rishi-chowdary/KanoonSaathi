package com.lexilegal.security;

import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

@Component
public class LoginRateLimiter {

    private static final int MAX_ATTEMPTS = 5;
    private static final long WINDOW_SECONDS = 60;

    private final Map<String, Window> attempts = new ConcurrentHashMap<>();

    public boolean tryAcquire(String clientIp) {
        long now = Instant.now().getEpochSecond();
        Window window = attempts.compute(clientIp, (key, existing) -> {
            if (existing == null || now - existing.startTime >= WINDOW_SECONDS) {
                return new Window(now, new AtomicInteger(1));
            }
            existing.count.incrementAndGet();
            return existing;
        });

        return window.count.get() <= MAX_ATTEMPTS;
    }

    public void reset(String clientIp) {
        attempts.remove(clientIp);
    }

    private static class Window {
        final long startTime;
        final AtomicInteger count;

        Window(long startTime, AtomicInteger count) {
            this.startTime = startTime;
            this.count = count;
        }
    }
}

