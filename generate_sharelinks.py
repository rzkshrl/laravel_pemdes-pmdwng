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

def create_drive_share_for_path(path, sid, expire_days=0):
    """
    Robust Drive share creator:
    - normalize path (strip /volume1)
    - try direct getinfo
    - if getinfo fails (error 102), try to resolve path iteratively by listing parent folders
      and performing case-insensitive matching of children names (helps when Drive expects
      slightly different folder name casing/spacing).
    - once we have a valid folder id, call SYNO.Drive.Share.create with the folder id.
    - return public URL on success or None.
    """
    api_getinfo = "SYNO.Drive.Files"
    api_share = "SYNO.Drive.Share"
    import json

    # normalize path (Drive expects path relative to drive root /TeamFolderName/...)
    if path.startswith("/volume1/"):
        path_for_api = path.replace("/volume1", "", 1)
    else:
        path_for_api = path
    path_for_api = path_for_api.rstrip("/")

    print("DEBUG path_for_api:", path_for_api)

    # Try direct getinfo first
    try:
        params_getinfo = {"path_list": json.dumps([path_for_api])}
        j_info = drive_api_call(api_getinfo, "getinfo", version=2, params=params_getinfo, sid=sid)
        print("DEBUG getinfo:", j_info)
    except Exception as e:
        print("DEBUG getinfo exception:", e)
        j_info = {"success": False}

    # If getinfo failed, try iterative resolution (case-insensitive child matching)
    if not j_info.get("success"):
        print("  getinfo failed, attempting iterative resolution of path segments...")
        segments = [s for s in path_for_api.split("/") if s]
        parent = "/"
        resolved = []
        ok = True
        for seg in segments:
            # try exact candidate first
            candidate = parent.rstrip("/") + "/" + seg
            try:
                j = drive_api_call(api_getinfo, "getinfo", version=2, params={"path_list": json.dumps([candidate])}, sid=sid)
                if j.get("success") and j.get("data", {}).get("items"):
                    parent = candidate
                    resolved.append(seg)
                    continue
            except Exception:
                pass

            # if exact not found, list parent and try case-insensitive match of children
            try:
                jlist = drive_api_call(api_getinfo, "list", version=2, params={"path_list": json.dumps([parent])}, sid=sid)
                items = jlist.get("data", {}).get("items", [])
                matched_name = None
                for it in items:
                    name = it.get("name", "")
                    if name and name.strip().lower() == seg.strip().lower():
                        matched_name = name
                        break
                if matched_name:
                    parent = parent.rstrip("/") + "/" + matched_name
                    resolved.append(matched_name)
                    continue
                else:
                    # not found among children
                    ok = False
                    print(f"    Segment '{seg}' not found under parent '{parent}'")
                    break
            except Exception as e:
                ok = False
                print("    Error listing parent:", parent, "->", e)
                break

        if not ok:
            print(f"  Could not resolve path segments for {path_for_api}, aborting.")
            return None

        # final getinfo on resolved parent
        try:
            params_getinfo = {"path_list": json.dumps([parent])}
            j_info = drive_api_call(api_getinfo, "getinfo", version=2, params=params_getinfo, sid=sid)
            print("DEBUG resolved getinfo:", j_info)
        except Exception as e:
            print("  Resolved getinfo exception:", e)
            return None

        if not j_info.get("success"):
            print("  Resolved getinfo still failed for:", parent)
            return None

    # Extract folder id
    items = j_info.get("data", {}).get("items", [])
    if not items:
        print("  No items returned in getinfo for path:", path_for_api)
        return None
    file_id = items[0].get("id")
    if not file_id:
        print("  No id found in getinfo items for path:", path_for_api)
        return None

    # Create share using the id
    try:
        items_param = json.dumps([{"type": "folder", "id": file_id}])
        params_share = {"items": items_param}
        if expire_days > 0:
            params_share["expire_in_days"] = str(expire_days)
        j = drive_api_call(api_share, "create", version=2, params=params_share, sid=sid)
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