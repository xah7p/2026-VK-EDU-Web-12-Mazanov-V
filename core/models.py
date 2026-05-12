from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(
        "auth.User",
        verbose_name ="Пользователь",
        on_delete=models.CASCADE,
        related_name="profile",
    )
    nickname = models.CharField(verbose_name="Никнейм", max_length=255, blank=True)
    avatar = models.ImageField(verbose_name="Аватар", upload_to="avatars/", blank=True, null=True)
    
    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"
    
    def __str__(self):
        return f"Профиль пользователя #{self.user_id}"
    
