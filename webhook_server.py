#!/usr/bin/env python3
from flask import Flask, request, jsonify
import os
import time
import logging

app = Flask(__name__)

# === Setup logging ===
logging.basicConfig(
    filename="/volume1/scripts/webhook_server.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}
    logging.info(f"Webhook diterima: {data}")

    # --- Ambil data dari JSON ---
    kec = (data.get("kecamatan") or "").strip()
    desa = (data.get("desa") or "").strip().replace("-", "_")
    tahun = (data.get("tahun") or "").strip()
    bulan = (data.get("bulan") or "").strip()
    fname = (data.get("files") or "").strip()

    # --- Validasi data wajib ---
    if not all([kec, desa, tahun, bulan, fname]):
        logging.warning(f"Data tidak lengkap, webhook dilewati: {data}")
        return jsonify({"status": "skip", "reason": "data incomplete"}), 400

    # --- Buat folder tujuan di NAS ---
    dest_folder = f"/volume1/PemdesData/Data Desa/{kec}/{desa}/SPJ {tahun}/{bulan}"
    os.makedirs(dest_folder, exist_ok=True)
    logging.info(f"Membuat folder tujuan: {dest_folder}")

    # --- Gunakan path fix di Google Drive ---
    gdrive_path = f'gdrive:/Form Upload Dokumen Desa (File responses)/Upload Dokumen (File responses)/{fname}'

    # --- Copy ke NAS ---
    cmd_copy = f'rclone copy "{gdrive_path}" "{dest_folder}" --ignore-existing -v'
    logging.info(f"Menjalankan copy: {cmd_copy}")
    exit_code = os.system(cmd_copy)
    logging.info(f"Hasil copy (exit code): {exit_code}")

    # --- Tunggu sebentar agar rclone benar-benar selesai ---
    time.sleep(3)

    # --- Verifikasi hasil copy ---
    dest_file = os.path.join(dest_folder, fname)
    if os.path.exists(dest_file):
        file_size = os.path.getsize(dest_file)
        logging.info(f"File ditemukan di NAS ({file_size} bytes), siap dihapus dari Drive")

        # --- Hapus file di Drive ---
        cmd_delete = f'rclone delete "{gdrive_path}" -v'
        logging.info(f"Menjalankan delete: {cmd_delete}")
        os.system(cmd_delete)
        logging.info(f"File {fname} berhasil dipindahkan & dihapus dari GDrive")
    else:
        logging.warning(f"File {fname} belum ditemukan di NAS, skip delete")

    # --- Jalankan validator (sort_form) ---
    os.system("python3 /volume1/scripts/sort_form.py")

    return jsonify({"status": "ok", "file": fname})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)