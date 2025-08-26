#!/bin/bash
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Start sync..." >> /volume1/scripts/rclone.log

rclone sync "gdrive:/Form Upload Dokumen Desa (File responses)/Respon Spreadsheet" "/volume1/homes/adminpemdes/FormResponseGDriveSync" --drive-export-formats xlsx,docx,pdf --log-file="/volume1/scripts/rclone.log" -v

rclone sync "gdrive:/Form Upload Dokumen Desa (File responses)/Upload Dokumen (File responses)" "/volume1/homes/adminpemdes/SynologyGDriveUpload" --log-file="/volume1/scripts/rclone.log" -v

echo "[$DATE] Finished sync." >> /volume1/scripts/rclone.log