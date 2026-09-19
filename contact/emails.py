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
    """Send an interactive, animated luxury auto-reply to the visitor."""
    subject = f"Thank you for contacting Venkatesh Babu — Received: {msg.subject}"
    recipient = msg.email

    # Safe snippet of message for code capsule
    safe_message = msg.message.replace('"', '\\"')

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <meta name="color-scheme" content="light dark">
      <meta name="supported-color-schemes" content="light dark">
      <title>Inquiry Received • Venkatesh Babu</title>
      <style>
        :root {{
          color-scheme: light dark;
          supported-color-schemes: light dark;
        }}
        @keyframes shimmerGlow {{
          0% {{ background-position: -200% 0; }}
          100% {{ background-position: 200% 0; }}
        }}
        @keyframes pulseDot {{
          0%, 100% {{ transform: scale(1); opacity: 1; }}
          50% {{ transform: scale(1.2); opacity: 0.65; }}
        }}
        body {{
          margin: 0;
          padding: 24px 12px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', Helvetica, Arial, sans-serif;
          background-color: #f1f5f9;
          color: #1e293b;
          -webkit-font-smoothing: antialiased;
        }}
        .email-wrapper {{
          max-width: 600px;
          margin: 0 auto;
          background-color: #ffffff;
          border-radius: 20px;
          border: 1px solid #e2e8f0;
          overflow: hidden;
          box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.08);
        }}
        .header-banner {{
          background: linear-gradient(135deg, #0d9488 0%, #06b6d4 50%, #6366f1 100%);
          padding: 36px 28px 30px;
          text-align: center;
          color: #ffffff;
          position: relative;
        }}
        .avatar-ring {{
          display: inline-block;
          width: 58px;
          height: 58px;
          border-radius: 50%;
          background: linear-gradient(135deg, #115e59, #14b8a6);
          border: 3px solid rgba(255, 255, 255, 0.9);
          line-height: 54px;
          text-align: center;
          font-size: 20px;
          font-weight: 800;
          color: #ffffff;
          box-shadow: 0 8px 20px rgba(13, 148, 136, 0.4);
          margin-bottom: 12px;
        }}
        .header-title {{
          margin: 0;
          font-size: 23px;
          font-weight: 800;
          letter-spacing: -0.4px;
          color: #ffffff;
        }}
        .header-sub {{
          margin: 6px 0 0;
          font-size: 13px;
          color: rgba(255, 255, 255, 0.92);
          font-weight: 500;
        }}
        .content-area {{
          padding: 30px 26px;
        }}
        .status-pill {{
          display: inline-block;
          padding: 6px 14px;
          border-radius: 999px;
          background-color: #ecfdf5;
          border: 1px solid #a7f3d0;
          font-size: 11px;
          font-weight: 700;
          color: #059669;
          letter-spacing: 0.04em;
          margin-bottom: 20px;
        }}
        .pulse-dot {{
          display: inline-block;
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background-color: #10b981;
          box-shadow: 0 0 8px #10b981;
          margin-right: 6px;
          vertical-align: middle;
          animation: pulseDot 2s infinite ease-in-out;
        }}
        .text-lead {{
          font-size: 15px;
          line-height: 1.65;
          color: #334155;
          margin: 0 0 16px;
        }}
        .terminal-capsule {{
          background-color: #0b0f19;
          border-radius: 12px;
          border: 1px solid #1e293b;
          overflow: hidden;
          margin: 24px 0;
          box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.3);
        }}
        .terminal-bar {{
          background-color: #111827;
          padding: 8px 14px;
          border-bottom: 1px solid #1f2937;
          font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
          font-size: 11px;
          color: #94a3b8;
          display: flex;
          align-items: center;
        }}
        .term-dot {{
          display: inline-block;
          width: 10px;
          height: 10px;
          border-radius: 50%;
          margin-right: 6px;
          vertical-align: middle;
        }}
        .term-dot-red {{ background-color: #ef4444; }}
        .term-dot-yellow {{ background-color: #f59e0b; }}
        .term-dot-green {{ background-color: #10b981; }}
        .terminal-body {{
          padding: 14px 16px;
          font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
          font-size: 12px;
          line-height: 1.6;
          color: #cbd5e1;
          overflow-x: auto;
        }}
        .line-num {{
          color: #475569;
          user-select: none;
          margin-right: 12px;
        }}
        .kw {{ color: #ec4899; }}
        .var {{ color: #38bdf8; }}
        .str {{ color: #34d399; }}
        .comment {{ color: #64748b; font-style: italic; }}
        .action-card {{
          display: block;
          background-color: #f8fafc;
          border: 1px solid #e2e8f0;
          border-radius: 12px;
          padding: 14px 16px;
          text-decoration: none;
          color: #1e293b;
          font-size: 12px;
          font-weight: 600;
          transition: all 0.2s ease;
        }}
        .action-card:hover {{
          background-color: #f1f5f9;
          border-color: #cbd5e1;
        }}
        .signature-card {{
          margin-top: 28px;
          padding-top: 20px;
          border-top: 1px solid #f1f5f9;
        }}
        .footer-note {{
          padding: 18px 24px;
          background-color: #f8fafc;
          border-top: 1px solid #e2e8f0;
          text-align: center;
          font-size: 11px;
          color: #94a3b8;
          line-height: 1.6;
        }}
        .footer-links a {{
          color: #0d9488;
          text-decoration: none;
          font-weight: 600;
          margin: 0 6px;
        }}

        /* Dark Mode Support */
        @media (prefers-color-scheme: dark) {{
          body {{
            background-color: #040711 !important;
            color: #e2e8f0 !important;
          }}
          .email-wrapper {{
            background-color: #0b0f19 !important;
            border-color: #1e293b !important;
            box-shadow: 0 10px 35px -5px rgba(0, 0, 0, 0.4) !important;
          }}
          .text-lead {{
            color: #cbd5e1 !important;
          }}
          .status-pill {{
            background-color: rgba(16, 185, 129, 0.12) !important;
            border-color: rgba(16, 185, 129, 0.3) !important;
            color: #34d399 !important;
          }}
          .action-card {{
            background-color: #111827 !important;
            border-color: #1f293d !important;
            color: #f1f5f9 !important;
          }}
          .signature-card {{
            border-top-color: #1e293b !important;
          }}
          .footer-note {{
            background-color: #07090e !important;
            border-top-color: #1e293b !important;
            color: #64748b !important;
          }}
        }}
      </style>
    </head>
    <body>
      <div class="email-wrapper">
        
        <!-- Header Banner with Glow Avatar -->
        <div class="header-banner">
          <div class="avatar-ring">VB</div>
          <h1 class="header-title">Message Received</h1>
          <p class="header-sub">Thank you for reaching out to Venkatesh Babu</p>
        </div>

        <!-- Main Content Area -->
        <div class="content-area">
          
          <!-- Animated Status Pill -->
          <div class="status-pill">
            <span class="pulse-dot"></span>
            <span>STATUS: QUEUED IN PRIORITY INBOX &bull; RESPONSE SLA: &lt; 24 HOURS</span>
          </div>

          <p class="text-lead">
            Hi <strong>{msg.name}</strong>,
          </p>
          <p class="text-lead">
            Thank you for getting in touch! I have successfully received your inquiry regarding <span style="color:#0d9488; font-weight:700;">"{msg.subject}"</span>.
          </p>
          <p class="text-lead" style="font-size:13.5px; color:#64748b;">
            I personally review every project proposal and technical inquiry. You will receive a direct, detailed response within <strong>24 hours</strong>.
          </p>

          <!-- IDE Terminal Styled Inquiry Capsule -->
          <div class="terminal-capsule">
            <div class="terminal-bar">
              <span class="term-dot term-dot-red"></span>
              <span class="term-dot term-dot-yellow"></span>
              <span class="term-dot term-dot-green"></span>
              <span style="margin-left:6px; font-weight:600;">client_inquiry_transcript.py</span>
            </div>
            <div class="terminal-body">
              <div><span class="line-num">01</span><span class="comment"># Submitted Inquiry Details</span></div>
              <div><span class="line-num">02</span><span class="var">sender</span> = <span class="str">"{msg.name} &lt;{msg.email}&gt;"</span></div>
              <div><span class="line-num">03</span><span class="var">subject</span> = <span class="str">"{msg.subject}"</span></div>
              <div><span class="line-num">04</span><span class="var">received_at</span> = <span class="str">"{msg.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"</span></div>
              <div><span class="line-num">05</span></div>
              <div><span class="line-num">06</span><span class="kw">def</span> <span class="var">inquiry_payload</span>():</div>
              <div><span class="line-num">07</span>&nbsp;&nbsp;&nbsp;&nbsp;<span class="kw">return</span> <span class="str">\"\"\"{safe_message}\"\"\"</span></div>
            </div>
          </div>

          <!-- Interactive Quick-Action Grid -->
          <div style="margin: 24px 0 16px;">
            <div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#94a3b8; margin-bottom:12px;">
              Quick Actions &amp; Direct Channels
            </div>
            
            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse:separate; border-spacing:8px 8px; margin:0 -8px;">
              <tr>
                <td width="50%" valign="top">
                  <a href="mailto:babuvenkatesh093@gmail.com?subject=Schedule%20Discussion%20with%20Venkatesh" class="action-card">
                    <div style="color:#0d9488; font-size:14px; margin-bottom:4px;">⚡ Schedule 1:1 Discussion</div>
                    <div style="font-size:11px; color:#64748b; font-weight:400;">Book an architecture or consultation call</div>
                  </a>
                </td>
                <td width="50%" valign="top">
                  <a href="https://wa.me/919952142302?text=Hello%20Venkatesh%2C%20following%20up%20on%20my%20portfolio%20inquiry" class="action-card">
                    <div style="color:#10b981; font-size:14px; margin-bottom:4px;">💬 WhatsApp Direct Chat</div>
                    <div style="font-size:11px; color:#64748b; font-weight:400;">Instant message at +91 99521 42302</div>
                  </a>
                </td>
              </tr>
              <tr>
                <td width="50%" valign="top">
                  <a href="https://github.com/venkatesh01-t" class="action-card">
                    <div style="color:#6366f1; font-size:14px; margin-bottom:4px;">💻 Explore GitHub Repos</div>
                    <div style="font-size:11px; color:#64748b; font-weight:400;">View 15+ open-source AI &amp; Python tools</div>
                  </a>
                </td>
                <td width="50%" valign="top">
                  <a href="https://venkatesh-snowy.vercel.app" class="action-card">
                    <div style="color:#06b6d4; font-size:14px; margin-bottom:4px;">🚀 Live Portfolio</div>
                    <div style="font-size:11px; color:#64748b; font-weight:400;">Case studies, certifications &amp; stack</div>
                  </a>
                </td>
              </tr>
            </table>
          </div>

          <!-- Signature Block -->
          <div class="signature-card">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td width="48" valign="top" style="padding-right:14px;">
                  <div style="width:44px; height:44px; border-radius:50%; background:linear-gradient(135deg, #0d9488, #6366f1); line-height:44px; text-align:center; color:#ffffff; font-weight:800; font-size:14px;">VB</div>
                </td>
                <td valign="top">
                  <div style="font-size:14px; font-weight:800; color:#0f172a;" class="text-lead">
                    Venkatesh Babu <span style="display:inline-block; margin-left:4px; font-size:11px; color:#0d9488; font-weight:700;">✓ Verified</span>
                  </div>
                  <div style="font-size:12px; color:#0d9488; font-weight:600; margin-top:2px;">
                    Python Developer • AI &amp; LLM Specialist • Automation Engineer
                  </div>
                  <div style="font-size:11px; color:#64748b; margin-top:4px;">
                    Madurai, Tamil Nadu, India &bull; <a href="tel:+919952142302" style="color:#64748b; text-decoration:none;">+91 99521 42302</a>
                  </div>
                </td>
              </tr>
            </table>
          </div>

        </div>

        <!-- Footer -->
        <div class="footer-note">
          <div class="footer-links">
            <a href="https://venkatesh-snowy.vercel.app">Portfolio</a> &bull;
            <a href="https://github.com/venkatesh01-t">GitHub</a> &bull;
            <a href="https://www.linkedin.com/in/venkatesh-babu-208891392">LinkedIn</a>
          </div>
          <p style="margin: 8px 0 0; font-size: 10.5px;">
            This automated confirmation was securely generated &amp; dispatched by Venkatesh Babu's portfolio contact system.
          </p>
        </div>

      </div>
    </body>
    </html>
    """

    plain_text = f"""
Hi {msg.name},

Thank you for reaching out! I have received your message regarding "{msg.subject}".

I review every technical inquiry and proposal personally. You can expect a direct response within 24 hours.

--------------------------------------------------
SUBMITTED INQUIRY TRANSCRIPT:
--------------------------------------------------
Sender:  {msg.name} <{msg.email}>
Subject: {msg.subject}
Date:    {msg.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

Message Details:
{msg.message}
--------------------------------------------------

DIRECT CONTACT & QUICK LINKS:
- WhatsApp:  https://wa.me/919952142302
- Portfolio: https://venkatesh-snowy.vercel.app
- GitHub:    https://github.com/venkatesh01-t
- LinkedIn:  https://www.linkedin.com/in/venkatesh-babu-208891392
- Phone:     +91 9952142302

Best regards,
Venkatesh Babu
Python Developer | AI & LLM Specialist | Python Automation Engineer
Madurai, Tamil Nadu, India
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
