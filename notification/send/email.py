import smtplib, os, json
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def notification(message) -> str | None:
    try:
        message = json.loads(s=message)
        mp3_fid = message["mp3_fid"]
        sender_address: str = os.environ("GMAIL_ADDRESS")
        sender_password: str = os.environ("GMAIL_PASSWORD")
        receiver_address = message["username"]

        msg: EmailMessage = EmailMessage()
        msg.set_content(f"mp3 file_id: {mp3_fid} is now ready to download!")
        msg["Subject"] = "MP3 Download"
        msg["From"] = sender_address
        msg["To"] = receiver_address

        session: smtplib.SMTP = smtplib.SMTP(
            host=os.environ.get("SMTP_HOST"), port=int(os.environ.get("SMTP_PORT"))
        )
        session.starttls()
        session.login(user=sender_address, password=sender_password)
        session.send_message(
            msg=msg, from_addr=sender_address, to_addrs=receiver_address
        )
        session.quit()
        print("Gmail Sent")
    except Exception as err:
        print(err)
        return err
