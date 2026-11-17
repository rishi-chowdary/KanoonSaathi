package com.lexilegal.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.util.UUID;

public record ChatQuestionRequest(
    UUID conversationId,
    @NotBlank(message = "question message must not be blank")
    @Size(max = 2000, message = "question must not exceed 2000 characters")
    String message
) {}
