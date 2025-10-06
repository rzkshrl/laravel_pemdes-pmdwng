#!/usr/bin/env python3
from flask import Flask, request, jsonify
import os
import threading
import logging
import datetime

app = Flask(__name__)

# === Konfigurasi dasar ===
RCLONE_PATH = "/bin/rclone"
DEST_BASE = "/volume1/PemdesData/Data Desa"
LOG_DIR = "/volume1/scripts/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# === Setup logging utama ===
logging.basicConfig(
    filename="/volume1/scripts/webhook_server.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


# === Fungsi utama pemindahan file ===
def process_webhook(data):
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        job_log = os.path.join(LOG_DIR, f"job_{timestamp}.log")

        # --- Ambil data dari JSON ---
        kec = (data.get("kecamatan") or "").strip()
        desa = (data.get("desa") or "").strip().replace("-", "_")
        tahun = (data.get("tahun") or "").strip()
        bulan = (data.get("bulan") or "").strip()
        fname = (data.get("files") or "").strip()
        file_ids = (data.get("fileIds") or "").split(",")

        if not all([kec, desa, tahun, bulan]) or not file_ids:
            logging.warning(f"[SKIP] Data tidak lengkap: {data}")
            return

        dest_folder = f"{DEST_BASE}/{kec}/{desa}/SPJ {tahun}/{bulan}"
        os.makedirs(dest_folder, exist_ok=True)
        logging.info(f"[TASK] Mulai proses untuk {fname} → {dest_folder}")

        # === Jalankan rclone move ===
        gdrive_path = (
            f'gdrive:/Form Upload Dokumen Desa (File responses)/Upload Dokumen (File responses)/{fname}'
        )
        cmd = (
            f'{RCLONE_PATH} move "{gdrive_path}" "{dest_folder}" '
            f'--drive-use-trash=false --ignore-existing '
            f'--checkers=16 --transfers=8 --tpslimit=8 '
            f'--stats=1s --stats-log-level NOTICE -v >> "{job_log}" 2>&1'
        )

        start_time = datetime.datetime.now()
        exit_code = os.system(cmd)
        duration = (datetime.datetime.now() - start_time).total_seconds()

        if exit_code == 0:
            logging.info(f"[SUCCESS] File {fname} berhasil dipindahkan dalam {duration:.2f} detik.")
        else:
            logging.error(f"[FAILED] rclone exit={exit_code} untuk {fname} (durasi {duration:.2f}s).")

        # === Validasi setelah selesai ===
        dest_file = os.path.join(dest_folder, fname)
        if os.path.exists(dest_file):
            logging.info(f"[VERIFY] File ditemukan di NAS: {dest_file}")
        else:
            logging.warning(f"[VERIFY] File belum muncul di NAS: {dest_file}")

        # === Jalankan sortir otomatis ===
        os.system("python3 /volume1/scripts/sort_form.py >> /volume1/scripts/sort_form.log 2>&1")

    except Exception as e:
        logging.error(f"[ERROR] Exception di process_webhook: {e}")


# === Endpoint webhook ===
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json or {}
    logging.info(f"Webhook diterima: {data}")

    # Jalankan proses di thread background agar cepat balas ke GAS
    threading.Thread(target=process_webhook, args=(data,)).start()

    # Balas cepat agar GAS tidak timeout
    return jsonify({"status": "accepted", "message": "Processing in background"}), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)