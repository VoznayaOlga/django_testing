from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from django.conf import settings
from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём двух пользователей с разными именами:
        cls.author = User.objects.create(username='Ганс Христиан Андерсен')
        cls.reader = User.objects.create(username='Читатель простой')
        # Создаем заметку от имени этого пользователя
        cls.note = Note.objects.create(title='Заголовок', text='Текст',
                                       slug='Prem',
                                       author=cls.author)

    def test_home_page(self):
        # доступность главной страницы для анонимного пользователя
        url = settings.LOGIN_REDIRECT_URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_done_and_add(self):
        # Аутентифицированному пользователю доступна страница со списком
        # заметок notes/, страница успешного добавления заметки done/,
        # страница добавления новой заметки add/.
        # Логиним пользователя в клиенте:
        self.client.force_login(self.reader)
        # Для каждой пары "пользователь - ожидаемый ответ"
        # перебираем имена тестируемых страниц:
        for name in ('notes:list', 'notes:success', 'notes:add'):
            with self.subTest(user=self.reader, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(str(self.note.slug),))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    # @unittest.skip('Редирект отключен')
    def test_redirect_for_anonymous_client(self):
        # При попытке перейти на страницу списка заметок,
        # страницу успешного добавления записи,
        # страницу добавления заметки, отдельной заметки,
        # редактирования или удаления заметки анонимный пользователь
        # перенаправляется на страницу логина
        # Сохраняем адрес страницы логина:
        login_url = settings.LOGIN_URL
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        pages = (
            ('notes:list', None),
            ('notes:delete', (str(self.note.slug),),),
            ('notes:edit', (str(self.note.slug),),),
            ('notes:add', None),
            ('notes:success', None),)
        for name, param in pages:
            with self.subTest(name=name):
                # Получаем адрес страницы
                url = reverse(name, args=param)
                # Получаем ожидаемый адрес страницы логина,
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором
                # передаётся адрес страницы, с которой пользователь
                # был переадресован.
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)
