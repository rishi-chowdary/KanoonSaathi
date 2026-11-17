package com.lexilegal.repository;

import com.lexilegal.entity.DocumentChunk;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface DocumentChunkRepository extends JpaRepository<DocumentChunk, UUID> {
    List<DocumentChunk> findByDocumentIdOrderByChunkIndexAsc(UUID documentId);
    List<DocumentChunk> findByDocumentIdAndPageNumberOrderByChunkIndexAsc(UUID documentId, Integer pageNumber);
    List<DocumentChunk> findTop5ByDocumentIdOrderByChunkIndexAsc(UUID documentId);

    @Query(value = """
        SELECT * FROM document_chunks
        WHERE document_id = :documentId
          AND search_vector @@ websearch_to_tsquery('english', :query)
        ORDER BY ts_rank(search_vector, websearch_to_tsquery('english', :query)) DESC
        LIMIT :limit
    """, nativeQuery = true)
    List<DocumentChunk> searchChunksFullText(
        @Param("documentId") UUID documentId,
        @Param("query") String query,
        @Param("limit") int limit
    );

    @Query(value = """
        SELECT * FROM document_chunks
        WHERE document_id = :documentId
          AND search_vector @@ plainto_tsquery('english', :query)
        ORDER BY ts_rank(search_vector, plainto_tsquery('english', :query)) DESC
        LIMIT :limit
    """, nativeQuery = true)
    List<DocumentChunk> searchChunksPlain(
        @Param("documentId") UUID documentId,
        @Param("query") String query,
        @Param("limit") int limit
    );
}
