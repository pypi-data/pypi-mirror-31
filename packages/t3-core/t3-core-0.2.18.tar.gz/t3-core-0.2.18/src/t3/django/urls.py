"""URL Configuration."""
from django.conf import settings
from django.http import HttpResponse
from django.urls import include, path


def build_urlpatterns(*paths):
    """
    Generate urlpatterns, adding URL_PREFIX, health checks, prometheus urls, and optional static files urls.

    Valid input is what would normally be assigned in urlpatterns

    ```
    paths = [
        path('', include('{project}.apps.{app}.urls'))
    ]
    ```
    """
    urlpatterns = [path(settings.URL_PREFIX, include(list(paths))), ]

    # Paths that check services health
    urlpatterns += [
        path('healthz', lambda request: HttpResponse(status=200), name='health-check'),
        path('readyz', lambda request: HttpResponse(status=200), name='ready-check'),
    ]

    # Prometheus paths
    urlpatterns += [path('', include('django_prometheus.urls')), ]

    # Include static file urls in development mode
    if not settings.AWS_STORAGE:
        from django.contrib.staticfiles.urls import staticfiles_urlpatterns
        urlpatterns += staticfiles_urlpatterns()

    return urlpatterns
