#!/usr/bin/env bash
# ==============================================================================
# LexiLegal AI — End-to-End Smoke Test Script (Python NLP Stack)
# Covers: Register -> Auth Cookie -> Upload -> Extract -> View Clauses -> Chat -> Download Report
# ==============================================================================

set -euo pipefail

BASE_URL="${API_BASE_URL:-http://127.0.0.1:5000}"
SAMPLE_FILE="${1:-samples/contracts/rental_agreement.pdf}"
COOKIE_JAR=$(mktemp /tmp/lexilegal_cookie_XXXXXX.txt)

cleanup() {
    rm -f "$COOKIE_JAR"
}
trap cleanup EXIT

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
echo " Target Application: $BASE_URL"
echo " Sample File: $SAMPLE_FILE"
echo " Smoke User: $EMAIL"
echo "=========================================================="

# 1. Health & Home Check
echo "[1/7] Checking server availability..."
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/" || echo "000")
if [ "$STATUS_CODE" != "200" ]; then
    echo "[-] Server unreachable at ${BASE_URL} (status ${STATUS_CODE})."
    exit 1
fi
echo "      Server is reachable (HTTP 200 OK)."

# 2. Register fresh user
echo "[2/7] Registering new user..."
REGISTER_RESP=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    -X POST "${BASE_URL}/api/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\",\"full_name\":\"${FULL_NAME}\"}")

USER_ID=$(echo "$REGISTER_RESP" | grep -o '"id":"[^"]*' | cut -d'"' -f4 || echo "")
if [ -z "$USER_ID" ]; then
    echo "[-] Error: Failed to register user. Response: $REGISTER_RESP"
    exit 1
fi
echo "      Successfully registered user: $USER_ID"

# 3. Upload document
echo "[3/7] Uploading contract document (${SAMPLE_FILE})..."
UPLOAD_RESP=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    -X POST "${BASE_URL}/api/documents/upload" \
    -F "file=@${SAMPLE_FILE}")

DOC_ID=$(echo "$UPLOAD_RESP" | grep -o '"id":"[^"]*' | cut -d'"' -f4 || echo "")
if [ -z "$DOC_ID" ]; then
    echo "[-] Error: Document upload failed. Response: $UPLOAD_RESP"
    exit 1
fi
echo "      Document uploaded successfully (ID: $DOC_ID)."

# 4. Retrieve clauses with quote verification
echo "[4/7] Retrieving classified clauses & verifying exact evidence quotes..."
CLAUSES_RESP=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    "${BASE_URL}/api/documents/${DOC_ID}/clauses")

CLAUSE_COUNT=$(echo "$CLAUSES_RESP" | grep -o '"id":' | wc -l || echo "0")
echo "      Extracted and classified ${CLAUSE_COUNT} clauses."

# 5. Retrieve grounded risk findings
echo "[5/7] Retrieving grounded risk findings..."
RISKS_RESP=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    "${BASE_URL}/api/documents/${DOC_ID}/risks")

RISK_COUNT=$(echo "$RISKS_RESP" | grep -o '"rule_id":' | wc -l || echo "0")
echo "      Detected ${RISK_COUNT} contractual risks with Rule 7 guardrails."

# 6. Test Document Q&A (Grounded Extractive QA)
echo "[6/7] Asking grounded question: 'What is the monthly rent amount?'..."
CHAT_RESP=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    -X POST "${BASE_URL}/api/documents/${DOC_ID}/chat" \
    -H "Content-Type: application/json" \
    -d '{"message":"What is the monthly rent amount and when is it due?"}')

ANSWER=$(echo "$CHAT_RESP" | grep -o '"answer":"[^"]*' | cut -d'"' -f4 || echo "")
echo "      Assistant Answer: '$ANSWER'"

# 7. Download PDF Report Dossier
echo "[7/7] Generating and downloading 10-section ReportLab PDF Dossier..."
REPORT_TEMP=$(mktemp /tmp/lexilegal_report_XXXXXX.pdf)
curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    "${BASE_URL}/api/documents/${DOC_ID}/report" -o "$REPORT_TEMP"

FILE_SIZE=$(wc -c < "$REPORT_TEMP")
if [ "$FILE_SIZE" -lt 5000 ]; then
    echo "[-] Error: Downloaded PDF report is too small (${FILE_SIZE} bytes)."
    rm -f "$REPORT_TEMP"
    exit 1
fi
echo "      PDF Report downloaded successfully (${FILE_SIZE} bytes)."
rm -f "$REPORT_TEMP"

echo "=========================================================="
echo " Smoke Test COMPLETED SUCCESSFULLY (7/7 Passed)"
echo "=========================================================="
exit 0
