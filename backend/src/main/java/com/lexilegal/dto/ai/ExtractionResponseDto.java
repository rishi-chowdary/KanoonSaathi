package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class ExtractionResponseDto {
    private List<PageDto> pages;
    private List<SectionDto> sections;
    private List<ChunkDto> chunks;

    @JsonProperty("language_guess")
    private String languageGuess;

    private List<String> warnings;

    public ExtractionResponseDto() {}

    public List<PageDto> getPages() {
        return pages;
    }

    public void setPages(List<PageDto> pages) {
        this.pages = pages;
    }

    public List<SectionDto> getSections() {
        return sections;
    }

    public void setSections(List<SectionDto> sections) {
        this.sections = sections;
    }

    public List<ChunkDto> getChunks() {
        return chunks;
    }

    public void setChunks(List<ChunkDto> chunks) {
        this.chunks = chunks;
    }

    public String getLanguageGuess() {
        return languageGuess;
    }

    public void setLanguageGuess(String languageGuess) {
        this.languageGuess = languageGuess;
    }

    public List<String> getWarnings() {
        return warnings;
    }

    public void setWarnings(List<String> warnings) {
        this.warnings = warnings;
    }
}
