#!/bin/bash

BASE="/volume1/Desa"
EXCEL="/volume1/scripts/daftar_desa.csv"

# Convert Excel → CSV dulu
# (pakai pandas / save manual dari Excel)

# Skip header row
read -r _ < "$EXCEL"

while IFS=, read -r kec desa; do
    USERNAME=$(echo "$desa" | tr '[:upper:]' '[:lower:]' | tr ' ' '_')
    SHARENAME="$USERNAME"
    FOLDER="$BASE/$kec/$desa"

    # 1. Tambah user Synology
    synouser --add "$USERNAME" "password123" "User $desa" 0 "" 0

    # 2. Buat share folder (jika perlu)
    synoshare --add "$SHARENAME" "$FOLDER" "Folder Desa $desa" 0

    # 3. Set permission hanya untuk folder desa
    synoshare --setuser "$SHARENAME" RW "$USERNAME"

done < <(tail -n +2 "$EXCEL")
done < <(tail -n +2 "$EXCEL")