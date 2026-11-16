package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;

public class ChunkDto {
    @JsonProperty("chunk_index")
    private int chunkIndex;

    @JsonProperty("page_start")
    private int pageStart;

    @JsonProperty("page_end")
    private int pageEnd;

    @JsonProperty("section_ref")
    private String sectionRef;

    private String content;

    @JsonProperty("token_count")
    private int tokenCount;

    public ChunkDto() {}

    public int getChunkIndex() {
        return chunkIndex;
    }

    public void setChunkIndex(int chunkIndex) {
        this.chunkIndex = chunkIndex;
    }

    public int getPageStart() {
        return pageStart;
    }

    public void setPageStart(int pageStart) {
        this.pageStart = pageStart;
    }

    public int getPageEnd() {
        return pageEnd;
    }

    public void setPageEnd(int pageEnd) {
        this.pageEnd = pageEnd;
    }

    public String getSectionRef() {
        return sectionRef;
    }

    public void setSectionRef(String sectionRef) {
        this.sectionRef = sectionRef;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public int getTokenCount() {
        return tokenCount;
    }

    public void setTokenCount(int tokenCount) {
        this.tokenCount = tokenCount;
    }
}

