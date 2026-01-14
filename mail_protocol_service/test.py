import smtplib

try:
    print("Testing port 587...")
    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
    server.set_debuglevel(1)
    server.starttls()
    server.login('sanjeevan@axtr.in', 'axiomisyisrhgmld')
    server.quit()
    print("✓ Port 587 works!")
except Exception as e:
    print(f"✗ Port 587 failed: {e}")

try:
    print("\nTesting port 465...")
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30)
    server.set_debuglevel(1)
    server.login('sanjeevan@axtr.in', 'axiomisyisrhgmld')
    server.quit()
    print("✓ Port 465 works!")
except Exception as e:
    print(f"✗ Port 465 failed: {e}")