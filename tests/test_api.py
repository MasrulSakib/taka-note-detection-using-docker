import glob
import os
import sys
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")
PREDICT_ENDPOINT = f"{API_URL}/predict"
SAMPLE_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "sample_images")


def test_health():
    print("\n[1/3] Testing /health endpoint...")
    res = requests.get(f"{API_URL}/health", timeout=5)
    print(f"  Status: {res.status_code}, Response: {res.json()}")
    assert res.status_code == 200 and res.json().get("status") == "ok"
    print("  PASS: Health check successful.")


def test_predict_valid_images():
    print("\n[2/3] Testing /predict with sample images...")
    image_paths = sorted(
        glob.glob(os.path.join(SAMPLE_IMAGES_DIR, "*.jpg"))
        + glob.glob(os.path.join(SAMPLE_IMAGES_DIR, "*.jpeg"))
        + glob.glob(os.path.join(SAMPLE_IMAGES_DIR, "*.png"))
    )

    if not image_paths:
        print("  Warning: No sample images found in tests/sample_images/")
        return

    for path in image_paths[:5]:
        filename = os.path.basename(path)
        with open(path, "rb") as f:
            res = requests.post(PREDICT_ENDPOINT, files={"file": (filename, f, "image/jpeg")})
        
        print(f"  Image: {filename} | Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"    -> Detections: {data['num_detections']}, Time: {data['inference_time_ms']}ms")
            for det in data.get("detections", []):
                print(f"       - {det['class_name']} (conf: {det['confidence']})")
        else:
            print(f"    -> Error: {res.text}")


def test_invalid_requests():
    print("\n[3/3] Testing invalid input handling...")
    
    # Missing file
    res = requests.post(PREDICT_ENDPOINT)
    print(f"  Missing file -> Status: {res.status_code}")
    assert res.status_code == 422

    # Invalid file type
    fake_file = ("test.txt", b"invalid image data", "text/plain")
    res = requests.post(PREDICT_ENDPOINT, files={"file": fake_file})
    print(f"  Invalid file type -> Status: {res.status_code}")
    assert res.status_code == 400

    # Empty file
    empty_file = ("empty.jpg", b"", "image/jpeg")
    res = requests.post(PREDICT_ENDPOINT, files={"file": empty_file})
    print(f"  Empty file -> Status: {res.status_code}")
    assert res.status_code == 400

    print("  PASS: Error handling verified.")


if __name__ == "__main__":
    print(f"=== Starting API Test Suite against {API_URL} ===")
    try:
        test_health()
        test_predict_valid_images()
        test_invalid_requests()
        print("\nAll tests completed successfully!")
    except Exception as err:
        print(f"\nTest execution failed: {err}")
        sys.exit(1)
