#!/usr/bin/env python3
"""
send_recruiters_drive_resume.py

Usage:
  python send_recruiters_drive_resume.py --csv recruiters.csv --drive-link "https://drive.google.com/file/d/1AbCdEfGhIjKlMnOpQrStUvWxYz/view?usp=sharing"
"""

import os
import csv
import time
import smtplib
import argparse
import getpass
import requests
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ---------- CONFIGURABLE FIELDS ----------
SENDER_NAME  = "Supriya Gowra"
SENDER_EMAIL = "supriyasuppug98@gmail.com"
SUBJECT_TEMPLATE = "Applying for DevOps Engineer position"

BODY_TEMPLATE = """Hi {name},

Trust you are doing well!

1. Total Experience: 4+ yrs
2. Notice Period: Immediate Joiner

Please find the attached resume for your reference and below details.
If anything else is required, please let me know.

I recently came across a DevOps position on LinkedIn and wanted to explore if my background aligns with the role.
I would greatly appreciate it if you could take a moment to review it and let me know if it could be a fit.
Thank you for your time and consideration.

I am eagerly waiting for new opportunities.

Thanks & Regards,
Supriya Gowra
8125336081
LinkedIn: https://www.linkedin.com/in/supriyagowra
"""
# -----------------------------------------

def download_from_drive(drive_link: str, output_path: Path):
    """Download a file from a public Google Drive link."""
    print("Downloading resume from Google Drive...")
    try:
        # Extract file ID from link
        if "id=" in drive_link:
            file_id = drive_link.split("id=")[1].split("&")[0]
        elif "/d/" in drive_link:
            file_id = drive_link.split("/d/")[1].split("/")[0]
        else:
            raise ValueError("Invalid Google Drive link format")

        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(url, allow_redirects=True)
        if response.status_code == 200:
            output_path.write_bytes(response.content)
            print(f"✅ Resume downloaded: {output_path}")
        else:
            raise RuntimeError(f"Failed to download (status {response.status_code})")
    except Exception as e:
        print(f"❌ Error downloading from Google Drive: {e}")
        exit(1)

def attach_file(msg, path):
    """Attach file to email safely with proper encoding."""
    with open(path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{path.name}"')
    msg.attach(part)
    custom_name = "Supriya G.pdf"
    part.add_header("Content-Disposition", f'attachment; filename="{custom_name}"')
    msg.attach(part)

def send_email(server, sender_name, sender_email, recipient, subject, body, attachment_path):
    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    attach_file(msg, attachment_path)
    server.send_message(msg)

def load_recruiters(csv_path: Path):
    """Read name,email rows from CSV."""
    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return []
    if "email" in [c.lower() for c in rows[0]]:
        rows = rows[1:]
    recruiters = []
    for row in rows:
        if len(row) < 2:
            continue
        name, email = row[0].strip(), row[1].strip()
        if not name:
            name = email.split("@")[0].split(".")[0].capitalize()
        recruiters.append((name, email))
    return recruiters

def main():
    parser = argparse.ArgumentParser(description="Send DevOps emails with resume downloaded from Drive.")
    parser.add_argument("--csv", required=True, help="Path to recruiters.csv (name,email).")
    parser.add_argument("--drive-link", required=True, help="Google Drive shareable link of resume.")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between emails (seconds).")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    recruiters = load_recruiters(csv_path)
    if not recruiters:
        print("No recruiters found in CSV.")
        return

    # Download resume from drive
    resume_path = Path("supriya.pdf")
    download_from_drive(args.drive_link, resume_path)

    # Get Gmail app password
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    if not app_password:
        app_password = getpass.getpass("Enter your Gmail App Password (will not be echoed): ")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, app_password)
            print(f"Logged in as {SENDER_EMAIL}. Sending {len(recruiters)} emails...\n")
            for i, (name, email) in enumerate(recruiters, start=1):
                body = BODY_TEMPLATE.format(name=name)
                try:
                    send_email(server, SENDER_NAME, SENDER_EMAIL, email, SUBJECT_TEMPLATE, body, resume_path)
                    print(f"[{i}/{len(recruiters)}] ✅ Sent to {email}")
                except Exception as e:
                    print(f"[{i}/{len(recruiters)}] ❌ Failed to {email}: {e}")
                if i != len(recruiters):
                    time.sleep(args.delay)
        print("\n✅ All done.")
    finally:
        if resume_path.exists():
            resume_path.unlink()  # delete temp file

if __name__ == "__main__":
    main()






























#!/usr/bin/env python3
"""
send_recruiters_drive_resume_dedup.py
"""

