package com.lexilegal.dto.response;

import com.lexilegal.dto.ai.GlossaryTermDto;
import java.util.ArrayList;
import java.util.List;

public class ReExplainClauseResponse {

    private ClauseResponse clause;
    private String mode;
    private String explanation;
    private List<GlossaryTermDto> glossary = new ArrayList<>();
    private List<String> whatCouldBeMissed = new ArrayList<>();
    private List<String> warnings = new ArrayList<>();
    private Boolean isGrounded = true;

    public ReExplainClauseResponse() {}

    public ReExplainClauseResponse(ClauseResponse clause, String mode, String explanation,
                                  List<GlossaryTermDto> glossary, List<String> whatCouldBeMissed,
                                  List<String> warnings, Boolean isGrounded) {
        this.clause = clause;
        this.mode = mode;
        this.explanation = explanation;
        this.glossary = glossary != null ? glossary : new ArrayList<>();
        this.whatCouldBeMissed = whatCouldBeMissed != null ? whatCouldBeMissed : new ArrayList<>();
        this.warnings = warnings != null ? warnings : new ArrayList<>();
        this.isGrounded = isGrounded != null ? isGrounded : true;
    }

    public ClauseResponse getClause() {
        return clause;
    }

    public void setClause(ClauseResponse clause) {
        this.clause = clause;
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
}

