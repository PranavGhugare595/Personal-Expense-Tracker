import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

from app.core.config import settings

logger = logging.getLogger("app.email_service")


def _build_html_email(user_name: str, today: str) -> str:
    """Returns a styled HTML email body for the daily expense reminder."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>Expense Reminder</title>
    </head>
    <body style="margin:0;padding:0;background:#f0f2f8;font-family:'Segoe UI',Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f8;padding:40px 0;">
        <tr>
          <td align="center">
            <table width="580" cellpadding="0" cellspacing="0"
                   style="background:#ffffff;border-radius:20px;overflow:hidden;
                          box-shadow:0 8px 32px rgba(108,99,255,0.12);">

              <!-- Header Banner -->
              <tr>
                <td style="background:linear-gradient(135deg,#6c63ff 0%,#e040fb 100%);
                           padding:36px 40px;text-align:center;">
                  <div style="font-size:40px;margin-bottom:8px;">💸</div>
                  <h1 style="margin:0;color:#ffffff;font-size:26px;font-weight:700;
                             letter-spacing:-0.5px;">AI Expense Tracker</h1>
                  <p style="margin:6px 0 0;color:rgba(255,255,255,0.85);font-size:14px;">
                    Your daily financial companion
                  </p>
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td style="padding:40px 44px;">

                  <p style="margin:0 0 8px;color:#6c63ff;font-weight:600;font-size:13px;
                             text-transform:uppercase;letter-spacing:1px;">
                    Daily Reminder · {today}
                  </p>

                  <h2 style="margin:0 0 16px;color:#1a1a2e;font-size:22px;font-weight:700;">
                    Hey {user_name}, you forgot to log today's expenses! 👋
                  </h2>

                  <p style="margin:0 0 24px;color:#555;font-size:15px;line-height:1.7;">
                    It looks like you haven't recorded any expenses for <strong>{today}</strong>.
                    Keeping track of every transaction — even small ones — helps you stay on top
                    of your budget and reach your financial goals faster.
                  </p>

                  <!-- Tip box -->
                  <table width="100%" cellpadding="0" cellspacing="0"
                         style="background:#f5f3ff;border-left:4px solid #6c63ff;
                                border-radius:0 12px 12px 0;margin-bottom:30px;">
                    <tr>
                      <td style="padding:16px 20px;">
                        <p style="margin:0;color:#6c63ff;font-size:13px;font-weight:600;">
                          💡 Quick Tip
                        </p>
                        <p style="margin:4px 0 0;color:#444;font-size:14px;line-height:1.6;">
                          Users who log expenses daily are <strong>3x more likely</strong> to
                          stay within their monthly budget. It only takes 30 seconds!
                        </p>
                      </td>
                    </tr>
                  </table>

                  <!-- CTA Button -->
                  <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                      <td align="center">
                        <a href="https://personal-expense-tracker-ten-phi.vercel.app"
                           style="display:inline-block;background:linear-gradient(135deg,#6c63ff,#e040fb);
                                  color:#ffffff;text-decoration:none;padding:14px 40px;
                                  border-radius:50px;font-size:15px;font-weight:600;
                                  letter-spacing:0.3px;box-shadow:0 4px 16px rgba(108,99,255,0.35);">
                          ➕ &nbsp; Log Today's Expenses
                        </a>
                      </td>
                    </tr>
                  </table>

                  <!-- Divider -->
                  <hr style="border:none;border-top:1px solid #eee;margin:36px 0;" />

                  <!-- Stats reminder -->
                  <p style="margin:0;color:#999;font-size:13px;text-align:center;line-height:1.8;">
                    You're receiving this because you haven't logged any expense today.<br/>
                    Keep the streak alive — your future self will thank you! 🚀
                  </p>

                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="background:#f8f7ff;padding:20px 44px;text-align:center;">
                  <p style="margin:0;color:#bbb;font-size:12px;">
                    © 2026 AI Expense Tracker &nbsp;|&nbsp;
                    This is an automated reminder sent at 9 PM daily.
                  </p>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """


def send_reminder_email(to_email: str, user_name: str) -> bool:
    """
    Sends a daily expense reminder HTML email to the given user.
    Returns True on success, False on failure.
    Silently skips if SMTP credentials are not configured.
    """
    if not settings.SMTP_EMAIL or not settings.SMTP_APP_PASSWORD:
        logger.warning(
            "[EmailService] SMTP_EMAIL or SMTP_APP_PASSWORD not set in .env — skipping email send."
        )
        return False

    today_str = date.today().strftime("%B %d, %Y")  # e.g. "May 27, 2026"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"💸 {user_name}, you forgot to log your expenses today!"
        msg["From"] = f"AI Expense Tracker <{settings.SMTP_EMAIL}>"
        msg["To"] = to_email

        # Plain-text fallback
        plain_text = (
            f"Hi {user_name},\n\n"
            f"You haven't logged any expenses for {today_str}.\n"
            f"Visit your tracker to add them now:\n"
            f"https://personal-expense-tracker-ten-phi.vercel.app\n\n"
            f"— AI Expense Tracker"
        )
        msg.attach(MIMEText(plain_text, "plain"))
        msg.attach(MIMEText(_build_html_email(user_name, today_str), "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.SMTP_EMAIL, settings.SMTP_APP_PASSWORD)
            server.sendmail(settings.SMTP_EMAIL, to_email, msg.as_string())

        logger.info(f"[EmailService] Reminder email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"[EmailService] Failed to send reminder to {to_email}: {e}")
        return False
