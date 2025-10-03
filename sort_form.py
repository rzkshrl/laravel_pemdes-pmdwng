import os
import shutil
import pandas as pd

# Path NAS
FORM_RESPONSES_XLSX = "/volume1/homes/adminpemdes/FormResponseGDriveSync/Respon Form Desa.xlsx"
SRC_DIR = "/volume1/homes/adminpemdes/SynologyGDriveUpload/"
DEST_BASE = "/volume1/PemdesData/Data Desa/"

df = pd.read_excel(FORM_RESPONSES_XLSX, sheet_name="Data Bersih")
df.columns = df.columns.str.strip()

print("Kolom terbaca:", df.columns.tolist())

KOLOM_KEC = "Kecamatan"
KOLOM_DESA = "Desa"
KOLOM_NAMA_FILE = "Nama File"
KOLOM_TAHUN = "Tahun"
KOLOM_BULAN = "Bulan"

for _, row in df.iterrows():
    kecamatan = str(row[KOLOM_KEC]).strip()
    desa = str(row[KOLOM_DESA]).strip().replace("-", "_")
    fname = str(row[KOLOM_NAMA_FILE]).strip()
    tahun = str(row[KOLOM_TAHUN]).strip()
    bulan = str(row[KOLOM_BULAN]).strip()

    print(f"[INFO] Desa={desa}, File={fname}")

    kec_folder = os.path.join(DEST_BASE, kecamatan)
    desa_folder = os.path.join(kec_folder, desa)
    spj_folder = os.path.join(desa_folder, f"SPJ {tahun}", bulan)
    os.makedirs(spj_folder, exist_ok=True)

    src_file = os.path.join(SRC_DIR, fname)
    dest_file = os.path.join(spj_folder, fname)

    print(f"DEBUG: src_file={src_file}, dest_file={dest_file}")

    if os.path.exists(src_file):
        if not os.path.exists(dest_file):
            print(f"Memindahkan {fname} -> {spj_folder}")
            shutil.move(src_file, dest_file)
            print(f"[INFO] File dipindah ke {dest_file}")
        else:
            local_size_src = os.path.getsize(src_file)
            local_size_dest = os.path.getsize(dest_file)
            if local_size_src == local_size_dest:
                print(f"[INFO] File sama, overwrite {dest_file}")
                shutil.move(src_file, dest_file)
            else:
                print(f"[WARNING] File berbeda ukuran, skip overwrite {dest_file}")
    elif os.path.exists(dest_file):
        print(f"[DEBUG] File {fname} sudah ada di tujuan, skip pemindahan.")
    else:
        print(f"[WARNING] File {fname} tidak ditemukan di {SRC_DIR} maupun tujuan.")