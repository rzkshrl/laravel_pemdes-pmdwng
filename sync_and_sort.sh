#!/bin/bash
# sync_and_sort.sh
# Script gabungan untuk sinkronisasi & sortir

LOGFILE="/volume1/scripts/sync_and_sort.log"

echo "==== $(date) Mulai sinkronisasi ====" >> "$LOGFILE"

/volume1/scripts/rclone_sync.sh >> "$LOGFILE" 2>&1

echo "==== $(date) Mulai sortir ====" >> "$LOGFILE"

/usr/bin/python3 /volume1/scripts/sort_form.py >> "$LOGFILE" 2>&1

echo "==== $(date) Selesai ====" >> "$LOGFILE"