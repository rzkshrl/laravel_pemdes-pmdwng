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
    file_ids = (data.get("fileIds") or "").split(",")

    # --- Validasi data wajib ---
    if not all([kec, desa, tahun, bulan]) or not file_ids:
        logging.warning(f"Data tidak lengkap, webhook dilewati: {data}")
        return jsonify({"status": "skip", "reason": "data incomplete"}), 400

    dest_folder = f"/volume1/PemdesData/Data Desa/{kec}/{desa}/SPJ {tahun}/{bulan}"
    os.makedirs(dest_folder, exist_ok=True)

    logging.info(f"Membuat folder tujuan: {dest_folder}")

    for fid in file_ids:
        fid = fid.strip()
        if not fid:
            continue

        # --- 1️⃣ Coba copy pakai nama file ---
        if fname and os.path.splitext(fname)[1]:
            gdrive_path = f'gdrive:/Form Upload Dokumen Desa (File responses)/Upload Dokumen (File responses)/{fname}'
            cmd_copy = f'rclone copy "{gdrive_path}" "{dest_folder}" --ignore-existing -v'
            logging.info(f'Mencoba copy (nama file): {cmd_copy}')
            result = os.system(cmd_copy)
        else:
            result = 999  # trigger fallback langsung

        # --- 2️⃣ Jika gagal, fallback pakai File ID ---
        if result != 0:
            gdrive_path = f'gdrive:{{{fid}}}'
            cmd_copy = f'rclone copy "{gdrive_path}" "{dest_folder}" --ignore-existing -v'
            logging.info(f'Fallback copy (file ID): {cmd_copy}')
            result = os.system(cmd_copy)

        logging.info(f"Hasil copy (exit code): {result}")

        # --- 3️⃣ Verifikasi hasil ---
        files_local = os.listdir(dest_folder)
        copied = any(fname in f for f in files_local) or any(fid in f for f in files_local)

        if copied:
            # Hapus dari GDrive setelah sukses
            cmd_delete = f'rclone delete "{gdrive_path}"'
            os.system(cmd_delete)
            logging.info(f"File {fname or fid} berhasil dipindahkan dan dihapus dari GDrive")
        else:
            logging.warning(f"File {fname or fid} belum ditemukan di NAS, skip delete")

    # --- 4️⃣ Jalankan validasi setelah pemindahan ---
    os.system("python3 /volume1/scripts/sort_form.py")

    return jsonify({"status": "ok", "processed": len(file_ids)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)