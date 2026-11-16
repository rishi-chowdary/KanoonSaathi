package com.lexilegal.repository;

import com.lexilegal.entity.MissingClauseWarning;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface MissingClauseWarningRepository extends JpaRepository<MissingClauseWarning, UUID> {
    List<MissingClauseWarning> findByAnalysisId(UUID analysisId);
}

