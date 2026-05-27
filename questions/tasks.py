from cent import Client, PublishRequest
from django.conf import settings
from .models import Answer
from application.celery import app

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

@app.task(bind=True, ignore_result=True)
def send_answer_to_centrifugo(self, answer_id):
    try:
        answer = Answer.objects.select_related("author", "question").get(pk=answer_id)
    except Answer.DoesNotExist:
        return False
    
    channel = f"question:{answer.question_id}"
    
    data = {"answer_id": answer.id}
    
    try:
        centrifugo_url = f"http://{settings.CENTRIFUGO_HOST}:{settings.CENTRIFUGO_PORT}/api"
        client = Client(centrifugo_url, api_key=settings.CENTRIFUGO_API_KEY, timeout=5)
        request = PublishRequest(channel=channel, data=data)
        client.publish(request)
        return True
    except Exception as e:
        print(f"Error sending to Centrifugo: {e}")
        return False
        