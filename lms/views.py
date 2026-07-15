from rest_framework import viewsets, generics, permissions, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import CourseSerializer, LessonSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Course, Lesson, Subscription
from .permissions import IsModer, IsOwner
from rest_framework.permissions import IsAuthenticated
from .paginators import StandardResultsSetPagination


# CRUD для курса через ViewSet
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Просмотр доступен всем авторизованным
            permission_classes = [IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [IsAuthenticated, ~IsModer]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsOwner]
        else:  # update, partial_update
            # Редактирование для модераторов ИЛИ владельцев
            permission_classes = [IsAuthenticated, IsModer | IsOwner]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Автоматически привязываем курс к текущему пользователю
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Модератор').exists():
            # Модератор видит все курсы
            return Course.objects.all()
        # Обычный пользователь видит только свои курсы
        return Course.objects.filter(owner=user)


# CRUD для урока через Generic-классы
class LessonListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, ~IsModer]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Модератор').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner]


class SubscriptionToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response({"error": "Не указан course_id"}, status=status.HTTP_400_BAD_REQUEST)

        course_item = get_object_or_404(Course, id=course_id)

        # Проверяем наличие подписки
        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            # Если есть - удаляем
            subs_item.delete()
            message = 'подписка удалена'
        else:
            # Если нет - создаем
            Subscription.objects.create(user=user, course=course_item)
            message = 'подписка добавлена'

        return Response({"message": message}, status=status.HTTP_200_OK)
