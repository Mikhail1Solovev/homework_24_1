import logging
from rest_framework import viewsets, generics
from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from myproject.permissions import IsModerator, IsOwnerOrModerator
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render
from rest_framework.pagination import PageNumberPagination
from .services.stripe_service import create_stripe_product, create_stripe_price, create_stripe_checkout_session

logger = logging.getLogger(__name__)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, IsModerator]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonListCreateView(generics.ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]

    def get(self, request, *args, **kwargs):
        lessons = self.get_queryset().select_related('course')  # Оптимизация запросов
        return render(request, 'lessons_list.html', {'lessons': lessons})

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]


class SubscriptionView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)

        try:
            subscription = Subscription.objects.get(user=user, course=course)
            subscription.delete()
            message = 'Подписка удалена'
            logger.info(
                f'Пользователь {user.email} отписался от курса {course.name}')
        except Subscription.DoesNotExist:
            Subscription.objects.create(user=user, course=course)
            message = 'Подписка добавлена'
            logger.info(
                f'Пользователь {user.email} подписался на курс {course.name}')

        return Response({"message": message})


class LessonListView(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]


# Новый класс для обработки оплаты через Stripe
class PaymentView(APIView):
    def post(self, request, *args, **kwargs):
        course_name = request.data.get('course_name')
        course_price = request.data.get('course_price')

        # Проверка цены курса в базе данных для предотвращения манипуляций
        course = get_object_or_404(Course, name=course_name)
        if str(course.price) != course_price:
            return Response({"error": "Некорректная цена курса."}, status=400)

        # Создание продукта и цены в Stripe
        product_id = create_stripe_product(course_name)
        price_id = create_stripe_price(product_id, course_price)

        # Создание сессии оплаты
        success_url = request.build_absolute_uri('/success/')
        cancel_url = request.build_absolute_uri('/cancel/')
        checkout_url = create_stripe_checkout_session(
            price_id, success_url, cancel_url)

        logger.info(
            f'Создана сессия оплаты для курса {course_name} пользователем {request.user.email}')
        return Response({"checkout_url": checkout_url})
