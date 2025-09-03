#!/bin/bash
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Start sync..." >> /volume1/scripts/rclone.log

rclone sync "gdrive:/Monitoring Dana Desa Tahap 2 (File responses)/Respon Spreadsheet" "/volume1/homes/adminpemdes/FormResponseGDriveSync" --drive-export-formats xlsx,docx,pdf --log-file="/volume1/scripts/rclone.log" -v

rclone sync "gdrive:/Monitoring Dana Desa Tahap 2 (File responses)/Upload Bukti Foto Screenshot Scan DD Tahap 2 (EARMARK) (File responses)" "/volume1/homes/adminpemdes/SynologyGDriveUpload/EARMARK" --log-file="/volume1/scripts/rclone.log" -v

rclone sync "gdrive:/Monitoring Dana Desa Tahap 2 (File responses)/Upload Bukti Foto Screenshot Scan DD Tahap 2 (NON-EARMARK) (File responses)" "/volume1/homes/adminpemdes/SynologyGDriveUpload/NON-EARMARK" --log-file="/volume1/scripts/rclone.log" -v

echo "[$DATE] Finished sync." >> /volume1/scripts/rclone.log