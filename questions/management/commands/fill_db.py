import itertools
import random

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from core.models import Profile
from questions.models import (
    Answer,
    AnswerLike,
    Question,
    QuestionLike,
    QuestionTag,
    Tag,
)


BATCH = 5000


def batched_bulk_create(model, objects, batch_size=BATCH):
    for i in range(0, len(objects), batch_size):
        chunk = objects[i : i + batch_size]
        model.objects.bulk_create(chunk, batch_size=batch_size)


def unique_user_entity_pairs(user_ids, entity_ids, target):
    if not user_ids or not entity_ids or target <= 0:
        return []

    max_pairs = len(user_ids) * len(entity_ids)
    need = min(target, max_pairs)

    if need == max_pairs:
        return list(itertools.product(user_ids, entity_ids))

    if max_pairs <= 2_000_000:
        all_pairs = list(itertools.product(user_ids, entity_ids))
        random.shuffle(all_pairs)
        return all_pairs[:need]

    pairs = set()
    while len(pairs) < need:
        pairs.add(
            (random.choice(user_ids), random.choice(entity_ids)),
        )
    return list(pairs)


class Command(BaseCommand):
    help = "Заполняет БД тестовыми данными: fill_db <ratio>"

    def add_arguments(self, parser):
        parser.add_argument(
            "ratio",
            type=int,
            help="Коэффициент наполнения",
        )

    def handle(self, *args, **options):
        ratio = options["ratio"]
        if ratio < 1:
            self.stderr.write("ratio должен быть >= 1")
            return

        n_users = ratio
        n_questions = ratio * 10
        n_answers = ratio * 100
        n_tags = ratio
        n_likes_total = ratio * 200
        n_q_likes = n_likes_total // 2
        n_a_likes = n_likes_total - n_q_likes

        fake = Faker()
        Faker.seed(0)
        random.seed(0)
        pwd = make_password("password123")

        self.stdout.write("Пользователи…")
        users = [
            User(
                username=f"user_{i}",
                email=f"user_{i}@example.test",
                password=pwd,
            )
            for i in range(n_users)
        ]
        batched_bulk_create(User, users)
        user_ids = list(
            User.objects.order_by("id").values_list("id", flat=True)
        )

        self.stdout.write("Профили…")
        profiles = [
            Profile(
                user_id=uid,
                nickname=(fake.first_name()[:32] or str(uid)),
            )
            for uid in user_ids
        ]
        batched_bulk_create(Profile, profiles)

        self.stdout.write("Теги…")
        tags = [Tag(name=f"tag_{i}") for i in range(n_tags)]
        batched_bulk_create(Tag, tags)
        tag_ids = list(
            Tag.objects.order_by("id").values_list("id", flat=True)
        )

        self.stdout.write("Вопросы…")
        questions = [
            Question(
                title=fake.sentence(nb_words=4)[:120],
                text=fake.text(max_nb_chars=320),
                author_id=random.choice(user_ids),
            )
            for _ in range(n_questions)
        ]
        batched_bulk_create(Question, questions)
        question_ids = list(
            Question.objects.order_by("id").values_list("id", flat=True)
        )

        self.stdout.write("Связи вопрос–тег…")
        qtags = []
        k_tags = min(3, len(tag_ids))
        for qid in question_ids:
            for tid in random.sample(tag_ids, k=k_tags):
                qtags.append(QuestionTag(question_id=qid, tag_id=tid))
        batched_bulk_create(QuestionTag, qtags)

        self.stdout.write("Ответы…")
        answers = [
            Answer(
                question_id=random.choice(question_ids),
                author_id=random.choice(user_ids),
                text=fake.text(max_nb_chars=220),
            )
            for _ in range(n_answers)
        ]
        batched_bulk_create(Answer, answers)
        answer_ids = list(
            Answer.objects.order_by("id").values_list("id", flat=True)
        )

        now = timezone.now()

        self.stdout.write("Лайки вопросов…")
        pairs_q = unique_user_entity_pairs(user_ids, question_ids, n_q_likes)
        if len(pairs_q) < n_q_likes:
            self.stdout.write(
                self.style.WARNING(
                    f"Лайков вопросов: запрошено {n_q_likes}, создано "
                    f"{len(pairs_q)} (максимум уникальных пар для этих "
                    f"пользователей и вопросов)."
                )
            )
        q_likes = [
            QuestionLike(user_id=u, question_id=q, created_at=now)
            for u, q in pairs_q
        ]
        batched_bulk_create(QuestionLike, q_likes)

        self.stdout.write("Лайки ответов…")
        pairs_a = unique_user_entity_pairs(user_ids, answer_ids, n_a_likes)
        if len(pairs_a) < n_a_likes:
            self.stdout.write(
                self.style.WARNING(
                    f"Лайков ответов: запрошено {n_a_likes}, создано "
                    f"{len(pairs_a)} (максимум уникальных пар)."
                )
            )
        a_likes = [
            AnswerLike(user_id=u, answer_id=a, created_at=now)
            for u, a in pairs_a
        ]
        batched_bulk_create(AnswerLike, a_likes)

        total_likes = len(pairs_q) + len(pairs_a)
        self.stdout.write(
            self.style.SUCCESS(
                f"Готово: users={n_users}, questions={n_questions}, "
                f"answers={n_answers}, tags={n_tags}, likes={total_likes}"
            )
        )
