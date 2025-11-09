"""
Backend Testing Script for ElevenLabs Music Generation API
Tests all music generation endpoints in the Director router
"""

import requests
import json
import time
import os
from pathlib import Path

# Backend URL
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

# Test results storage
test_results = []

def log_test(test_name, passed, details=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    result = {
        "test": test_name,
        "passed": passed,
        "details": details
    }
    test_results.append(result)
    print(f"{status} - {test_name}")
    if details:
        print(f"   Details: {details}")
    print()

def print_response(response):
    """Pretty print response"""
    print(f"   Status Code: {response.status_code}")
    try:
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"   Response: {response.text[:200]}")

# ==================== Test Setup ====================

print("=" * 80)
print("ELEVENLABS MUSIC GENERATION API TESTING")
print("=" * 80)
print()

# Check backend health
print("Checking backend health...")
try:
    response = requests.get(f"{API_BASE}/health", timeout=10)
    if response.status_code == 200:
        print("✅ Backend is healthy")
        print_response(response)
    else:
        print("❌ Backend health check failed")
        print_response(response)
        exit(1)
except Exception as e:
    print(f"❌ Cannot connect to backend: {str(e)}")
    exit(1)

print()

# ==================== Test 1: Create a Test Project ====================

print("=" * 80)
print("TEST 1: Create a test project for music generation")
print("=" * 80)

try:
    project_data = {
        "user_goal": "Create a tech demo video with upbeat background music",
        "product_type": "software",
        "target_platform": "YouTube"
    }
    
    response = requests.post(
        f"{API_BASE}/director/project",
        json=project_data,
        timeout=30
    )
    
    print_response(response)
    
    if response.status_code == 200:
        project_response = response.json()
        project_id = project_response.get("project_id")
        
        if project_id:
            log_test(
                "Create test project",
                True,
                f"Project created with ID: {project_id}"
            )
        else:
            log_test("Create test project", False, "No project_id in response")
            exit(1)
    else:
        log_test("Create test project", False, f"Status code: {response.status_code}")
        exit(1)
        
except Exception as e:
    log_test("Create test project", False, f"Exception: {str(e)}")
    exit(1)

# ==================== Test 2: Music Info Before Generation ====================

print("=" * 80)
print("TEST 2: Get music info before generation (should return has_music: false)")
print("=" * 80)

try:
    response = requests.get(
        f"{API_BASE}/director/music/info/{project_id}",
        timeout=10
    )
    
    print_response(response)
    
    if response.status_code == 200:
        music_info = response.json()
        has_music = music_info.get("has_music")
        
        if has_music == False:
            log_test(
                "Music info before generation",
                True,
                "Correctly returns has_music: false"
            )
        else:
            log_test(
                "Music info before generation",
                False,
                f"Expected has_music: false, got: {has_music}"
            )
    else:
        log_test(
            "Music info before generation",
            False,
            f"Status code: {response.status_code}"
        )
        
except Exception as e:
    log_test("Music info before generation", False, f"Exception: {str(e)}")

# ==================== Test 3: Generate Music - 10 seconds ====================

print("=" * 80)
print("TEST 3: Generate music with 10 second duration")
print("=" * 80)

try:
    music_data = {
        "project_id": project_id,
        "prompt": "Create an upbeat electronic track with energetic vibes for a tech demo video",
        "duration_seconds": 10
    }
    
    print(f"Generating music with prompt: {music_data['prompt']}")
    print(f"Duration: {music_data['duration_seconds']} seconds")
    print("This may take 30-60 seconds...")
    print()
    
    response = requests.post(
        f"{API_BASE}/director/music/generate",
        json=music_data,
        timeout=120  # 2 minutes timeout for music generation
    )
    
    print_response(response)
    
    if response.status_code == 200:
        music_response = response.json()
        
        # Check required fields
        required_fields = ["success", "filename", "file_path", "duration_seconds"]
        missing_fields = [f for f in required_fields if f not in music_response]
        
        if missing_fields:
            log_test(
                "Generate music (10s)",
                False,
                f"Missing fields: {missing_fields}"
            )
        elif music_response.get("success") == True:
            filename = music_response.get("filename")
            duration = music_response.get("duration_seconds")
            
            # Verify file was created
            music_dir = Path("/app/backend/uploads/music")
            file_path = music_dir / filename
            
            if file_path.exists():
                file_size = file_path.stat().st_size
                log_test(
                    "Generate music (10s)",
                    True,
                    f"Music generated: {filename}, Duration: {duration}s, Size: {file_size} bytes"
                )
                
                # Store for later tests
                generated_filename_10s = filename
            else:
                log_test(
                    "Generate music (10s)",
                    False,
                    f"File not found at: {file_path}"
                )
        else:
            log_test(
                "Generate music (10s)",
                False,
                f"success field is not True: {music_response.get('success')}"
            )
    else:
        log_test(
            "Generate music (10s)",
            False,
            f"Status code: {response.status_code}"
        )
        
