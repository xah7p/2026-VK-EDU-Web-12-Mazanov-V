from pathlib import Path

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from core.models import Profile

User = get_user_model()


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter your login", "autocomplete": "username"}
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        )


class SignUpForm(forms.Form):
    username = forms.CharField(
        label="Логин",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Логин"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "email@example.com"}
        ),
    )
    first_name = forms.CharField(
        label="Имя",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя"}),
    )
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Пароль", "autocomplete": "new-password"}
        ),
    )
    password2 = forms.CharField(
        label="Повтор пароля",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Повторите пароль",
                "autocomplete": "new-password",
            }
        ),
    )

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким логином уже существует.")
        return username

    def clean_password1(self):
        password = self.cleaned_data["password1"]
        user = User(
            username=self.cleaned_data.get("username") or "",
            email=self.cleaned_data.get("email") or "",
            first_name=self.cleaned_data.get("first_name") or "",
        )
        validate_password(password, user)
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise ValidationError("Пароли не совпадают.")
        return cleaned

    @transaction.atomic
    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["first_name"],
        )
        Profile.objects.create(user=user, nickname="")
        return user


_AVATAR_CT_EXT = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


class ProfileEditForm(forms.Form):
    username = forms.CharField(
        label="Логин",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Необязательно",
            }
        ),
    )
    nickname = forms.CharField(
        label="Никнейм",
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    avatar = forms.ImageField(
        label="Аватар",
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "form-control",
                "accept": "image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp",
            }
        ),
    )

    AVATAR_MAX_BYTES = 2 * 1024 * 1024
    AVATAR_ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp"}

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if not avatar or avatar is False:
            return avatar
        ext = Path(avatar.name).suffix.lower()
        if not ext and getattr(avatar, "content_type", None):
            ext = _AVATAR_CT_EXT.get(avatar.content_type, "")
        if ext not in self.AVATAR_ALLOWED_EXT:
            raise ValidationError(
                "Допустимые форматы: JPEG, PNG, WebP."
            )
        if avatar.size > self.AVATAR_MAX_BYTES:
            raise ValidationError(
                "Размер файла не должен превышать 2 МБ."
            )
        return avatar

    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.profile, _ = Profile.objects.get_or_create(user=user)
        kwargs.setdefault(
            "initial",
            {
                "username": user.username,
                "email": user.email or "",
                "nickname": self.profile.nickname or "",
            },
        )
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            raise ValidationError("Укажите логин.")
        if (
            User.objects.exclude(pk=self.user.pk)
            .filter(username=username)
            .exists()
        ):
            raise ValidationError("Этот логин уже занят.")
        return username

    def clean_email(self):
        raw = self.cleaned_data.get("email")
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            return ""
        return raw.strip()

    @transaction.atomic
    def save(self):
        self.user.username = self.cleaned_data["username"]
        self.user.email = (self.cleaned_data.get("email") or "").strip()
        self.user.save()
        self.profile.nickname = self.cleaned_data.get("nickname") or ""
        avatar = self.cleaned_data.get("avatar")
        if avatar is False:
            if self.profile.avatar:
                self.profile.avatar.delete(save=False)
            self.profile.avatar = None
        elif avatar:
            if self.profile.avatar:
                self.profile.avatar.delete(save=False)
            self.profile.avatar = avatar
        self.profile.save()
        return self.user
