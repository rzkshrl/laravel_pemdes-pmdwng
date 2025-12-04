# sort_form.py (versi validator)
import os
import pandas as pd

# Path metadata & tujuan
FORM_RESPONSES_XLSX = "/volume1/homes/adminpemdes/FormResponseGDriveSync/Respon Form Desa.xlsx"
DEST_BASE = "/volume1/KEUANGAN DESA_PEMDES/Pengumpulan Data Desa/"

# Baca metadata dari "Data Bersih"
df = pd.read_excel(FORM_RESPONSES_XLSX, sheet_name="Data Bersih")
df.columns = df.columns.str.strip()

print("Validasi struktur berdasarkan Data Bersih...")

KOLOM_KEC = "Kecamatan"
KOLOM_DESA = "Desa"
KOLOM_TAHUN = "Tahun"
KOLOM_BULAN = "Bulan"
KOLOM_FILE = "Nama File"

missing_files = []
ok_files = 0

for _, row in df.iterrows():
    kecamatan = str(row[KOLOM_KEC]).strip()
    desa = str(row[KOLOM_DESA]).strip().replace("-", "_")
    tahun = str(row[KOLOM_TAHUN]).strip()
    bulan = str(row[KOLOM_BULAN]).strip()
    fname = str(row[KOLOM_FILE]).strip()

    spj_folder = os.path.join(DEST_BASE, kecamatan, desa, f"SPJ {tahun}", bulan)
    dest_file = os.path.join(spj_folder, fname)

    if os.path.exists(dest_file):
        ok_files += 1
    else:
        missing_files.append(dest_file)

print(f"[SUMMARY] Total file OK: {ok_files}")
if missing_files:
    print(f"[WARNING] Ada {len(missing_files)} file hilang:")
    for f in missing_files[:20]:  # tampilkan max 20 biar log tidak kebanjiran
        print("  -", f)