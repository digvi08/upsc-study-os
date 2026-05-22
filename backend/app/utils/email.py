"""Email utility using SMTP."""
import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def send_email(to: str, subject: str, html_body: str) -> bool:
    """Send an email via SMTP. Returns True on success."""
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP not configured — skipping email send")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_user
        msg["To"] = to
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.sendmail(settings.smtp_user, to, msg.as_string())
        return True
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return False


def send_password_reset_email(to: str, reset_token: str, full_name: str) -> bool:
    reset_url = f"https://your-app.vercel.app/auth/reset-password?token={reset_token}"
    html = f"""
    <div style="font-family: Inter, sans-serif; max-width: 600px; margin: 0 auto; background: #0f0f23; color: #e2e8f0; padding: 40px; border-radius: 16px;">
      <h1 style="color: #6366f1;">Reset Your Password</h1>
      <p>Hi {full_name},</p>
      <p>Click the button below to reset your password. This link expires in 1 hour.</p>
      <a href="{reset_url}"
         style="display: inline-block; background: linear-gradient(135deg, #6366f1, #4f46e5); color: white;
                padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 20px 0;">
        Reset Password
      </a>
      <p style="color: #64748b; font-size: 14px;">If you didn't request this, ignore this email.</p>
    </div>
    """
    return send_email(to, "Reset Your AI UPSC Study OS Password", html)


def send_welcome_email(to: str, full_name: str) -> bool:
    html = f"""
    <div style="font-family: Inter, sans-serif; max-width: 600px; margin: 0 auto; background: #0f0f23; color: #e2e8f0; padding: 40px; border-radius: 16px;">
      <h1 style="color: #6366f1;">Welcome to AI UPSC Study OS! 🎓</h1>
      <p>Hi {full_name},</p>
      <p>Your AI-powered UPSC preparation journey starts now. Here's what you can do:</p>
      <ul style="color: #94a3b8; line-height: 2;">
        <li>📚 Organize your syllabus with Subjects & Topics</li>
        <li>🔍 Analyze PYQ trends with AI insights</li>
        <li>🤖 Chat with your AI Mentor anytime</li>
        <li>📝 Create smart notes with AI summaries</li>
        <li>🔄 Never forget with spaced repetition revision</li>
      </ul>
      <a href="https://your-app.vercel.app/dashboard"
         style="display: inline-block; background: linear-gradient(135deg, #6366f1, #4f46e5); color: white;
                padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 20px 0;">
        Start Preparing →
      </a>
    </div>
    """
    return send_email(to, "Welcome to AI UPSC Study OS!", html)


def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)
