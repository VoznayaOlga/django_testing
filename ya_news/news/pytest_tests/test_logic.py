from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(client, news, comment_form_data):
    """Анонимный пользователь не может отправить комментарий."""
    url = reverse("news:detail", args=(news.id,))
    # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
    # предварительно подготовленные данные формы с текстом комментария.
    client.get(url, comment_form_data)
    # Считаем количество комментариев.
    # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author, author_client, news,
                                 comment_form_data):
    """Авторизованный пользователь может отправить комментарий."""
    # Совершаем запрос через авторизованный клиент.
    url = reverse("news:detail", args=(news.id,))
    response = author_client.post(url, data=comment_form_data)
    # Проверяем, что редирект привёл к разделу с комментами.
    assertRedirects(response, f'{url}#comments')
    # Считаем количество комментариев.
    # Убеждаемся, что есть один комментарий.
    assert Comment.objects.count() == 1
    # Получаем объект комментария из базы.
    comment = Comment.objects.get()
    # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
    assert comment.text == comment_form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(news, author_client,
                                 comment_bad_words_form_data):
    """Если комментарий содержит запрещённые слова.

    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse("news:detail", args=(news.id,))
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    # Отправляем запрос через авторизованный клиент.
    response = author_client.post(url, data=comment_bad_words_form_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING)
    # Дополнительно убедимся, что комментарий не был создан.
    assert Comment.objects.count() == 0


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
    # Ожидаем ноль комментариев в системе.
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(news, comment,
                                                  not_author_client):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    delete_url = reverse('news:delete', args=(comment.id,))
    # Выполняем запрос на удаление от пользователя-читателя.
    response = not_author_client.delete(delete_url)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Убедимся, что комментарий по-прежнему на месте.
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author, comment, author_client,
                                 comment_form_data):
    """Авторизованный пользователь может редактировать свои комментарии."""
    old_comment = comment.text
    new_comment = old_comment + ' отредактированный'
    comment_form_data['text'] = new_comment
    edit_url = reverse('news:edit', args=(comment.id,))
    author_client.post(edit_url, comment_form_data)
    # Ожидаем ноль комментариев в системе.
    assert Comment.objects.count() == 1
    # Получаем единственные коммент в системе, можно было и без pk
    edit_comment = Comment.objects.get(pk=comment.id)
    assert edit_comment.text == new_comment
    assert edit_comment.author == comment.author
    assert edit_comment.news == comment.news
    assert edit_comment.created == comment.created


def test_user_cant_edit_comment_of_another_user(author, comment,
                                                not_author_client,
                                                comment_form_data):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    comment_form_data['text'] = comment.text + ' отредактированный'
    edit_url = reverse('news:edit', args=(comment.id,))
    not_author_client.post(edit_url, comment_form_data)
    # Ожидаем ноль комментариев в системе.
    assert Comment.objects.count() == 1
    # Получаем единственные коммент в системе, можно было и без pk
    edit_comment = Comment.objects.get(pk=comment.id)
    assert edit_comment.text == comment.text
    assert edit_comment.author == comment.author
    assert edit_comment.news == comment.news
    assert edit_comment.created == comment.created
