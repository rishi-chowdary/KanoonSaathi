package com.lexilegal.dto.response;

import java.util.List;
import java.util.UUID;

public class DocumentTextResponse {
    private UUID documentId;
    private Integer page;
    private Integer pageCount;
    private String text;
    private List<PageTextDto> pages;

    public DocumentTextResponse() {}

    public static class PageTextDto {
        private int pageNumber;
        private String text;

        public PageTextDto() {}

        public PageTextDto(int pageNumber, String text) {
            this.pageNumber = pageNumber;
            this.text = text;
        }

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
    }

    public UUID getDocumentId() {
        return documentId;
    }

    public void setDocumentId(UUID documentId) {
        this.documentId = documentId;
    }

    public Integer getPage() {
        return page;
    }

    public void setPage(Integer page) {
        this.page = page;
    }

    public Integer getPageCount() {
        return pageCount;
    }

    public void setPageCount(Integer pageCount) {
        this.pageCount = pageCount;
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }

    public List<PageTextDto> getPages() {
        return pages;
    }

    public void setPages(List<PageTextDto> pages) {
        this.pages = pages;
    }
}

