import os
import pandas as pd
import subprocess

# --- Helpers & toggles ---
ENABLE_LOCK_PARENTS = False  # set True only if you really want to hide Kecamatan/root from listing

def run_cmd(cmd, ok_msg, err_msg):
    rc = os.system(cmd)
    if rc == 0:
        print(ok_msg)
    else:
        print(f"{err_msg} (exit={rc})")
    return rc

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

    # Tambah akses shared folder level root (cek dulu)
    try:
        share_info = os.popen(f"synoshare --get {SHARED_FOLDER} 2>/dev/null").read()
        if (username in share_info) and ("RW" in share_info.split(username)[-1][:20]):
            print(f"⚠️ Shared folder sudah RW untuk {username}")
        else:
            run_cmd(f"synoshare --setuser {SHARED_FOLDER} {username} RW",
                    f"✅ Shared folder access diberikan ke {username}",
                    f"⚠️ Gagal set shared folder {username}")
    except Exception as e:
        print(f"⚠️ Gagal cek/set shared folder {username}. {e}")

    # Atur permission hanya untuk user desa tsb
    try:
        acl_check = os.popen(f"synoacltool -get '{folder_path}' | grep {username}").read()
        if "allow" in acl_check:
            print(f"⚠️ Permission sudah ada untuk {username} di {folder_path}")
        else:
            run_cmd(f"synoacltool -add '{folder_path}' 'user:{username}:allow:rwxpdDaARWcCo:fd--' 2>/dev/null",
                    f"✅ Permission diberikan ke {username} untuk {folder_path}",
                    f"⚠️ Gagal set permission {username} di {folder_path}")
    except Exception as e:
        print(f"⚠️ Gagal set permission {username}. {e}")



    # Opsi 2: Jadikan folder desa sebagai My Drive langsung (bind mount)
    try:
        user_drive = f"/var/services/homes/{username}/Drive"
        if os.path.islink(user_drive) or os.path.exists(user_drive):
            print(f"⚠️ My Drive sudah ada untuk {username}, skip bind")
        else:
            os.makedirs(user_drive, exist_ok=True)
            run_cmd(f"mount --bind '{folder_path}' '{user_drive}'",
                    f"🔗 My Drive {username} diarahkan ke {folder_path}",
                    f"⚠️ Gagal bind My Drive untuk {username}")
    except Exception as e:
        print(f"⚠️ Gagal setup My Drive untuk {username}. {e}")

    # (Opsional) Lock folder kecamatan agar user tidak bisa intip desa lain
    if ENABLE_LOCK_PARENTS:
        try:
            kec_path = os.path.join(BASE_PATH, kecamatan)
            kec_acl = os.popen(f"synoacltool -get '{kec_path}' 2>/dev/null").read()
            # Hindari pola dengan tanda '-' yang memicu error; jika perlu, gunakan deny minimal 'r' saja.
            if "everyone@" in kec_acl and "deny" in kec_acl:
                print(f"⚠️ Folder {kecamatan} sudah di-lock")
            else:
                run_cmd(f"synoacltool -add '{kec_path}' 'everyone@:deny:r-x:fd--' 2>/dev/null",
                        f"🔒 Lock folder {kecamatan}",
                        f"⚠️ Gagal lock folder {kecamatan}")
        except Exception as e:
            print(f"⚠️ Gagal lock folder {kecamatan}. {e}")
    else:
        pass

    # (Opsional) Lock root folder agar semua user tidak bisa melihat isi selain foldernya sendiri
    if ENABLE_LOCK_PARENTS:
        try:
            root_acl = os.popen(f"synoacltool -get '{BASE_PATH}' 2>/dev/null").read()
            if "everyone@" in root_acl and "deny" in root_acl:
                print(f"⚠️ Root folder {BASE_PATH} sudah di-lock")
            else:
                run_cmd(f"synoacltool -add '{BASE_PATH}' 'everyone@:deny:r-x:fd--' 2>/dev/null",
                        f"🔒 Lock root folder {BASE_PATH}",
                        f"⚠️ Gagal lock root folder {BASE_PATH}")
        except Exception as e:
            print(f"⚠️ Gagal lock root folder {BASE_PATH}. {e}")
    else:
        pass