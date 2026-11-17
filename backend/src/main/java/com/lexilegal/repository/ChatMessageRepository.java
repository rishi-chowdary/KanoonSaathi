package com.lexilegal.repository;

import com.lexilegal.entity.ChatMessage;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface ChatMessageRepository extends JpaRepository<ChatMessage, UUID> {
    List<ChatMessage> findByConversationIdOrderByCreatedAtAsc(UUID conversationId);
    List<ChatMessage> findTop6ByConversationIdOrderByCreatedAtDesc(UUID conversationId);
    Optional<ChatMessage> findTopByConversationIdOrderByCreatedAtDesc(UUID conversationId);
    long countByConversationId(UUID conversationId);
    void deleteByConversationId(UUID conversationId);
}

