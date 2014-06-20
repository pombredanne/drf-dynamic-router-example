from models import Poll, Choice
from rest_framework.serializers import ModelSerializer

class PollSerializer(ModelSerializer):
    class Meta:
        model = Poll

class ChoiceSerializer(ModelSerializer):
    class Meta:
        model = Choice
