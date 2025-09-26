#!/usr/bin/env python3
# debug_drive_teamfolders.py
import requests, urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- KONFIGURASI ---
NAS_HOST   = "pemdesnas.synology.me"
NAS_PORT   = 5001
ADMIN_USER = "desaAPI"
ADMIN_PASS = "pemdesnasAPI123"
USE_HTTPS  = True
VERIFY_SSL = False

scheme   = "https" if USE_HTTPS else "http"
base_url = f"{scheme}://{NAS_HOST}:{NAS_PORT}"
session  = requests.Session()

def login():
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
    return j["data"]["sid"]

def drive_api(api, method, version=1, params=None, sid=None):
    url = f"{base_url}/webapi/entry.cgi"
    data = {"api": api, "version": version, "method": method}
    if params:
        data.update(params)
    if sid:
        data["_sid"] = sid
    r = session.post(url, data=data, verify=VERIFY_SSL, timeout=30)
    r.raise_for_status()
    return r.json()

def main():
    sid = login()
    print("✅ Logged in, SID:", sid)

    # list folder /PemdesData
    print("\n=== SYNO.FileStation.List (path /PemdesData) ===")
    try:
        res = drive_api("SYNO.FileStation.List", "list", version=2,
                        params={"folder_path": "/PemdesData"}, sid=sid)
        print(res)
    except Exception as e:
        print("Error listing /PemdesData:", e)

    # list folder /PemdesData/Data Desa
    print("\n=== SYNO.FileStation.List (path /PemdesData/Data Desa) ===")
    try:
        res = drive_api("SYNO.FileStation.List", "list", version=2,
                        params={"folder_path": "/PemdesData/Data Desa"}, sid=sid)
        print(res)
    except Exception as e:
        print("Error listing /PemdesData/Data Desa:", e)

if __name__ == "__main__":
    main()