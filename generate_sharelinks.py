#!/usr/bin/env python3
# generate_sharelinks.py
# Men-generate share link untuk setiap folder desa via DSM WebAPI (FileStation.Sharing)
# Output: /volume1/scripts/desa_sharelinks.csv  (Kecamatan,Desa,FolderPath,ShareLink)

import os, sys, time, urllib3
import requests
import pandas as pd

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------- CONFIG ----------
NAS_HOST = "https://pemdesnas.synology.me"           # ganti -> host/IP DSM
NAS_PORT = 5001
ADMIN_USER = "adminpemdes"                   # user yang punya hak FileStation
ADMIN_PASS = "Admin1234"                # simpan aman
EXCEL_PATH = "/volume1/scripts/daftar_desa.xlsx"
BASE_FOLDER = "/volume1/PemdesData/Data Desa"
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
        "version": "2",
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
    params = {"api":"SYNO.API.Auth","version":2,"method":"logout","session":"FileStation","_sid":sid}
    try:
        session.get(url, params=params, verify=VERIFY_SSL, timeout=10)
    except:
        pass

def fs_api_call(api, method, version=3, params=None, sid=None):
    # generic call to entry.cgi
    url = f"{base_url}/webapi/entry.cgi"
    p = {"api": api, "version": version, "method": method}
    if params:
        p.update(params)
    if sid:
        p["_sid"] = sid
    r = session.get(url, params=p, verify=VERIFY_SSL, timeout=30)
    r.raise_for_status()
    return r.json()

def get_share_list_for_path(path, sid):
    # try multiple versions if needed
    api = "SYNO.FileStation.Sharing"
    for ver in (3,2,1):
        try:
            j = fs_api_call(api, "list", version=ver, params={"path": path}, sid=sid)
            if j.get("success") and "data" in j:
                return j["data"]
        except Exception:
            continue
    return None

def create_share_for_path(path, sid, expire_days=0):
    api = "SYNO.FileStation.Sharing"
    for ver in (3,2,1):
        try:
            params = {"path": path, "expire_in_days": str(expire_days)}
            j = fs_api_call(api, "create", version=ver, params=params, sid=sid)
            if j.get("success") and "data" in j:
                # data.links may be present
                links = j["data"].get("links") or j["data"]
                # try to return first url found
                if isinstance(links, list) and len(links) > 0:
                    if isinstance(links[0], dict) and "url" in links[0]:
                        return links[0]["url"]
                    else:
                        return str(links[0])
                # fallback
                return str(j["data"])
        except Exception:
            continue
    return None

def ensure_path_slash(path):
    # FileStation expects Unix-style path; ensure no trailing slash except root
    return path.rstrip("/") if path != "/" else path

def main():
    sid = login()
    print("Logged in, sid:", sid)

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

        if not os.path.isdir(folder_path):
            print("  [SKIP] folder not found:", folder_path)
            rows_out.append({"Kecamatan":kec,"Desa":desa,"FolderPath":folder_path,"ShareLink":""})
            continue

        # check existing shares
        existing = get_share_list_for_path(folder_path, sid)
        link = ""
        try:
            if existing and isinstance(existing, dict) and existing.get("links"):
                # pick first active link
                links = existing["links"]
                if isinstance(links, list) and len(links)>0:
                    link = links[0].get("url","")
            # if no existing, create
            if not link:
                print("  Creating share link...")
                link = create_share_for_path(folder_path, sid, expire_days=EXPIRE_DAYS)
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