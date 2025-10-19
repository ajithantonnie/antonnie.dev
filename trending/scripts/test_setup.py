#!/usr/bin/env python3
"""
Test script to validate the trending news generator setup
"""
import sys
import os
import subprocess

def test_python_version():
    """Test if Python version is compatible"""
    print(f"✓ Python version: {sys.version}")
    return sys.version_info >= (3, 8)

def test_script_exists():
    """Test if the main script exists"""
    script_path = os.path.join(os.path.dirname(__file__), "news_generator.py")
    exists = os.path.exists(script_path)
    print(f"{'✓' if exists else '✗'} Script exists: {script_path}")
    return exists

def test_requirements():
    """Test if requirements file exists"""
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    exists = os.path.exists(req_path)
    print(f"{'✓' if exists else '✗'} Requirements file exists: {req_path}")
    return exists

def test_posts_directory():
    """Test if posts directory can be created"""
    posts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "posts")
    try:
        os.makedirs(posts_dir, exist_ok=True)
        print(f"✓ Posts directory ready: {posts_dir}")
        return True
    except Exception as e:
        print(f"✗ Failed to create posts directory: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing trending news generator setup...")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_script_exists,
        test_requirements,
        test_posts_directory
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append(False)
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed ({passed}/{total})")
        print("✅ Ready for GitHub Actions automation!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed ({passed}/{total})")
        return 1

if __name__ == "__main__":
    exit(main())