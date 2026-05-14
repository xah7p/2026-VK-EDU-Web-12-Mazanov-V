from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.templatetags.static import static

User = get_user_model()

DEFAULT_AVATAR = static("default_user_avatar.png")


def get_sidebar_context(limit_tags=12, limit_members=5):
    Tag = apps.get_model("questions", "Tag")

    popular_tags = list(
        Tag.objects.annotate(n=Count("questiontag"))
        .order_by("-n", "name")
        .values_list("name", flat=True)[:limit_tags]
    )

    members_qs = (
        User.objects.annotate(ans_count=Count("answers"))
        .filter(ans_count__gt=0)
        .select_related("profile")
        .order_by("-ans_count")[:limit_members]
    )
    best_members = []
    for u in members_qs:
        avatar = DEFAULT_AVATAR
        profile = getattr(u, "profile", None)
        if profile and profile.avatar:
            avatar = profile.avatar.url
        best_members.append({"name": u.username, "avatar": avatar})

    if not best_members:
        for u in User.objects.select_related("profile").order_by("-id")[:limit_members]:
            avatar = DEFAULT_AVATAR
            profile = getattr(u, "profile", None)
            if profile and profile.avatar:
                avatar = profile.avatar.url
            best_members.append({"name": u.username, "avatar": avatar})

    return {
        "popular_tags": popular_tags,
        "best_members": best_members,
    }