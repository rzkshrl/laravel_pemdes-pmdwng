#!/usr/bin/env python3
import os
import subprocess

BASE = "/volume1/PemdesData/Data Desa"

def enforce_acl(path):
    """Jalankan synoacltool -enforce-inherit pada path"""
    try:
        result = subprocess.run(
            ["synoacltool", "-enforce-inherit", path, ":fd--"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print(f"✅ OK: {path}")
        else:
            print(f"⚠️ Gagal: {path} ({result.stderr.strip()})")
    except Exception as e:
        print(f"❌ Error pada {path}: {e}")

def main():
    print("=== Mulai enforce inheritance ACL di semua folder desa ===")
    for root, dirs, _ in os.walk(BASE):
        for d in dirs:
            folder_path = os.path.join(root, d)
            enforce_acl(folder_path)
    print("=== Selesai ===")

if __name__ == "__main__":
    main()