"""
Quick test script to verify server can start
Run this to check if all imports and basic setup work
"""
import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

print("Testing imports...")
try:
    from speech_to_text.config import SERVER_HOST, SERVER_PORT, REPO_ID, DEVICE
    print(f"✅ Config loaded: {SERVER_HOST}:{SERVER_PORT}, Device: {DEVICE}")
except Exception as e:
    print(f"❌ Config import failed: {e}")
    sys.exit(1)

try:
    from speech_to_text.server import app
    print("✅ Server app imported successfully")
except Exception as e:
    print(f"❌ Server import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All imports successful!")
print("=" * 60)
print("\nTo start the server, run:")
print("  python ../start_speech_to_text.py")
print("\nNote: First run will download the model (~3GB) and may take 10-30 minutes")
print("=" * 60)



