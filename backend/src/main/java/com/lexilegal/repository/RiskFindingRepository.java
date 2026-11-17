package com.lexilegal.repository;

import com.lexilegal.entity.RiskFinding;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface RiskFindingRepository extends JpaRepository<RiskFinding, UUID>, JpaSpecificationExecutor<RiskFinding> {
    List<RiskFinding> findByAnalysisId(UUID analysisId);
    void deleteByAnalysisId(UUID analysisId);

    @Query("SELECT COUNT(r) FROM RiskFinding r WHERE r.analysis.document.user.id = :userId")
    long countByUserId(@Param("userId") UUID userId);

    @Query("SELECT r.level, COUNT(r) FROM RiskFinding r WHERE r.analysis.document.user.id = :userId GROUP BY r.level")
    List<Object[]> countRisksByLevelForUser(@Param("userId") UUID userId);

    @Query("SELECT r.category, COUNT(r) FROM RiskFinding r WHERE r.analysis.document.user.id = :userId GROUP BY r.category")
    List<Object[]> countRisksByCategoryForUser(@Param("userId") UUID userId);
}

