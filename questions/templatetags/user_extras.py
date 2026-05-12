from django import template
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def avatar_url(user):
    default = static("default_user_avatar.png")
    if not user or isinstance(user, AnonymousUser):
        return default
    try:
        profile = user.profile
    except ObjectDoesNotExist:
        return default
    if profile.avatar:
        return profile.avatar.url
    return default
