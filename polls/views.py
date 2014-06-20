from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from models import Poll, Choice
from serializers import PollSerializer, ChoiceSerializer
from rest_framework.decorators import link
import random

class PollViewSet(ModelViewSet):
    model = Poll
    serialier_class = PollSerializer

    @link()
    def random_poll(self, request):
        p = random.choice(self.model.objects.all())
        return Response(self.serialier_class(p).data)

    @link()
    def question_only(self, request, pk=None):
        p = self.model.objects.get(pk=pk)
        data = {'question': p.question}
        return Response(data)


class ChoiceViewSet(ModelViewSet):
    model = Choice
    serialier_class = ChoiceSerializer
