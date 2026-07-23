import logging
import os
import smtplib
from datetime import date
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email_with_attachments(filename_base: str, recipient_email: str) -> None:
    """
    Sends generated CSV and XLSX files to the client's email address.
    """
    # Load SMTP settings from environment variables (.env)
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port_str = os.getenv("SMTP_PORT")
    sender_email = os.getenv("SMTP_USER")
    sender_password = os.getenv("SMTP_PASSWORD")

    # Check if all settings are specified
    if not sender_email or not sender_password:
        logging.error(
            "Mail settings (SMTP_USER / SMTP_PASSWORD) not found in .env. Sending canceled."
        )
        print("Error: Mail settings missing from .env. Email not sent.")
        return

    # Convert the port to a number (default 465 for SSL)
    smtp_port = int(smtp_port_str) if smtp_port_str else 465

    # Create a message object
    msg = MIMEMultipart("mixed")
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = f"Job search results from {date.today().strftime('%d.%m.%Y')}"

    # The text of the letter itself (the body of the message)
    dashboard_link = os.getenv("STREAMLITE_LINK")

    text_body = (
        "Greetings!\n\n"
        "The script has successfully completed searching for vacancies matching your request.\n"
        "The latest results files (in CSV and Excel formats) are attached to this email.\n\n"
        f"View the live dashboard: {dashboard_link}\n\n"
        "Have a nice day!"
    )

    html_body = f"""\
    <html>
    <body>
        <p>Greetings!</p>
        <p>The script has successfully completed searching for vacancies matching your request.<br>
        The latest results files (in CSV and Excel formats) are attached to this email.</p>
        <p><a href="{dashboard_link}">View the live dashboard</a></p>
        <p>Have a nice day!</p>
    </body>
    </html>
    """
    
    alt = MIMEMultipart("alternative")
    alt.attach(MIMEText(text_body, "plain", "utf-8"))
    alt.attach(MIMEText(html_body, "html", "utf-8"))
    msg.attach(alt)
    
    # List of files we want to attach
    files_to_send = [
    os.path.join("output", f"{filename_base}.csv"),
    os.path.join("output", f"{filename_base}.xlsx"),
    ]

    for file_path in files_to_send:
        if os.path.exists(file_path):
            # Open the file in binary reading mode
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode the file in base64 so that it arrives correctly by email
            encoders.encode_base64(part)

            # Add a header with the file name
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {os.path.basename(file_path)}",
            )
            # Attach a file to the email
            msg.attach(part)
        else:
            logging.warning(f"File {file_path} not found. Skipping attachment.")

    # Connect to the server and send a letter
    try:
        print(f"Connecting to a mail server {smtp_server}...")
        server: smtplib.SMTP
        # If port 465, we use the standard secure SMTP_SSL
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            # For other ports (e.g. 587 with STARTTLS encryption)
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()

        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        logging.info(f"The letter has been successfully sent to the recipient: {recipient_email}")
        print(f"Success! The email with the files has been sent to {recipient_email}")

    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        print(f"Error sending email: {e}")
