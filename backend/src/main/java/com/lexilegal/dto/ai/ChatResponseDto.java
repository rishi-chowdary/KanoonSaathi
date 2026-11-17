package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public record ChatResponseDto(
    String answer,
    List<CitationItemDto> citations,
    String confidence,
    @JsonProperty("addressed_in_document") Boolean addressedInDocument
) {}
