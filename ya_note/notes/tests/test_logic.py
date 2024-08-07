from http import HTTPStatus

from pytils.translit import slugify
from django.conf import settings

from notes.forms import WARNING
from notes.models import Note
from notes.tests.conftest import (TestNoteBaseClass,
                                  TestNoteBaseClassWithCreation,
                                  NOTES_ADD_URL, NOTES_EDIT_URL,
                                  NOTES_DELETE_URL,
                                  NOTES_SUCCESS_URL)


class TestNoteCreate(TestNoteBaseClass):

    def test_empty_slug(self):
        Note.objects.all().delete()
        self.form_data.pop('slug')
        response = self.author_client.post(NOTES_ADD_URL, data=self.form_data)
        # Проверяем, что даже без slug заметка была создана:
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        # Получаем созданную заметку из базы:
        new_note = Note.objects.get()
        # Формируем ожидаемый slug:
        expected_slug = slugify(self.form_data['title'])
        # Проверяем, что slug заметки соответствует ожидаемому:
        self.assertEqual(new_note.slug, expected_slug)

    def test_anonymous_user_cant_create_note(self):
        excepted_notes_count = Note.objects.count()
        response = self.client.post(NOTES_ADD_URL, self.form_data)
        expected_url = f'{settings.LOGIN_URL}?next={NOTES_ADD_URL}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), excepted_notes_count)

    def test_user_can_create_note(self):
        Note.objects.all().delete()
        response = self.author_client.post(NOTES_ADD_URL, data=self.form_data)
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        # Сверяем атрибуты объекта с ожидаемыми.
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, response.wsgi_request.user)


class TestNote(TestNoteBaseClassWithCreation):

    def test_not_unique_slug(self):
        excepted_notes_count = Note.objects.count()
        # Подменяем slug новой заметки на slug уже существующей записи:
        self.form_data['slug'] = self.note.slug
        # Пытаемся создать новую заметку:
        response = self.author_client.post(NOTES_ADD_URL, data=self.form_data)
        # Проверяем, что в ответе содержится ошибка формы для поля slug:
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        # Убеждаемся, что количество заметок в базе осталось равным 1:
        self.assertEqual(Note.objects.count(), excepted_notes_count)

    def test_author_can_edit_note(self):
        # В POST-запросе на адрес редактирования заметки
        # отправляем form_data - новые значения для полей заметки:
        response = self.author_client.post(NOTES_EDIT_URL, self.form_data)
        # Проверяем редирект:
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        # Обновляем объект заметки note: получаем обновлённые данные из БД:
        edit_note = Note.objects.get(id=self.note.id)
        # Проверяем, что атрибуты заметки соответствуют обновлённым:
        self.assertEqual(edit_note.title, self.form_data['title'])
        self.assertEqual(edit_note.text, self.form_data['text'])
        self.assertEqual(edit_note.slug, self.form_data['slug'])
        self.assertEqual(edit_note.author, self.note.author)

    def test_other_user_cant_edit_note(self):
        response = self.reader_client.post(NOTES_EDIT_URL, self.form_data)
        # Проверяем, что страница не найдена:
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Получаем новый объект запросом из БД.
        note_from_db = Note.objects.get(id=self.note.id)
        # Проверяем, что атрибуты объекта из БД равны атрибутам
        # заметки до запроса.
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, note_from_db.author)

    def test_author_can_delete_note(self):
        excepted_notes_count = Note.objects.count() - 1
        response = self.author_client.post(NOTES_DELETE_URL)
        self.assertRedirects(response, NOTES_SUCCESS_URL)
        self.assertEqual(Note.objects.count(), excepted_notes_count)

    def test_other_user_cant_delete_note(self):
        excepted_notes_count = Note.objects.count()
        response = self.reader_client.post(NOTES_DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), excepted_notes_count)
