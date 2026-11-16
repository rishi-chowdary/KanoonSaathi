package com.lexilegal.repository;

import com.lexilegal.entity.Document;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface DocumentRepository extends JpaRepository<Document, UUID> {
    Page<Document> findByUserIdOrderByCreatedAtDesc(UUID userId, Pageable pageable);
    Page<Document> findByUserIdAndOriginalFilenameContainingIgnoreCaseOrderByCreatedAtDesc(UUID userId, String filename, Pageable pageable);
    Page<Document> findByUserIdAndStatusOrderByCreatedAtDesc(UUID userId, String status, Pageable pageable);
    Page<Document> findByUserIdAndStatusAndOriginalFilenameContainingIgnoreCaseOrderByCreatedAtDesc(UUID userId, String status, String filename, Pageable pageable);
    Optional<Document> findByIdAndUserId(UUID id, UUID userId);
    Optional<Document> findByUserIdAndFileHash(UUID userId, String fileHash);
    long countByUserId(UUID userId);
}
