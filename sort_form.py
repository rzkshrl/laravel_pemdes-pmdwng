import os
import shutil
import pandas as pd

# Path NAS
FORM_RESPONSES_XLSX = "/volume1/FormResponses/ResponForm.xlsx"
SRC_DIR = "/volume1/FormResponses/"
DEST_BASE = "/volume1/DataDesa/"

# Baca data dari Spreadsheet
df = pd.read_excel(FORM_RESPONSES_XLSX)

# Sesuaikan nama kolom sesuai header di Form
KOLOM_DESA = "Nama/Kode Desa"
KOLOM_UPLOAD = "Upload Dokumen"

for _, row in df.iterrows():
    desa = str(row[KOLOM_DESA]).strip()
    upload_links = str(row[KOLOM_UPLOAD]).split(",")  # bisa lebih dari 1 file

    # Buat folder desa
    desa_folder = os.path.join(DEST_BASE, desa)
    os.makedirs(desa_folder, exist_ok=True)

    # Cari file di folder sync berdasarkan nama file
    for link in upload_links:
        if "/file/d/" in link:  # link Google Drive
            file_id = link.split("/file/d/")[1].split("/")[0]
            # biasanya Cloud Sync rename file pakai nama asli
            # jadi bisa pakai nama asli di log Sheet (opsional)
            # untuk sederhana, cek semua file di SRC_DIR
            for fname in os.listdir(SRC_DIR):
                fpath = os.path.join(SRC_DIR, fname)
                if os.path.isfile(fpath) and file_id in fname:
                    print(f"Memindahkan {fname} -> {desa_folder}")
                    shutil.move(fpath, os.path.join(desa_folder, fname))