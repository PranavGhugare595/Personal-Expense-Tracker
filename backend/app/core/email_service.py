import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_verification_email(to_email: str, full_name: str, token: str) -> bool:
    """Send a styled HTML verification email to the user."""
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 40px 20px; text-align: center;">
        <div style="max-width: 400px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 8px; border: 1px solid #e0e0e0;">
            <h2 style="color: #333333; margin-top: 0;">Verify Your Email</h2>
            <p style="color: #555555; font-size: 16px;">Hi <strong>{full_name}</strong>,</p>
            <p style="color: #555555; font-size: 14px; margin-bottom: 30px;">
                Please click the button below to verify your email address.
            </p>
            <a href="{verification_url}" style="display: inline-block; padding: 12px 24px; background-color: #007bff; color: #ffffff; text-decoration: none; border-radius: 4px; font-weight: bold;">
                Verify Email
            </a>
        </div>
    </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["From"] = settings.SMTP_EMAIL
    message["To"] = to_email
    message["Subject"] = "Verify your Personal Expense Tracker account"

    # Plain text fallback
    plain_text = (
        f"Hi {full_name},\n\n"
        f"Did you recently register an account with us? If so, please confirm it's you by clicking the link below:\n\n"
        f"{verification_url}\n\n"
        f"This link expires in 24 hours.\n"
        f"If you didn't create an account, you can safely ignore this email."
    )
    message.attach(MIMEText(plain_text, "plain"))
    message.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            start_tls=True,
            username=settings.SMTP_EMAIL,
            password=settings.SMTP_PASSWORD,
        )
        logger.info(f"[EMAIL] Verification email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"[EMAIL] Failed to send verification email to {to_email}: {e}")
        return False


async def send_expense_reminder_email(to_email: str, full_name: str) -> bool:
    """Send a reminder email to the user to log their expenses."""
    app_url = settings.FRONTEND_URL

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 40px 20px; text-align: center;">
        <div style="max-width: 400px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 8px; border: 1px solid #e0e0e0;">
            <h2 style="color: #333333; margin-top: 0;">Did you forget something?</h2>
            <p style="color: #555555; font-size: 16px;">Hi <strong>{full_name}</strong>,</p>
            <p style="color: #555555; font-size: 14px; margin-bottom: 30px;">
                We noticed you haven't logged any expenses today. Keeping track of your daily expenses is key to reaching your savings target!
            </p>
            <a href="{app_url}" style="display: inline-block; padding: 12px 24px; background-color: #28a745; color: #ffffff; text-decoration: none; border-radius: 4px; font-weight: bold;">
                Log Expenses Now
            </a>
        </div>
    </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["From"] = settings.SMTP_EMAIL
    message["To"] = to_email
    message["Subject"] = "Friendly reminder: Log your expenses for today!"

    # Plain text fallback
    plain_text = (
        f"Hi {full_name},\n\n"
        f"We noticed you haven't logged any expenses today. Keeping track of your daily expenses is key to reaching your savings target!\n\n"
        f"Log them now here: {app_url}\n\n"
    )
    message.attach(MIMEText(plain_text, "plain"))
    message.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            start_tls=True,
            username=settings.SMTP_EMAIL,
            password=settings.SMTP_PASSWORD,
        )
        logger.info(f"[EMAIL] Reminder email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"[EMAIL] Failed to send reminder email to {to_email}: {e}")
        return False


async def send_savings_warning_email(to_email: str, full_name: str) -> bool:
    """Send a warning email when a user dips into their savings allocation."""
    app_url = settings.FRONTEND_URL

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 40px 20px; text-align: center;">
        <div style="max-width: 400px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 8px; border: 1px solid #ff4d4d;">
            <h2 style="color: #ff4d4d; margin-top: 0;">Budget Alert! 🚨</h2>
            <p style="color: #555555; font-size: 16px;">Hi <strong>{full_name}</strong>,</p>
            <p style="color: #555555; font-size: 14px; margin-bottom: 30px;">
                You just logged an expense that pushed your monthly spending over your safe budget limit. 
                This means you are now using money that was allocated for your savings target.
            </p>
            <p style="color: #555555; font-size: 14px; margin-bottom: 30px;">
                Review your dashboard to see where you can cut back for the rest of the month!
            </p>
            <a href="{app_url}" style="display: inline-block; padding: 12px 24px; background-color: #ff4d4d; color: #ffffff; text-decoration: none; border-radius: 4px; font-weight: bold;">
                Review Budget
            </a>
        </div>
    </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message["From"] = settings.SMTP_EMAIL
    message["To"] = to_email
    message["Subject"] = "🚨 Budget Alert: You dipped into your savings!"

    # Plain text fallback
    plain_text = (
        f"Hi {full_name},\n\n"
        f"You just logged an expense that pushed your monthly spending over your safe budget limit. "
        f"This means you are now using money that was allocated for your savings target.\n\n"
        f"Review your budget here: {app_url}\n\n"
    )
    message.attach(MIMEText(plain_text, "plain"))
    message.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            start_tls=True,
            username=settings.SMTP_EMAIL,
            password=settings.SMTP_PASSWORD,
        )
        logger.info(f"[EMAIL] Savings warning email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"[EMAIL] Failed to send savings warning email to {to_email}: {e}")
        return False
