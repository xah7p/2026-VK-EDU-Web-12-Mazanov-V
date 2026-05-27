from collections import defaultdict
from datetime import timedelta

from django.core.cache import cache
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.templatetags.static import static
from django.utils import timezone

POPULAR_TAGS_DAYS = 90  
BEST_MEMBERS_DAYS = 7
CACHE_TIMEOUT_SECONDS = 60 * 60 

User = get_user_model()

DEFAULT_AVATAR = static("default_user_avatar.png")


def get_sidebar_context(limit_tags=10, limit_members=10):
    popular_tags_key = _popular_tags_cache_key(limit_tags)
    best_members_key = _best_members_cache_key(limit_members)
    
    popular_tags = cache.get(popular_tags_key)
    if popular_tags is None:
        popular_tags = _compute_popular_tags(limit_tags)
        cache.set(popular_tags_key, popular_tags, timeout=CACHE_TIMEOUT_SECONDS)
    
    best_members = cache.get(best_members_key)
    if best_members is None:
        best_members = _compute_best_members(limit_members)
        cache.set(best_members_key, best_members, timeout=CACHE_TIMEOUT_SECONDS)
    
    return {
        "popular_tags": popular_tags,
        "best_members": best_members,
    }

def _popular_tags_cache_key(limit_tags):
    return f"sidebar:popular_tags:v1:days{POPULAR_TAGS_DAYS}:top{limit_tags}"

def _best_members_cache_key(limit_members):
    return f"sidebar:best_members:v1:days{BEST_MEMBERS_DAYS}:top{limit_members}" 

def _compute_popular_tags(limit_tags):
    QuestionTag = apps.get_model("questions", "QuestionTag")
    threshold = timezone.now() - timedelta(days=POPULAR_TAGS_DAYS)
    
    qs = (
        QuestionTag.objects.filter(question__created_at__gte=threshold)
        .values("tag__name")
        .annotate(n=Count("question_id"))
        .order_by("-n", "tag__name")
        .values_list("tag__name", flat=True)[:limit_tags]
    )
    return list(qs)

def _compute_best_members(limit_members: int) -> list[dict]:
    User = get_user_model()
    QuestionLike = apps.get_model("questions", "QuestionLike")
    AnswerLike = apps.get_model("questions", "AnswerLike")
    threshold = timezone.now() - timedelta(days=BEST_MEMBERS_DAYS)
    scores = defaultdict(int)
    q_scores = (
        QuestionLike.objects.filter(
            question__created_at__gte=threshold,
            question__author_id__isnull=False,
        )
        .values("question__author_id")
        .annotate(score=Sum("value"))
    )
    for row in q_scores:
        scores[row["question__author_id"]] += int(row["score"] or 0)
    a_scores = (
        AnswerLike.objects.filter(
            answer__created_at__gte=threshold,
            answer__author_id__isnull=False,
        )
        .values("answer__author_id")
        .annotate(score=Sum("value"))
    )
    for row in a_scores:
        scores[row["answer__author_id"]] += int(row["score"] or 0)
    top_user_ids = sorted(scores.keys(), key=lambda uid: scores[uid], reverse=True)[
        :limit_members
    ]
    if not top_user_ids:
        members_qs = (
            User.objects.filter(answers__created_at__gte=threshold)
            .annotate(ans_count=Count("answers"))
            .filter(ans_count__gt=0)
            .select_related("profile")
            .order_by("-ans_count", "-id")[:limit_members]
        )
        result = []
        for u in members_qs:
            avatar = DEFAULT_AVATAR
            profile = getattr(u, "profile", None)
            if profile and profile.avatar:
                avatar = profile.avatar.url
            result.append({"name": u.username, "avatar": avatar})
        return result
    users_by_id = {
        u.id: u
        for u in User.objects.filter(id__in=top_user_ids).select_related("profile")
    }
    result = []
    for uid in top_user_ids:
        u = users_by_id.get(uid)
        if not u:
            continue
        avatar = DEFAULT_AVATAR
        profile = getattr(u, "profile", None)
        if profile and profile.avatar:
            avatar = profile.avatar.url
        result.append({"name": u.username, "avatar": avatar})
    return result