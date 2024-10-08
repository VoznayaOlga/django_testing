from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

NEWS_DELETE_URL = pytest.lazy_fixture('news_edit_url')
NEWS_DETAIL_URL = pytest.lazy_fixture('news_detail_url')
NEWS_EDIT_URL = pytest.lazy_fixture('news_edit_url')
NEWS_HOME_URL = pytest.lazy_fixture('news_home_url')
USERS_LOGIN_URL = pytest.lazy_fixture('users_logout')
USERS_LOGOUT_URL = pytest.lazy_fixture('users_logout')
USERS_SIGNUP_URL = pytest.lazy_fixture('users_signup')


@pytest.mark.parametrize(
    'url',
    # Значения, которые будут передаваться в name.
    (
        NEWS_HOME_URL,
        USERS_LOGIN_URL,
        USERS_LOGOUT_URL,
        USERS_SIGNUP_URL,
        NEWS_DETAIL_URL,
    )
)
# Указываем в фикстурах встроенный клиент.
# Проверяем доступность страниц для анонимного пользователя
def test_pages_availability_for_anonymous_user(client, news, comment, url):
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    # parametrized_client - название параметра,
    # в который будут передаваться фикстуры;
    # Параметр expected_status - ожидаемый статус ответа.
    'parametrized_client, expected_status',
    # В кортеже с кортежами передаём значения для параметров:
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'url',
    (NEWS_EDIT_URL,
     NEWS_DELETE_URL),
)
# В параметры теста добавляем имена parametrized_client и expected_status.
# Проверяем доступность редактирования и удаления для автора и не автора
def test_pages_availability_for_different_users(
        parametrized_client, comment, expected_status, url
):
    # Делаем запрос от имени клиента parametrized_client:
    response = parametrized_client.get(url)
    # Ожидаем ответ страницы, указанный в expected_status:
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (NEWS_EDIT_URL,
     NEWS_DELETE_URL),
)
# Передаём в тест анонимный клиент, name проверяемых страниц
def test_redirect_for_anonymous_client(client, url, users_login):
    # Формируем URL в зависимости от того, передан ли объект комментария:
    expected_url = f'{users_login}?next={url}'
    response = client.get(url)
    # Ожидаем, что со всех проверяемых страниц анонимный клиент
    # будет перенаправлен на страницу логина:
    assertRedirects(response, expected_url)
