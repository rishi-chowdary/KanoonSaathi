package com.lexilegal.config;

import com.lexilegal.entity.Document;
import com.lexilegal.repository.DocumentRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Component
public class StartupJobRecoveryListener {

    private static final Logger log = LoggerFactory.getLogger(StartupJobRecoveryListener.class);

    private final DocumentRepository documentRepository;

    public StartupJobRecoveryListener(DocumentRepository documentRepository) {
        this.documentRepository = documentRepository;
    }

    @EventListener(ApplicationReadyEvent.class)
    @Transactional
    public void recoverInterruptedJobs() {
        List<Document> stuckDocs = documentRepository.findByStatusIn(List.of("ANALYZING", "EXTRACTING"));
        if (stuckDocs.isEmpty()) {
            log.info("Startup recovery: No interrupted jobs found in database.");
            return;
        }

        log.warn("Startup recovery: Found {} interrupted document(s) in ANALYZING/EXTRACTING state", stuckDocs.size());
        for (Document doc : stuckDocs) {
            String prevStatus = doc.getStatus();
            doc.setStatus("FAILED");
            doc.setFailureReason("Analysis was interrupted by server restart. Please click Re-analyze to resume.");
            documentRepository.save(doc);
            log.warn("Startup recovery: Document {} transitioned from {} to FAILED", doc.getId(), prevStatus);
        }
    }
}
