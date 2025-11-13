"""
Test AWS S3 Configuration
==========================

Verifies that AWS credentials and S3 bucket are properly configured.

Usage:
    python test_aws.py
"""

import os
import sys
import tempfile
from dotenv import load_dotenv

load_dotenv()


def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_step(step_num, text):
    print(f"\n{step_num}️⃣  {text}")


def print_success(text):
    print(f"   ✅ {text}")


def print_error(text):
    print(f"   ❌ {text}")


def test_environment_variables():
    """Test if all required environment variables are set"""
    print_step("1", "Checking environment variables...")
    
    required_vars = [
        "REPLICATE_API_TOKEN",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_S3_BUCKET",
        "AWS_REGION"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if "KEY" in var or "TOKEN" in var:
                masked = f"{value[:8]}...{value[-4:]}" if len(value) > 12 else "***"
                print_success(f"{var}: {masked}")
            else:
                print_success(f"{var}: {value}")
        else:
            print_error(f"{var}: NOT SET")
            missing_vars.append(var)
    
    return len(missing_vars) == 0


def test_aws_service():
    """Test AWS service initialization"""
    print_step("2", "Testing AWS service...")
    
    try:
        from ai_backend.services.aws_service import init_aws_service
        
        aws_service = init_aws_service(
            access_key=os.getenv("AWS_ACCESS_KEY_ID"),
            secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            bucket=os.getenv("AWS_S3_BUCKET"),
            region=os.getenv("AWS_REGION", "us-east-1")
        )
        
        if aws_service.test_connection():
            print_success("AWS S3 connection successful")
            return True
        else:
            print_error("AWS S3 connection failed")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_file_upload():
    """Test file upload"""
    print_step("3", "Testing file upload...")
    
    try:
        from ai_backend.services.storage import upload_to_s3
        
        # Create test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content for AWS S3")
            test_file = f.name
        
        # Upload
        url = upload_to_s3(test_file, folder="test")
        
        if url:
            print_success(f"Upload successful: {url}")
            
            # Verify accessibility
            import requests
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    print_success("File is publicly accessible")
                else:
                    print_warning(f"File returned status {response.status_code}")
            except:
                print_warning("Could not verify public access")
            
            return True
        else:
            print_error("Upload failed")
            return False
            
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print_header("AWS S3 Configuration Test Suite")
    
    results = []
    
    results.append(("Environment Variables", test_environment_variables()))
    results.append(("AWS Service", test_aws_service()))
    results.append(("File Upload", test_file_upload()))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed\n")
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}  {test_name}")
    
    if passed == total:
        print_header("✅ All Tests Passed!")
        return 0
    else:
        print_header("❌ Some Tests Failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())