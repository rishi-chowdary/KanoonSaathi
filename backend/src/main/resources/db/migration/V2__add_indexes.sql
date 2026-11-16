CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_user_hash ON documents(user_id, file_hash);
CREATE INDEX idx_analyses_document_id ON document_analyses(document_id);
CREATE INDEX idx_clauses_analysis_id ON extracted_clauses(analysis_id);
CREATE INDEX idx_clauses_category ON extracted_clauses(category);
CREATE INDEX idx_clauses_importance ON extracted_clauses(importance);
CREATE INDEX idx_risks_analysis_id ON risk_findings(analysis_id);
CREATE INDEX idx_risks_level ON risk_findings(level);
CREATE INDEX idx_risks_category ON risk_findings(category);
CREATE INDEX idx_missing_clauses_analysis_id ON missing_clause_warnings(analysis_id);
CREATE INDEX idx_chunks_doc_id ON document_chunks(document_id);
CREATE INDEX idx_chunks_search_vector ON document_chunks USING GIN(search_vector);
CREATE INDEX idx_chat_conv_doc_user ON chat_conversations(document_id, user_id);
CREATE INDEX idx_chat_messages_conv_id ON chat_messages(conversation_id);

