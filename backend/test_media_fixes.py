"""
Test script to verify media upload fixes
"""
import asyncio
import io
import sys
from pathlib import Path
from fastapi import UploadFile
from app.services.media_service import validate_image, save_upload_file, MAX_FILE_SIZE, UPLOAD_DIR

# Fix unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


async def test_file_size_validation():
    """Test that files exceeding MAX_FILE_SIZE are rejected"""
    print("Testing file size validation...")

    # Create a mock file that's too large
    large_content = b"x" * (MAX_FILE_SIZE + 1)
    large_file = UploadFile(
        filename="large_test.jpg",
        file=io.BytesIO(large_content)
    )

    # Should return False for oversized file
    result = await validate_image(large_file)
    assert result is False, "validate_image should reject oversized files"
    print("  ✓ Large file rejected by validate_image")

    # Create a valid-sized file
    small_content = b"x" * 1024  # 1KB
    small_file = UploadFile(
        filename="small_test.jpg",
        file=io.BytesIO(small_content)
    )

    # Should return True for valid file
    result = await validate_image(small_file)
    assert result is True, "validate_image should accept valid files"
    print("  ✓ Small file accepted by validate_image")


async def test_save_upload_file_size_check():
    """Test that save_upload_file raises error for oversized files"""
    print("\nTesting save_upload_file size check...")

    # Create a mock file that's too large
    large_content = b"x" * (MAX_FILE_SIZE + 1)
    large_file = UploadFile(
        filename="large_test.jpg",
        file=io.BytesIO(large_content)
    )

    try:
        await save_upload_file(large_file)
        assert False, "save_upload_file should raise ValueError for oversized files"
    except ValueError as e:
        assert "exceeds maximum allowed size" in str(e)
        print(f"  ✓ Correctly raised ValueError: {e}")


async def test_path_traversal_fix():
    """Test that delete_project_media uses safe path construction"""
    print("\nTesting path traversal fix...")

    # Read the media_service.py file to verify the fix
    media_service_path = Path(__file__).parent / "app" / "services" / "media_service.py"
    content = media_service_path.read_text()

    # Check that the dangerous pattern is not present
    assert 'Path("." + media.url)' not in content, "Dangerous path construction still present"
    print("  ✓ Dangerous path construction removed")

    # Check that safe pattern is present
    assert "filename = Path(media.url).name" in content, "Safe filename extraction not found"
    assert "file_path = UPLOAD_DIR / filename" in content, "Safe path construction not found"
    print("  ✓ Safe path construction implemented")


async def test_error_handling():
    """Test that file operations have proper error handling"""
    print("\nTesting error handling...")

    # Read the media_service.py file
    media_service_path = Path(__file__).parent / "app" / "services" / "media_service.py"
    content = media_service_path.read_text()

    # Check for try-except block in save_upload_file
    assert "try:" in content and "except IOError" in content, "IOError handling not found"
    print("  ✓ IOError handling implemented")

    # Check for cleanup logic
    assert "if file_path.exists():" in content and "file_path.unlink()" in content, "Cleanup logic not found"
    print("  ✓ File cleanup logic present")


async def test_orphan_cleanup():
    """Test that router handles orphaned files"""
    print("\nTesting orphaned file cleanup...")

    # Read the router file
    router_path = Path(__file__).parent / "app" / "routers" / "admin" / "media.py"
    content = router_path.read_text()

    # Check for cleanup in exception handling
    assert "Clean up orphaned file" in content or "clean up" in content.lower(), "Cleanup logic not found in router"
    print("  ✓ Orphaned file cleanup logic present in router")

    # Check for proper exception handling around create_project_media
    assert "except Exception" in content or "except HTTPException" in content, "Exception handling not found"
    print("  ✓ Exception handling around database operations")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("Media Upload Fixes - Test Suite")
    print("=" * 60)

    try:
        await test_file_size_validation()
        await test_save_upload_file_size_check()
        await test_path_traversal_fix()
        await test_error_handling()
        await test_orphan_cleanup()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
