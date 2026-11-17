import requests
import uuid

BASE_URL = "http://localhost:8080/api"

def main():
    print("=== VERIFYING PHASE 8 CROSS-TENANT AUTHORIZATION ISOLATION ===")

    # 1. Register User A
    email_a = f"usera_{uuid.uuid4().hex[:8]}@lexilegal.ai"
    reg_a = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email_a,
        "password": "Password123!",
        "fullName": "User Alpha"
    }).json()
    token_a = reg_a["token"]
    print(f"Registered User A: {email_a}")

    # 2. User A uploads a contract
    with open("samples/contracts/rental_agreement.pdf", "rb") as f:
        upload_res = requests.post(
            f"{BASE_URL}/documents/upload",
            headers={"Authorization": f"Bearer {token_a}"},
            files={"file": ("rental.pdf", f, "application/pdf")}
        ).json()
    doc_id = upload_res["id"]
    print(f"User A uploaded document: {doc_id}")

    # 3. User A starts a conversation
    chat_a = requests.post(
        f"{BASE_URL}/documents/{doc_id}/chat",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"message": "What is the monthly rent?"}
    ).json()
    conv_id = chat_a["conversationId"]
    print(f"User A created conversation: {conv_id}")

    # 4. Register User B
    email_b = f"userb_{uuid.uuid4().hex[:8]}@lexilegal.ai"
    reg_b = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email_b,
        "password": "Password123!",
        "fullName": "User Beta"
    }).json()
    token_b = reg_b["token"]
    print(f"Registered User B: {email_b}")

    # 5. User B attempts unauthorized operations
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Test 5A: User B attempts to read User A's conversations list
    res_list = requests.get(f"{BASE_URL}/documents/{doc_id}/chat/conversations", headers=headers_b)
    print(f"Test 5A: User B GET /documents/{doc_id}/chat/conversations -> HTTP {res_list.status_code} (Expected: 404)")
    assert res_list.status_code == 404, f"Expected 404 but got {res_list.status_code}"

    # Test 5B: User B attempts to read User A's conversation messages
    res_msg = requests.get(f"{BASE_URL}/documents/{doc_id}/chat/conversations/{conv_id}/messages", headers=headers_b)
    print(f"Test 5B: User B GET /documents/{doc_id}/chat/conversations/{conv_id}/messages -> HTTP {res_msg.status_code} (Expected: 404)")
    assert res_msg.status_code == 404, f"Expected 404 but got {res_msg.status_code}"

    # Test 5C: User B attempts to post a message to User A's conversation
    res_post = requests.post(
        f"{BASE_URL}/documents/{doc_id}/chat",
        headers=headers_b,
        json={"conversationId": conv_id, "message": "Can I read this?"}
    )
    print(f"Test 5C: User B POST /documents/{doc_id}/chat -> HTTP {res_post.status_code} (Expected: 404)")
    assert res_post.status_code == 404, f"Expected 404 but got {res_post.status_code}"

    # Test 5D: User B attempts to delete User A's conversation
    res_del = requests.delete(f"{BASE_URL}/documents/{doc_id}/chat/conversations/{conv_id}", headers=headers_b)
    print(f"Test 5D: User B DELETE /documents/{doc_id}/chat/conversations/{conv_id} -> HTTP {res_del.status_code} (Expected: 404)")
    assert res_del.status_code == 404, f"Expected 404 but got {res_del.status_code}"

    print("\n[ALL AUTHORIZATION ISOLATION TESTS PASSED]: User B strictly received HTTP 404 for all attempts.")

if __name__ == "__main__":
    main()

