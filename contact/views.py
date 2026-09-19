import json
import threading
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

from django.conf import settings
from django.http import HttpResponse, JsonResponse, Http404
import os

from .models import ContactMessage
from .emails import send_contact_emails
from .validators import validate_email_address, check_spam_signals


@ensure_csrf_cookie
def index_view(request):
    """Renders the main portfolio homepage."""
    return render(request, 'index.html')


def serve_seo_file(filename, content_type):
    file_path = os.path.join(settings.BASE_DIR, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return HttpResponse(content, content_type=content_type)
    raise Http404()


def robots_txt(request):
    return serve_seo_file('robots.txt', 'text/plain; charset=utf-8')


def sitemap_xml(request):
    return serve_seo_file('sitemap.xml', 'application/xml; charset=utf-8')


def llms_txt(request):
    return serve_seo_file('llms.txt', 'text/plain; charset=utf-8')


def llms_full_txt(request):
    return serve_seo_file('llms-full.txt', 'text/plain; charset=utf-8')


def google_verification(request):
    return serve_seo_file('googleb82a06046fcf2753.html', 'text/html; charset=utf-8')



@require_POST
def contact_submit(request):
    """
    Handles contact form submissions via AJAX/fetch.
    Saves to local database and dispatches emails in a background worker thread.
    """
    # Parse payload (supports both JSON and standard form-data)
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'success': False, 'error': 'Invalid JSON format.'}, status=400)
    else:
        data = request.POST

    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    subject = data.get('subject', '').strip()
    message = data.get('message', '').strip()

    # 1. Anti-spam & honeypot defense
    is_spam, spam_reason = check_spam_signals(data)
    if is_spam:
        return JsonResponse({'success': False, 'error': spam_reason, 'errors': {'spam': spam_reason}}, status=400)

    # 2. Comprehensive input validation
    errors = {}
    if not name:
        errors['name'] = 'Full name is required.'
    if not email:
        errors['email'] = 'Email address is required.'
    else:
        is_valid_email, email_error = validate_email_address(email)
        if not is_valid_email:
            errors['email'] = email_error

    if not subject:
        errors['subject'] = 'Subject is required.'
    if not message:
        errors['message'] = 'Message content is required.'

    if errors:
        return JsonResponse({'success': False, 'errors': errors, 'error': next(iter(errors.values()))}, status=400)

    # Extract client IP and User-Agent
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]

    # Save to local database
    contact_msg = ContactMessage.objects.create(
        name=name,
        email=email,
        subject=subject,
        message=message,
        ip_address=ip,
        user_agent=user_agent
    )

    # Send emails (in background thread, with timeout join for serverless runtimes)
    email_thread = threading.Thread(
        target=send_contact_emails,
        args=(contact_msg,),
        daemon=True
    )
    email_thread.start()
    if os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        email_thread.join(timeout=3.5)

    return JsonResponse({
        'success': True,
        'message': f"Thank you, {name}! Your message has been received. A confirmation has been sent to {email}."
    })
