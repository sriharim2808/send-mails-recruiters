#!/usr/bin/env python3
"""
send_recruiters.py

Usage examples:
  # Prompt for app password interactively:
  python send_recruiters_secure.py --csv recruiters.csv --attachments resume.pdf cover.pdf

  # Use environment variable (preferred for automation):
  setx GMAIL_APP_PASSWORD "jngm hjsz epxn gjld"   # windows (restart shell)
  export GMAIL_APP_PASSWORD="jngm hjsz epxn gjld" # linux/mac (current shell)
  python send_recruiters_secure.py --csv recruiters.csv --attachments resume.pdf

Options:
  --csv           Path to CSV containing name,email columns (header optional)
  --attachments   Optional list of files to attach
  --delay         Seconds to wait between sends (default: 2.0)
  --subject       Email subject override
  --from-email    Sender email override (defaults to configured SENDER_EMAIL)
  --dry-run       Don't actually send; print what would be sent
  --retries       Number of retries on transient failures (default: 2)
"""

import argparse
import csv
import os
import sys
import time
import smtplib
import getpass
from pathlib import Path
from typing import List, Tuple
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# ----------------- CONFIG - edit these defaults if you like -----------------
SENDER_NAME = "Supriya Gowra"
SENDER_EMAIL = "supriyasuppug98@gmail.com"
DEFAULT_SUBJECT = "Applying for DevOps Engineer position"

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
# ---------------------------------------------------------------------------

def load_recruiters(csv_path: Path) -> List[Tuple[str, str]]:
    """Return list of (name, email) from CSV; handle optional header."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    recs = []
    with csv_path.open(newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        return []
    # Detect header
    first = [c.strip().lower() for c in rows[0]]
    if "email" in first or "name" in first:
        rows = rows[1:]
    for r in rows:
        if len(r) < 2:
            continue
        name, email = r[0].strip(), r[1].strip()
        if not email:
            continue
        if not name:
            # fallback name from email
            local = email.split("@")[0]
            name = local.replace(".", " ").replace("_", " ").title()
        recs.append((name, email))
    return recs

def attach_file(msg: MIMEMultipart, path: Path):
    with path.open("rb") as f:
        part = MIMEApplication(f.read(), Name=path.name)
    part["Content-Disposition"] = f'attachment; filename="{path.name}"'
    msg.attach(part)

def build_message(sender_name: str, sender_email: str, to_email: str, subject: str, body_text: str, attachments: List[Path]) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body_text, "plain"))
    for a in attachments:
        attach_file(msg, a)
    return msg

def send_via_gmail(sender_email: str, app_password: str, messages: List[Tuple[str, MIMEMultipart]], dry_run: bool=False, retries: int=2, delay_between_sends: float=2.0):
    if dry_run:
        print("DRY RUN: No messages will be sent. Listing planned sends:")
        for i, (recipient, msg) in enumerate(messages, start=1):
            print(f"[{i}/{len(messages)}] To: {recipient} Subject: {msg['Subject']}")
        return

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            print(f"Logged in as {sender_email}. Sending {len(messages)} messages...")
            for i, (recipient, msg) in enumerate(messages, start=1):
                attempt = 0
                while attempt <= retries:
                    try:
                        server.send_message(msg)
                        print(f"[{i}/{len(messages)}] Sent to {recipient}")
                        break
                    except smtplib.SMTPException as e:
                        attempt += 1
                        if attempt > retries:
                            print(f"[{i}/{len(messages)}] FAILED to {recipient}: {e}")
                        else:
                            backoff = 2 ** attempt
                            print(f"[{i}/{len(messages)}] Transient error: {e}. Retrying in {backoff}s (attempt {attempt}/{retries})")
                            time.sleep(backoff)
                if i != len(messages):
                    time.sleep(delay_between_sends)
    except smtplib.SMTPAuthenticationError:
        raise RuntimeError("Authentication failed. Check Gmail App Password & ensure 2FA is enabled.")
    except Exception as e:
        raise RuntimeError(f"SMTP error: {e}")

def main():
    p = argparse.ArgumentParser(description="Send personalized DevOps-application emails via Gmail App Password.")
    p.add_argument("--csv", required=True, help="Path to recruiters CSV (name,email).")
    p.add_argument("--attachments", nargs="*", help="Files to attach (e.g. resume.pdf).")
    p.add_argument("--delay", type=float, default=2.0, help="Seconds between sends (default 2.0).")
    p.add_argument("--subject", type=str, default=DEFAULT_SUBJECT, help="Email subject.")
    p.add_argument("--from-email", type=str, default=SENDER_EMAIL, help="Sender email address.")
    p.add_argument("--dry-run", action="store_true", help="Print actions without sending emails.")
    p.add_argument("--retries", type=int, default=2, help="Retries for transient send errors (default 2).")
    args = p.parse_args()

    csv_path = Path(args.csv)
    attachments = []
    if args.attachments:
        for a in args.attachments:
            pth = Path(a)
            if not pth.exists():
                print(f"Attachment not found: {a}", file=sys.stderr)
                sys.exit(1)
            attachments.append(pth)

    try:
        recruiters = load_recruiters(csv_path)
    except Exception as e:
        print("Error reading CSV:", e, file=sys.stderr)
        sys.exit(1)
    if not recruiters:
        print("No recruiter entries found in CSV.", file=sys.stderr)
        sys.exit(1)

    # Acquire Gmail App Password from env or prompt
    app_password = os.getenv("GMAIL_APP_PASSWORD")
    if not app_password:
        # Prompt securely
        try:
            app_password = getpass.getpass(prompt="Enter your Gmail App Password (will not be echoed): ")
        except Exception:
            # fallback
            app_password = input("Enter your Gmail App Password: ")
        if not app_password:
            print("No Gmail App Password provided. Aborting.", file=sys.stderr)
            sys.exit(1)

    subject = args.subject
    sender_email = args.from_email
    sender_name = SENDER_NAME

    # Build messages
    messages = []
    for name, email in recruiters:
        body = BODY_TEMPLATE.format(name=name)
        msg = build_message(sender_name, sender_email, email, subject, body, attachments)
        messages.append((email, msg))

    try:
        send_via_gmail(sender_email, app_password, messages, dry_run=args.dry_run, retries=args.retries, delay_between_sends=args.delay)
    except RuntimeError as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