except Exception as e:
    log_test("Generate music (10s)", False, f"Exception: {str(e)}")

# ==================== Test 4: Music Info After Generation ====================

print("=" * 80)
print("TEST 4: Get music info after generation (should return has_music: true)")
print("=" * 80)

try:
    response = requests.get(
        f"{API_BASE}/director/music/info/{project_id}",
        timeout=10
    )
    
    print_response(response)
    
    if response.status_code == 200:
        music_info = response.json()
        has_music = music_info.get("has_music")
        
        if has_music == True:
            # Check metadata fields
            expected_fields = ["filename", "prompt", "duration_seconds", "generated_at"]
            missing_fields = [f for f in expected_fields if f not in music_info]
            
            if missing_fields:
                log_test(
                    "Music info after generation",
                    False,
                    f"Missing metadata fields: {missing_fields}"
                )
            else:
                log_test(
                    "Music info after generation",
                    True,
                    f"Correctly returns has_music: true with metadata"
                )
        else:
            log_test(
                "Music info after generation",
                False,
                f"Expected has_music: true, got: {has_music}"
            )
    else:
        log_test(
            "Music info after generation",
            False,
            f"Status code: {response.status_code}"
        )
        
except Exception as e:
    log_test("Music info after generation", False, f"Exception: {str(e)}")

# ==================== Test 5: Serve Music File ====================

print("=" * 80)
print("TEST 5: Serve music file via GET endpoint")
print("=" * 80)

