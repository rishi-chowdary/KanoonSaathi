package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class MissingProvisionsRequestDto {

    @JsonProperty("document_id")
    private String documentId;

    private List<PageDto> pages;
    private List<ChunkDto> chunks;

    @JsonProperty("document_type_hint")
    private String documentTypeHint;

    public MissingProvisionsRequestDto() {}

    public MissingProvisionsRequestDto(String documentId, List<PageDto> pages, List<ChunkDto> chunks, String documentTypeHint) {
        this.documentId = documentId;
        this.pages = pages;
        this.chunks = chunks;
        this.documentTypeHint = documentTypeHint;
    }

    public String getDocumentId() { return documentId; }
    public void setDocumentId(String documentId) { this.documentId = documentId; }

    public List<PageDto> getPages() { return pages; }
    public void setPages(List<PageDto> pages) { this.pages = pages; }

    public List<ChunkDto> getChunks() { return chunks; }
    public void setChunks(List<ChunkDto> chunks) { this.chunks = chunks; }

    public String getDocumentTypeHint() { return documentTypeHint; }
    public void setDocumentTypeHint(String documentTypeHint) { this.documentTypeHint = documentTypeHint; }
}

