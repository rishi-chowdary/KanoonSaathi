CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'USER',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_filename VARCHAR(255) NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    page_count INTEGER NOT NULL DEFAULT 0,
    is_scanned BOOLEAN NOT NULL DEFAULT FALSE,
    status VARCHAR(50) NOT NULL DEFAULT 'UPLOADED',
    failure_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE document_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL UNIQUE REFERENCES documents(id) ON DELETE CASCADE,
    title VARCHAR(255),
    document_type VARCHAR(100),
    purpose TEXT,
    parties JSONB NOT NULL DEFAULT '[]'::jsonb,
    summary_short TEXT NOT NULL,
    summary_detailed TEXT NOT NULL,
    main_conditions JSONB NOT NULL DEFAULT '[]'::jsonb,
    obligations_summary JSONB NOT NULL DEFAULT '[]'::jsonb,
    financial_terms_summary JSONB NOT NULL DEFAULT '[]'::jsonb,
    llm_provider VARCHAR(50) NOT NULL,
    llm_model VARCHAR(100) NOT NULL,
    verification_rate NUMERIC(5, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE extracted_clauses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES document_analyses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    custom_label VARCHAR(100),
    original_text TEXT NOT NULL,
    simplified_simple TEXT NOT NULL,
    simplified_detailed TEXT NOT NULL,
    simplified_professional TEXT NOT NULL,
    importance VARCHAR(20) NOT NULL,
    affected_party VARCHAR(255),
    source_page INTEGER NOT NULL,
    section_reference VARCHAR(100),
    evidence_quote TEXT NOT NULL,
    quote_verified BOOLEAN NOT NULL DEFAULT FALSE,
    provenance VARCHAR(30) NOT NULL DEFAULT 'EXTRACTED',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE risk_findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES document_analyses(id) ON DELETE CASCADE,
    category VARCHAR(50) NOT NULL,
    level VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    original_clause TEXT NOT NULL,
    explanation TEXT NOT NULL,
    why_it_matters TEXT NOT NULL,
    possible_consequences TEXT NOT NULL,
    suggested_questions JSONB NOT NULL DEFAULT '[]'::jsonb,
    source_page INTEGER NOT NULL,
    evidence_quote TEXT NOT NULL,
    quote_verified BOOLEAN NOT NULL DEFAULT FALSE,
    jurisdiction_caveat TEXT,
    provenance VARCHAR(30) NOT NULL DEFAULT 'AI_INTERPRETATION',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE extracted_information (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL UNIQUE REFERENCES document_analyses(id) ON DELETE CASCADE,
    contract_amount VARCHAR(255) NOT NULL DEFAULT 'Not specified',
    contract_amount_page INTEGER,
    payment_deadlines TEXT NOT NULL DEFAULT 'Not specified',
    payment_deadlines_page INTEGER,
    penalties TEXT NOT NULL DEFAULT 'Not specified',
    penalties_page INTEGER,
    start_date VARCHAR(100) NOT NULL DEFAULT 'Not specified',
    start_date_page INTEGER,
    end_date VARCHAR(100) NOT NULL DEFAULT 'Not specified',
    end_date_page INTEGER,
    renewal_date VARCHAR(100) NOT NULL DEFAULT 'Not specified',
    renewal_date_page INTEGER,
    notice_period VARCHAR(255) NOT NULL DEFAULT 'Not specified',
    notice_period_page INTEGER,
    termination_conditions TEXT NOT NULL DEFAULT 'Not specified',
    termination_conditions_page INTEGER,
    obligations JSONB NOT NULL DEFAULT '[]'::jsonb,
    important_dates JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE missing_clause_warnings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES document_analyses(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL,
    clause_name VARCHAR(255) NOT NULL,
    why_it_matters TEXT NOT NULL,
    typical_provision TEXT NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    label VARCHAR(50) NOT NULL DEFAULT 'Possible omission',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    page_number INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL DEFAULT 0,
    search_vector TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE chat_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL DEFAULT 'General Inquiries',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES chat_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    citations JSONB NOT NULL DEFAULT '[]'::jsonb,
    addressed_in_document BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

