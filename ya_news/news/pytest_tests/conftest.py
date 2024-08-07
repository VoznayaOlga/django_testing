from datetime import datetime, timedelta

# Импортируем класс клиента.
import pytest
from django.test.client import Client
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

# Импортируем модель заметки, чтобы создать экземпляр.
from news.forms import BAD_WORDS
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
    return News.objects.create(  # Создаём объект новости.
        title='Заголовок',
        text='Текст заметки',
    )


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


@pytest.fixture
def comments_for_news(news, author):
    comment_list = []
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',)
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()
        comment_list.append(comment)


@pytest.fixture(autouse=True)
def connect_db(db):
    return True


@pytest.fixture
def comment_form_data():
    return {'text': 'Текст комментария'}


@pytest.fixture
def comment_bad_words_form_data():
    return {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


@pytest.fixture
def news_detail_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def news_delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def news_edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def news_home_url():
    return reverse('news:home')


@pytest.fixture
def edited_comment(comment):
    return {'comment_text': comment.text,
            'comment_edited_text': comment.text + ' отредактированный'}


@pytest.fixture
def users_login():
    return reverse('users:login')


@pytest.fixture
def users_logout():
    return reverse('users:logout')


@pytest.fixture
def users_signup():
    return reverse('users:signup')
