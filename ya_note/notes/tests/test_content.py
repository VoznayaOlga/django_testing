from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNoteList(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Ганс Христиан Андерсен')
        cls.reader = User.objects.create(username='Читатель простой')
        # Создаем заметку от имени этого пользователя
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       slug='Prem',
                                       author=cls.author)

    def test_note_in_list_for_author(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_in_list_for_not_author(self):
        self.client.force_login(self.reader)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_pages_contains_form(self):
        self.client.force_login(self.author)
        pages = (
            ('notes:edit', (str(self.note.slug),),),
            ('notes:add', None),)
        for name, param in pages:
            with self.subTest(name=name):
                # Получаем адрес страницы
                url = reverse(name, args=param)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
