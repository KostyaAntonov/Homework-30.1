from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(
        validators=[validate_youtube_url],
        allow_blank=True,
        required=False
    )

    class Meta:
        model = Lesson
        fields = '__all__'
        read_only_fields = ('owner',)


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'preview', 'description', 'lessons_count', 'lessons', 'is_subscribed', 'owner']
        read_only_fields = ('owner',)

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False
