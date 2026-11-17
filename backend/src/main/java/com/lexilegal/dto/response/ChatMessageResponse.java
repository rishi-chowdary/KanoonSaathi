package com.lexilegal.dto.response;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

public record ChatMessageResponse(
    UUID id,
    UUID conversationId,
    String role,
    String content,
    List<ChatCitationResponse> citations,
    Boolean addressedInDocument,
    Instant createdAt
) {}
