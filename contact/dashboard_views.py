import csv
import json
from datetime import timedelta
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import ContactMessage


def dashboard_login(request):
    """Custom aesthetic dark-mode login for portfolio admin."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard')

    error_message = None
    if request.method == 'POST':
        user_name = request.POST.get('username', '').strip()
        pass_word = request.POST.get('password', '').strip()
        user = authenticate(request, username=user_name, password=pass_word)

        if user is not None:
            if user.is_staff:
                login(request, user)
                next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard'
                return redirect(next_url)
            else:
                error_message = "Access restricted. Staff account required."
        else:
            error_message = "Invalid username or password. Please try again."

    return render(request, 'dashboard/login.html', {'error': error_message})


def dashboard_logout(request):
    """Logs out and redirects to dashboard login."""
    logout(request)
    return redirect('dashboard_login')


@staff_member_required(login_url='dashboard_login')
def dashboard_home(request):
    """Main creative and interactive dashboard interface."""
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    total_count = ContactMessage.objects.count()
    unread_count = ContactMessage.objects.filter(is_read=False).count()
    replied_count = ContactMessage.objects.filter(replied=True).count()
    starred_count = ContactMessage.objects.filter(is_starred=True).count()
    today_count = ContactMessage.objects.filter(created_at__gte=today_start).count()

    response_rate = int((replied_count / total_count * 100)) if total_count > 0 else 100

    recent_messages = ContactMessage.objects.all()[:40]
    smtp_active = bool(settings.GMAIL_APP_PASSWORD)

    context = {
        'total_count': total_count,
        'unread_count': unread_count,
        'replied_count': replied_count,
        'starred_count': starred_count,
        'today_count': today_count,
        'response_rate': response_rate,
        'smtp_active': smtp_active,
        'gmail_user': settings.GMAIL_USER,
        'messages': recent_messages,
    }
    return render(request, 'dashboard/dashboard.html', context)


@staff_member_required(login_url='dashboard_login')
def dashboard_messages_api(request):
    """Returns filtered and searched messages in JSON format."""
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('filter', 'all')

    qs = ContactMessage.objects.all()

    if status_filter == 'unread':
        qs = qs.filter(is_read=False)
    elif status_filter == 'replied':
        qs = qs.filter(replied=True)
    elif status_filter == 'starred':
        qs = qs.filter(is_starred=True)

    if query:
        qs = qs.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(subject__icontains=query) |
            Q(message__icontains=query) |
            Q(ip_address__icontains=query)
        )

    messages_data = []
    for msg in qs[:60]:
        messages_data.append({
            'id': msg.id,
            'name': msg.name,
            'email': msg.email,
            'subject': msg.subject,
            'message': msg.message,
            'is_read': msg.is_read,
            'is_starred': msg.is_starred,
            'replied': msg.replied,
            'replied_at': msg.replied_at.strftime('%b %d, %Y %I:%M %p') if msg.replied_at else None,
            'reply_subject': msg.reply_subject,
            'reply_content': msg.reply_content,
            'ip_address': msg.ip_address or 'Unknown',
            'user_agent': msg.user_agent or 'Unknown Browser',
            'date_formatted': msg.created_at.strftime('%b %d, %Y'),
            'time_formatted': msg.created_at.strftime('%I:%M %p'),
            'relative_time': _get_relative_time(msg.created_at),
        })

    return JsonResponse({'success': True, 'messages': messages_data, 'total': len(messages_data)})


@require_POST
@staff_member_required(login_url='dashboard_login')
def dashboard_toggle_status_api(request):
    """Toggles read, starred, or replied status, or deletes a message."""
    try:
        data = json.loads(request.body)
        msg_id = data.get('id')
        action = data.get('action')

        msg = ContactMessage.objects.get(id=msg_id)

        if action == 'toggle_read':
            msg.is_read = not msg.is_read
            msg.save(update_fields=['is_read', 'updated_at'])
            return JsonResponse({'success': True, 'is_read': msg.is_read})
        elif action == 'toggle_star':
            msg.is_starred = not msg.is_starred
            msg.save(update_fields=['is_starred', 'updated_at'])
            return JsonResponse({'success': True, 'is_starred': msg.is_starred})
        elif action == 'toggle_replied':
            msg.replied = not msg.replied
            if msg.replied and not msg.replied_at:
                msg.replied_at = timezone.now()
            msg.save(update_fields=['replied', 'replied_at', 'updated_at'])
            return JsonResponse({'success': True, 'replied': msg.replied})
        elif action == 'delete':
            msg.delete()
            return JsonResponse({'success': True, 'deleted': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)

    except ContactMessage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_POST
@staff_member_required(login_url='dashboard_login')
def dashboard_send_reply_api(request):
    """
    Sends a direct email reply to the visitor via Google SMTP
    and records the reply in the database.
    """
    try:
        data = json.loads(request.body)
        msg_id = data.get('message_id')
        reply_subject = data.get('subject', '').strip()
        reply_body = data.get('reply_body', '').strip()

        if not reply_subject or not reply_body:
            return JsonResponse({'success': False, 'error': 'Subject and reply content cannot be empty.'}, status=400)

        msg = ContactMessage.objects.get(id=msg_id)

        # Build styled reply email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8fafc; color: #334155; padding: 24px; margin: 0; }}
            .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 14px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }}
            .header {{ background: linear-gradient(135deg, #0d9488, #14b8a6, #8b5cf6); padding: 24px; color: white; }}
            .body {{ padding: 24px; font-size: 14px; line-height: 1.7; color: #334155; white-space: pre-wrap; }}
            .quote-box {{ background: #f1f5f9; border-left: 3px solid #14b8a6; padding: 12px 16px; margin: 20px 0; border-radius: 0 8px 8px 0; font-size: 12px; color: #64748b; }}
            .footer {{ padding: 16px 24px; background: #f8fafc; border-top: 1px solid #e2e8f0; font-size: 11px; color: #94a3b8; text-align: center; }}
          </style>
        </head>
        <body>
          <div class="card">
            <div class="header">
              <h2 style="margin:0; font-size:18px;">Venkatesh Babu</h2>
              <p style="margin:4px 0 0; font-size:12px; opacity:0.9;">Python Developer • AI & Automation Engineer</p>
            </div>
            <div class="body">
{reply_body}

              <div class="quote-box">
                <strong>Regarding your inquiry:</strong><br>
                <em>"{msg.subject}"</em><br>
                Received on: {msg.created_at.strftime('%B %d, %Y')}
              </div>
            </div>
            <div class="footer">
              Venkatesh Babu • Madurai, Tamil Nadu, India • <a href="https://venkatesh-snowy.vercel.app" style="color:#0d9488;">Portfolio</a> • <a href="https://github.com/venkatesh01-t" style="color:#0d9488;">GitHub</a>
            </div>
          </div>
        </body>
        </html>
        """

        plain_text = f"""
{reply_body}

---
In response to your inquiry:
Subject: {msg.subject}
Date: {msg.created_at.strftime('%Y-%m-%d')}
Message:
{msg.message}

--
Venkatesh Babu
Python Developer | AI & LLM Developer | Python Automation Engineer
Madurai, Tamil Nadu, India
https://venkatesh-snowy.vercel.app
        """.strip()

        # Send via Django Email Backend
        email = EmailMultiAlternatives(
            subject=reply_subject,
            body=plain_text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[msg.email],
            reply_to=[settings.ADMIN_NOTIFICATION_EMAIL]
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        # Update message state
        msg.replied = True
        msg.is_read = True
        msg.replied_at = timezone.now()
        msg.reply_subject = reply_subject
        msg.reply_content = reply_body
        msg.save(update_fields=['replied', 'is_read', 'replied_at', 'reply_subject', 'reply_content', 'updated_at'])

        return JsonResponse({
            'success': True,
            'message': f"Reply sent successfully to {msg.email}!"
        })

    except ContactMessage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Message not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f"Failed to send email: {str(e)}"}, status=500)


