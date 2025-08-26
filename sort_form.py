import os
import shutil
import pandas as pd

# Path NAS
FORM_RESPONSES_XLSX = "/volume1/homes/adminpemdes/FormResponseGDriveSync/Respon Form Desa.xlsx"
SRC_DIR = "/volume1/homes/adminpemdes/SynologyGDriveUpload/"
DEST_BASE = "/volume1/homes/adminpemdes/PemdesData/Data Desa/"

KOLOM_DESA = "Nama Desa"
KOLOM_UPLOAD = "Upload Dokumen"

df = pd.read_excel(FORM_RESPONSES_XLSX)

for _, row in df.iterrows():
    desa = str(row[KOLOM_DESA]).strip()
    uploads = str(row[KOLOM_UPLOAD]).split(",")

    # Buat folder desa
    desa_folder = os.path.join(DEST_BASE, desa)
    os.makedirs(desa_folder, exist_ok=True)

    for upload in uploads:
        upload = upload.strip()

        # Ambil nama file asli (kalau berupa link Google Drive)
        if "drive.google.com" in upload:
            fname = upload.split("/")[-1]  # ambil bagian akhir link
        else:
            fname = upload

        # Cari file di folder sumber
        found_file = None
        for f in os.listdir(SRC_DIR):
            if fname in f:   # cocokkan substring
                found_file = f
                break

        if found_file:
            src_file = os.path.join(SRC_DIR, found_file)
            dest_file = os.path.join(desa_folder, found_file)
            if not os.path.exists(dest_file):
                print(f"Memindahkan {found_file} -> {desa_folder}")
                shutil.move(src_file, dest_file)
        else:
            print(f"[WARNING] File tidak ditemukan untuk '{fname}'")