package com.lexilegal.repository;

import com.lexilegal.entity.ExtractedInformation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface ExtractedInformationRepository extends JpaRepository<ExtractedInformation, UUID> {
    Optional<ExtractedInformation> findByAnalysisId(UUID analysisId);
}
