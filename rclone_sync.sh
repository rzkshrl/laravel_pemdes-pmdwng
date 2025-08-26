#!/bin/bash
LOGFILE="/var/log/rclone_sync.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo "[$TIMESTAMP] Mulai sinkron..." >> $LOGFILE

rclone sync gdrive:/Form Upload Dokumen Desa (File responses)/Upload Dokumen (File responses) /volume1/homes/adminpemdes/SynologyGDriveUpload \
    --progress \
    --create-empty-src-dirs \
    --log-file=$LOGFILE \
    --log-level INFO

echo "[$TIMESTAMP] Selesai sinkron." >> $LOGFILE