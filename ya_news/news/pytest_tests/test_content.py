# import pytest
from django.conf import settings

from news.forms import CommentForm


def test_news_count(client, news_page, news_home_url):
    """Количество новостей на главной странице — не более 10"""
    # Загружаем главную страницу.
    response = client.get(news_home_url)
    # Код ответа не проверяем, его уже проверили в тестах маршрутов.
    # Получаем список объектов из словаря контекста.
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    # Определяем количество записей в списке.
    # Проверяем, что на странице именно 10 новостей
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, news_page, news_home_url):
    """Новости отсортированы от самой свежей к самой старой.

    Свежие новости в начале списка.
    """
    response = client.get(news_home_url)
    assert 'object_list' in response.context
    object_list = response.context['object_list']
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted_dates


def test_comments_order(client, news, comments_for_news, news_detail_url):
    """Комментарии на странице отдельной новости.

    Отсортированы в хронологическом порядке:
    старые в начале списка, новые — в конце.
    """
    response = client.get(news_detail_url)
    # Проверяем, что объект новости находится в словаре контекста
    # под ожидаемым именем - названием модели.
    assert 'news' in response.context
    # Получаем объект новости.
    news = response.context['news']
    # Получаем все комментарии к новости.
    all_comments = news.comment_set.all()
    # Собираем временные метки всех комментариев
    all_timestamps = [comment.created for comment in all_comments]
    # Сортируем временные метки
    sorted_timestamps = sorted(all_timestamps)
    # Проверяем, что временные метки отсортированы правильно
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(client, news, news_detail_url):
    """Анонимному пользователю недоступна форма.

    для отправки комментария на странице отдельной новости
    """
    response = client.get(news_detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(author_client, news, news_detail_url):
    """Авторизованному пользователю доступна форма
    для отправки комментария на странице отдельной новости
    """
    response = author_client.get(news_detail_url)
    assert 'form' in response.context
    # Проверим, что объект формы соответствует нужному классу формы.
    assert isinstance(response.context['form'], CommentForm)
