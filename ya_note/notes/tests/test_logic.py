from pytils.translit import slugify
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreate(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Ганс Христиан Андерсен')
        cls.reader = User.objects.create(username='Читатель простой')
        # Создаем заметку от имени этого пользователя
        cls.form_data = {'text': 'Текст', 'title': 'Заголовок', 'slug': 'Slug',
                         'author': cls.author}

    def test_empty_slug(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        # Убираем поле slug из словаря:
        self.form_data.pop('slug')
        response = self.client.post(url, data=self.form_data)
        # Проверяем, что даже без slug заметка была создана:
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        # Получаем созданную заметку из базы:
        new_note = Note.objects.get()
        # Формируем ожидаемый slug:
        expected_slug = slugify(self.form_data['title'])
        # Проверяем, что slug заметки соответствует ожидаемому:
        self.assertEqual(new_note.slug, expected_slug)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(url, self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)

    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        redirect_url = reverse('notes:success')
        response = self.client.post(url, data=self.form_data)
        self.assertRedirects(response, redirect_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()
        # Сверяем атрибуты объекта с ожидаемыми.
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.form_data['author'])


class TestNote(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Ганс Христиан Андерсен')
        cls.reader = User.objects.create(username='Читатель простой')
        # Создаем заметку от имени этого пользователя
        cls.form_data = {'text': 'Текст', 'title': 'Заголовок', 'slug': 'Slug',
                         'author': cls.author}
        cls.note = Note.objects.create(title=cls.form_data['title'],
                                       text=cls.form_data['text'],
                                       slug=cls.form_data['slug'],
                                       author=cls.form_data['author'])

    def test_not_unique_slug(self):
        url = reverse('notes:add')
        # Подменяем slug новой заметки на slug уже существующей записи:
        self.form_data['slug'] = self.note.slug
        # Пытаемся создать новую заметку:
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        # Проверяем, что в ответе содержится ошибка формы для поля slug:
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        # Убеждаемся, что количество заметок в базе осталось равным 1:
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        self.client.force_login(self.author)
        # Получаем адрес страницы редактирования7 заметки:
        url = reverse('notes:edit', args=(self.note.slug,))
        # В POST-запросе на адрес редактирования заметки
        # отправляем form_data - новые значения для полей заметки:
        response = self.client.post(url, self.form_data)
        # Проверяем редирект:
        self.assertRedirects(response, reverse('notes:success'))
        # Обновляем объект заметки note: получаем обновлённые данные из БД:
        self.note.refresh_from_db()
        # Проверяем, что атрибуты заметки соответствуют обновлённым:
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        self.client.force_login(self.reader)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, self.form_data)
        # Проверяем, что страница не найдена:
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Получаем новый объект запросом из БД.
        note_from_db = Note.objects.get(id=self.note.id)
        # Проверяем, что атрибуты объекта из БД равны атрибутам
        # заметки до запроса.
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        self.client.force_login(self.author)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        self.client.force_login(self.reader)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
