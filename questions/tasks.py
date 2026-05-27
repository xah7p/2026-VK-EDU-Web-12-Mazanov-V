from cent import Client, PublishRequest
from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from application.celery import app
from .models import Answer
from questions.context import ( 
    _compute_popular_tags,
    _compute_best_members,
    _popular_tags_cache_key,
    _best_members_cache_key,
    CACHE_TIMEOUT_SECONDS,
)

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


@app.task(
    name="questions.tasks.recalculate_popular_tags_cache",
    bind=True,
    ignore_result=True,
)
def recalculate_popular_tags_cache(self, limit_tags = 10):
    tags = _compute_popular_tags(limit_tags)
    cache_key = _popular_tags_cache_key(limit_tags)
    cache.set(cache_key, tags, timeout=CACHE_TIMEOUT_SECONDS)


@app.task(
    name="questions.tasks.recalculate_best_members_cache",
    bind=True,
    ignore_result=True,
)
def recalculate_best_members_cache(self, limit_members = 10):
    tags = _compute_best_members(limit_members)
    cache_key = _best_members_cache_key(limit_members)
    cache.set(cache_key, tags, timeout=CACHE_TIMEOUT_SECONDS)
    

@app.task(bind=True, ignore_result=True)
def send_new_answer_email(self, answer_id):
    try:
        answer = Answer.objects.select_related("question", "question__author").get(pk=answer_id)
    except Answer.DoesNotExist:
        return False
    
    question = answer.question
    author = question.author
    
    if author is None:
        return False
    
    recipient = getattr(author, "email", "") or ""
    if not recipient:
        return False
    
    subject = f"Новый ответ на ваш вопрос: {question.title}"
    message = (
        f"На ваш вопрос появился новый ответ.\n\n"
        f"Вопрос: {question.title}\n"
        f"Ссылка: {question.get_absolute_url()}\n\n"
        f"Текст ответа:\n{answer.text}\n"
    )
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient],
        fail_silently=False
    )
    return True