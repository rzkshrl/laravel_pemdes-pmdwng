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

def get_teamfolder_id(sid, teamfolder_name="PemdesData"):
    print(f"DEBUG: Fetching teamfolder list to find '{teamfolder_name}' ID...")
    try:
        j = drive_api_call("SYNO.Drive.Teamfolder", "list", version=1, sid=sid)
        if j.get("success") and "data" in j:
            for tf in j["data"].get("items", []):
                if tf.get("name") == teamfolder_name:
                    print(f"DEBUG: Found teamfolder '{teamfolder_name}' with id: {tf.get('id')}")
                    return tf.get("id")
    except Exception as e:
        print(f"DEBUG: Error fetching teamfolder list: {e}")
    print(f"DEBUG: Teamfolder '{teamfolder_name}' not found.")
    return None

def create_drive_share_for_path(path, sid, expire_days=0):
    """
    Robust Drive share creator:
    - Use teamfolder id for 'PemdesData'
    - Traverse subfolders by listing children with SYNO.Drive.Files.list and matching names case-insensitively
    - Finally create share for the resolved folder id
    - Return public URL on success or None
    """
    import json

    # Normalize path and remove /volume1/PemdesData prefix
    prefix = "/volume1/PemdesData"
    if not path.startswith(prefix):
        print(f"DEBUG: Path '{path}' does not start with expected prefix '{prefix}'")
        return None

    subpath = path[len(prefix):].lstrip("/")
    print(f"DEBUG: Subpath inside PemdesData: '{subpath}'")

    # Get teamfolder id for PemdesData
    teamfolder_id = get_teamfolder_id(sid, "PemdesData")
    if not teamfolder_id:
        print("DEBUG: Could not find teamfolder id for 'PemdesData'")
        return None

    # Traverse subfolders by segments
    segments = [s for s in subpath.split("/") if s]
    current_id = teamfolder_id
    api_files = "SYNO.Drive.Files"

    for seg in segments:
        print(f"DEBUG: Listing children of id {current_id} to find segment '{seg}'...")
        try:
            params_list = {"id_list": json.dumps([current_id])}
            jlist = drive_api_call(api_files, "list", version=2, params=params_list, sid=sid)
            if not jlist.get("success"):
                print(f"DEBUG: Failed to list children of id {current_id}")
                return None
            items = jlist.get("data", {}).get("items", [])
            matched_id = None
            for it in items:
                name = it.get("name", "")
                if name and name.strip().lower() == seg.strip().lower():
                    matched_id = it.get("id")
                    print(f"DEBUG: Matched segment '{seg}' to id {matched_id}")
                    break
            if not matched_id:
                print(f"DEBUG: Segment '{seg}' not found under id {current_id}")
                return None
            current_id = matched_id
        except Exception as e:
            print(f"DEBUG: Exception listing children of id {current_id}: {e}")
            return None

    # current_id is the id of the final folder
    print(f"DEBUG: Final folder id to share: {current_id}")

    # Create share using the id
    try:
        items_param = json.dumps([{"type": "folder", "id": current_id}])
        params_share = {"items": items_param}
        if expire_days > 0:
            params_share["expire_in_days"] = str(expire_days)
        j = drive_api_call("SYNO.Drive.Share", "create", version=2, params=params_share, sid=sid)
        print("DEBUG create:", j)
        if j.get("success") and "data" in j:
            links = j["data"].get("links", []) or []
            if isinstance(links, list) and len(links) > 0 and isinstance(links[0], dict) and "url" in links[0]:
                return links[0]["url"]
            # fallback: maybe data contains url directly
            if isinstance(j["data"], dict):
                for v in j["data"].values():
                    if isinstance(v, str) and v.startswith("http"):
                        return v
    except Exception as e:
        print("  Error create_share_for_path:", e)

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

        if not os.path.isdir(folder_path):
            print("  [SKIP] folder not found:", folder_path)
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