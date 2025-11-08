import os
import time
import shutil
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def upload_to_google_drive(folder_name):
    # --- Authenticate ---
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.json")

    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile("mycreds.json")

    drive = GoogleDrive(gauth)

    # --- Paths ---
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
    folder_name = folder_name
    source_folder = os.path.join(downloads_dir, folder_name)

    if not os.path.exists(source_folder):
        print(f"⚠️ Folder not found: {source_folder}")
        return

    # --- Create ZIP file ---
    zip_filename = f"{folder_name}.zip"
    zip_path = os.path.join(downloads_dir, zip_filename)

    print(f"📦 Zipping folder: {source_folder}")
    shutil.make_archive(base_name=source_folder, format="zip", root_dir=source_folder)
    print(f"✅ Created ZIP: {zip_path}")

    # --- Upload ZIP file ---
    gfile = drive.CreateFile({
        "title": zip_filename,
    })
    gfile.SetContentFile(zip_path)
    gfile.Upload()

    # --- Make shareable ---
    gfile.InsertPermission({
        'type': 'anyone',
        'value': 'anyone',
        'role': 'reader'
    })

    # --- Get public link ---
    shareable_link = f"https://drive.google.com/uc?id={gfile['id']}&export=download"

    print(f"🎉 Uploaded ZIP successfully!")
    print(f"🔗 Download Link: {shareable_link}")
    return shareable_link
    # --- Optional: clean up local ZIP after upload ---
    # os.remove(zip_path)
    # shutil.rmtree(source_folder)

