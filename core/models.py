import uuid
from pathlib import Path

from django.db import models


def avatar_upload_path(instance, filename):
    ext = Path(filename).suffix.lower()
    if ext not in (".jpg", ".jpeg", ".png", ".webp"):
        ext = ".img"
    return f"avatars/{uuid.uuid4().hex}{ext}"


class Profile(models.Model):
    user = models.OneToOneField(
        "auth.User",
        verbose_name ="Пользователь",
        on_delete=models.CASCADE,
        related_name="profile",
    )
    nickname = models.CharField(verbose_name="Никнейм", max_length=255, blank=True)
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
    )
    
    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"
    
    def __str__(self):
        return f"Профиль пользователя #{self.user_id}"
    
