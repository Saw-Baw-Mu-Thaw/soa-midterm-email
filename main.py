from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from config import SMTP_HOST, SMTP_PASS, SMTP_PORT, SMTP_USER


app = FastAPI(title="Email Service", version="1.0")

class SendOTPRequest(BaseModel):
    transaction_id: int
    email: str
    otp_code: str
    customer_name: str = "Customer"

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False

@app.post("/send-otp")
async def send_otp(req: SendOTPRequest):
    subject = f"Your OTP for Transaction #{req.transaction_id}"
    html = f"""
    <h2>Secure Transaction Verification</h2>
    <p>Hi <strong>{req.customer_name}</strong>,</p>
    <p>Your OTP code is:</p>
    <h1 style="color: #4CAF50; font-size: 32px; letter-spacing: 5px;">
        <b>{req.otp_code}</b>
    </h1>
    <p>Valid for <b>5 minutes</b>. Do not share!</p>
    <hr>
    <small>Transaction ID: {req.transaction_id}</small>
    """

    if send_email(req.email, subject, html):
        return {"success": True, "message": "OTP email sent!"}
    else:
        raise HTTPException(500, "Failed to send email")

@app.get("/")
async def root():
    return {"message": "Email Service Running! Send OTP to /send-otp"}

if __name__ == "__main__":
    uvicorn.run("email:app", host="0.0.0.0", port=8003, reload=True)