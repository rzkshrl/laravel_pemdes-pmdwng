import os
import pandas as pd
import subprocess

# Load Excel daftar desa
df = pd.read_excel("/volume1/scripts/daftar_desa.xlsx")
print("Columns in Excel file:", df.columns.tolist())  # Debug: print column names

BASE_PATH = "/volume1/PemdesData/Data Desa"

for _, row in df.iterrows():
    kecamatan = str(row["Kecamatan"]).strip().replace(" ", "_")
    desa = str(row["Desa"]).strip().replace(" ", "_")
    username = desa.lower()

    # Buat folder Kecamatan/Desa jika belum ada
    folder_path = os.path.join(BASE_PATH, kecamatan, desa)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"✅ Folder dibuat: {folder_path}")
    else:
        print(f"⚠️ Folder sudah ada: {folder_path}")

    # Buat user per desa (jika belum ada)
    try:
        subprocess.run(
            ["synouser", "--add", username, "password123", username, username, "/sbin/nologin", "0"],
            capture_output=True, text=True, check=True
        )
        print(f"✅ User dibuat: {username}")
    except Exception as e:
        print(f"⚠️ User {username} gagal dibuat/sudah ada. {e}")

    # Atur permission hanya untuk user desa tsb
    try:
        subprocess.run(
            ["synoacltool", "-add", folder_path, f"user:{username}:allow:rwxpdDaARWcCo"],
            check=True
        )
        print(f"✅ Permission diberikan ke {username} untuk {folder_path}")
    except Exception as e:
        print(f"⚠️ Gagal set permission {username}. {e}")