@staff_member_required(login_url='dashboard_login')
def dashboard_analytics_api(request):
    """Provides 7-day message trajectory and topic distribution for Chart.js."""
    today = timezone.now().date()
    days_data = []

    # Last 7 Days count
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = ContactMessage.objects.filter(
            created_at__date=day
        ).count()
        days_data.append({
            'date': day.strftime('%a, %b %d'),
            'label': day.strftime('%a'),
            'count': count
        })

    # Topic Breakdown
    topic_map = {
        'Python / Automation': Q(subject__icontains='automation') | Q(subject__icontains='selenium') | Q(subject__icontains='playwright') | Q(subject__icontains='python'),
        'AI / LLM / ML': Q(subject__icontains='ai') | Q(subject__icontains='llm') | Q(subject__icontains='vision') | Q(subject__icontains='model'),
        'Django / Web / API': Q(subject__icontains='django') | Q(subject__icontains='api') | Q(subject__icontains='web') | Q(subject__icontains='site') | Q(subject__icontains='project'),
        'Consultation / Hire': Q(subject__icontains='hire') | Q(subject__icontains='consult') | Q(subject__icontains='offer') | Q(subject__icontains='work'),
    }

    topics_data = {}
    categorized_total = 0
    for label, query_filter in topic_map.items():
        c = ContactMessage.objects.filter(query_filter).count()
        topics_data[label] = c
        categorized_total += c

    total_msgs = ContactMessage.objects.count()
    other_count = max(0, total_msgs - categorized_total)
    topics_data['General Inquiries'] = other_count

    return JsonResponse({
        'success': True,
        'trend': days_data,
        'topics': {
            'labels': list(topics_data.keys()),
            'data': list(topics_data.values())
        }
    })


@staff_member_required(login_url='dashboard_login')
def dashboard_export_csv(request):
    """Exports all contact messages to a CSV spreadsheet."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="venkatesh_inquiries_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID',
        'Date & Time',
        'Sender Name',
        'Sender Email',
        'Subject',
        'Message',
        'Status (Read)',
        'Status (Replied)',
        'Starred',
        'Replied At',
        'Client IP',
        'Client Browser/Device'
    ])

    for msg in ContactMessage.objects.all().order_by('-created_at'):
        writer.writerow([
            msg.id,
            msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            msg.name,
            msg.email,
            msg.subject,
            msg.message,
            'Yes' if msg.is_read else 'No',
            'Yes' if msg.replied else 'No',
            'Yes' if msg.is_starred else 'No',
            msg.replied_at.strftime('%Y-%m-%d %H:%M:%S') if msg.replied_at else 'N/A',
            msg.ip_address or 'N/A',
            msg.user_agent or 'N/A',
        ])

    return response


@staff_member_required(login_url='dashboard_login')
def dashboard_smtp_test_api(request):
    """Tests the active Google SMTP connection."""
    try:
        connection = get_connection(fail_silently=False)
        connection.open()
        connection.close()
        return JsonResponse({'success': True, 'message': f'Connected to Google SMTP ({settings.GMAIL_USER}) successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Google SMTP error: {str(e)}'}, status=500)


def _get_relative_time(dt):
    """Human-friendly relative timestamp."""
    now = timezone.now()
    diff = now - dt

    if diff.days == 0:
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            m = diff.seconds // 60
            return f"{m}m ago"
        else:
            h = diff.seconds // 3600
            return f"{h}h ago"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return f"{diff.days}d ago"
    else:
        return dt.strftime('%b %d')
