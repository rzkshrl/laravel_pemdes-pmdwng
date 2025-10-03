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
    logging.info(f"Webhook diterima: {data}")

    # Jalankan rclone sync
    ret1 = os.system("/volume1/scripts/rclone_sync.sh")
    logging.info(f"rclone_sync.sh selesai dengan kode {ret1}")

    # Jalankan sortir
    ret2 = os.system("python3 /volume1/scripts/sort_form.py")
    logging.info(f"sort_form.py selesai dengan kode {ret2}")

    return jsonify({"status": "ok", "message": "Sync + Sort triggered"})

if __name__ == "__main__":
    # production: pakai 0.0.0.0 agar bisa diakses dari luar
    app.run(host="0.0.0.0", port=5000, debug=False)