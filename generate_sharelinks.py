#!/usr/bin/env python3
# generate_sharelinks.py
# Men-generate share link untuk setiap folder desa via DSM WebAPI (Synology Drive Sharing)
# Output: /volume1/scripts/desa_sharelinks.csv  (Kecamatan,Desa,FolderPath,ShareLink)

import os, sys, time, urllib3
import requests
import pandas as pd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------- CONFIG ----------
NAS_HOST = "pemdesnas.synology.me"           # ganti -> host/IP DSM
NAS_PORT = 5001
ADMIN_USER = "desaAPI"                   # user yang punya hak Drive
ADMIN_PASS = "pemdesnasAPI123"                # simpan aman
EXCEL_PATH = "/volume1/scripts/daftar_desa.xlsx"
BASE_FOLDER = "/PemdesData/Data Desa"  # Logical path for FileStation, not physical /volume1
OUT_CSV = "/volume1/scripts/desa_sharelinks.csv"
EXPIRE_DAYS = 0   # 0 = never expire; atau ganti ke angka (mis. 30)
USE_HTTPS = True
VERIFY_SSL = False  # kalau self-signed cert, set False; kalau CA valid set True
# ----------------------------

scheme = "https" if USE_HTTPS else "http"
base_url = f"{scheme}://{NAS_HOST}:{NAS_PORT}"

session = requests.Session()

def login():
    # auth.cgi login -> return sid
    url = f"{base_url}/webapi/auth.cgi"
    params = {
        "api": "SYNO.API.Auth",
        "version": "3",
        "method": "login",
        "account": ADMIN_USER,
        "passwd": ADMIN_PASS,
        "session": "FileStation",
        "format": "sid"
    }
    r = session.get(url, params=params, verify=VERIFY_SSL, timeout=20)
    r.raise_for_status()
    j = r.json()
    if not j.get("success"):
        raise RuntimeError("Login failed: " + str(j))
    sid = j["data"]["sid"]
    return sid

def logout(sid):
    url = f"{base_url}/webapi/auth.cgi"
    params = {"api":"SYNO.API.Auth","version":2,"method":"logout","session":"Drive","_sid":sid}
    try:
        session.get(url, params=params, verify=VERIFY_SSL, timeout=10)
    except:
        pass

def drive_api_call(api, method, version=1, params=None, sid=None):
    # generic call to entry.cgi for Drive API using POST
    url = f"{base_url}/webapi/entry.cgi"
    p = {"api": api, "version": version, "method": method}
    if params:
        p.update(params)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = p
    if sid:
        data["_sid"] = sid
    r = session.post(url, data=data, verify=VERIFY_SSL, timeout=30)
    r.raise_for_status()
    return r.json()

def get_drive_share_for_path(path, sid):
    api = "SYNO.Drive.Share"
    try:
        j = drive_api_call(api, "list", version=1, params={"path": path}, sid=sid)
        if j.get("success") and "data" in j:
            return j["data"]
    except Exception:
        pass
    return None

def create_drive_share_for_path(path, sid, expire_days=0):
    """
    Buat share link langsung berdasarkan path (pakai FileStation untuk validasi).
    """
    import json

    # pastikan path valid di FileStation
    try:
        res = drive_api_call("SYNO.FileStation.List", "list", version=2,
                             params={"folder_path": path}, sid=sid)
        if not res.get("success"):
            print(f"DEBUG: Path '{path}' tidak valid di FileStation")
            return None
    except Exception as e:
        print(f"DEBUG: Gagal validasi path {path} di FileStation: {e}")
        return None

    # create share link, try version=1 then version=2
    items_param = json.dumps([{"type": "folder", "path": path}])
    params_share = {"items": items_param}
    if expire_days > 0:
        params_share["expire_in_days"] = str(expire_days)
    last_exc = None
    for ver in [1, 2]:
        try:
            j = drive_api_call("SYNO.Drive.Share", "create", version=ver, params=params_share, sid=sid)
            print(f"DEBUG create (version={ver}):", j)
            if j.get("success") and "data" in j:
                links = j["data"].get("links", []) or []
                if isinstance(links, list) and len(links) > 0 and isinstance(links[0], dict) and "url" in links[0]:
                    return links[0]["url"]
        except Exception as e:
            print(f"  Error create_drive_share_for_path version={ver}:", e)
            last_exc = e
    return None

def ensure_path_slash(path):
    # Drive expects Unix-style path; ensure no trailing slash except root
    return path.rstrip("/") if path != "/" else path

def main():
    sid = login()
    print("Logged in, sid:", sid)

    # Debug: list root to show available team folders
    try:
        jroot = drive_api_call("SYNO.Drive.Files", "list", version=2,
                               params={"path_list": '["/"]'}, sid=sid)
        print("DEBUG root list:", jroot)
    except Exception as e:
        print("DEBUG root list failed:", e)

    df = pd.read_excel(EXCEL_PATH)
    df.columns = df.columns.str.strip()
    required = ["Kecamatan", "Desa"]
    for c in required:
        if c not in df.columns:
            print("Excel missing column:", c)
            logout(sid)
            return

    rows_out = []
    for _, row in df.iterrows():
        kec = str(row["Kecamatan"]).strip()
        desa = str(row["Desa"]).strip()
        folder_path = os.path.join(BASE_FOLDER, kec, desa)
        folder_path = ensure_path_slash(folder_path)
        print("Processing:", kec, "/", desa, "->", folder_path)

        # Validasi folder_path menggunakan FileStation API, bukan os.path.isdir
        try:
            res = drive_api_call("SYNO.FileStation.List", "list", version=2,
                                params={"folder_path": folder_path}, sid=sid)
            if not res.get("success"):
                print(f"  [SKIP] folder not found in FileStation: {folder_path}")
                rows_out.append({"Kecamatan":kec,"Desa":desa,"FolderPath":folder_path,"ShareLink":""})
                continue
        except Exception as e:
            print(f"  [SKIP] Error validating folder in FileStation: {folder_path} ({e})")
            rows_out.append({"Kecamatan":kec,"Desa":desa,"FolderPath":folder_path,"ShareLink":""})
            continue

        link = ""
        try:
            existing = get_drive_share_for_path(folder_path, sid)
            if existing and isinstance(existing, dict) and existing.get("links"):
                links = existing["links"]
                if isinstance(links, list) and len(links) > 0:
                    link = links[0].get("url", "")
            if not link:
                print("  Creating share link...")
                link = create_drive_share_for_path(folder_path, sid, expire_days=EXPIRE_DAYS)
                if link:
                    print("  Created ->", link)
                else:
                    print("  Failed to create link for", folder_path)
        except Exception as e:
            print("  Error checking/creating share:", e)

        rows_out.append({"Kecamatan":kec,"Desa":desa,"FolderPath":folder_path,"ShareLink":link})

        # small pause to avoid API rate/overload
        time.sleep(0.5)

    # write CSV
    out_df = pd.DataFrame(rows_out)
    out_df.to_csv(OUT_CSV, index=False, encoding="utf-8")
    print("Saved mapping to", OUT_CSV)

    logout(sid)
    print("Logged out.")

if __name__ == "__main__":
    main()