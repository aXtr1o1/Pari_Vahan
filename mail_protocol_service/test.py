import os, json, mimetypes
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request, AuthorizedSession
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS = os.path.join(BASE_DIR, "client_secret_1060828715024-3l943t0jtk7g9s5ibc83vq63tvgo4egb.apps.googleusercontent.com.json")
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")

def _get_creds() -> Credentials:
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
    return creds

def _multipart_body(metadata: dict, file_path: str, boundary: str) -> tuple[bytes, str]:
    mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    with open(file_path, "rb") as f:
        content = f.read()

    parts = []
    parts.append(f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode())
    parts.append(json.dumps(metadata).encode("utf-8"))
    parts.append(b"\r\n")
    parts.append(f"--{boundary}\r\nContent-Type: {mime}\r\n\r\n".encode())
    parts.append(content)
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())

    body = b"".join(parts)
    content_type = f"multipart/related; boundary={boundary}"
    return body, content_type

def upload_csv_to_drive_requests(delta_csv_path: str, cumulative_csv_path: str, master_csv_path: str, make_public: bool=True) -> dict:
    for p in (delta_csv_path, cumulative_csv_path, master_csv_path):
        if not os.path.isfile(p):
            raise FileNotFoundError(f"File not found: {p}")

    session = AuthorizedSession(_get_creds())
    session.timeout = 60  # default for our calls

    def list_one(q: str):
        r = session.get(
            "https://www.googleapis.com/drive/v3/files",
            params={"q": q, "spaces": "drive", "fields": "files(id,name,webViewLink)"},
            timeout=60,
        )
        r.raise_for_status()
        files = r.json().get("files", [])
        return files[0] if files else None

    def get_or_create_folder(name: str, parent_id: str | None = None) -> str:
        q = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            q += f" and '{parent_id}' in parents"
        f = list_one(q)
        if f:
            return f["id"]

        meta = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            meta["parents"] = [parent_id]

        r = session.post("https://www.googleapis.com/drive/v3/files", json=meta, params={"fields": "id"}, timeout=60)
        r.raise_for_status()
        return r.json()["id"]

    def make_anyone_reader(file_id: str):
        r = session.post(
            f"https://www.googleapis.com/drive/v3/files/{file_id}/permissions",
            json={"type": "anyone", "role": "reader"},
            timeout=60,
        )
        r.raise_for_status()

    def upload_new(file_path: str, parent_id: str) -> dict:
        boundary = "axtr_boundary"
        meta = {"name": os.path.basename(file_path), "parents": [parent_id]}
        body, ctype = _multipart_body(meta, file_path, boundary)

        r = session.post(
            "https://www.googleapis.com/upload/drive/v3/files",
            params={"uploadType": "multipart", "fields": "id,name,webViewLink"},
            data=body,
            headers={"Content-Type": ctype},
            timeout=120,
        )
        r.raise_for_status()
        out = r.json()
        if make_public:
            make_anyone_reader(out["id"])
        return out

    def upload_or_overwrite(file_path: str, parent_id: str) -> dict:
        name = os.path.basename(file_path)
        existing = list_one(f"name = '{name}' and trashed = false and '{parent_id}' in parents")

        if existing:
            # Try to delete the existing file first (works with drive.file scope for files we created)
            try:
                r_del = session.delete(
                    f"https://www.googleapis.com/drive/v3/files/{existing['id']}",
                    timeout=60,
                )
                r_del.raise_for_status()
                # File deleted successfully, now create new one
                existing = None
            except Exception:
                # If delete fails (file not created by us or permission issue), try to update
                # Use PATCH with uploadType=multipart for full update
                boundary = "axtr_boundary"
                meta = {"name": name}
                body, ctype = _multipart_body(meta, file_path, boundary)
                
                r = session.patch(
                    f"https://www.googleapis.com/upload/drive/v3/files/{existing['id']}",
                    params={"uploadType": "multipart", "fields": "id,name,webViewLink"},
                    data=body,
                    headers={"Content-Type": ctype},
                    timeout=120,
                )
                r.raise_for_status()
                out = r.json()
                if make_public:
                    make_anyone_reader(out["id"])
                return out

        # Upload new file (or recreate if we deleted the old one)
        boundary = "axtr_boundary"
        meta = {"name": name, "parents": [parent_id]}
        body, ctype = _multipart_body(meta, file_path, boundary)
        
        r = session.post(
            "https://www.googleapis.com/upload/drive/v3/files",
            params={"uploadType": "multipart", "fields": "id,name,webViewLink"},
            data=body,
            headers={"Content-Type": ctype},
            timeout=120,
        )
        r.raise_for_status()
        out = r.json()
        
        if make_public:
            make_anyone_reader(out["id"])
        return out

    root_id = get_or_create_folder("Parivahan scraped data")
    delta_id = get_or_create_folder("Delta", root_id)
    cum_id = get_or_create_folder("Cumulative", root_id)

    delta_file = upload_new(delta_csv_path, delta_id)
    cumulative_file = upload_new(cumulative_csv_path, cum_id)
    master_file = upload_or_overwrite(master_csv_path, root_id)

    if make_public:
        for fid in (root_id, delta_id, cum_id):
            make_anyone_reader(fid)

    return {
        "scraped_root_link": f"https://drive.google.com/drive/folders/{root_id}",
        "delta": {"path": f"scraped_data/delta/{delta_file['name']}", "link": delta_file.get("webViewLink")},
        "cumulative": {"path": f"scraped_data/cumulative/{cumulative_file['name']}", "link": cumulative_file.get("webViewLink")},
        "master": {"path": f"My Drive/{master_file['name']}", "link": master_file.get("webViewLink")},
    }
    


# define main to run the 
if __name__ == "__main__":
    result = upload_csv_to_drive_requests(
        delta_csv_path="C:\\Users\\sanje_3wfdh8z\\OneDrive\\Desktop\\Pari\\delta_folder\\2025-02-30_delta.csv",
        cumulative_csv_path="C:\\Users\\sanje_3wfdh8z\\OneDrive\\Desktop\\Pari\\cumulative_folder\\2025-01-31.csv",
        master_csv_path="final_master.csv"
    )
    print(json.dumps(result, indent=2))