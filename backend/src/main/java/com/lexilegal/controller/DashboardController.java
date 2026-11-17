package com.lexilegal.controller;

import com.lexilegal.dto.response.DashboardStatsResponse;
import com.lexilegal.security.UserPrincipal;
import com.lexilegal.service.DashboardService;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/dashboard")
public class DashboardController {

    private final DashboardService dashboardService;

    public DashboardController(DashboardService dashboardService) {
        this.dashboardService = dashboardService;
    }

    @GetMapping("/stats")
    public ResponseEntity<DashboardStatsResponse> getStats(
            @AuthenticationPrincipal UserPrincipal principal) {
        DashboardStatsResponse stats = dashboardService.getStatsForUser(principal.getId());
        return ResponseEntity.ok(stats);
    }
}

