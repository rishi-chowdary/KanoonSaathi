package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public record ChatRequestDto(
    String question,
    @JsonProperty("retrieved_chunks") List<ChatRetrievedChunkDto> retrievedChunks,
    @JsonProperty("conversation_history") List<ChatMessageHistoryDto> conversationHistory
) {}
