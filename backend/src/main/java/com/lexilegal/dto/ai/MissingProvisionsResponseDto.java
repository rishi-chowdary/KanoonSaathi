package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

public class MissingProvisionsResponseDto {

    @JsonProperty("document_id")
    private String documentId;

    @JsonProperty("detected_document_type")
    private String detectedDocumentType = "other";

    @JsonProperty("missing_provisions")
    private List<MissingProvisionItemDto> missingProvisions = new ArrayList<>();

    @JsonProperty("total_missing")
    private Integer totalMissing = 0;

    private String disclaimer;

    public MissingProvisionsResponseDto() {}

    public String getDocumentId() { return documentId; }
    public void setDocumentId(String documentId) { this.documentId = documentId; }

    public String getDetectedDocumentType() { return detectedDocumentType; }
    public void setDetectedDocumentType(String detectedDocumentType) { this.detectedDocumentType = detectedDocumentType; }

    public List<MissingProvisionItemDto> getMissingProvisions() { return missingProvisions; }
    public void setMissingProvisions(List<MissingProvisionItemDto> missingProvisions) { this.missingProvisions = missingProvisions; }

    public Integer getTotalMissing() { return totalMissing; }
    public void setTotalMissing(Integer totalMissing) { this.totalMissing = totalMissing; }

    public String getDisclaimer() { return disclaimer; }
    public void setDisclaimer(String disclaimer) { this.disclaimer = disclaimer; }
}

