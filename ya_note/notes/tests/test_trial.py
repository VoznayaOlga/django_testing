# news/tests/test_trial.py
from django.test import TestCase

from notes.models import Note
from django.contrib.auth import get_user_model

User = get_user_model()


class TestNotes(TestCase):
    # Все нужные переменные сохраняем в атрибуты класса.
    TITLE = 'Заголовок новости'
    TEXT = 'Тестовый текст'

    @classmethod
    def setUpTestData(cls):
        # Создаем автора
        cls.author = User.objects.create(username='Ганс Христиан Андерсен')
        # Создаем заметку от имени автора
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author
        )

    def test_successful_creation(self):
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_title(self):
        # Чтобы проверить равенство с константой -
        # обращаемся к ней через self, а не через cls:
        self.assertEqual(self.note.title, self.TITLE)
