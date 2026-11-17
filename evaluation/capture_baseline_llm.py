import json
import os
import sys
import time
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8080/api"

SAMPLE_FILES = [
    "samples/contracts/rental_agreement.pdf",
    "samples/contracts/clean_nda.pdf",
    "samples/contracts/employment_agreement.pdf",
    "samples/contracts/one_sided_agreement.pdf",
    "samples/contracts/service_agreement.docx",
    "samples/contracts/promissory_note.txt",
]

CHAT_PROBES = {
    "rental_agreement.pdf": [
        "What is the monthly rent amount and when is it due?",
        "Can the tenant sublet the premises?",
    ],
    "clean_nda.pdf": [
        "What is the definition of Confidential Information?",
        "What is the term or duration of the non-disclosure obligations?",
    ],
    "employment_agreement.pdf": [
        "What is the employee compensation and payment schedule?",
        "What are the termination notice conditions?",
    ],
    "one_sided_agreement.pdf": [
        "Who has the right to terminate this agreement early?",
        "Is there an auto-renewal provision and what is the notice window?",
    ],
    "service_agreement.docx": [
        "What are the service fees and payment terms?",
        "Who owns the intellectual property created under this agreement?",
    ],
    "promissory_note.txt": [
        "What is the principal amount and interest rate?",
        "When is the repayment due?",
    ],
}


def make_request(url, method="GET", data=None, headers=None):
    headers = headers or {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8")), resp.status
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return json.loads(err_body), e.code
        except Exception:
            return {"error": err_body}, e.code


def upload_multipart(url, file_path, token):
    boundary = "----WebKitFormBoundary" + hex(int(time.time() * 1000))[2:]
    filename = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Authorization": f"Bearer {token}",
    }

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    print("=== LexiLegal AI: Capturing Baseline LLM Outputs ===")
    out_dir = os.path.join(os.path.dirname(__file__), "baseline_llm")
    os.makedirs(out_dir, exist_ok=True)

    # 1. Register a dedicated baseline capture user
    ts = int(time.time())
    email = f"baseline_{ts}@example.com"
    reg_payload = json.dumps({
        "email": email,
        "password": "BaselinePassword123!",
        "fullName": "Baseline Evaluator",
    }).encode("utf-8")

    reg_resp, code = make_request(
        f"{BASE_URL}/auth/register",
        method="POST",
        data=reg_payload,
        headers={"Content-Type": "application/json"}
    )
    if code != 201:
        print(f"[-] Registration failed: {reg_resp}")
        sys.exit(1)

    token = reg_resp["token"]
    auth_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    print(f"[+] Authenticated as {email}")

    for file_rel in SAMPLE_FILES:
        file_path = os.path.abspath(file_rel)
        if not os.path.exists(file_path):
            print(f"[-] File not found: {file_rel}, skipping.")
            continue

        base_name = os.path.basename(file_path)
        print(f"\n[*] Processing: {base_name}...")

        # Upload
        up_resp = upload_multipart(f"{BASE_URL}/documents/upload", file_path, token)
        doc_id = up_resp["id"]
        print(f"    Uploaded: doc_id={doc_id}. Polling status...")

        # Poll status
        status = "UPLOADED"
        for _ in range(40):
            time.sleep(3)
            stat_resp, _ = make_request(f"{BASE_URL}/documents/{doc_id}/status", headers=auth_headers)
            status = stat_resp.get("status")
            if status in ("COMPLETED", "COMPLETED_WITH_WARNINGS", "FAILED"):
                break
            print(f"    Status: {status}...")

        if status not in ("COMPLETED", "COMPLETED_WITH_WARNINGS"):
            print(f"[-] Processing {base_name} did not complete. Status: {status}")
            continue

        print(f"    Completed with status: {status}")

        # Fetch all outputs
        analysis, _ = make_request(f"{BASE_URL}/documents/{doc_id}/analysis", headers=auth_headers)
        clauses, _ = make_request(f"{BASE_URL}/documents/{doc_id}/clauses?page=0&size=100", headers=auth_headers)
        risks, _ = make_request(f"{BASE_URL}/documents/{doc_id}/risks", headers=auth_headers)
        key_info, _ = make_request(f"{BASE_URL}/documents/{doc_id}/key-info", headers=auth_headers)
        missing, _ = make_request(f"{BASE_URL}/documents/{doc_id}/missing", headers=auth_headers)

        # Chat probes
        chat_results = []
        questions = CHAT_PROBES.get(base_name, ["What are the main obligations?"])
        for q in questions:
            q_payload = json.dumps({"message": q}).encode("utf-8")
            chat_resp, _ = make_request(
                f"{BASE_URL}/documents/{doc_id}/chat",
                method="POST",
                data=q_payload,
                headers=auth_headers,
            )
            chat_results.append({
                "question": q,
                "answer": chat_resp.get("content", ""),
                "citations": chat_resp.get("citations", []),
                "confidence": chat_resp.get("confidence", ""),
            })

        baseline_record = {
            "file": base_name,
            "document_id": doc_id,
            "captured_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "llm_provider": "gemini-3.5-flash-lite",
            "status": status,
            "analysis": analysis,
            "clauses": clauses.get("content", []),
            "risks": risks if isinstance(risks, list) else [],
            "key_info": key_info,
            "missing_provisions": missing if isinstance(missing, list) else [],
            "chat_probes": chat_results,
        }

        out_path = os.path.join(out_dir, f"{os.path.splitext(base_name)[0]}_baseline.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(baseline_record, f, indent=2, ensure_ascii=False)

        print(f"    [+] Saved baseline to {out_path} ({len(clauses.get('content', []))} clauses, {len(risks if isinstance(risks, list) else [])} risks)")

    print("\n[+] Baseline capture completed successfully!")


if __name__ == "__main__":
    main()

