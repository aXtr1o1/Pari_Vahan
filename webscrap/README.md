# RTO Data Web Scraping Tool

This project automates the process of scraping RTO (Regional Transport Office) data from the Parivahan government website, organizing the downloaded files, uploading them to Google Drive, and sending email notifications with the download link.

## Features

- Automated web scraping using Selenium
- Downloads RTO data as Excel files
- Organizes files by date
- Uploads files to Google Drive
- Sends email notifications with download links
- Checkpoint system to resume from last completed RTO

## Prerequisites

- Python 3.7 or higher
- Google account with 2FA enabled
- Chrome browser installed
- Google Cloud Project with OAuth 2.0 credentials

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd webscrap
```

2. Install required Python packages:
```bash
pip install selenium webdriver-manager pydrive2
```

## Configuration

### 1. Email Setup (Gmail with App Password)

**Important:** The sender's email account must have **2-Factor Authentication (2FA) enabled** and you must create an **App Password** for this application.

#### Steps to enable 2FA and create App Password:

1. Go to your Google Account settings: https://myaccount.google.com/
2. Navigate to **Security** section
3. Enable **2-Step Verification** if not already enabled
4. After enabling 2FA, go to **App passwords** (you may need to search for it)
5. Select **Mail** and **Other (Custom name)** as the app type
6. Enter a name for the app password (e.g., "RTO Scraper")
7. Click **Generate**
8. Copy the 16-character app password (it will look like: `xxxx xxxx xxxx xxxx`)
9. Update the `app_password` variable in `email_service.py` with this password

**Note:** Use the app password, NOT your regular Gmail password in the code.

### 2. Google Drive API Setup (client_secrets.json)

To enable Google Drive upload functionality, you need to obtain OAuth 2.0 credentials from Google Cloud Console.

#### Steps to get client_secrets.json:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** → **Credentials**
4. Click **+ CREATE CREDENTIALS** → **OAuth client ID**
5. If prompted, configure the OAuth consent screen:
   - Choose **External** (unless you have a Google Workspace account)
   - Fill in the required information (App name, User support email, etc.)
   - Add your email to test users if needed
   - Click **Save and Continue** through the steps
6. Back in Credentials, select **Application type**: **Desktop app**
7. Give it a name (e.g., "RTO Scraper Desktop Client")
8. Click **Create**
9. A dialog will appear with your **Client ID** and **Client Secret**
10. Click **Download JSON** to download the credentials file
11. Rename the downloaded file to `client_secrets.json` and place it in the project root directory

Alternatively, you can manually create `client_secrets.json` with the following structure:
```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
```

#### Enable Google Drive API:

1. In Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Google Drive API"
3. Click on it and press **Enable**

### 3. Update Configuration in web_scrap.py

Edit the following variables in `web_scrap.py`:

```python
sender_email = "your-email@gmail.com"
recipient_email = "recipient@example.com"
```

### 4. Update App Password in email_service.py

Edit the `app_password` variable in `email_service.py`:

```python
app_password = "your-16-character-app-password"  # Remove spaces if present
```

## Usage

Run the main script:

```bash
python web_scrap.py
```

The script will:
1. Open a Chrome browser window
2. Navigate to the Parivahan RTO dashboard
3. Select Tamil Nadu state
4. Iterate through all RTOs and download data
5. Organize files in a date-stamped folder
6. Upload the folder to Google Drive
7. Send an email with the download link

## First Run Authentication

On the first run, the script will open a browser window for Google Drive authentication:
1. Sign in with your Google account
2. Grant permissions to access Google Drive
3. The credentials will be saved in `mycreds.json` for future runs

## File Structure

```
webscrap/
├── web_scrap.py           # Main scraping script
├── email_service.py       # Email sending functionality
├── onedrive_service.py    # Google Drive upload functionality
├── client_secrets.json    # Google OAuth 2.0 credentials
├── mycreds.json          # Saved authentication tokens (generated on first run)
├── rto_progress.json     # Checkpoint file for resuming
└── README.md             # This file
```

## Checkpoint System

The script saves progress in `rto_progress.json`. If the script is interrupted, it will resume from the last completed RTO on the next run.

## Troubleshooting

### Email Authentication Failed
- Ensure 2FA is enabled on your Gmail account
- Verify you're using an App Password, not your regular password
- Check that the app password is correctly entered (no spaces)

### Google Drive Authentication Failed
- Verify `client_secrets.json` is in the project root
- Ensure Google Drive API is enabled in your Google Cloud project
- Check that the OAuth consent screen is properly configured
- Delete `mycreds.json` and re-authenticate if needed

### Selenium Errors
- Ensure Chrome browser is installed and up to date
- The script uses webdriver-manager to automatically download ChromeDriver
- If issues persist, try updating Chrome to the latest version

## Notes

- The script includes delays between actions to ensure page elements load properly
- Downloaded files are organized in `Downloads/{YYYY-MM-DD}_RTO_Files/`
- The script creates a ZIP file before uploading to Google Drive
- Email notifications are sent after successful upload

## License

This project is for personal/educational use only.