try:
    if 'generated_filename_10s' in locals():
        response = requests.get(
            f"{API_BASE}/director/music/{project_id}/{generated_filename_10s}",
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        print(f"   Content-Length: {len(response.content)} bytes")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            
            if 'audio/mpeg' in content_type or 'audio/mp3' in content_type:
                log_test(
                    "Serve music file",
                    True,
                    f"File served successfully, Size: {len(response.content)} bytes"
                )
            else:
                log_test(
                    "Serve music file",
                    False,
                    f"Wrong content-type: {content_type}"
                )
        else:
            log_test(
                "Serve music file",
                False,
                f"Status code: {response.status_code}"
            )
    else:
        log_test("Serve music file", False, "No filename from previous test")
        
except Exception as e:
    log_test("Serve music file", False, f"Exception: {str(e)}")

# ==================== Test 6: Generate Music - 20 seconds ====================

print("=" * 80)
print("TEST 6: Generate music with 20 second duration")
print("=" * 80)

try:
    music_data = {
        "project_id": project_id,
        "prompt": "Energetic electronic music with driving beats and synth melodies",
        "duration_seconds": 20
    }
    
    print(f"Generating 20s music...")
    print()
    
    response = requests.post(
        f"{API_BASE}/director/music/generate",
        json=music_data,
        timeout=120
    )
    
    print_response(response)
    
    if response.status_code == 200:
        music_response = response.json()
        
        if music_response.get("success") == True:
            duration = music_response.get("duration_seconds")
            
            if duration == 20.0:
                log_test(
                    "Generate music (20s)",
                    True,
                    f"Music generated with correct duration: {duration}s"
                )
            else:
                log_test(
                    "Generate music (20s)",
                    False,
                    f"Wrong duration: expected 20.0, got {duration}"
                )
        else:
            log_test("Generate music (20s)", False, "success field is not True")
    else:
        log_test(
            "Generate music (20s)",
            False,
            f"Status code: {response.status_code}"
        )
        
except Exception as e:
    log_test("Generate music (20s)", False, f"Exception: {str(e)}")

# ==================== Test 7: Generate Music - 30 seconds ====================

print("=" * 80)
print("TEST 7: Generate music with 30 second duration")
print("=" * 80)

try:
    music_data = {
        "project_id": project_id,
        "prompt": "Uplifting corporate background music with piano and strings",
        "duration_seconds": 30
    }
    
    print(f"Generating 30s music...")
    print()
    
    response = requests.post(
        f"{API_BASE}/director/music/generate",
        json=music_data,
        timeout=120
    )
    
    print_response(response)
    
    if response.status_code == 200:
        music_response = response.json()
        
        if music_response.get("success") == True:
            duration = music_response.get("duration_seconds")
            
            if duration == 30.0:
                log_test(
                    "Generate music (30s)",
                    True,
                    f"Music generated with correct duration: {duration}s"
                )
            else:
                log_test(
                    "Generate music (30s)",
                    False,
                    f"Wrong duration: expected 30.0, got {duration}"
                )
        else:
            log_test("Generate music (30s)", False, "success field is not True")
    else:
        log_test(
            "Generate music (30s)",
            False,
            f"Status code: {response.status_code}"
        )
        
except Exception as e:
    log_test("Generate music (30s)", False, f"Exception: {str(e)}")

# ==================== Test 8: Edge Case - Invalid Duration (< 10) ====================

print("=" * 80)
print("TEST 8: Edge case - Invalid duration less than 10 seconds")
print("=" * 80)

try:
    music_data = {
        "project_id": project_id,
        "prompt": "Test music",
        "duration_seconds": 5  # Invalid: less than 10
    }
    
    response = requests.post(
        f"{API_BASE}/director/music/generate",
        json=music_data,
        timeout=30
    )
    
    print_response(response)
    
    if response.status_code == 400:
        error_detail = response.json().get("detail", "")
        if "between 10 and 60" in error_detail.lower():
            log_test(
                "Invalid duration (< 10)",
                True,
                "Correctly rejected with 400 error"
            )
        else:
            log_test(
                "Invalid duration (< 10)",
                False,
                f"Wrong error message: {error_detail}"
            )
    else:
        log_test(
            "Invalid duration (< 10)",
            False,
            f"Expected 400, got {response.status_code}"
        )
        
except Exception as e:
    log_test("Invalid duration (< 10)", False, f"Exception: {str(e)}")

# ==================== Test 9: Edge Case - Invalid Duration (> 60) ====================

print("=" * 80)
print("TEST 9: Edge case - Invalid duration greater than 60 seconds")
print("=" * 80)

try:
    music_data = {
        "project_id": project_id,
        "prompt": "Test music",
        "duration_seconds": 90  # Invalid: greater than 60
    }
    
    response = requests.post(
        f"{API_BASE}/director/music/generate",
        json=music_data,
        timeout=30
    )
    
    print_response(response)
    
    if response.status_code == 400:
        error_detail = response.json().get("detail", "")
        if "between 10 and 60" in error_detail.lower():
            log_test(
                "Invalid duration (> 60)",
                True,
                "Correctly rejected with 400 error"
            )
        else:
            log_test(
                "Invalid duration (> 60)",
                False,
                f"Wrong error message: {error_detail}"
            )
    else:
        log_test(
            "Invalid duration (> 60)",
            False,
            f"Expected 400, got {response.status_code}"
        )
        
except Exception as e:
    log_test("Invalid duration (> 60)", False, f"Exception: {str(e)}")

# ==================== Test 10: Edge Case - Non-existent Project ====================

print("=" * 80)
print("TEST 10: Edge case - Non-existent project_id")
print("=" * 80)

try:
    fake_project_id = "00000000-0000-0000-0000-000000000000"
    
    music_data = {
        "project_id": fake_project_id,
        "prompt": "Test music",
        "duration_seconds": 30
    }
    
    response = requests.post(
        f"{API_BASE}/director/music/generate",
        json=music_data,
        timeout=30
    )
    
    print_response(response)
    
    if response.status_code == 404:
        error_detail = response.json().get("detail", "")
        if "not found" in error_detail.lower():
            log_test(
                "Non-existent project_id",
                True,
                "Correctly rejected with 404 error"
            )
        else:
            log_test(
                "Non-existent project_id",
                False,
                f"Wrong error message: {error_detail}"
            )
    else:
        log_test(
            "Non-existent project_id",
            False,
            f"Expected 404, got {response.status_code}"
        )
        
except Exception as e:
    log_test("Non-existent project_id", False, f"Exception: {str(e)}")

# ==================== Test 11: Edge Case - Empty Prompt ====================

print("=" * 80)
print("TEST 11: Edge case - Empty prompt")
print("=" * 80)

try:
    music_data = {
        "project_id": project_id,
        "prompt": "",  # Empty prompt
        "duration_seconds": 30
    }
    
    response = requests.post(
        f"{API_BASE}/director/music/generate",
        json=music_data,
        timeout=30
    )
    
    print_response(response)
    
    # Empty prompt might be rejected by validation or by ElevenLabs API
    if response.status_code in [400, 422, 500]:
        log_test(
            "Empty prompt",
            True,
            f"Correctly rejected with {response.status_code} error"
        )
    else:
        log_test(
            "Empty prompt",
            False,
            f"Expected error status, got {response.status_code}"
        )
        
except Exception as e:
    log_test("Empty prompt", False, f"Exception: {str(e)}")

# ==================== Test 12: Music Info Endpoint with Non-existent Project ====================

print("=" * 80)
print("TEST 12: Music info endpoint with non-existent project")
print("=" * 80)

try:
    fake_project_id = "00000000-0000-0000-0000-000000000000"
    
    response = requests.get(
        f"{API_BASE}/director/music/info/{fake_project_id}",
        timeout=10
    )
    
    print_response(response)
    
    if response.status_code == 404:
        log_test(
            "Music info - non-existent project",
            True,
            "Correctly returns 404 for non-existent project"
        )
    else:
        log_test(
            "Music info - non-existent project",
            False,
            f"Expected 404, got {response.status_code}"
        )
        
except Exception as e:
    log_test("Music info - non-existent project", False, f"Exception: {str(e)}")

# ==================== Test 13: Serve Music File with Non-existent File ====================

print("=" * 80)
print("TEST 13: Serve music file with non-existent filename")
print("=" * 80)

try:
    fake_filename = "nonexistent_music_file.mp3"
    
    response = requests.get(
        f"{API_BASE}/director/music/{project_id}/{fake_filename}",
        timeout=10
    )
    
    print_response(response)
    
    if response.status_code == 404:
        log_test(
            "Serve non-existent music file",
            True,
            "Correctly returns 404 for non-existent file"
        )
    else:
        log_test(
            "Serve non-existent music file",
            False,
            f"Expected 404, got {response.status_code}"
        )
        
except Exception as e:
    log_test("Serve non-existent music file", False, f"Exception: {str(e)}")

# ==================== Test 14: Verify MongoDB Update ====================

print("=" * 80)
print("TEST 14: Verify project document in MongoDB has music metadata")
print("=" * 80)

try:
    response = requests.get(
        f"{API_BASE}/director/project/{project_id}",
        timeout=10
    )
    
    print_response(response)
    
    if response.status_code == 200:
        project_data = response.json()
        music_data = project_data.get("music")
        
        if music_data:
            required_fields = ["filename", "file_path", "prompt", "duration_seconds", "generated_at"]
            missing_fields = [f for f in required_fields if f not in music_data]
            
            if missing_fields:
                log_test(
                    "MongoDB music metadata",
                    False,
                    f"Missing fields in music metadata: {missing_fields}"
                )
            else:
                log_test(
                    "MongoDB music metadata",
                    True,
                    "Project document correctly updated with music metadata"
                )
        else:
            log_test(
                "MongoDB music metadata",
                False,
                "No music field in project document"
            )
    else:
        log_test(
            "MongoDB music metadata",
            False,
            f"Status code: {response.status_code}"
        )
        
except Exception as e:
    log_test("MongoDB music metadata", False, f"Exception: {str(e)}")

# ==================== Test Summary ====================

print()
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print()

passed_tests = [t for t in test_results if t["passed"]]
failed_tests = [t for t in test_results if not t["passed"]]

print(f"Total Tests: {len(test_results)}")
print(f"Passed: {len(passed_tests)}")
print(f"Failed: {len(failed_tests)}")
print()

if failed_tests:
    print("FAILED TESTS:")
    print("-" * 80)
    for test in failed_tests:
        print(f"❌ {test['test']}")
        if test['details']:
            print(f"   {test['details']}")
    print()

if passed_tests:
    print("PASSED TESTS:")
    print("-" * 80)
    for test in passed_tests:
        print(f"✅ {test['test']}")
    print()

# Exit with appropriate code
exit_code = 0 if len(failed_tests) == 0 else 1
print(f"Exit code: {exit_code}")
exit(exit_code)
