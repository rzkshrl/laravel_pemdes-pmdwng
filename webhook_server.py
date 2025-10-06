#!/usr/bin/env python3
from flask import Flask, request, jsonify
import os
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

    # --- Folder tujuan ---
    dest_folder = f"/volume1/PemdesData/Data Desa/{kec}/{desa}/SPJ {tahun}/{bulan}"
    os.makedirs(dest_folder, exist_ok=True)
    logging.info(f"Membuat folder tujuan: {dest_folder}")

    # --- Path file di Google Drive ---
    gdrive_folder = "gdrive:/Form Upload Dokumen Desa (File responses)/Upload Dokumen (File responses)"
    gdrive_path = f"{gdrive_folder}/{fname}"

    # --- Copy ke NAS ---
    cmd_copy = f"rclone copy '{gdrive_path}' '{dest_folder}' --ignore-existing"
    copy_result = os.system(cmd_copy)
    logging.info(f"Menjalankan: {cmd_copy}, hasil: {copy_result}")

    # --- Verifikasi apakah file berhasil diunduh ---
    dest_file = os.path.join(dest_folder, fname)
    if os.path.exists(dest_file):
        logging.info(f"File berhasil disalin ke {dest_file}")
        
        # --- Hapus file dari Google Drive ---
        cmd_delete = f"rclone delete '{gdrive_path}'"
        del_result = os.system(cmd_delete)
        logging.info(f"File dihapus dari Google Drive: {gdrive_path}, hasil: {del_result}")
    else:
        logging.warning(f"File {fname} belum ditemukan di NAS, skip delete")

    # --- Jalankan validasi setelah pemindahan ---
    os.system("python3 /volume1/scripts/sort_form.py")

    return jsonify({"status": "ok", "processed": 1})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)