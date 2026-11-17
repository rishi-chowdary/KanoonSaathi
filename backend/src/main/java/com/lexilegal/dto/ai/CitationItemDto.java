package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;

public record CitationItemDto(
    Integer page,
    @JsonProperty("section_ref") String sectionRef,
    String quote,
    @JsonProperty("quote_verified") Boolean quoteVerified
) {}
