from django.urls import path
from .views import (
    index_view,
    contact_submit,
    robots_txt,
    sitemap_xml,
    llms_txt,
    llms_full_txt,
    google_verification,
)
from .dashboard_views import (
    dashboard_login,
    dashboard_logout,
    dashboard_home,
    dashboard_messages_api,
    dashboard_toggle_status_api,
    dashboard_send_reply_api,
    dashboard_analytics_api,
    dashboard_export_csv,
    dashboard_smtp_test_api,
)

urlpatterns = [
    # Public Portfolio Routes
    path('', index_view, name='home'),
    path('api/contact/', contact_submit, name='contact_submit'),

    # SEO & AI Indexing Protocols
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap_xml, name='sitemap_xml'),
    path('llms.txt', llms_txt, name='llms_txt'),
    path('llms-full.txt', llms_full_txt, name='llms_full_txt'),
    path('googleb82a06046fcf2753.html', google_verification, name='google_verification'),

    # Admin Interactive Dashboard Routes
    path('dashboard/', dashboard_home, name='dashboard'),
    path('dashboard/login/', dashboard_login, name='dashboard_login'),
    path('dashboard/logout/', dashboard_logout, name='dashboard_logout'),

    # Dashboard REST APIs
    path('dashboard/api/messages/', dashboard_messages_api, name='dashboard_messages_api'),
    path('dashboard/api/toggle/', dashboard_toggle_status_api, name='dashboard_toggle_status_api'),
    path('dashboard/api/reply/', dashboard_send_reply_api, name='dashboard_send_reply_api'),
    path('dashboard/api/analytics/', dashboard_analytics_api, name='dashboard_analytics_api'),
    path('dashboard/api/smtp-test/', dashboard_smtp_test_api, name='dashboard_smtp_test_api'),
    path('dashboard/export/csv/', dashboard_export_csv, name='dashboard_export_csv'),
]
