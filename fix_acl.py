#!/usr/bin/env python3
import os
import subprocess

BASE = "/volume1/PemdesData/Data Desa"
USER = "desaAPI"

def set_acl(path):
    """Tambahkan ACL untuk user desa"""
    try:
        result = subprocess.run(
            ["synoacltool", "-add", path, f"user:{USER}:allow:r-x---a-R-c---:fd--"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print(f"✅ ACL ditambahkan: {path}")
        else:
            print(f"⚠️ Gagal ACL: {path} ({result.stderr.strip()})")
    except Exception as e:
        print(f"❌ Error pada {path}: {e}")

def enforce_acl(path):
    """Paksa inheritance ACL"""
    try:
        result = subprocess.run(
            ["synoacltool", "-enforce-inherit", path],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            print(f"✅ Inherit OK: {path}")
        else:
            print(f"⚠️ Gagal enforce: {path} (exit={result.returncode})")
    except Exception as e:
        print(f"❌ Error enforce {path}: {e}")

def main():
    print("=== Mulai atur ACL untuk semua folder desa ===")
    for root, dirs, _ in os.walk(BASE):
        for d in dirs:
            folder_path = os.path.join(root, d)
            set_acl(folder_path)
            enforce_acl(folder_path)
    print("=== Selesai ===")

if __name__ == "__main__":
    main()