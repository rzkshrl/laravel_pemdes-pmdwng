#!/usr/bin/env python3
from flask import Flask, request, jsonify
import os
import logging

app = Flask(__name__)

# Setup logging
logging.basicConfig(
    filename="/volume1/scripts/webhook_server.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print(f"Webhook diterima: {data}")

    kec = data.get("kecamatan")
    desa = data.get("desa")
    tahun = data.get("tahun")
    bulan = data.get("bulan")
    file_ids = data.get("fileIds", "").split(",")

    dest_folder = f"/volume1/PemdesData/Data Desa/{kec}/{desa}/SPJ {tahun}/{bulan}"
    os.makedirs(dest_folder, exist_ok=True)

    for fid in file_ids:
        fid = fid.strip()
        if not fid:
            continue
        gdrive_path = f"gdrive:{fid}"

        # Copy ke NAS
        cmd_copy = f"rclone copy '{gdrive_path}' '{dest_folder}' --ignore-existing"
        os.system(cmd_copy)

        # Verifikasi file terunduh di NAS sebelum delete
        files_local = os.listdir(dest_folder)
        if any(fid in f for f in files_local):
            cmd_delete = f"rclone delete '{gdrive_path}'"
            os.system(cmd_delete)
            print(f"[INFO] File {fid} dipindahkan & dihapus dari Google Drive")
        else:
            print(f"[WARNING] File {fid} belum ditemukan di NAS, skip delete")

    # Jalankan sortir setelah file berhasil dipindah
    os.system("python3 /volume1/scripts/sort_form.py")

    return jsonify({"status": "ok", "processed": len(file_ids)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)