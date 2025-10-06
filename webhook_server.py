#!/usr/bin/env python3
from flask import Flask, request, jsonify
import os
import logging
import time

app = Flask(__name__)

# === Setup logging ===
LOG_FILE = "/volume1/scripts/webhook_server.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

RCLONE = "/bin/rclone"  # path rclone di NAS kamu
RCLONE_FLAGS = (
    "--ignore-existing "
    "--checkers=16 "
    "--transfers=8 "
    "--drive-chunk-size=64M "
    "--buffer-size=32M "
    "--tpslimit=8 "
    "--low-level-retries=10 "
    "--retries=5 "
    "--retries-sleep=2s "
    "--timeout=2m -v"
)

@app.route("/webhook", methods=["POST"])
def webhook():
    start_time = time.time()
    data = request.json or {}
    logging.info(f"Webhook diterima: {data}")

    kec = (data.get("kecamatan") or "").strip()
    desa = (data.get("desa") or "").strip().replace("-", "_")
    tahun = (data.get("tahun") or "").strip()
    bulan = (data.get("bulan") or "").strip()
    fname = (data.get("files") or "").strip()
    file_ids = (data.get("fileIds") or "").split(",")

    # Validasi data wajib
    if not all([kec, desa, tahun, bulan, fname]):
        logging.warning(f"Data tidak lengkap, webhook dilewati: {data}")
        return jsonify({"status": "skip", "reason": "data incomplete"}), 400

    dest_folder = f"/volume1/PemdesData/Data Desa/{kec}/{desa}/SPJ {tahun}/{bulan}"
    os.makedirs(dest_folder, exist_ok=True)
    logging.info(f"Membuat folder tujuan: {dest_folder}")

    # === Jalankan proses copy ===
    gdrive_path = f'gdrive:/Form Upload Dokumen Desa (File responses)/Upload Dokumen (File responses)/{fname}'
    cmd_copy = f'{RCLONE} copy "{gdrive_path}" "{dest_folder}" {RCLONE_FLAGS}'
    logging.info(f"Menjalankan copy: {cmd_copy}")
    copy_exit = os.system(cmd_copy)
    logging.info(f"Hasil copy (exit code): {copy_exit}")

    # === Verifikasi file terunduh ===
    files_local = os.listdir(dest_folder)
    found_file = any(fname in f for f in files_local)

    if found_file:
        # Jika ditemukan, hapus dari GDrive
        cmd_delete = f'{RCLONE} delete "{gdrive_path}" --drive-use-trash=false -v'
        os.system(cmd_delete)
        logging.info(f"File {fname} berhasil dipindahkan & dihapus dari Google Drive")
    else:
        logging.warning(f"File {fname} belum ditemukan di NAS, skip delete")

    # === Jalankan validasi sortir ===
    os.system("python3 /volume1/scripts/sort_form.py")

    elapsed = round(time.time() - start_time, 2)
    logging.info(f"[PERFORMANCE] Total waktu proses: {elapsed} detik")

    return jsonify({"status": "ok", "file": fname, "duration_sec": elapsed})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)