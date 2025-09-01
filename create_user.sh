#!/bin/bash

BASE="/volume1/Desa"
EXCEL="/volume1/scripts/Rekap_Desa.csv"

# Convert Excel → CSV dulu
# (pakai pandas / save manual dari Excel)

while IFS=, read -r kec desa; do
    USERNAME=$(echo "$desa" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')
    FOLDER="$BASE/$kec/$desa"

    # 1. Tambah user Synology
    synouser --add "$USERNAME" "password123" "User $desa" 0 "" 0

    # 2. Set permission hanya untuk folder desa
    synoshare --add "$desa" "$FOLDER" "Folder Desa $desa" 0
    synoshare --setuser "$desa" RW "$USERNAME"

done < $EXCEL