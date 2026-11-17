#!/usr/bin/env bash
# End-to-end live HTTP smoke test against a running KanoonSaathi server.

set -euo pipefail

BASE_URL="${API_BASE_URL:-http://127.0.0.1:5000}"
SAMPLE_FILE="${1:-samples/contracts/rental_agreement.pdf}"
COOKIE_JAR=$(mktemp /tmp/kanoonsaathi_cookie_XXXXXX.txt)
REPORT_TEMP=$(mktemp /tmp/kanoonsaathi_report_XXXXXX.pdf)

cleanup() {
    rm -f "$COOKIE_JAR" "$REPORT_TEMP"
}
trap cleanup EXIT

if [ ! -f "$SAMPLE_FILE" ]; then
    echo "Error: sample file '$SAMPLE_FILE' does not exist."
    exit 1
fi

TIMESTAMP=$(date +%s)
EMAIL="smoke_${TIMESTAMP}@example.com"
PASSWORD="SmokePassword123!"
FULL_NAME="Smoke Test Runner"

echo "Running live smoke test against $BASE_URL using $SAMPLE_FILE ($EMAIL)"

echo "[1/8] Checking server availability..."
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/" || echo "000")
if [ "$STATUS_CODE" != "200" ]; then
    echo "Error: server unreachable at ${BASE_URL} (status ${STATUS_CODE})."
    exit 1
fi

echo "[2/8] Registering new user..."
REGISTER_RESP=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    -X POST "${BASE_URL}/api/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\",\"full_name\":\"${FULL_NAME}\"}")
USER_ID=$(printf '%s' "$REGISTER_RESP" | python3 -c "import json,sys; d=json.load(sys.stdin); print((d.get('user') or d).get('id',''))")
if [ -z "$USER_ID" ]; then
    echo "Error: failed to register user. Response: $REGISTER_RESP"
    exit 1
fi
echo "      Registered user $USER_ID"

echo "[3/8] Uploading contract (${SAMPLE_FILE})..."
UPLOAD_RESP=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    -X POST "${BASE_URL}/api/documents/upload" \
    -F "file=@${SAMPLE_FILE}")
DOC_ID=$(printf '%s' "$UPLOAD_RESP" | python3 -c "import json,sys; print(json.load(sys.stdin).get('id',''))")
if [ -z "$DOC_ID" ]; then
    echo "Error: document upload failed. Response: $UPLOAD_RESP"
    exit 1
fi
echo "      Uploaded document $DOC_ID"

echo "[4/8] Checking clauses, risks, and key info..."
CLAUSE_COUNT=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" "${BASE_URL}/api/documents/${DOC_ID}/clauses" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('clauses', d) if isinstance(d, dict) else d))")
RISK_COUNT=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" "${BASE_URL}/api/documents/${DOC_ID}/risks" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d.get('risks', d) if isinstance(d, dict) else d))")
echo "      Clauses: ${CLAUSE_COUNT}, risks: ${RISK_COUNT}"

echo "[5/8] Asking answerable and unanswerable Q&A questions..."
ANS_1=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    -X POST "${BASE_URL}/api/documents/${DOC_ID}/chat" \
    -H "Content-Type: application/json" \
    -d '{"message":"What is the monthly rent amount and when is it due?"}' \
    | python3 -c "import json,sys; print(json.load(sys.stdin).get('content',''))")
ANS_2=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    -X POST "${BASE_URL}/api/documents/${DOC_ID}/chat" \
    -H "Content-Type: application/json" \
    -d '{"message":"What is the employee stock option vesting schedule?"}' \
    | python3 -c "import json,sys; print(json.load(sys.stdin).get('content',''))")
if [ -z "$ANS_1" ] || [ -z "$ANS_2" ]; then
    echo "Error: empty chat answer returned."
    exit 1
fi
echo "      Answer 1: $ANS_1"
echo "      Answer 2: $ANS_2"

echo "[6/8] Downloading PDF report..."
curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" "${BASE_URL}/api/documents/${DOC_ID}/report" -o "$REPORT_TEMP"
FILE_SIZE=$(wc -c < "$REPORT_TEMP")
if [ "$FILE_SIZE" -lt 5000 ]; then
    echo "Error: downloaded PDF report is too small (${FILE_SIZE} bytes)."
    exit 1
fi
echo "      PDF report downloaded (${FILE_SIZE} bytes)"

echo "[7/8] Checking dashboard stats..."
DASH_DOCS=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" "${BASE_URL}/api/dashboard/stats" \
    | python3 -c "import json,sys; print(json.load(sys.stdin).get('totalDocuments', -1))")
echo "      Dashboard totalDocuments: $DASH_DOCS"

echo "[8/8] Deleting smoke test document..."
DEL_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    -X DELETE "${BASE_URL}/api/documents/${DOC_ID}")
if [ "$DEL_STATUS" != "200" ]; then
    echo "Error: delete failed with status $DEL_STATUS"
    exit 1
fi
echo "      Deleted document $DOC_ID (HTTP 200)"
echo "Smoke test passed (8/8)."
