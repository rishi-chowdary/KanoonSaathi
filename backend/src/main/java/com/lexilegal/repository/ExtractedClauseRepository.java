package com.lexilegal.repository;

import com.lexilegal.entity.ExtractedClause;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface ExtractedClauseRepository extends JpaRepository<ExtractedClause, UUID> {
    List<ExtractedClause> findByAnalysisId(UUID analysisId);
}

