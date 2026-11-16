package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;

public class PageDto {
    @JsonProperty("page_number")
    private int pageNumber;

    private String text;

    @JsonProperty("ocr_used")
    private boolean ocrUsed;

    public PageDto() {}

    public int getPageNumber() {
        return pageNumber;
    }

    public void setPageNumber(int pageNumber) {
        this.pageNumber = pageNumber;
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }

    public boolean isOcrUsed() {
        return ocrUsed;
    }

    public void setOcrUsed(boolean ocrUsed) {
        this.ocrUsed = ocrUsed;
    }
}

