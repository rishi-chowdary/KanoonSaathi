package com.lexilegal.dto.response;

public record ChatCitationResponse(
    Integer page,
    String sectionRef,
    String quote,
    Boolean quoteVerified
) {}
