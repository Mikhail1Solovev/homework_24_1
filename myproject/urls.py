from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="Документация для API вашего проекта",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def home(request):
    return render(request, 'index.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/courses/', include(('courses.urls', 'courses'), namespace='courses')),
    path('api/users/', include('users.urls')),
    path('', home),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