import os
import csv
import time
import smtplib
import argparse
import getpass
import requests
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ---------- CONFIGURABLE FIELDS ----------
SENDER_NAME  = "Supriya Gowra"
SENDER_EMAIL = "supriyasuppug98@gmail.com"
SUBJECT_TEMPLATE = "Applying for DevOps Engineer position"

BODY_TEMPLATE = """Hi {name},

Trust you are doing well!

1. Total Experience: 4+ yrs
2. Notice Period: Immediate Joiner

Please find the attached resume for your reference and below details.
If anything else is required, please let me know.

I recently came across a DevOps position on LinkedIn and wanted to explore if my background aligns with the role.
I would greatly appreciate it if you could take a moment to review it and let me know if it could be a fit.
Thank you for your time and consideration.

I am eagerly waiting for new opportunities.

Thanks & Regards,
Supriya Gowra
8125336081
LinkedIn: https://www.linkedin.com/in/supriyagowra
"""
# -----------------------------------------

def download_from_drive(drive_link: str, output_path: Path):
    """Download a file from a public Google Drive link."""
    print("Downloading resume from Google Drive...")
    try:
        if "id=" in drive_link:
            file_id = drive_link.split("id=")[1].split("&")[0]
        elif "/d/" in drive_link:
            file_id = drive_link.split("/d/")[1].split("/")[0]
        else:
            raise ValueError("Invalid Google Drive link format")

        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        response = requests.get(url, allow_redirects=True)
        if response.status_code == 200:
            output_path.write_bytes(response.content)
            print(f"✅ Resume downloaded: {output_path}")
        else:
            raise RuntimeError(f"Failed to download (status {response.status_code})")
    except Exception as e:
        print(f"❌ Error downloading from Google Drive: {e}")
        exit(1)

def attach_file(msg, path):
    """Attach file to email safely with proper encoding."""
    with open(path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    custom_name = "Supriya G.pdf"
    part.add_header("Content-Disposition", f'attachment; filename="{custom_name}"')
    msg.attach(part)

def send_email(server, sender_name, sender_email, recipient, subject, body, attachment_path):
    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    attach_file(msg, attachment_path)
    server.send_message(msg)

def load_recruiters(csv_path: Path):
    """Read name,email rows from CSV."""
    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return []
    if "email" in [c.lower() for c in rows[0]]:
        rows = rows[1:]
    recruiters = []
    for row in rows:
        if len(row) < 2:
            continue
        name, email = row[0].strip(), row[1].strip().lower()
        if not name:
            name = email.split("@")[0].split(".")[0].capitalize()
        recruiters.append((name, email))
    return recruiters

def main():
    parser = argparse.ArgumentParser(description="Send DevOps emails with resume downloaded from Drive.")
    parser.add_argument("--csv", required=True, help="Path to recruiters.csv (name,email).")
    parser.add_argument("--drive-link", required=True, help="Google Drive shareable link of resume.")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between emails (seconds).")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    recruiters = load_recruiters(csv_path)
    if not recruiters:
        print("No recruiters found in CSV.")
        return

    # ✅ Deduplicate recruiters by email (skip repeated ones)
    seen_emails = set()
    unique_recruiters = []
    for name, email in recruiters:
        if email in seen_emails:
            print(f"⚠️ Skipping duplicate email: {email}")
            continue
        seen_emails.add(email)
        unique_recruiters.append((name, email))

    print(f"\nTotal unique recruiters: {len(unique_recruiters)} (Skipped {len(recruiters) - len(unique_recruiters)} duplicates)\n")

    # Download resume from drive
    resume_path = Path("supriya.pdf")
    download_from_drive(args.drive_link, resume_path)

    # Get Gmail app password
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    if not app_password:
        app_password = getpass.getpass("Enter your Gmail App Password (will not be echoed): ")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, app_password)
            print(f"Logged in as {SENDER_EMAIL}. Sending {len(unique_recruiters)} emails...\n")
            for i, (name, email) in enumerate(unique_recruiters, start=1):
                body = BODY_TEMPLATE.format(name=name)
                try:
                    send_email(server, SENDER_NAME, SENDER_EMAIL, email, SUBJECT_TEMPLATE, body, resume_path)
                    print(f"[{i}/{len(unique_recruiters)}] ✅ Sent to {email}")
                except Exception as e:
                    print(f"[{i}/{len(unique_recruiters)}] ❌ Failed to {email}: {e}")
                if i != len(unique_recruiters):
                    time.sleep(args.delay)
        print("\n✅ All done.")
    finally:
        if resume_path.exists():
            resume_path.unlink()

if __name__ == "__main__":
    main()
