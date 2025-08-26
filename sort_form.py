import os
import shutil
import pandas as pd

# Path NAS
FORM_RESPONSES_XLSX = "/volume1/homes/adminpemdes/FormResponeGDriveSync/Respon Form Desa.xlsx"
SRC_DIR = "/volume1/homes/adminpemdes/SynologyGDriveUpload/"
DEST_BASE = "/volume1/homes/adminpemdes/PemdesData/Data Desa/"

# Baca data dari Spreadsheet
df = pd.read_excel(FORM_RESPONSES_XLSX)

# Nama kolom sesuai header di Google Form Responses
KOLOM_DESA = "Nama Desa"
KOLOM_UPLOAD = "Upload Dokumen"

# Baca data form
df = pd.read_excel(FORM_RESPONSES_XLSX)

for _, row in df.iterrows():
    desa = str(row[KOLOM_DESA]).strip()
    files = str(row[KOLOM_UPLOAD]).split(",")  # kalau lebih dari 1 file dipisah koma

    # Buat folder untuk desa (jika belum ada)
    desa_folder = os.path.join(DEST_BASE, desa)
    os.makedirs(desa_folder, exist_ok=True)

    for fname in files:
        fname = fname.strip()
        src_file = os.path.join(SRC_DIR, fname)
        if os.path.exists(src_file):
            dest_file = os.path.join(desa_folder, fname)
            if not os.path.exists(dest_file):  # hindari overwrite
                print(f"Memindahkan {fname} -> {desa_folder}")
                shutil.move(src_file, dest_file)