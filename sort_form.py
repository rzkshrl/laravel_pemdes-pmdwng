import os
import shutil
import pandas as pd

# Path NAS
FORM_RESPONSES_XLSX = "/volume1/homes/adminpemdes/FormResponseGDriveSync/Respon Form Desa.xlsx"
SRC_DIR = "/volume1/homes/adminpemdes/SynologyGDriveUpload/"
DEST_BASE = "/volume1/homes/adminpemdes/PemdesData/Data Desa/"

df = pd.read_excel(FORM_RESPONSES_XLSX)

df.columns = df.columns.str.strip()   # hapus spasi berlebih

# Debug: tampilkan kolom
print("Kolom terbaca:", df.columns.tolist())

KOLOM_DESA = "Nama Desa"
KOLOM_LINK = "Upload Dokumen"
KOLOM_NAMA_FILE = "Nama File Asli"

for _, row in df.iterrows():
    desa = str(row[KOLOM_DESA]).strip()
    link = str(row[KOLOM_LINK]).strip()
    fname = str(row[KOLOM_NAMA_FILE]).strip()

    print(f"[INFO] Desa={desa}, File={fname}, Link={link}")

    desa_folder = os.path.join(DEST_BASE, desa)
    os.makedirs(desa_folder, exist_ok=True)

    src_file = os.path.join(SRC_DIR, fname)
    dest_file = os.path.join(desa_folder, fname)

    if os.path.exists(src_file):
        if not os.path.exists(dest_file):
            print(f"Memindahkan {fname} -> {desa_folder}")
            shutil.move(src_file, dest_file)
    else:
        print(f"[WARNING] File {fname} tidak ditemukan di {SRC_DIR}")