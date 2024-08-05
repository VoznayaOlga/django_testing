# conftest.py
import pytest

# Импортируем класс клиента.
from django.test.client import Client
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import News, Comment


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):  # Вызываем фикстуру автора.
    # Создаём новый экземпляр клиента, чтобы не менять глобальный.
    client = Client()
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)  # Логиним обычного пользователя в клиенте.
    return client


@pytest.fixture
def news():
    news = News.objects.create(  # Создаём объект новости.
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(  # Создаём объект комментария к новости.
        news=news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
# Фикстура запрашивает другую фикстуру
def id_for_args(comment):
    return (comment.id,)


@pytest.fixture
# Фикстура запрашивает другую фикстуру
def news_id_for_args(news):
    return (news.id,)


@pytest.fixture
def news_page():
    news_list = []
    today = datetime.today()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news_ = News.objects.create(
            title=f'Новость {index}', text='Просто текст.',
            date=today - timedelta(days=index)
        )
        news_list.append(news_)
    return news_list


@pytest.fixture
def comments_for_news(news):
    comment_list = []
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news, author, text=f'Tекст {index}',)
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()
        comment_list.append(comment)
    return comment_list
