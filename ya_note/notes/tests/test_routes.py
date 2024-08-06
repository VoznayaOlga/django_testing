from http import HTTPStatus

from django.conf import settings

from notes.tests.conftest import (TestNoteBaseClassWithCreation,
                                  NOTES_ADD_URL,
                                  NOTES_DELETE_URL,
                                  NOTES_EDIT_URL,
                                  NOTES_LIST_URL,
                                  NOTES_SUCCESS_URL
                                  )


class TestRoutes(TestNoteBaseClassWithCreation):

    def test_home_page(self):
        # доступность главной страницы для анонимного пользователя
        url = settings.LOGIN_REDIRECT_URL
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_authorized_user(self):
        users_statuses = (
            (NOTES_LIST_URL, self.reader_client, HTTPStatus.OK),
            (NOTES_SUCCESS_URL, self.reader_client, HTTPStatus.OK),
            (NOTES_ADD_URL, self.reader_client, HTTPStatus.OK),
            (NOTES_EDIT_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (NOTES_DELETE_URL, self.reader_client, HTTPStatus.NOT_FOUND),
            (NOTES_EDIT_URL, self.author_client, HTTPStatus.OK),
            (NOTES_DELETE_URL, self.author_client, HTTPStatus.OK),
        )
        for url, user_client, status in users_statuses:
            with self.subTest(url=url, user_client=user_client, status=status):
                response = user_client.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        # При попытке перейти на страницу списка заметок,
        # страницу успешного добавления записи,
        # страницу добавления заметки, отдельной заметки,
        # редактирования или удаления заметки анонимный пользователь
        # перенаправляется на страницу логина
        # Сохраняем адрес страницы логина:
        login_url = settings.LOGIN_URL
        # В цикле перебираем имена страниц, с которых ожидаем редирект:
        urls = [NOTES_LIST_URL, NOTES_ADD_URL, NOTES_EDIT_URL,
                NOTES_ADD_URL, NOTES_SUCCESS_URL]
        for url in urls:
            with self.subTest(url=url):
                # Получаем ожидаемый адрес страницы логина,
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором
                # передаётся адрес страницы, с которой пользователь
                # был переадресован.
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)
