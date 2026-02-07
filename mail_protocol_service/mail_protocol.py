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
from mail_protocol_service.test import upload_csv_to_drive_requests

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

    # Use SMTP with STARTTLS for port 587, or SMTP_SSL for port 465
    if smtp_port == 465:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    else:
        # Port 587 uses STARTTLS, not direct SSL
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
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

    print("Uploading CSV to Drive and sending email...")
    links = upload_csv_to_drive_requests(delta_csv_path, cumulative_csv_path, master_csv_path, make_public=True)

    print("Sending email...")
    send_download_mail(
        to_email=recipient_email,
        download_link=links["master"]["link"],
        filename=os.path.basename(delta_csv_path),
        folder_link=links["scraped_root_link"],
        attachment_path=Prepossessed_sheet_name
    )
    print("Email sent successfully")
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



