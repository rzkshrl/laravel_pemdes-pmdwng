#!/bin/bash
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Start sync..." >> /volume1/scripts/rclone.log

# Spreadsheet tetap sync (tidak dipindah, karena butuh tetap ada di GDrive)
rclone sync "gdrive:/Form Upload Dokumen Desa (File responses)/Respon Spreadsheet" \
  "/volume1/homes/adminpemdes/FormResponseGDriveSync" \
  --drive-export-formats xlsx,docx,pdf \
  --log-file="/volume1/scripts/rclone.log" -v

# File upload dipindah (hapus otomatis dari Drive setelah pindah sukses)
rclone move "gdrive:/Form Upload Dokumen Desa (File responses)/Upload Dokumen (File responses)" \
  "/volume1/homes/adminpemdes/SynologyGDriveUpload" \
  --checkers=8 --transfers=8 --retries=5 --low-level-retries=10 \
  --log-file="/volume1/scripts/rclone.log" -v

echo "[$DATE] Finished sync." >> /volume1/scripts/rclone.log