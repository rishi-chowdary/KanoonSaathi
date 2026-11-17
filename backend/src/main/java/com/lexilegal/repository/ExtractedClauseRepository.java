package com.lexilegal.repository;

import com.lexilegal.entity.ExtractedClause;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface ExtractedClauseRepository extends JpaRepository<ExtractedClause, UUID>, JpaSpecificationExecutor<ExtractedClause> {
    List<ExtractedClause> findByAnalysisId(UUID analysisId);
    void deleteByAnalysisId(UUID analysisId);

    @Query("SELECT COUNT(c) FROM ExtractedClause c WHERE c.analysis.document.user.id = :userId")
    long countByUserId(@Param("userId") UUID userId);
}
