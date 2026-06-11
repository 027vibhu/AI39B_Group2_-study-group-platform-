"""Email sending via the Resend HTTP API.

Uses the standard library (urllib) so no extra dependency is required.
Credentials come from config (loaded from the .env file):
  RESEND_API_KEY, RESEND_FROM
"""

import json
import urllib.request
import urllib.error

from config import Config

RESEND_ENDPOINT = "https://api.resend.com/emails"


def send_email(to, subject, html):
    """Send an email through Resend.

    Returns (ok: bool, error: str | None). Never raises.
    """
    api_key = Config.RESEND_API_KEY
    sender = Config.RESEND_FROM

    if not api_key or not sender:
        return False, "Resend is not configured (missing RESEND_API_KEY or RESEND_FROM)."

    payload = json.dumps({
        "from": sender,
        "to": [to],
        "subject": subject,
        "html": html,
    }).encode("utf-8")

    req = urllib.request.Request(
        RESEND_ENDPOINT,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # Resend is fronted by Cloudflare, which blocks the default
            # "Python-urllib/x" agent with a 403 (error 1010). Send a normal UA.
            "User-Agent": "Lorevia/1.0 (+https://mingma.tech)",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if 200 <= resp.status < 300:
                return True, None
            return False, f"Resend returned status {resp.status}."
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode("utf-8", "replace")
        except Exception:
            detail = ""
        return False, f"Resend HTTP {e.code}: {detail}"
    except urllib.error.URLError as e:
        return False, f"Could not reach Resend: {e.reason}"
    except Exception as e:  # noqa: BLE001
        return False, f"Unexpected error sending email: {e}"


def send_reset_code(to, code):
    """Send a password-reset verification code."""
    subject = "Your Lorevia password reset code"
    html = f"""
        <div style="font-family:Arial,Helvetica,sans-serif;max-width:480px;margin:0 auto;">
          <h2 style="color:#222;">Reset your password</h2>
          <p>Use the verification code below to reset your Lorevia password. It expires in 10 minutes.</p>
          <p style="font-size:32px;font-weight:bold;letter-spacing:8px;color:#4a3aff;
                    background:#f4f3ff;padding:16px 24px;border-radius:12px;text-align:center;">
            {code}
          </p>
          <p style="color:#888;font-size:13px;">If you didn't request this, you can safely ignore this email.</p>
        </div>
    """
    return send_email(to, subject, html)
