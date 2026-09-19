import json
from django.test import TestCase, Client
from django.core import mail
from django.urls import reverse
from .models import ContactMessage
from .emails import send_contact_emails


class ContactMessageModelTest(TestCase):
    def test_create_contact_message(self):
        msg = ContactMessage.objects.create(
            name="Alice Developer",
            email="alice@example.com",
            subject="Python AI Consultation",
            message="Hi Venkatesh, I need help building an automated LLM pipeline.",
            ip_address="127.0.0.1"
        )
        self.assertEqual(msg.name, "Alice Developer")
        self.assertEqual(msg.email, "alice@example.com")
        self.assertFalse(msg.is_read)
        self.assertFalse(msg.replied)
        self.assertIn("Alice Developer", str(msg))


class ContactAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('contact_submit')

    def test_valid_submission(self):
        payload = {
            'name': 'Rajesh Kumar',
            'email': 'rajesh@example.com',
            'subject': 'Project Collaboration',
            'message': 'Hello, we would like to hire you for a Django and Selenium automation project.'
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('Rajesh', data['message'])

        # Verify saved in SQLite database
        msg = ContactMessage.objects.filter(email='rajesh@example.com').first()
        self.assertIsNotNone(msg)
        self.assertEqual(msg.name, 'Rajesh Kumar')
        self.assertEqual(msg.subject, 'Project Collaboration')

    def test_missing_fields_validation(self):
        payload = {
            'name': '',
            'email': 'invalid-email',
            'subject': '',
            'message': ''
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('errors', data)

    def test_invalid_email_validation(self):
        payload = {
            'name': 'Test User',
            'email': 'not-an-email',
            'subject': 'Hello',
            'message': 'Testing message'
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['success'])
        self.assertIn('email', data['errors'])


class EmailNotificationTest(TestCase):
    def setUp(self):
        mail.outbox = []

    def test_dual_email_dispatch(self):
        msg = ContactMessage.objects.create(
            name="John Client",
            email="client@example.com",
            subject="Website Development Inquiry",
            message="Looking forward to working with you on this project."
        )

        success = send_contact_emails(msg)
        self.assertTrue(success)

        # Should send 2 emails: 1 to admin, 1 auto-reply to visitor
        self.assertEqual(len(mail.outbox), 2)

        # Verify Admin Notification
        admin_email = mail.outbox[0]
        self.assertIn("John Client", admin_email.subject)
        self.assertIn("babuvenkatesh093@gmail.com", admin_email.to[0])

        # Verify Visitor Auto-Reply
        visitor_email = mail.outbox[1]
        self.assertIn("Thank you for contacting Venkatesh Babu", visitor_email.subject)
        self.assertEqual(visitor_email.to, ["client@example.com"])
        self.assertIn("Website Development Inquiry", visitor_email.body)

        # Verify Interactive HTML auto-reply features
        self.assertEqual(len(visitor_email.alternatives), 1)
        html_body, mime_type = visitor_email.alternatives[0]
        self.assertEqual(mime_type, "text/html")
        self.assertIn("STATUS: QUEUED IN PRIORITY INBOX", html_body)
        self.assertIn("client_inquiry_transcript.py", html_body)
        self.assertIn("Schedule 1:1 Discussion", html_body)
        self.assertIn("WhatsApp Direct Chat", html_body)
        self.assertIn("Explore GitHub Repos", html_body)
        self.assertIn("Live Portfolio", html_body)
        self.assertIn("prefers-color-scheme: dark", html_body)


class HomePageViewTest(TestCase):
    def test_homepage_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Venkatesh")
        self.assertContains(response, "contact-form")


class DashboardAuthAndViewsTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='admin_test',
            password='secretpassword',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular_test',
            password='secretpassword',
            is_staff=False
        )

    def test_unauthenticated_redirect(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard_login'), response.url)

    def test_staff_login_success(self):
        response = self.client.post(reverse('dashboard_login'), {
            'username': 'admin_test',
            'password': 'secretpassword'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard'), response.url)

        # Access dashboard as logged in staff
        dashboard_res = self.client.get(reverse('dashboard'))
        self.assertEqual(dashboard_res.status_code, 200)
        self.assertContains(dashboard_res, "Venkatesh Babu")
        self.assertContains(dashboard_res, "Control Center")

    def test_regular_user_access_denied(self):
        response = self.client.post(reverse('dashboard_login'), {
            'username': 'regular_test',
            'password': 'secretpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Access restricted. Staff account required.")

    def test_logout(self):
        self.client.login(username='admin_test', password='secretpassword')
        response = self.client.get(reverse('dashboard_logout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('dashboard_login'), response.url)


class DashboardAPIsTest(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='admin_api',
            password='secretpassword',
            is_staff=True
        )
        self.client.login(username='admin_api', password='secretpassword')

        # Seed sample messages
        self.msg1 = ContactMessage.objects.create(
            name="John Doe",
            email="john@example.com",
            subject="Python Web Scraping & Automation",
            message="Need a Selenium automation script.",
            is_read=False,
            is_starred=False,
            replied=False
        )
        self.msg2 = ContactMessage.objects.create(
            name="Jane Smith",
            email="jane@example.com",
            subject="AI Agent Consultation",
            message="Can we build an LLM workflow together?",
            is_read=True,
            is_starred=True,
            replied=True
        )

    def test_get_messages_api(self):
        res = self.client.get(reverse('dashboard_messages_api'))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['total'], 2)

    def test_get_messages_filtered(self):
        # Unread filter
        res = self.client.get(reverse('dashboard_messages_api') + '?filter=unread')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['messages'][0]['email'], 'john@example.com')

        # Starred filter
        res = self.client.get(reverse('dashboard_messages_api') + '?filter=starred')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['messages'][0]['email'], 'jane@example.com')

        # Search query
        res = self.client.get(reverse('dashboard_messages_api') + '?q=Selenium')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['total'], 1)
        self.assertEqual(data['messages'][0]['name'], 'John Doe')

    def test_toggle_message_status(self):
        # Toggle read
        res = self.client.post(
            reverse('dashboard_toggle_status_api'),
            data=json.dumps({'id': self.msg1.id, 'action': 'toggle_read'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.msg1.refresh_from_db()
        self.assertTrue(self.msg1.is_read)

        # Toggle star
        res = self.client.post(
            reverse('dashboard_toggle_status_api'),
            data=json.dumps({'id': self.msg1.id, 'action': 'toggle_star'}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        self.msg1.refresh_from_db()
        self.assertTrue(self.msg1.is_starred)

    def test_direct_reply_dispatch(self):
        mail.outbox = []
        payload = {
            'message_id': self.msg1.id,
            'subject': 'Re: Python Web Scraping & Automation',
            'reply_body': 'Hi John, I would be thrilled to work on your Selenium automation pipeline!'
        }
        res = self.client.post(
            reverse('dashboard_send_reply_api'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])

        # Verify DB state
        self.msg1.refresh_from_db()
        self.assertTrue(self.msg1.replied)
        self.assertIsNotNone(self.msg1.replied_at)
        self.assertEqual(self.msg1.reply_subject, 'Re: Python Web Scraping & Automation')
        self.assertIn('Selenium automation pipeline', self.msg1.reply_content)

        # Verify Outbox
        self.assertEqual(len(mail.outbox), 1)
        reply_email = mail.outbox[0]
        self.assertEqual(reply_email.to, ['john@example.com'])
        self.assertIn('Re: Python Web Scraping & Automation', reply_email.subject)

    def test_analytics_api(self):
        res = self.client.get(reverse('dashboard_analytics_api'))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertIn('trend', data)
        self.assertIn('topics', data)
        self.assertEqual(len(data['trend']), 7)

    def test_csv_export(self):
        res = self.client.get(reverse('dashboard_export_csv'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment; filename="venkatesh_inquiries_', res['Content-Disposition'])
        content = res.content.decode('utf-8')
        self.assertIn('John Doe', content)
        self.assertIn('Jane Smith', content)


class SEORoutesTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_robots_txt(self):
        res = self.client.get(reverse('robots_txt'))
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/plain', res['Content-Type'])
        self.assertContains(res, 'GPTBot')
        self.assertContains(res, 'sitemap.xml')
        self.assertContains(res, 'llms.txt')

    def test_sitemap_xml(self):
        res = self.client.get(reverse('sitemap_xml'))
        self.assertEqual(res.status_code, 200)
        self.assertIn('application/xml', res['Content-Type'])
        self.assertContains(res, 'https://venkatesh-snowy.vercel.app/')

    def test_llms_txt(self):
        res = self.client.get(reverse('llms_txt'))
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/plain', res['Content-Type'])
        self.assertContains(res, 'Venkatesh')
        self.assertContains(res, 'Python Automation')

    def test_llms_full_txt(self):
        res = self.client.get(reverse('llms_full_txt'))
        self.assertEqual(res.status_code, 200)
        self.assertIn('text/plain', res['Content-Type'])
        self.assertContains(res, 'Full Knowledge Base')

    def test_google_verification(self):
        res = self.client.get(reverse('google_verification'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'google-site-verification')


