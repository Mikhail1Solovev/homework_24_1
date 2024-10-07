from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonListCreateView, SubscriptionView, LessonDetailView, PaymentView

app_name = 'courses'

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls)),
    path('subscribe/', SubscriptionView.as_view(), name='subscribe'),
    path('lessons/', LessonListCreateView.as_view(), name='lesson-list'),  # <-- Маршрут для списка уроков
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
    path('pay/', PaymentView.as_view(), name='payment'),  # Новый маршрут для Stripe оплаты
]
