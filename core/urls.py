from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Transparently route root asset requests to static URL to prevent 404s in development & production
    path('js/<path:path>', RedirectView.as_view(url='/static/js/%(path)s', permanent=False)),
    path('css/<path:path>', RedirectView.as_view(url='/static/css/%(path)s', permanent=False)),
    path('fonts/<path:path>', RedirectView.as_view(url='/static/fonts/%(path)s', permanent=False)),
    path('', include('contact.urls')),
]
