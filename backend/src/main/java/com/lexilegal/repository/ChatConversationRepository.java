package com.lexilegal.repository;

import com.lexilegal.entity.ChatConversation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface ChatConversationRepository extends JpaRepository<ChatConversation, UUID> {
    List<ChatConversation> findByDocumentIdAndUserIdOrderByUpdatedAtDesc(UUID documentId, UUID userId);
    List<ChatConversation> findByDocumentIdAndUserIdOrderByCreatedAtDesc(UUID documentId, UUID userId);
    Optional<ChatConversation> findByIdAndUserId(UUID id, UUID userId);
    void deleteByIdAndUserId(UUID id, UUID userId);
}

