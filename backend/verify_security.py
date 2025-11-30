import requests
import time

BASE_URL = "http://localhost:8000"

def test_security():
    print("Testing Security Features...")
    
    # 1. Rate Limiting
    print("\n1. Rate Limiting (Expect 429 after 5 requests)")
    # Use a valid-ish PDF header to pass validation if rate limit doesn't catch it
    files = {'file': ('test.pdf', b'%PDF-1.4\n%dummy content', 'application/pdf')}
    hit_limit = False
    for i in range(10):
        try:
            res = requests.post(f"{BASE_URL}/api/resume/upload", files=files)
            print(f"Req {i+1}: {res.status_code}")
            if res.status_code == 500:
                print(f"❌ Error details: {res.text}")
            if res.status_code == 429:
                print("✅ Rate limit verified")
                hit_limit = True
                break
        except Exception as e:
            print(f"Connection failed: {e}")
            break
            
    if not hit_limit:
        print("❌ Rate limit failed")

    # 2. File Validation (Invalid Type)
    print("\n2. File Validation - Invalid Type")
    # Text file masquerading as PDF (no PDF header)
    files = {'file': ('test.pdf', b'Just text no pdf header', 'application/pdf')}
    try:
        res = requests.post(f"{BASE_URL}/api/resume/upload", files=files)
        if res.status_code == 400 and "Invalid file type" in res.text:
             print("✅ Type validation verified")
        elif res.status_code == 429:
             print("⚠️ Rate limited (expected if previous test ran)")
        else:
             print(f"❌ Type validation failed: {res.status_code} {res.text}")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    test_security()
