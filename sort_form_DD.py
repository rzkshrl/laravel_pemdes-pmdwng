import os
import shutil
import pandas as pd

FORM_RESPONSES_XLSX = "/volume1/homes/adminpemdes/FormResponseGDriveSync/Monitoring Dana Desa Tahap 2 (Jawaban).xlsx"
DEST_BASE = "/volume1/PemdesData/Data Desa/"

KOLOM_KEC = "Kecamatan"
KOLOM_DESA = "Desa"
KOLOM_LINK = "Link File"
KOLOM_NAMA = "Nama File"

sheet_configs = [
    {
        "sheet_name": "Data EARMARK",
        "src_dir": "/volume1/homes/adminpemdes/SynologyGDriveUpload/EARMARK",
        "subfolder": "EARMARK",
        "info": "EARMARK"
    },
    {
        "sheet_name": "Data NON-EARMARK",
        "src_dir": "/volume1/homes/adminpemdes/SynologyGDriveUpload/NON-EARMARK",
        "subfolder": "NON-EARMARK",
        "info": "NON-EARMARK"
    }
]

def process_sheet(sheet_name, src_dir, subfolder, info):
    df = pd.read_excel(FORM_RESPONSES_XLSX, sheet_name=sheet_name)
    df.columns = df.columns.str.strip()
    print(f"Kolom {info} terbaca:", df.columns.tolist())

    for _, row in df.iterrows():
        kecamatan = str(row[KOLOM_KEC]).strip()
        desa = str(row[KOLOM_DESA]).strip().replace("-", "_")
        fname = str(row[KOLOM_NAMA]).strip()

        print(f"[INFO {info}] Desa={desa}, File={fname}")

        kec_folder = os.path.join(DEST_BASE, kecamatan)
        desa_folder = os.path.join(kec_folder, desa, "Dana Desa 2025", subfolder)
        os.makedirs(desa_folder, exist_ok=True)

        src_file = os.path.join(src_dir, fname)
        dest_file = os.path.join(desa_folder, fname)

        if os.path.exists(src_file):
            if not os.path.exists(dest_file):
                print(f"Memindahkan {fname} -> {desa_folder}/")
                shutil.move(src_file, dest_file)
        else:
            print(f"[WARNING] File {fname} tidak ditemukan di {src_dir}")

for config in sheet_configs:
    process_sheet(**config)
