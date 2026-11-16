package com.lexilegal.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;

public class UpdateProfileRequest {

    @NotBlank(message = "full name is required")
    private String fullName;

    @Pattern(
        regexp = "^$|^(?=.*[A-Za-z])(?=.*\\d).{8,}$",
        message = "new password must be at least 8 characters long and contain both letters and numbers"
    )
    private String password;

    public UpdateProfileRequest() {}

    public UpdateProfileRequest(String fullName, String password) {
        this.fullName = fullName;
        this.password = password;
    }

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}

