import os
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import dotenv
from datetime import datetime, timedelta


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv.load_dotenv(os.path.join(BASE_DIR, ".env"))
print("ENV PATH:", os.path.join(BASE_DIR, ".env"))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.yaml")



scrape_dt = datetime.today()
parivahan_dt = scrape_dt - timedelta(days=1)
scrape_date = scrape_dt.strftime("%d %B %Y")
parivahan_date = parivahan_dt.strftime("%d %B %Y")
def upload_csv_to_drive(
    delta_csv_path: str,
    cumulative_csv_path: str,
    master_csv_path: str,
    make_public: bool = True
) -> dict:


    for path in (delta_csv_path, cumulative_csv_path, master_csv_path):
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")

    # ---------- auth ----------
    gauth = GoogleAuth(settings_file=SETTINGS_FILE)
    gauth.LoadCredentialsFile("mycreds.txt")

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()

    gauth.SaveCredentialsFile("mycreds.txt")
    drive = GoogleDrive(gauth)

    # ---------- helpers ----------
    def get_or_create_folder(name: str, parent_id: str = None):
        q = f"title = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            q += f" and '{parent_id}' in parents"

        folders = drive.ListFile({"q": q}).GetList()
        if folders:
            return folders[0]

        meta = {"title": name, "mimeType": "application/vnd.google-apps.folder"}
        if parent_id:
            meta["parents"] = [{"id": parent_id}]

        folder = drive.CreateFile(meta)
        folder.Upload()
        return folder

    def upload_master(local_path: str, parent_id: str):
        title = os.path.basename(local_path)
        # Look for an existing master file in the same folder
        q = (
            f"title = '{title}' and "
            f"mimeType != 'application/vnd.google-apps.folder' and "
            f"trashed = false and "
            f"'{parent_id}' in parents"
        )
        files = drive.ListFile({"q": q}).GetList()
        if files:
            f = files[0]          # reuse existing file -> will be overwritten
        else:
            f = drive.CreateFile({
                "title": title,
                "parents": [{"id": parent_id}],
            })
        f.SetContentFile(local_path)
        f.Upload()
        if make_public:
            f.InsertPermission({
                "type": "anyone",
                "value": "anyone",
                "role": "reader",
            })
        return f

    def upload_file(local_path: str, parent_id: str = None):
        file_meta = {"title": os.path.basename(local_path)}
        if parent_id:
            file_meta["parents"] = [{"id": parent_id}]

        f = drive.CreateFile(file_meta)
        f.SetContentFile(local_path)
        f.Upload()

        if make_public:
            f.InsertPermission({
                "type": "anyone",
                "value": "anyone",
                "role": "reader",
            })

        return f

    # ---------- folder structure ----------
    scraped_root = get_or_create_folder("Parivahan scraped data")
    delta_folder = get_or_create_folder("Delta", scraped_root["id"])
    cumulative_folder = get_or_create_folder("Cumulative", scraped_root["id"])

    # ---------- uploads ----------
    delta_file = upload_file(delta_csv_path, delta_folder["id"])
    cumulative_file = upload_file(cumulative_csv_path, cumulative_folder["id"])  
    master_file = upload_master(master_csv_path, scraped_root["id"])
    
    # ---------- folder permissions ----------
    if make_public:
        permission = {
            "type": "anyone",
            "value": "anyone",
            "role": "reader",
        }
        for obj in (scraped_root, delta_folder, cumulative_folder):
            obj.InsertPermission(permission)

    # ---------- response ----------
    
    return {
        "scraped_root_link": f"https://drive.google.com/drive/folders/{scraped_root['id']}",
        "delta": {
            "path": f"scraped_data/delta/{delta_file['title']}",
            "link": f"https://drive.google.com/file/d/{delta_file['id']}/view",
        },

        "cumulative": {
            "path": f"scraped_data/cumulative/{cumulative_file['title']}",
            "link": f"https://drive.google.com/file/d/{cumulative_file['id']}/view",
        },

        "master": {
            "path": f"My Drive/{master_file['title']}",
            "link": f"https://drive.google.com/file/d/{master_file['id']}/view",
        },
        
    }


def send_download_mail(
    to_email: str,
    download_link: str,
    filename: str,
    folder_link: str,
    attachment_path: str | None = None,   # NEW
):
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = "sanjeevan@axtr.in"
    smtp_password = "axiomisyisrhgmld"

    if not smtp_user or not smtp_password:
        raise RuntimeError("SMTP credentials not set")

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = to_email
    msg["Subject"] = f"Parivahan Delta Data - {scrape_date}"

    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; font-size: 14px; color: #000;">
        <p>Team,</p>
        <p>
            PFA PariVahan Scraped Data For Today, <b>{scrape_date}</b>
        </p>
        <p><b>File Link:</b> <a href="{download_link}">{download_link}</a></p>
        <p><b>Folder Link:</b> <a href="{folder_link}">{folder_link}</a></p>
        <p><i>This is an automated mail.</i></p>
    </body>
    </html>
    """

    msg.attach(MIMEText(body, "html"))

    # -------------------------
    # ATTACH CSV FILE (NEW)
    # -------------------------
    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{os.path.basename(attachment_path)}"'
        )
        msg.attach(part)

    # with smtplib.SMTP(smtp_host, smtp_port) as server:
    #     server.starttls()
    #     server.login(smtp_user, smtp_password)
    #     server.send_message(msg)

    import smtplib
    with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
Prepossessed_sheet_name = os.path.join(BASE_DIR, "master_preprocessed.csv")
Prepossessed_sheet_name = "master_preprocessed.csv"
def upload_and_email(
    delta_csv_path: str,
    cumulative_csv_path: str,
    master_csv_path: str,
    recipient_email: str,
):
    links = upload_csv_to_drive(delta_csv_path, cumulative_csv_path, master_csv_path, make_public=True)

    send_download_mail(
        to_email=recipient_email,
        download_link=links["master"]["link"],
        filename=os.path.basename(delta_csv_path),
        folder_link=links["scraped_root_link"],
        attachment_path=Prepossessed_sheet_name
    )

    print("CSV uploaded and email sent")
    print("Delta file link:", links["delta"]["link"])
    print("Folder link:", links["scraped_root_link"])


if __name__ == "__main__":



    upload_and_email(
        "C:/Users/sanje_3wfdh8z/OneDrive/Desktop/Pari/mail_protocol_service/output.csv",
        "C:/Users/sanje_3wfdh8z/OneDrive/Desktop/Pari/mail_protocol_service/output.csv",
        "C:/Users/sanje_3wfdh8z/OneDrive/Desktop/Pari/mail_protocol_service/output.csv",
        "sanjeevan@axtr.in",
    )



