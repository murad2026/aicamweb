import resend
import secrets

resend.api_key = "re_BbSi9QHe_MJnG5U7dMtLuNVYnHdDBbPSb"

def send_verification_email(to_email, username, token):
    verify_url = f"https://b48a-108-26-229-43.ngrok-free.app/auth/verify/{token}"
    try:
        resend.Emails.send({
            "from": "AI Any Camera <noreply@aianycamera.com>",
            "to": to_email,
            "subject": "Verify your email — AI Any Camera",
            "html": f"""
            <div style="font-family: sans-serif; max-width: 500px; margin: 0 auto;">
                <h2 style="color: #00ff88;">AI ANY CAMERA</h2>
                <p>Hi {username},</p>
                <p>Please verify your email address to activate your account.</p>
                <a href="{verify_url}" style="background: #00ff88; color: #000; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 20px 0; font-weight: bold;">
                    Verify Email
                </a>
                <p style="color: #666; font-size: 12px;">Link expires in 24 hours.</p>
            </div>
            """
        })
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_password_reset_email(to_email, token):
    reset_url = f"https://49ea-108-26-229-43.ngrok-free.app/reset-password?token={token}"
    try:
        resend.Emails.send({
            "from": "AI Any Camera <noreply@aianycamera.com>",
            "to": to_email,
            "subject": "Reset your password — AI Any Camera",
            "html": f"""
            <div style="font-family: sans-serif; max-width: 500px; margin: 0 auto;">
                <h2 style="color: #00ff88;">AI ANY CAMERA</h2>
                <p>Click below to reset your password:</p>
                <a href="{reset_url}" style="background: #00ff88; color: #000; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 20px 0; font-weight: bold;">
                    Reset Password
                </a>
                <p style="color: #666; font-size: 12px;">Link expires in 1 hour. If you didn't request this, ignore this email.</p>
            </div>
            """
        })
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False
