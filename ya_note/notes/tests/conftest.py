from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()

DEFAULT_SLAG = 'Default_Slug'
NOTES_LIST_URL = reverse('notes:list')
NOTES_ADD_URL = reverse('notes:add')
NOTES_EDIT_URL = reverse('notes:edit', args=(DEFAULT_SLAG,))
NOTES_DETAIL_URL = reverse('notes:detail', args=(DEFAULT_SLAG,))
NOTES_DELETE_URL = reverse('notes:delete', args=(DEFAULT_SLAG,))
NOTES_SUCCESS_URL = reverse('notes:success')


class TestNoteBaseClass(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Ганс Христиан Андерсен')
        cls.reader = User.objects.create(username='Читатель простой')
        # Создаем заметку от имени этого пользователя
        cls.form_data = {'text': 'Текст', 'title': 'Заголовок',
                         'slug': DEFAULT_SLAG}
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)


class TestNoteBaseClassWithCreation(TestNoteBaseClass):
    @classmethod
    def setUpTestData(cls):
        super(TestNoteBaseClassWithCreation, cls).setUpTestData()
        cls.note = Note.objects.create(title='Заголовок новости', text='Текст',
                                       slug=DEFAULT_SLAG,
                                       author=cls.author)
