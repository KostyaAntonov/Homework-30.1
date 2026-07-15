from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import Course, Lesson, Subscription

User = get_user_model()


class LessonCRUDAndSubscriptionTests(APITestCase):
    def setUp(self):
        # Создаем пользователей
        self.owner = User.objects.create_user(email='owner@test.com', password='testpass123')
        self.moderator = User.objects.create_user(email='mod@test.com', password='testpass123')
        self.random_user = User.objects.create_user(email='random@test.com', password='testpass123')

        # Создаем группу модератора и добавляем туда пользователя
        from django.contrib.auth.models import Group
        self.moder_group, _ = Group.objects.get_or_create(name='Модератор')
        self.moderator.groups.add(self.moder_group)

        # Создаем курс и урок
        self.course = Course.objects.create(name='Test Course', description='Desc', owner=self.owner)
        self.lesson = Lesson.objects.create(
            name='Test Lesson',
            description='Desc',
            video_url='https://youtube.com/watch?v=123',
            course=self.course,
            owner=self.owner
        )

        self.client = APIClient()

    def test_create_lesson_valid_youtube_url(self):
        self.client.force_authenticate(user=self.owner)
        data = {
            'name': 'New Lesson',
            'description': 'New Desc',
            'video_url': 'https://www.youtube.com/watch?v=abc',
            'course': self.course.id
        }
        response = self.client.post('/api/lms/lessons/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson_invalid_url(self):
        self.client.force_authenticate(user=self.owner)
        data = {
            'name': 'Bad Lesson',
            'description': 'Bad Desc',
            'video_url': 'https://udemy.com/course/123',  # Не youtube
            'course': self.course.id
        }
        response = self.client.post('/api/lms/lessons/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_url', response.data)

    def test_update_lesson_by_owner(self):
        self.client.force_authenticate(user=self.owner)
        data = {'name': 'Updated Lesson Name'}
        response = self.client.patch(f'/api/lms/lessons/{self.lesson.id}/update/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, 'Updated Lesson Name')

    def test_delete_lesson_by_random_user_forbidden(self):
        self.client.force_authenticate(user=self.random_user)
        response = self.client.delete(f'/api/lms/lessons/{self.lesson.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_by_owner_success(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(f'/api/lms/lessons/{self.lesson.id}/delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())

    def test_subscription_toggle_add_and_remove(self):
        self.client.force_authenticate(user=self.random_user)

        # 1. Добавляем подписку
        response = self.client.post('/api/lms/subscriptions/toggle/', {'course_id': self.course.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка добавлена')
        self.assertTrue(Subscription.objects.filter(user=self.random_user, course=self.course).exists())

        # 2. Удаляем подписку
        response = self.client.post('/api/lms/subscriptions/toggle/', {'course_id': self.course.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка удалена')
        self.assertFalse(Subscription.objects.filter(user=self.random_user, course=self.course).exists())

    def test_course_serializer_shows_subscription_status(self):
        # Создаем подписку владельца на его же курс (для теста логики сериализатора)
        Subscription.objects.create(user=self.owner, course=self.course)

        # Авторизуемся как владелец (он точно имеет право видеть этот курс)
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(f'/api/lms/courses/{self.course.id}/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])
