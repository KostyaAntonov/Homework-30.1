from rest_framework import serializers
from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    # Задание 1: Поле для подсчета количества уроков
    lessons_count = serializers.SerializerMethodField()

    # Задание 3: Поле для вывода информации по всем урокам курса
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'preview', 'description', 'lessons_count', 'lessons']

    def get_lessons_count(self, obj):
        # Возвращаем количество уроков, связанных с этим курсом
        return obj.lessons.count()