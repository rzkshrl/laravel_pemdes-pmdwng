#!/usr/bin/env python3
from flask import Flask, request, jsonify
import os
import logging
import time
import requests
import datetime

app = Flask(__name__)

# === KONFIGURASI ===
WEBAPP_URL = "https://script.google.com/macros/s/AKfycbx_JabPPsfeDoYUF643Ap2RF9CRswr12GLI7a3dAwYgbF3Mcr-t_uXRAlHEuEB1JtwbJw/exec"
LOG_PATH = "/volume1/scripts/webhook_server.log"
RCLONE_PATH = "/bin/rclone"

# === Logging setup ===
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def kirim_status(data, status):
    """Kirim status ke Google Apps Script WebApp"""
    payload = {
        "tahun": data.get("tahun"),
        "kecamatan": data.get("kecamatan"),
        "desa": data.get("desa"),
        "bulan": data.get("bulan"),
        "jenisDokumen": data.get("jenisDokumen"),
        "file": data.get("files"),
        "status": status
    }
    try:
        r = requests.post(WEBAPP_URL, json=payload, timeout=10)
        logging.info(f"[CALLBACK] Status '{status}' terkirim ke Google Sheet ({r.status_code})")
    except Exception as e:
        logging.warning(f"[CALLBACK] Gagal kirim status '{status}': {e}")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}
    logging.info(f"Webhook diterima: {data}")

    kec = (data.get("kecamatan") or "").strip()
    desa = (data.get("desa") or "").strip().replace("-", "_")
    tahun = (data.get("tahun") or "").strip()
    bulan = (data.get("bulan") or "").strip()
    jenis = (data.get("jenisDokumen") or "").strip()
    fname = (data.get("files") or "").strip()

    if not all([kec, desa, tahun, bulan, jenis, fname]):
        logging.warning(f"Data tidak lengkap, webhook dilewati: {data}")
        return jsonify({"status": "skip", "reason": "data incomplete"}), 400

    dest_folder = f"/volume1/PemdesData/Data Desa/{kec}/{desa}/{jenis} {tahun}/{bulan}"
    os.makedirs(dest_folder, exist_ok=True)
    logging.info(f"Membuat folder tujuan: {dest_folder}")

    # === 1. Kirim status awal: sedang diproses ===
    kirim_status(data, "Sedang diproses ⏳")

    start_time = time.time()

    # === 2. Jalankan rclone copy ===
    gdrive_path = f"gdrive:/Form Upload Dokumen Desa (File responses)/Upload Dokumen (File responses)/{fname}"
    cmd_copy = f'"{RCLONE_PATH}" copy "{gdrive_path}" "{dest_folder}" --ignore-existing -v'
    logging.info(f"Menjalankan: {cmd_copy}")
    exit_code = os.system(cmd_copy)
    logging.info(f"Hasil copy (exit code): {exit_code}")

    # === 3. Verifikasi hasil ===
    success = False
    if exit_code == 0:
        files_local = os.listdir(dest_folder)
        if any(fname in f for f in files_local):
            success = True

    if success:
        # === 4. Hapus file di Google Drive ===
        cmd_delete = f'"{RCLONE_PATH}" delete "{gdrive_path}"'
        os.system(cmd_delete)
        logging.info(f"File {fname} berhasil dipindahkan & dihapus dari Google Drive")

        # === 5. Kirim status selesai ===
        kirim_status(data, "Selesai ✅")
    else:
        # === 6. Jika gagal, kirim status gagal ===
        logging.warning(f"File {fname} gagal disalin atau tidak ditemukan di NAS")
        kirim_status(data, "Gagal ❌")

    # === 7. Jalankan validasi lokal ===
    os.system("python3 /volume1/scripts/sort_form.py")

    durasi = time.time() - start_time
    logging.info(f"[PERFORMANCE] Total waktu proses: {durasi:.2f} detik")

    return jsonify({"status": "ok", "processed": 1})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)