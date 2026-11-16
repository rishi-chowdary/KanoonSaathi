package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;

public class SectionDto {
    private String title;

    @JsonProperty("section_ref")
    private String sectionRef;

    @JsonProperty("page_number")
    private int pageNumber;

    public SectionDto() {}

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getSectionRef() {
        return sectionRef;
    }

    public void setSectionRef(String sectionRef) {
        this.sectionRef = sectionRef;
    }

    public int getPageNumber() {
        return pageNumber;
    }

    public void setPageNumber(int pageNumber) {
        this.pageNumber = pageNumber;
    }
}
