import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from dotenv import load_dotenv
import os


load_dotenv()
sender_email = os.getenv("SENDER_EMAIL")
app_password = os.getenv("APP_PASSWORD")
recipient_email = os.getenv("RECIPIENT_EMAIL")

print(f"Sender Email: {sender_email}")
print(f"Recipient Email: {recipient_email}")  

def send_drive_link_via_email(link):
    if sender_email == "":
        print("❌ Sender email not provided.")
    if recipient_email == "":
        print("❌ Recipient email not provided.")
    # --- Email body ---
    body = f"""
<html>
  <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e2e2; border-radius: 8px;">
      <p>Dear Team,</p>

      <p>
        I hope this message finds you well. Please find below the download link for the latest <strong>RTO Report</strong> 
        generated on <strong>{time.strftime('%d %B %Y')}</strong>.
      </p>

      <p>
        📎 <strong>Download Link:</strong><br>
        <a href="{link}" style="color: #1a73e8; text-decoration: none; font-weight: bold;">
          Click here to download the RTO Report
        </a>
      </p>

      <p>
        Kindly ensure that the report is reviewed and stored securely as per your internal documentation process. 
        The shared link provides view and download access to anyone with the link.
      </p>

      <p>
        If you have any questions or require additional data, please feel free to reach out.
      </p>

      <br>

      <p style="margin-bottom: 4px;">Best regards,</p>
      <p style="font-weight: bold; margin-bottom: 0;">Automation System</p>
      <p style="margin-top: 0;">Data Processing Team<br>
      Murphy Construction Company</p>

      <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
      <p style="font-size: 12px; color: #777;">
        This is an automated email. Please do not reply directly to this message.
      </p>
    </div>
  </body>
</html>
"""

    
      # --- Create MIME message ---
    msg = MIMEMultipart()
    msg["From"] = sender_email # type: ignore
    msg["To"] = recipient_email # type: ignore
    msg["Subject"] = "RTO Report Download Link"
    msg.attach(MIMEText(body, "html"))

    # --- Send email via Gmail ---
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password) # type: ignore
            server.send_message(msg)
        print(f"✅ Email sent to {recipient_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")