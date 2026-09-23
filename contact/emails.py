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


AVATAR_IMG_URL = "https://venkatesh01-t.vercel.app/static/1.png"

def _send_admin_alert(msg):
    """Notify Venkatesh with a luxury, animated VIP admin alert when a client reaches out."""
    subject = f"🔔 [VIP Inquiry] {msg.name}: {msg.subject}"
    recipient = settings.ADMIN_NOTIFICATION_EMAIL

    safe_message = msg.message.replace('"', '\\"')

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <meta name="color-scheme" content="dark light">
      <title>New VIP Inquiry • Venkatesh Babu</title>
      <style>
        :root {{ color-scheme: dark light; }}
        @keyframes auraSpin {{
          0% {{ transform: rotate(0deg); }}
          100% {{ transform: rotate(360deg); }}
        }}
        @keyframes auraPulse {{
          0%, 100% {{ box-shadow: 0 0 20px rgba(20, 184, 166, 0.7), 0 0 40px rgba(99, 102, 241, 0.4); }}
          50% {{ box-shadow: 0 0 32px rgba(20, 184, 166, 0.95), 0 0 55px rgba(99, 102, 241, 0.65); }}
        }}
        @keyframes radarPing {{
          0% {{ transform: scale(0.9); opacity: 0.9; }}
          70% {{ transform: scale(2.2); opacity: 0; }}
          100% {{ transform: scale(2.2); opacity: 0; }}
        }}
        @keyframes holoMesh {{
          0% {{ background-position: 0% 50%; }}
          50% {{ background-position: 100% 50%; }}
          100% {{ background-position: 0% 50%; }}
        }}
        body {{
          margin: 0;
          padding: 24px 12px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif;
          background-color: #07090e;
          color: #e2e8f0;
          -webkit-font-smoothing: antialiased;
        }}
        .card {{
          max-width: 620px;
          margin: 0 auto;
          background-color: #0d121f;
          border-radius: 20px;
          border: 1px solid #1e293b;
          overflow: hidden;
          box-shadow: 0 15px 40px -5px rgba(0, 0, 0, 0.5);
        }}
        .header {{
          background: linear-gradient(135deg, #0d9488 0%, #0891b2 30%, #4f46e5 70%, #7c3aed 100%);
          background-size: 250% 250%;
          animation: holoMesh 8s ease infinite;
          padding: 34px 26px 28px;
          text-align: center;
          color: #ffffff;
        }}
        .avatar-wrap {{
          display: inline-block;
          position: relative;
          width: 78px;
          height: 78px;
          margin-bottom: 12px;
        }}
        .avatar-halo {{
          position: absolute;
          top: -3px;
          left: -3px;
          right: -3px;
          bottom: -3px;
          border-radius: 50%;
          background: linear-gradient(135deg, #14b8a6, #06b6d4, #8b5cf6, #ec4899);
          animation: auraSpin 6s linear infinite, auraPulse 3s ease-in-out infinite;
        }}
        .avatar-img {{
          position: relative;
          z-index: 2;
          width: 78px;
          height: 78px;
          border-radius: 50%;
          object-fit: cover;
          object-position: 50% 12%;
          display: block;
          border: 3px solid #ffffff;
        }}
        .badge-pill {{
          display: inline-block;
          padding: 5px 13px;
          border-radius: 999px;
          background-color: rgba(245, 158, 11, 0.15);
          border: 1px solid rgba(245, 158, 11, 0.4);
          color: #fbbf24;
          font-size: 11px;
          font-weight: 800;
          letter-spacing: 0.05em;
          margin-bottom: 20px;
        }}
        .radar-box {{
          position: relative;
          display: inline-block;
          width: 8px;
          height: 8px;
          margin-right: 6px;
          vertical-align: middle;
        }}
        .radar-dot {{
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background-color: #f59e0b;
        }}
        .radar-wave {{
          position: absolute;
          top: 0;
          left: 0;
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background-color: rgba(245, 158, 11, 0.6);
          animation: radarPing 2s cubic-bezier(0, 0, 0.2, 1) infinite;
        }}
        .content {{
          padding: 28px 26px;
        }}
        .meta-table {{
          width: 100%;
          background-color: #111827;
          border-radius: 12px;
          border: 1px solid #1f2937;
          border-collapse: separate;
          border-spacing: 0;
          overflow: hidden;
          margin-bottom: 22px;
        }}
        .meta-table td {{
          padding: 11px 16px;
          border-bottom: 1px solid #1f2937;
          font-size: 12.5px;
        }}
        .meta-table tr:last-child td {{
          border-bottom: none;
        }}
        .meta-label {{
          width: 28%;
          color: #94a3b8;
          font-weight: 600;
          text-transform: uppercase;
          font-size: 11px;
          letter-spacing: 0.04em;
        }}
        .meta-val {{
          color: #f1f5f9;
          font-weight: 500;
        }}
        .terminal-capsule {{
          background-color: #080c14;
          border-radius: 12px;
          border: 1px solid #1e293b;
          overflow: hidden;
          margin: 22px 0;
        }}
        .terminal-bar {{
          background-color: #0f172a;
          padding: 8px 14px;
          border-bottom: 1px solid #1e293b;
          font-family: ui-monospace, monospace;
          font-size: 11px;
          color: #64748b;
        }}
        .terminal-body {{
          padding: 16px;
          font-family: ui-monospace, monospace;
          font-size: 12.5px;
          line-height: 1.6;
          color: #e2e8f0;
          white-space: pre-wrap;
        }}
        .btn-card {{
          display: block;
          padding: 13px 16px;
          border-radius: 12px;
          text-decoration: none;
          font-size: 12px;
          font-weight: 700;
          text-align: center;
          transition: all 0.2s;
        }}
        .footer {{
          padding: 18px 24px;
          background-color: #07090e;
          border-top: 1px solid #1e293b;
          text-align: center;
          font-size: 11px;
          color: #64748b;
        }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <div class="avatar-wrap">
            <div class="avatar-halo"></div>
            <img src="{AVATAR_IMG_URL}" alt="Venkatesh Babu" class="avatar-img" width="78" height="78" />
          </div>
          <h1 style="margin:0; font-size:22px; font-weight:800; letter-spacing:-0.4px;">Incoming Client Inquiry</h1>
          <p style="margin:4px 0 0; font-size:12.5px; opacity:0.92;">Portfolio Notification System • Priority Dispatch</p>
        </div>

        <div class="content">
          <div class="badge-pill">
            <span class="radar-box"><span class="radar-wave"></span><span class="radar-dot"></span></span>
            <span>ACTION REQUIRED &bull; NEW INBOX DISPATCH</span>
          </div>

          <table class="meta-table">
            <tr>
              <td class="meta-label">Client Name</td>
              <td class="meta-val"><strong style="color:#ffffff; font-size:14px;">{msg.name}</strong></td>
            </tr>
            <tr>
              <td class="meta-label">Verified Email</td>
              <td class="meta-val"><a href="mailto:{msg.email}" style="color:#38bdf8; text-decoration:none; font-weight:600;">{msg.email}</a></td>
            </tr>
            <tr>
              <td class="meta-label">Subject</td>
              <td class="meta-val"><span style="color:#10b981; font-weight:700;">{msg.subject}</span></td>
            </tr>
            <tr>
              <td class="meta-label">Received At</td>
              <td class="meta-val">{msg.created_at.strftime('%B %d, %Y at %I:%M %p UTC')}</td>
            </tr>
            <tr>
              <td class="meta-label">Client Network</td>
              <td class="meta-val" style="font-family:ui-monospace, monospace; font-size:11.5px; color:#94a3b8;">
                IP: {msg.ip_address or 'Unknown'}
              </td>
            </tr>
          </table>

          <div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#94a3b8; margin-bottom:8px;">
            Submitted Message Content:
          </div>

          <div class="terminal-capsule">
            <div class="terminal-bar">
              <span style="color:#ef4444;">●</span> <span style="color:#f59e0b;">●</span> <span style="color:#10b981;">●</span>
              <span style="margin-left:6px;">message_payload.txt</span>
            </div>
            <div class="terminal-body">{msg.message}</div>
          </div>

          <!-- Quick Action Buttons Grid -->
          <div style="margin-top:24px;">
            <div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#94a3b8; margin-bottom:12px;">
              Immediate Actions for Venkatesh
            </div>

            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse:separate; border-spacing:8px 8px; margin:0 -8px;">
              <tr>
                <td width="50%" valign="top">
                  <a href="mailto:{msg.email}?subject=Re:%20{msg.subject}" class="btn-card" style="background:#0d9488; color:#ffffff;">
                    ⚡ Direct Email Reply
                  </a>
                </td>
                <td width="50%" valign="top">
                  <a href="https://wa.me/919952142302" class="btn-card" style="background:#10b981; color:#ffffff;">
                    💬 Open WhatsApp
                  </a>
                </td>
              </tr>
              <tr>
                <td colspan="2" valign="top">
                  <a href="https://venkatesh01-t.vercel.app/dashboard/" class="btn-card" style="background:#1e293b; color:#cbd5e1; border:1px solid #334155;">
                    📊 View Full Metrics in Portfolio Dashboard
                  </a>
                </td>
              </tr>
            </table>
          </div>
        </div>

        <div class="footer">
          Venkatesh Babu Portfolio System &bull; Secure Multi-Channel Email Relay
        </div>
      </div>
    </body>
    </html>
    """

    plain_text = f"""
New Portfolio Message Received:
==================================================
From:       {msg.name} <{msg.email}>
Subject:    {msg.subject}
Date:       {msg.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}
Client IP:  {msg.ip_address or 'Unknown'}
User-Agent: {msg.user_agent or 'Unknown'}

Message:
--------------------------------------------------
{msg.message}
--------------------------------------------------

Immediate Action:
- Reply directly: mailto:{msg.email}?subject=Re:%20{msg.subject}
- Dashboard: https://venkatesh01-t.vercel.app/dashboard/
==================================================
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
    """Send an interactive, animated luxury auto-reply with Venkatesh's photo and trending animations."""
    subject = f"Thank you for contacting Venkatesh Babu — Received: {msg.subject}"
    recipient = msg.email

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
        @keyframes auraSpin {{
          0% {{ transform: rotate(0deg); }}
          100% {{ transform: rotate(360deg); }}
        }}
        @keyframes auraPulse {{
          0%, 100% {{ box-shadow: 0 0 20px rgba(20, 184, 166, 0.7), 0 0 40px rgba(99, 102, 241, 0.4); }}
          50% {{ box-shadow: 0 0 32px rgba(20, 184, 166, 0.95), 0 0 55px rgba(99, 102, 241, 0.65); }}
        }}
        @keyframes holoMesh {{
          0% {{ background-position: 0% 50%; }}
          50% {{ background-position: 100% 50%; }}
          100% {{ background-position: 0% 50%; }}
        }}
        @keyframes radarPing {{
          0% {{ transform: scale(0.9); opacity: 0.9; }}
          70% {{ transform: scale(2.2); opacity: 0; }}
          100% {{ transform: scale(2.2); opacity: 0; }}
        }}
        @keyframes blinkCursor {{
          0%, 49% {{ opacity: 1; }}
          50%, 100% {{ opacity: 0; }}
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
          background: linear-gradient(135deg, #0d9488 0%, #0891b2 25%, #4f46e5 60%, #7c3aed 100%);
          background-size: 250% 250%;
          animation: holoMesh 8s ease infinite;
          padding: 38px 28px 30px;
          text-align: center;
          color: #ffffff;
          position: relative;
        }}
        .avatar-wrap {{
          display: inline-block;
          position: relative;
          width: 82px;
          height: 82px;
          margin-bottom: 14px;
        }}
        .avatar-halo {{
          position: absolute;
          top: -3px;
          left: -3px;
          right: -3px;
          bottom: -3px;
          border-radius: 50%;
          background: linear-gradient(135deg, #14b8a6, #06b6d4, #8b5cf6, #ec4899);
          animation: auraSpin 6s linear infinite, auraPulse 3s ease-in-out infinite;
        }}
        .avatar-photo {{
          position: relative;
          z-index: 2;
          width: 82px;
          height: 82px;
          border-radius: 50%;
          object-fit: cover;
          object-position: 50% 12%;
          display: block;
          border: 3px solid #ffffff;
          box-shadow: 0 6px 18px rgba(0, 0, 0, 0.25);
        }}
        .header-title {{
          margin: 0;
          font-size: 24px;
          font-weight: 800;
          letter-spacing: -0.4px;
          color: #ffffff;
        }}
        .header-sub {{
          margin: 6px 0 0;
          font-size: 13.5px;
          color: rgba(255, 255, 255, 0.94);
          font-weight: 500;
        }}
        .content-area {{
          padding: 32px 26px;
        }}
        .status-pill {{
          display: inline-block;
          padding: 6px 15px;
          border-radius: 999px;
          background-color: #ecfdf5;
          border: 1px solid #a7f3d0;
          font-size: 11px;
          font-weight: 700;
          color: #059669;
          letter-spacing: 0.04em;
          margin-bottom: 22px;
        }}
        .radar-box {{
          position: relative;
          display: inline-block;
          width: 8px;
          height: 8px;
          margin-right: 7px;
          vertical-align: middle;
        }}
        .radar-dot {{
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background-color: #10b981;
        }}
        .radar-wave {{
          position: absolute;
          top: 0;
          left: 0;
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background-color: rgba(16, 185, 129, 0.6);
          animation: radarPing 2s cubic-bezier(0, 0, 0.2, 1) infinite;
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
        }}
        .term-dot {{
          display: inline-block;
          width: 10px;
          height: 10px;
          border-radius: 50%;
          margin-right: 5px;
          vertical-align: middle;
        }}
        .term-dot-red {{ background-color: #ef4444; }}
        .term-dot-yellow {{ background-color: #f59e0b; }}
        .term-dot-green {{ background-color: #10b981; }}
        .cursor-blink {{
          display: inline-block;
          width: 7px;
          height: 13px;
          background-color: #38bdf8;
          vertical-align: middle;
          margin-left: 4px;
          animation: blinkCursor 0.9s infinite;
        }}
        .terminal-body {{
          padding: 14px 16px;
          font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
          font-size: 12px;
          line-height: 1.65;
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
          transform: translateY(-1px);
        }}
        .signature-card {{
          margin-top: 30px;
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
        
        <!-- Animated Holographic Header Banner with Profile Avatar -->
        <div class="header-banner">
          <div class="avatar-wrap">
            <div class="avatar-halo"></div>
            <img src="{AVATAR_IMG_URL}" alt="Venkatesh Babu" class="avatar-photo" width="82" height="82" />
          </div>
          <h1 class="header-title">Message Received</h1>
          <p class="header-sub">Thank you for reaching out to Venkatesh Babu</p>
        </div>

        <!-- Main Content Area -->
        <div class="content-area">
          
          <!-- Live Radar SLA Indicator -->
          <div class="status-pill">
            <span class="radar-box"><span class="radar-wave"></span><span class="radar-dot"></span></span>
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
              <span class="cursor-blink"></span>
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
                  <a href="https://venkatesh01-t.vercel.app" class="action-card">
                    <div style="color:#06b6d4; font-size:14px; margin-bottom:4px;">🚀 Live Portfolio</div>
                    <div style="font-size:11px; color:#64748b; font-weight:400;">Case studies, certifications &amp; stack</div>
                  </a>
                </td>
              </tr>
            </table>
          </div>

          <!-- Verified Developer Signature Card -->
          <div class="signature-card">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td width="54" valign="top" style="padding-right:14px;">
                  <img src="{AVATAR_IMG_URL}" alt="Venkatesh Babu" width="48" height="48" style="width:48px; height:48px; border-radius:50%; object-fit:cover; object-position:50% 12%; display:block; border:2px solid #0d9488;" />
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
            <a href="https://venkatesh01-t.vercel.app">Portfolio</a> &bull;
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
- Portfolio: https://venkatesh01-t.vercel.app
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
