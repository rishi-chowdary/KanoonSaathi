package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class RiskAnalysisRequestDto {

    @JsonProperty("document_id")
    private String documentId;

    private List<PageDto> pages;
    private List<ChunkDto> chunks;

    @JsonProperty("governing_law_found")
    private Boolean governingLawFound;

    public RiskAnalysisRequestDto() {}

    public RiskAnalysisRequestDto(String documentId, List<PageDto> pages, List<ChunkDto> chunks, Boolean governingLawFound) {
        this.documentId = documentId;
        this.pages = pages;
        this.chunks = chunks;
        this.governingLawFound = governingLawFound;
    }

    public String getDocumentId() { return documentId; }
    public void setDocumentId(String documentId) { this.documentId = documentId; }

    public List<PageDto> getPages() { return pages; }
    public void setPages(List<PageDto> pages) { this.pages = pages; }

    public List<ChunkDto> getChunks() { return chunks; }
    public void setChunks(List<ChunkDto> chunks) { this.chunks = chunks; }

    public Boolean getGoverningLawFound() { return governingLawFound; }
    public void setGoverningLawFound(Boolean governingLawFound) { this.governingLawFound = governingLawFound; }
}

