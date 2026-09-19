import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

def send_contact_emails(contact_message):
    """
    Sends two emails upon contact form submission:
    1. Notification email to the admin (Venkatesh)
    2. Professional auto-reply acknowledgment email to the visitor
    """
    admin_success = _send_admin_alert(contact_message)
    visitor_success = _send_visitor_autoreply(contact_message)
    return admin_success and visitor_success


def _send_admin_alert(msg):
    """Notify Venkatesh that a new contact message was received."""
    subject = f"🔔 [Portfolio] New Message from {msg.name}: {msg.subject}"
    recipient = settings.ADMIN_NOTIFICATION_EMAIL

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0f172a; color: #e2e8f0; padding: 24px; margin: 0; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #1e293b; border-radius: 16px; border: 1px solid #334155; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        .header {{ background: linear-gradient(135deg, #14b8a6, #06b6d4, #8b5cf6); padding: 24px; text-align: center; color: white; }}
        .header h2 {{ margin: 0; font-size: 20px; }}
        .header p {{ margin: 4px 0 0; opacity: 0.9; font-size: 13px; }}
        .content {{ padding: 24px; }}
        .field {{ margin-bottom: 16px; }}
        .field-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #14b8a6; font-weight: 700; }}
        .field-value {{ font-size: 15px; color: #f8fafc; margin-top: 4px; }}
        .message-box {{ background: #0f172a; border-left: 4px solid #14b8a6; border-radius: 8px; padding: 16px; margin-top: 16px; font-size: 14px; line-height: 1.6; white-space: pre-wrap; color: #cbd5e1; }}
        .footer {{ padding: 16px 24px; background: #0f172a; text-align: center; font-size: 12px; color: #64748b; border-top: 1px solid #334155; }}
        .btn {{ display: inline-block; background: #14b8a6; color: white; text-decoration: none; padding: 10px 20px; border-radius: 8px; font-size: 13px; font-weight: 600; margin-top: 16px; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h2>New Contact Inquiry</h2>
          <p>Received from your portfolio website</p>
        </div>
        <div class="content">
          <div class="field">
            <div class="field-label">Sender Name</div>
            <div class="field-value"><strong>{msg.name}</strong></div>
          </div>
          <div class="field">
            <div class="field-label">Sender Email</div>
            <div class="field-value"><a href="mailto:{msg.email}" style="color: #38bdf8;">{msg.email}</a></div>
          </div>
          <div class="field">
            <div class="field-label">Subject</div>
            <div class="field-value">{msg.subject}</div>
          </div>
          <div class="field">
            <div class="field-label">Timestamp & IP</div>
            <div class="field-value" style="font-size: 12px; color: #94a3b8;">{msg.created_at.strftime('%B %d, %Y at %I:%M %p')} • IP: {msg.ip_address or 'Unknown'}</div>
          </div>
          <div class="field-label" style="margin-top: 20px;">Message</div>
          <div class="message-box">{msg.message}</div>
          <div style="text-align: center;">
            <a href="mailto:{msg.email}?subject=Re: {msg.subject}" class="btn">Reply to {msg.name}</a>
          </div>
        </div>
        <div class="footer">
          Venkatesh Babu Portfolio System • Direct Contact Notification
        </div>
      </div>
    </body>
    </html>
    """

    plain_text = f"""
New Portfolio Message:
------------------------------------------
From: {msg.name} <{msg.email}>
Subject: {msg.subject}
Date: {msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}
IP: {msg.ip_address or 'Unknown'}

Message:
{msg.message}
------------------------------------------
Reply directly to: {msg.email}
    """.strip()

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
            reply_to=[msg.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Failed to send admin notification email: {e}")
        return False


def _send_visitor_autoreply(msg):
    """Send an automatic acknowledgment reply to the visitor."""
    subject = f"Thank you for contacting Venkatesh Babu — Received: {msg.subject}"
    recipient = msg.email

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; color: #334155; padding: 24px; margin: 0; }}
        .container {{ max-width: 560px; margin: 0 auto; background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }}
        .header {{ background: linear-gradient(135deg, #0d9488, #14b8a6, #8b5cf6); padding: 32px 24px; text-align: center; color: white; }}
        .header h1 {{ margin: 0; font-size: 22px; font-weight: 800; }}
        .header p {{ margin: 6px 0 0; opacity: 0.92; font-size: 13px; }}
        .content {{ padding: 28px 24px; }}
        p {{ margin: 0 0 16px; font-size: 14px; line-height: 1.6; color: #475569; }}
        .highlight {{ color: #0d9488; font-weight: 600; }}
        .summary-box {{ background: #f1f5f9; border-radius: 12px; padding: 16px; margin: 20px 0; border: 1px solid #e2e8f0; }}
        .summary-title {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; font-weight: 700; margin-bottom: 8px; }}
        .summary-item {{ font-size: 13px; color: #1e293b; margin-bottom: 4px; }}
        .signature {{ border-top: 1px solid #f1f5f9; padding-top: 20px; margin-top: 24px; }}
        .signature-name {{ font-weight: 700; color: #0f172a; font-size: 15px; }}
        .signature-title {{ font-size: 12px; color: #0d9488; margin-top: 2px; }}
        .footer {{ padding: 16px 24px; background: #f8fafc; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
        .social-links a {{ color: #0d9488; text-decoration: none; margin: 0 8px; font-weight: 600; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>Message Received!</h1>
          <p>Thank you for reaching out</p>
        </div>
        <div class="content">
          <p>Hi <strong>{msg.name}</strong>,</p>
          <p>Thank you for getting in touch! I have received your message regarding <span class="highlight">"{msg.subject}"</span> and will review it promptly.</p>
          <p>I typically respond to inquiries within <strong>24 hours</strong>. If your matter is urgent, you can also reach me directly at <a href="tel:+919952142302" style="color:#0d9488;">+91 9952142302</a>.</p>
          
          <div class="summary-box">
            <div class="summary-title">Summary of Your Message</div>
            <div class="summary-item"><strong>Subject:</strong> {msg.subject}</div>
            <div class="summary-item"><strong>Date:</strong> {msg.created_at.strftime('%B %d, %Y')}</div>
            <div class="summary-item" style="margin-top: 8px; font-style: italic; color: #64748b;">"{msg.message[:200]}{'...' if len(msg.message) > 200 else ''}"</div>
          </div>

          <div class="signature">
            <div class="signature-name">Venkatesh Babu</div>
            <div class="signature-title">Python Developer • AI & LLM Specialist • Automation Engineer</div>
            <p style="font-size: 12px; color: #64748b; margin-top: 6px;">Madurai, Tamil Nadu, India</p>
          </div>
        </div>
        <div class="footer">
          <div class="social-links">
            <a href="https://venkatesh-snowy.vercel.app">Portfolio</a> •
            <a href="https://github.com/venkatesh01-t">GitHub</a> •
            <a href="https://www.linkedin.com/in/venkatesh-babu-208891392">LinkedIn</a>
          </div>
          <p style="margin-top: 8px; font-size: 10px;">This is an automated confirmation sent from Venkatesh Babu's portfolio contact system.</p>
        </div>
      </div>
    </body>
    </html>
    """

    plain_text = f"""
Hi {msg.name},

Thank you for reaching out! I have received your message regarding "{msg.subject}".

I typically review and reply to all technical inquiries and project proposals within 24 hours. If your message is urgent, feel free to call or WhatsApp me at +91 9952142302.

Summary of your message:
Subject: {msg.subject}
Date: {msg.created_at.strftime('%Y-%m-%d')}
Message:
{msg.message}

Best regards,
Venkatesh Babu
Python Developer | AI & LLM Specialist | Automation Engineer
Madurai, Tamil Nadu, India
Portfolio: https://venkatesh-snowy.vercel.app
GitHub: https://github.com/venkatesh01-t
LinkedIn: https://www.linkedin.com/in/venkatesh-babu-208891392
    """.strip()

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
            reply_to=[settings.ADMIN_NOTIFICATION_EMAIL],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Failed to send visitor auto-reply email: {e}")
        return False
