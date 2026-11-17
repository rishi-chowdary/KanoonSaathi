package com.lexilegal.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public class SimplifyRequest {

    @NotBlank(message = "Text cannot be blank")
    @Size(max = 10000, message = "Text exceeds maximum allowable length of 10000 characters")
    private String text;

    @Pattern(
        regexp = "^(simple_english|detailed|professional)$",
        message = "Mode must be one of: simple_english, detailed, professional"
    )
    private String mode = "simple_english";

    @Size(max = 2000, message = "Document context exceeds maximum length of 2000 characters")
    private String documentContext;

    public SimplifyRequest() {}

    public SimplifyRequest(String text, String mode, String documentContext) {
        this.text = text;
        this.mode = mode != null ? mode : "simple_english";
        this.documentContext = documentContext;
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }

    public String getMode() {
        return mode;
    }

    public void setMode(String mode) {
        this.mode = mode;
    }

    public String getDocumentContext() {
        return documentContext;
    }

    public void setDocumentContext(String documentContext) {
        this.documentContext = documentContext;
    }
}

