import pytest

from django.urls import reverse
from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

COMMENT_TEXT = 'Текст комментария'


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse("news:detail", args=(news.id,))
    form_data = {'text': COMMENT_TEXT}
    # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
    # предварительно подготовленные данные формы с текстом комментария.
    client.get(url, form_data)
    # Считаем количество комментариев.
    comments_count = Comment.objects.count()
    # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
    assert comments_count == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client', (pytest.lazy_fixture('author_client'),)
)
def test_user_can_create_comment(author, parametrized_client, news):
    """Авторизованный пользователь может отправить комментарий."""
    # Совершаем запрос через авторизованный клиент.
    url = reverse("news:detail", args=(news.id,))
    form_data = {'text': COMMENT_TEXT}
    response = parametrized_client.post(url, data=form_data)
    # Проверяем, что редирект привёл к разделу с комментами.
    assertRedirects(response, f'{url}#comments')
    # Считаем количество комментариев.
    comments_count = Comment.objects.count()
    # Убеждаемся, что есть один комментарий.
    assert comments_count == 1
    # Получаем объект комментария из базы.
    comment = Comment.objects.get()
    # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(news, author_client):
    """Если комментарий содержит запрещённые слова.

    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse("news:detail", args=(news.id,))
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    response = author_client.post(url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING)
    # Дополнительно убедимся, что комментарий не был создан.
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(news, author, comment, author_client):
    """Авторизованный пользователь может удалять свои комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    news_url = reverse('news:detail', args=(news.id,))  # Адрес новости.
    url_to_comments = news_url + '#comments'  # Адрес блока с комментариями.
    # От имени автора комментария отправляем DELETE-запрос на удаление.
    response = author_client.delete(delete_url)
    # Проверяем, что редирект привёл к разделу с комментариями.
    # Заодно проверим статус-коды ответов.
    assertRedirects(response, url_to_comments)
    # Считаем количество комментариев в системе.
    comments_count = Comment.objects.count()
    # Ожидаем ноль комментариев в системе.
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(news, comment,
                                                  not_author_client):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    # Выполняем запрос на удаление от пользователя-читателя.
    response = not_author_client.delete(delete_url)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Убедимся, что комментарий по-прежнему на месте.
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(author, comment, author_client):
    """Авторизованный пользователь может редактировать свои комментарии."""
    old_comment = comment.text
    new_comment = old_comment + ' отредактированный'
    form_data = {'text': new_comment}
    edit_url = reverse('news:edit', args=(comment.id,))
    author_client.post(edit_url, form_data)
    comments_count = Comment.objects.count()
    # Ожидаем ноль комментариев в системе.
    comment.refresh_from_db()
    assert comment.text == new_comment
    assert comments_count == 1


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(author, comment,
                                                not_author_client):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    old_comment = comment.text
    new_comment = old_comment + ' отредактированный'
    form_data = {'text': new_comment}
    edit_url = reverse('news:edit', args=(comment.id,))
    not_author_client.post(edit_url, form_data)
    comments_count = Comment.objects.count()
    # Ожидаем ноль комментариев в системе.
    comment.refresh_from_db()
    assert comment.text == old_comment
    assert comments_count == 1
