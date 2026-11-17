package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class DocumentSummaryRequestDto {

    @JsonProperty("document_id")
    private String documentId;

    private List<PageDto> pages;
    private List<ChunkDto> chunks;

    public DocumentSummaryRequestDto() {}

    public DocumentSummaryRequestDto(String documentId, List<PageDto> pages, List<ChunkDto> chunks) {
        this.documentId = documentId;
        this.pages = pages;
        this.chunks = chunks;
    }

    public String getDocumentId() {
        return documentId;
    }

    public void setDocumentId(String documentId) {
        this.documentId = documentId;
    }

    public List<PageDto> getPages() {
        return pages;
    }

    public void setPages(List<PageDto> pages) {
        this.pages = pages;
    }

    public List<ChunkDto> getChunks() {
        return chunks;
    }

    public void setChunks(List<ChunkDto> chunks) {
        this.chunks = chunks;
    }
}
