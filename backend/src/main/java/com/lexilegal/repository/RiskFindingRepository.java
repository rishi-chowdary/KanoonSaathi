package com.lexilegal.repository;

import com.lexilegal.entity.RiskFinding;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface RiskFindingRepository extends JpaRepository<RiskFinding, UUID>, JpaSpecificationExecutor<RiskFinding> {
    List<RiskFinding> findByAnalysisId(UUID analysisId);
    void deleteByAnalysisId(UUID analysisId);
}

