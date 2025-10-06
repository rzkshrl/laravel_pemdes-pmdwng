#!/usr/bin/env python3
from flask import Flask, request, jsonify
import os
import logging

app = Flask(__name__)

# === Logging setup ===
LOG_PATH = "/volume1/scripts/webhook_server.log"
RCLONE_LOG = "/volume1/scripts/rclone_webhook_debug.log"
RCLONE_CONFIG = "/root/.config/rclone/rclone.conf"

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}
    logging.info(f"Webhook diterima: {data}")

    kec = (data.get("kecamatan") or "").strip()
    desa = (data.get("desa") or "").strip().replace("-", "_")
    tahun = (data.get("tahun") or "").strip()
    bulan = (data.get("bulan") or "").strip()
    fname = (data.get("files") or "").strip()
    file_ids = (data.get("fileIds") or "").split(",")

    if not all([kec, desa, tahun, bulan, fname]):
        logging.warning(f"Data tidak lengkap, dilewati: {data}")
        return jsonify({"status": "skip", "reason": "incomplete data"}), 400

    dest_folder = f"/volume1/PemdesData/Data Desa/{kec}/{desa}/SPJ {tahun}/{bulan}"
    os.makedirs(dest_folder, exist_ok=True)
    logging.info(f"Membuat folder tujuan: {dest_folder}")

    # --- Lokasi file di Google Drive ---
    gdrive_path = f"gdrive:/Form Upload Dokumen Desa (File responses)/Upload Dokumen (File responses)/{fname}"

    # --- Copy file ---
    cmd_copy = (
        f'rclone --config "{RCLONE_CONFIG}" copy "{gdrive_path}" "{dest_folder}" '
        f'--ignore-existing -vv --log-file="{RCLONE_LOG}"'
    )
    logging.info(f"Menjalankan copy: {cmd_copy}")
    os.system(cmd_copy)

    # --- Verifikasi file sudah muncul ---
    files_local = os.listdir(dest_folder)
    if any(fname in f for f in files_local):
        logging.info(f"File {fname} berhasil di-copy ke NAS, lanjut delete di GDrive")
        cmd_delete = f'rclone --config "{RCLONE_CONFIG}" delete "{gdrive_path}" -vv --log-file="{RCLONE_LOG}"'
        os.system(cmd_delete)
    else:
        logging.warning(f"File {fname} belum muncul di NAS, skip delete")

    # --- Jalankan validasi sort_form.py ---
    logging.info(f"Menjalankan sort_form.py untuk validasi folder...")
    os.system("python3 /volume1/scripts/sort_form.py")

    return jsonify({"status": "ok", "file": fname})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)