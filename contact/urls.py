from django.urls import path
from .views import (
    index_view,
    about_view,
    services_hub_view,
    service_python_automation_view,
    service_ai_llm_view,
    service_django_api_view,
    service_web_scraping_view,
    service_technical_seo_view,
    projects_hub_view,
    project_dental_clinic_view,
    project_drowsiness_detection_view,
    project_weather_forecasting_view,
    project_web_scraping_view,
    blog_hub_view,
    blog_selenium_2026_view,
    blog_playwright_vs_selenium_view,
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
    path('about/', about_view, name='about'),

    # Services Routes
    path('services/', services_hub_view, name='services_hub'),
    path('services/python-automation/', service_python_automation_view, name='service_python_automation'),
    path('services/ai-llm-development/', service_ai_llm_view, name='service_ai_llm'),
    path('services/django-api-development/', service_django_api_view, name='service_django_api'),
    path('services/web-scraping/', service_web_scraping_view, name='service_web_scraping'),
    path('services/technical-seo/', service_technical_seo_view, name='service_technical_seo'),

    # Projects Routes
    path('projects/', projects_hub_view, name='projects_hub'),
    path('projects/dental-clinic-system/', project_dental_clinic_view, name='project_dental_clinic'),
    path('projects/drowsiness-detection/', project_drowsiness_detection_view, name='project_drowsiness_detection'),
    path('projects/weather-forecasting/', project_weather_forecasting_view, name='project_weather_forecasting'),
    path('projects/web-scraping-automation/', project_web_scraping_view, name='project_web_scraping'),

    # Blog Routes
    path('blog/', blog_hub_view, name='blog_hub'),
    path('blog/python-automation-selenium-2026/', blog_selenium_2026_view, name='blog_selenium_2026'),
    path('blog/playwright-vs-selenium-python/', blog_playwright_vs_selenium_view, name='blog_playwright_vs_selenium'),

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
