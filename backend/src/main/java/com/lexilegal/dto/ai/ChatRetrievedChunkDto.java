package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;

public record ChatRetrievedChunkDto(
    @JsonProperty("chunk_id") String chunkId,
    @JsonProperty("page_number") Integer pageNumber,
    @JsonProperty("content") String content,
    @JsonProperty("section_ref") String sectionRef
) {}
