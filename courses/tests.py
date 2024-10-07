from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Course, Lesson, Subscription
from django.contrib.auth import get_user_model
from rest_framework import status
from django.contrib.auth.models import Group

User = get_user_model()


class LessonCRUDTestCase(APITestCase):
    def setUp(self):
        # Создаём группу 'Moderators'
        self.moderators_group, created = Group.objects.get_or_create(
            name='Moderators')

        # Создаём пользователей
        self.owner = User.objects.create_user(
            username='owner', password='password123')
        self.moderator = User.objects.create_user(
            username='moderator', password='password123', is_staff=True)
        self.other_user = User.objects.create_user(
            username='other', password='password123')

        # Добавляем модератора в группу 'Moderators'
        self.moderators_group.user_set.add(self.moderator)

        # Создаём курс
        self.course = Course.objects.create(
            title="Test Course",
            description="Course Description",
            owner=self.owner
        )

        # Создаём урок
        self.lesson = Lesson.objects.create(
            title="Initial Lesson",
            content="Lesson Content",
            # Валидная ссылка на YouTube
            video_link="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            course=self.course,
            owner=self.owner
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_create_lesson_as_owner(self):
        """
        Владелец курса может создать новый урок.
        """
        self.authenticate(self.owner)
        url = reverse('courses:lesson-list')
        data = {
            'title': 'New Lesson',
            'content': 'New Content',
            # Валидная ссылка на YouTube
            'video_link': 'https://www.youtube.com/watch?v=abcdefghijk',
            'course': self.course.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        self.assertEqual(Lesson.objects.last().title, 'New Lesson')

    def test_create_lesson_as_non_owner(self):
        """
        Пользователь, не являющийся владельцем или модератором, не может создать урок.
        """
        self.authenticate(self.other_user)
        url = reverse('courses:lesson-list')
        data = {
            'title': 'Unauthorized Lesson',
            'content': 'Should not be created',
            # Валидная ссылка на YouTube
            'video_link': 'https://www.youtube.com/watch?v=abcdefghijk',
            'course': self.course.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 1)  # Не должно увеличиться

    def test_update_lesson_as_owner(self):
        """
        Владелец курса может обновить урок.
        """
        self.authenticate(self.owner)
        url = reverse('courses:lesson-detail', args=[self.lesson.id])
        data = {'title': 'Updated Lesson Title'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson Title')

    def test_delete_lesson_as_moderator(self):
        """
        Модератор может удалить любой урок.
        """
        self.authenticate(self.moderator)
        url = reverse('courses:lesson-detail', args=[self.lesson.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        # Создаём группу 'Moderators' (если ещё не создана)
        self.moderators_group, created = Group.objects.get_or_create(
            name='Moderators')

        # Создаём пользователей
        self.user = User.objects.create_user(
            username='subscriber', password='password123')
        self.other_user = User.objects.create_user(
            username='other', password='password123')

        # Создаём курс
        self.course = Course.objects.create(
            title="Another Test Course",
            description="Another Description",
            owner=self.user
        )

        # Создаём подписку от имени пользователя
        Subscription.objects.create(user=self.user, course=self.course)

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def test_subscribe_to_course(self):
        """
        Пользователь может подписаться на курс.
        """
        self.authenticate(self.other_user)
        url = reverse('courses:subscribe')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(
            Subscription.objects.filter(
                user=self.other_user,
                course=self.course).exists())

    def test_unsubscribe_from_course(self):
        """
        Пользователь может отписаться от курса.
        """
        # Создаём подписку
        Subscription.objects.create(user=self.other_user, course=self.course)
        self.authenticate(self.other_user)
        url = reverse('courses:subscribe')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(
            Subscription.objects.filter(
                user=self.other_user,
                course=self.course).exists())

    def test_subscribe_without_authentication(self):
        """
        Анонимный пользователь не может подписаться на курс.
        """
        url = reverse('courses:subscribe')
        data = {'course_id': self.course.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
