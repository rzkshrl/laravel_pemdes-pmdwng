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
        user_check = os.popen(f"synouser --get {username}").read()
        if "User does not exist" in user_check or not user_check.strip():
            os.system(f"synouser --add {username} password123 '{username}' 0 '' 0")
            print(f"✅ User dibuat: {username}")
        else:
            print(f"⚠️ User sudah ada: {username}")
    except Exception as e:
        print(f"⚠️ User {username} gagal dibuat/sudah ada. {e}")

    # Tambah akses shared folder level root
    try:
        share_check = os.popen(f"synoshare --getuser {SHARED_FOLDER}").read()
        if f"{username}:RW" in share_check:
            print(f"⚠️ Shared folder sudah RW untuk {username}")
        else:
            os.system(f"synoshare --setuser {SHARED_FOLDER} {username} RW")
            print(f"✅ Shared folder access diberikan ke {username}")
    except Exception as e:
        print(f"⚠️ Gagal set shared folder {username}. {e}")

    # Atur permission hanya untuk user desa tsb
    try:
        acl_check = os.popen(f"synoacltool -get '{folder_path}' | grep {username}").read()
        if "allow" in acl_check:
            print(f"⚠️ Permission sudah ada untuk {username} di {folder_path}")
        else:
            os.system(f"synoacltool -add '{folder_path}' 'user:{username}:allow:rwxpdDaARWcCo:fd--'")
            print(f"✅ Permission diberikan ke {username} untuk {folder_path}")
    except Exception as e:
        print(f"⚠️ Gagal set permission {username}. {e}")


    # Buat symlink ke folder desa di home user
    try:
        user_home = f"/var/services/homes/{username}"
        desa_link = os.path.join(user_home, "DesaKu")
        if not os.path.exists(desa_link):
            os.system(f"ln -s '{folder_path}' '{desa_link}'")
            print(f"🔗 Symlink dibuat: {desa_link} -> {folder_path}")
        else:
            print(f"⚠️ Symlink sudah ada untuk {username}")
    except Exception as e:
        print(f"⚠️ Gagal membuat symlink untuk {username}. {e}")

    # Lock folder kecamatan agar user tidak bisa intip desa lain
    try:
        kec_path = os.path.join(BASE_PATH, kecamatan)
        kec_acl_check = os.popen(f"synoacltool -get '{kec_path}' | grep everyone@").read()
        if "deny" in kec_acl_check:
            print(f"⚠️ Folder {kecamatan} sudah di-lock")
        else:
            os.system(f"synoacltool -add '{kec_path}' 'everyone@:deny:r-x---a-R-c--:fd--' 2>/dev/null")
            print(f"🔒 Lock folder {kecamatan}")
    except Exception as e:
        print(f"⚠️ Gagal lock folder {kecamatan}. {e}")

    # Lock root folder agar semua user tidak bisa melihat isi selain foldernya sendiri
    try:
        root_acl_check = os.popen(f"synoacltool -get '{BASE_PATH}' | grep everyone@").read()
        if "deny" in root_acl_check:
            print(f"⚠️ Root folder {BASE_PATH} sudah di-lock")
        else:
            os.system(f"synoacltool -add '{BASE_PATH}' 'everyone@:deny:r-x---a-R-c--:fd--' 2>/dev/null")
            print(f"🔒 Lock root folder {BASE_PATH}")
    except Exception as e:
        print(f"⚠️ Gagal lock root folder {BASE_PATH}. {e}")