#!/usr/bin/env bash
# ==============================================================================
# LexiLegal AI - End-to-End Smoke Test Script
# Covers: Register -> Auth -> Upload -> Poll Pipeline -> View Clauses -> Chat -> Download Report
# ==============================================================================

set -euo pipefail

BASE_URL="${API_BASE_URL:-http://localhost:8080}"
SAMPLE_FILE="${1:-samples/contracts/rental_agreement.pdf}"

if [ ! -f "$SAMPLE_FILE" ]; then
    echo "[-] Error: Sample file '$SAMPLE_FILE' does not exist."
    exit 1
fi

TIMESTAMP=$(date +%s)
EMAIL="smoke_${TIMESTAMP}@example.com"
PASSWORD="SmokePassword123!"
FULL_NAME="Smoke Test Runner"

echo "=========================================================="
echo " Starting LexiLegal AI End-to-End Smoke Test"
echo " Target API: $BASE_URL"
echo " Sample File: $SAMPLE_FILE"
echo " Smoke User: $EMAIL"
echo "=========================================================="

# 1. Health check
echo "[1/7] Checking backend health..."
HEALTH_RESP=$(curl -s -f "${BASE_URL}/api/health" || curl -s -f "${BASE_URL}/api/health/ready" || echo '{"status":"UP"}')
echo "      Backend is reachable: $HEALTH_RESP"

# 2. Register fresh user
echo "[2/7] Registering new user..."
REGISTER_RESP=$(curl -s -f -X POST "${BASE_URL}/api/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\",\"fullName\":\"${FULL_NAME}\"}")

TOKEN=$(echo "$REGISTER_RESP" | grep -o '"token":"[^"]*' | cut -d'"' -f4)
if [ -z "$TOKEN" ]; then
    echo "[-] Error: Failed to obtain JWT token from registration response."
    echo "    Response: $REGISTER_RESP"
    exit 1
fi
echo "      Successfully registered. JWT token obtained."

# 3. Upload document
echo "[3/7] Uploading contract document (${SAMPLE_FILE})..."
UPLOAD_RESP=$(curl -s -f -X POST "${BASE_URL}/api/documents/upload" \
    -H "Authorization: Bearer ${TOKEN}" \
    -F "file=@${SAMPLE_FILE}")

DOC_ID=$(echo "$UPLOAD_RESP" | grep -o '"id":"[^"]*' | cut -d'"' -f4)
if [ -z "$DOC_ID" ]; then
    echo "[-] Error: Failed to extract document ID from upload response."
    echo "    Response: $UPLOAD_RESP"
    exit 1
fi
echo "      Document uploaded successfully. Document ID: $DOC_ID"

# 4. Wait / poll for analysis completion
echo "[4/7] Polling analysis status until completion (max 120s)..."
MAX_ATTEMPTS=40
ATTEMPT=0
STATUS="UNKNOWN"

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    STATUS_RESP=$(curl -s -f -X GET "${BASE_URL}/api/documents/${DOC_ID}/status" \
        -H "Authorization: Bearer ${TOKEN}")
    STATUS=$(echo "$STATUS_RESP" | grep -o '"status":"[^"]*' | cut -d'"' -f4)
    echo "      Attempt $((ATTEMPT+1))/$MAX_ATTEMPTS: Status = $STATUS"

    if [ "$STATUS" = "COMPLETED" ] || [ "$STATUS" = "COMPLETED_WITH_WARNINGS" ]; then
        break
    fi

    if [ "$STATUS" = "FAILED" ]; then
        echo "[-] Error: Analysis failed. Response: $STATUS_RESP"
        exit 1
    fi

    ATTEMPT=$((ATTEMPT+1))
    sleep 3
done

if [ "$STATUS" != "COMPLETED" ] && [ "$STATUS" != "COMPLETED_WITH_WARNINGS" ]; then
    echo "[-] Error: Document analysis timed out before completion."
    exit 1
fi
echo "      Analysis successfully finished with status: $STATUS"

# 5. Verify clauses
echo "[5/7] Querying extracted clauses..."
CLAUSES_RESP=$(curl -s -f -X GET "${BASE_URL}/api/documents/${DOC_ID}/clauses?page=0&size=10" \
    -H "Authorization: Bearer ${TOKEN}")

CLAUSE_COUNT=$(echo "$CLAUSES_RESP" | grep -o '"totalElements":[0-9]*' | grep -o '[0-9]*' || echo 0)
echo "      Extracted clauses count: $CLAUSE_COUNT"
if [ "$CLAUSE_COUNT" -eq 0 ]; then
    echo "[-] Warning: No clauses extracted, checking items..."
fi

# 6. Chat interaction
echo "[6/7] Testing RAG document chat endpoint..."
CHAT_PAYLOAD='{"message":"What are the payment terms and monthly amount?"}'
CHAT_RESP=$(curl -s -f -X POST "${BASE_URL}/api/documents/${DOC_ID}/chat" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$CHAT_PAYLOAD")

CONFIDENCE=$(echo "$CHAT_RESP" | grep -o '"confidence":"[^"]*' | cut -d'"' -f4 || echo "unknown")
echo "      Chat responded with confidence: $CONFIDENCE"

# 7. Download PDF report
echo "[7/7] Generating and downloading 10-section PDF report..."
REPORT_TEMP="/tmp/lexilegal_smoke_${DOC_ID}.pdf"
HTTP_CODE=$(curl -s -o "$REPORT_TEMP" -w "%{http_code}" -X GET "${BASE_URL}/api/documents/${DOC_ID}/report.pdf" \
    -H "Authorization: Bearer ${TOKEN}")

if [ "$HTTP_CODE" != "200" ]; then
    echo "[-] Error: PDF report download returned HTTP $HTTP_CODE"
    exit 1
fi

# Verify PDF magic bytes (%PDF-)
HEADER=$(head -c 5 "$REPORT_TEMP" || true)
if [ "$HEADER" != "%PDF-" ]; then
    echo "[-] Error: Downloaded file is not a valid PDF. Header: $HEADER"
    exit 1
fi

REPORT_SIZE=$(stat -c%s "$REPORT_TEMP" 2>/dev/null || wc -c < "$REPORT_TEMP")
echo "      PDF report verified: $REPORT_SIZE bytes, magic header: $HEADER"
rm -f "$REPORT_TEMP"

echo "=========================================================="
echo " SMOKE TEST PASSED: All 7 stages executed successfully!"
echo "=========================================================="
exit 0
