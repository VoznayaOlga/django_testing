import pytest
from django.conf import settings
from django.urls import reverse
from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client):
    """Количество новостей на главной странице — не более 10"""
    # Загружаем главную страницу.
    url = reverse("news:home")
    response = client.get(url)
    # Код ответа не проверяем, его уже проверили в тестах маршрутов.
    # Получаем список объектов из словаря контекста.
    object_list = response.context['object_list']
    # Определяем количество записей в списке.
    news_count = object_list.count()
    # Проверяем, что на странице именно 10 новостей
    assert news_count <= settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    """Новости отсортированы от самой свежей к самой старой.

    Свежие новости в начале списка.
    """
    url = reverse("news:home")
    response = client.get(url)
    object_list = response.context['object_list']
    # Получаем даты новостей в том порядке, как они выведены на странице.
    all_dates = [news.date for news in object_list]
    # Сортируем полученный список по убыванию.
    sorted_dates = sorted(all_dates, reverse=True)
    # Проверяем, что исходный список был отсортирован правильно.
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news):
    """Комментарии на странице отдельной новости.

    Отсортированы в хронологическом порядке:
    старые в начале списка, новые — в конце.
    """
    pytest.lazy_fixture('comments_for_news')
    url = reverse("news:detail", args=(news.id,))
    response = client.get(url)
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


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news):
    """Анонимному пользователю недоступна форма.

    для отправки комментария на странице отдельной новости
    """
    url = reverse("news:detail", args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, news):
    """Авторизованному пользователю доступна форма.

    для отправки комментария на странице отдельной новости
    """
    url = reverse("news:detail", args=(news.id,))
    response = author_client.get(url)
    # Проверим, что объект формы соответствует нужному классу формы.
    assert isinstance(response.context['form'], CommentForm)
