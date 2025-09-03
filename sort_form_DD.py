import os
import shutil
import pandas as pd

# Path NAS
FORM_RESPONSES_XLSX = "/volume1/homes/adminpemdes/FormResponseGDriveSync/Monitoring Dana Desa Tahap 2 (Jawaban).xlsx"
SRC_DIR = "/volume1/homes/adminpemdes/SynologyGDriveUpload/"
DEST_BASE = "/volume1/PemdesData/Data Desa/"

dfEarmark = pd.read_excel(FORM_RESPONSES_XLSX, sheet_name="Data EARMARK")

dfEarmark.columns = dfEarmark.columns.str.strip()   # hapus spasi berlebih

# Debug: tampilkan kolom
print("Kolom terbaca:", dfEarmark.columns.tolist())

KOLOM_KEC = "Kecamatan"
KOLOM_DESA = "Desa"
KOLOM_LINK = "Link File"
KOLOM_NAMA_FILE = "Nama File"

for _, row in dfEarmark.iterrows():
    kecamatan = str(row[KOLOM_KEC]).strip()
    desa = str(row[KOLOM_DESA]).strip().replace("-", "_")
    link = str(row[KOLOM_LINK]).strip()
    fname = str(row[KOLOM_NAMA_FILE]).strip()

    print(f"[INFO] Desa={desa}, File={fname}, Link={link}")

    # Buat folder jika belum ada
    kec_folder = os.path.join(DEST_BASE, kecamatan)
    desa_folder = os.path.join(kec_folder, desa, "Dana Desa 2025")

    src_file = os.path.join(SRC_DIR, fname)
    dest_file = os.path.join(desa_folder, fname)         

    if os.path.exists(src_file):
        if not os.path.exists(dest_file):
            print(f"Memindahkan {fname} -> {os.path.join(kec_folder, desa, 'Dana Desa 2025')}/")
            shutil.move(src_file, dest_file)
    else:
        print(f"[WARNING] File {fname} tidak ditemukan di {SRC_DIR}")

dfNonEarmark = pd.read_excel(FORM_RESPONSES_XLSX, sheet_name="Data NON-EARMARK")

dfNonEarmark.columns = dfNonEarmark.columns.str.strip()   # hapus spasi berlebih

# Debug: tampilkan kolom
print("Kolom terbaca:", dfNonEarmark.columns.tolist())

KOLOM_KEC = "Kecamatan"
KOLOM_DESA = "Desa"
KOLOM_LINK = "Link File"
KOLOM_NAMA_FILE = "Nama File"

for _, row in dfNonEarmark.iterrows():
    kecamatan = str(row[KOLOM_KEC]).strip()
    desa = str(row[KOLOM_DESA]).strip().replace("-", "_")
    link = str(row[KOLOM_LINK]).strip()
    fname = str(row[KOLOM_NAMA_FILE]).strip()

    print(f"[INFO] Desa={desa}, File={fname}, Link={link}")

    # Buat folder jika belum ada
    kec_folder = os.path.join(DEST_BASE, kecamatan)
    desa_folder = os.path.join(kec_folder, desa, "Dana Desa 2025")

    src_file = os.path.join(SRC_DIR, fname)
    dest_file = os.path.join(desa_folder, fname)         

    if os.path.exists(src_file):
        if not os.path.exists(dest_file):
            print(f"Memindahkan {fname} -> {kec_folder}/{desa_folder}/")
            shutil.move(src_file, dest_file)
    else:
        print(f"[WARNING] File {fname} tidak ditemukan di {SRC_DIR}")