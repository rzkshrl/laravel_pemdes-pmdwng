import os
import pandas as pd
import subprocess

# Load Excel daftar desa
df = pd.read_excel("/volume1/scripts/daftar_desa.xlsx")
print("Columns in Excel file:", df.columns.tolist())  # Debug: print column names

BASE_PATH = "/volume1/PemdesData/Data Desa"
SHARED_FOLDER = "PemdesData"  # nama shared folder di DSM

for _, row in df.iterrows():
    kecamatan = str(row["Kecamatan"]).strip().replace(" ", "_")
    desa = str(row["Desa"]).strip().replace(" ", "_")
    username = desa.lower()
    usernameKecamatan = kecamatan.lower()

    # Buat folder Kecamatan/Desa jika belum ada
    folder_path = os.path.join(BASE_PATH, kecamatan, desa)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"✅ Folder dibuat: {folder_path}")
    else:
        print(f"⚠️ Folder sudah ada: {folder_path}")

    # Buat user per desa (jika belum ada)
    try:
        os.system(f"synouser --add {username} password123 '{username}' 0 '' 0")
        print(f"✅ User dibuat: {username}")
    except Exception as e:
        print(f"⚠️ User {username} gagal dibuat/sudah ada. {e}")

    # Tambah akses shared folder level root
    try:
        os.system(f"synoshare --setuser {SHARED_FOLDER} {username} RW")
        print(f"✅ Shared folder access diberikan ke {username}")
    except Exception as e:
        print(f"⚠️ Gagal set shared folder {username}. {e}")

    # Atur permission hanya untuk user desa tsb
    try:
        os.system(f"synoacltool -add '{folder_path}' 'user:{username}:allow:rwxpdDaARWcCo:fd--'")
        print(f"✅ Permission diberikan ke {username} untuk {folder_path}")
    except Exception as e:
        print(f"⚠️ Gagal set permission {username}. {e}")


    # Lock folder kecamatan agar user tidak bisa intip desa lain
    try:
        kec_path = os.path.join(BASE_PATH, kecamatan)
        os.system(f"synoacltool -add '{kec_path}' 'everyone@:deny:r-x---a-R-c--:fd--' 2>/dev/null")
        print(f"🔒 Lock folder {kecamatan}")
    except Exception as e:
        print(f"⚠️ Gagal lock folder {kecamatan}. {e}")

    # Lock root folder agar semua user tidak bisa melihat isi selain foldernya sendiri
    try:
        os.system(f"synoacltool -add '{BASE_PATH}' 'everyone@:deny:r-x---a-R-c--:fd--' 2>/dev/null")
        print(f"🔒 Lock root folder {BASE_PATH}")
    except Exception as e:
        print(f"⚠️ Gagal lock root folder {BASE_PATH}. {e}")