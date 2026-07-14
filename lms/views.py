from rest_framework import viewsets, generics, permissions, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from .permissions import IsModer, IsOwner


# CRUD для курса через ViewSet
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

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
