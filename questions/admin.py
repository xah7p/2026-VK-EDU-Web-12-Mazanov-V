from django.contrib import admin
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import Answer, AnswerLike, Question, QuestionLike, QuestionTag, Tag


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    fields = ("author", "text", "created_at")
    readonly_fields = ("created_at",)
    raw_id_fields = ("author",)
    show_change_link = True


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "created_at", "answers_count", "likes_count")
    list_filter = ("created_at",)
    search_fields = ("title", "text", "author__username", "author__email")
    raw_id_fields = ("author",)
    readonly_fields = ("created_at",)
    inlines = (AnswerInline,)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("author").annotate(
            _answers_count=Count("answers", distinct=True),
            _likes_count=Count("question_likes", distinct=True),
        )
    
    @admin.display(description="Ответов", ordering="_answers_count")
    def answers_count(self, obj):
        return obj._answers_count
    
    @admin.display(description="Лайков", ordering="_likes_count")
    def likes_count(self, obj):
        return obj._likes_count
    

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "author", "created_at", "likes_count")
    list_filter = ("created_at",)
    search_fields = ("text", "question__title", "author__username")
    raw_id_fields = ("question", "author")
    readonly_fields = ("created_at",)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("question", "author").annotate(
            _likes_count=Count("answer_likes", distinct=True),
        )
        
    @admin.display(description="Лайков", ordering="_likes_count")
    def likes_count(self, obj):
        return obj._likes_count
    
    
@admin.register(QuestionTag)
class QuestionTagAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "tag")
    list_filter = ("tag",)
    search_fields = ("question__title", "tag__name")
    raw_id_fields = ("question", "tag")
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("question", "tag")
    
    
@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "question__title")
    raw_id_fields = ("user", "question")
    readonly_fields = ("created_at",)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "question")
    
    
@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "answer", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "answer__text")
    raw_id_fields = ("user", "answer")
    readonly_fields = ("created_at",)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "answer")