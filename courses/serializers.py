from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .validators import validate_video_link


class CourseSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    lessons = serializers.StringRelatedField(many=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'owner', 'lessons']


class LessonSerializer(serializers.ModelSerializer):
    video_link = serializers.CharField(validators=[validate_video_link])
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'video_link', 'owner', 'course']


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ['user', 'course', 'is_subscribed']

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Subscription.objects.filter(
            user=user, course=obj.course).exists()
