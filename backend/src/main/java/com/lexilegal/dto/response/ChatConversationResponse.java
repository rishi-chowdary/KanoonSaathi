package com.lexilegal.dto.response;

import java.time.Instant;
import java.util.UUID;

public record ChatConversationResponse(
    UUID id,
    UUID documentId,
    String title,
    Instant createdAt,
    Instant updatedAt,
    Integer messageCount,
    ChatMessageResponse lastMessage
) {}

