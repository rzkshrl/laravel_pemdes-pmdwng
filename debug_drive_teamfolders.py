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
        "session": "Drive",
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

    # coba list teamfolder v2 dan v1
    for ver in [2,1]:
        print(f"\n=== SYNO.Drive.Teamfolder.list (v{ver}) ===")
        try:
            res = drive_api("SYNO.Drive.Teamfolder", "list", version=ver, sid=sid)
            print(res)
        except Exception as e:
            print("Error v", ver, ":", e)

    # coba list root path
    print("\n=== SYNO.Drive.Files.list (root /) ===")
    try:
        res = drive_api("SYNO.Drive.Files", "list", version=2,
                        params={"path_list": '["/"]'}, sid=sid)
        print(res)
    except Exception as e:
        print("Error root list:", e)

if __name__ == "__main__":
    main()