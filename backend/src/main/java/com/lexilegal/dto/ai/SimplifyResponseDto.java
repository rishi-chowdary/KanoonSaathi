package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class SimplifyResponseDto {

    @JsonProperty("original_text")
    private String originalText;

    private String mode;
    private String explanation;
    private List<GlossaryTermDto> glossary = new ArrayList<>();

    @JsonProperty("what_could_be_missed")
    private List<String> whatCouldBeMissed = new ArrayList<>();

    private List<String> warnings = new ArrayList<>();

    @JsonProperty("is_grounded")
    private Boolean isGrounded = true;

    @JsonProperty("llm_provider")
    private String llmProvider;

    @JsonProperty("llm_model")
    private String llmModel;

    public SimplifyResponseDto() {}

    public String getOriginalText() {
        return originalText;
    }

    public void setOriginalText(String originalText) {
        this.originalText = originalText;
    }

    public String getMode() {
        return mode;
    }

    public void setMode(String mode) {
        this.mode = mode;
    }

    public String getExplanation() {
        return explanation;
    }

    public void setExplanation(String explanation) {
        this.explanation = explanation;
    }

    public List<GlossaryTermDto> getGlossary() {
        return glossary;
    }

    public void setGlossary(List<GlossaryTermDto> glossary) {
        this.glossary = glossary;
    }

    public List<String> getWhatCouldBeMissed() {
        return whatCouldBeMissed;
    }

    public void setWhatCouldBeMissed(List<String> whatCouldBeMissed) {
        this.whatCouldBeMissed = whatCouldBeMissed;
    }

    public List<String> getWarnings() {
        return warnings;
    }

    public void setWarnings(List<String> warnings) {
        this.warnings = warnings;
    }

    public Boolean getIsGrounded() {
        return isGrounded;
    }

    public void setIsGrounded(Boolean grounded) {
        isGrounded = grounded;
    }

    public String getLlmProvider() {
        return llmProvider;
    }

    public void setLlmProvider(String llmProvider) {
        this.llmProvider = llmProvider;
    }

    public String getLlmModel() {
        return llmModel;
    }

    public void setLlmModel(String llmModel) {
        this.llmModel = llmModel;
    }
}

