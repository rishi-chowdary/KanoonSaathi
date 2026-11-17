package com.lexilegal.repository;

import com.lexilegal.entity.DocumentAnalysis;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface DocumentAnalysisRepository extends JpaRepository<DocumentAnalysis, UUID> {
    Optional<DocumentAnalysis> findByDocumentId(UUID documentId);

    @Query("SELECT a FROM DocumentAnalysis a WHERE a.document.user.id = :userId ORDER BY a.createdAt DESC")
    List<DocumentAnalysis> findRecentAnalysesForUser(@Param("userId") UUID userId, Pageable pageable);
}

