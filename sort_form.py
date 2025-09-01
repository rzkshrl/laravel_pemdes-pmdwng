import os
import shutil
import pandas as pd

# Path NAS
FORM_RESPONSES_XLSX = "/volume1/homes/adminpemdes/FormResponseGDriveSync/Respon Form Desa.xlsx"
SRC_DIR = "/volume1/homes/adminpemdes/SynologyGDriveUpload/"
DEST_BASE = "/volume1/PemdesData/Data Desa/"

df = pd.read_excel(FORM_RESPONSES_XLSX, sheet_name="Data Bersih")

df.columns = df.columns.str.strip()   # hapus spasi berlebih

# Debug: tampilkan kolom
print("Kolom terbaca:", df.columns.tolist())

KOLOM_KEC = "Kecamatan"
KOLOM_DESA = "Desa"
KOLOM_LINK = "Upload File"
KOLOM_NAMA_FILE = "Nama File"

for _, row in df.iterrows():
    kecamatan = str(row[KOLOM_KEC]).strip()
    desa = str(row[KOLOM_DESA]).strip().replace("-", "_")
    link = str(row[KOLOM_LINK]).strip()
    fname = str(row[KOLOM_NAMA_FILE]).strip()

    print(f"[INFO] Desa={desa}, File={fname}, Link={link}")

    # Buat folder jika belum ada
    kec_folder = os.path.join(DEST_BASE, kecamatan)
    desa_folder = os.path.join(kec_folder, desa)

    src_file = os.path.join(SRC_DIR, fname)
    dest_file = os.path.join(desa_folder, fname)         

    if os.path.exists(src_file):
        if not os.path.exists(dest_file):
            print(f"Memindahkan {fname} -> {kec_folder}/{desa_folder}/")
            shutil.move(src_file, dest_file)
    else:
        print(f"[WARNING] File {fname} tidak ditemukan di {SRC_DIR}")