from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING
from news.models import Comment


def test_anonymous_user_cant_create_comment(client, news, comment_form_data,
                                            news_detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    Comment.objects.all().delete()
    # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
    # предварительно подготовленные данные формы с текстом комментария.
    client.post(news_detail_url, comment_form_data)
    # Считаем количество комментариев.
    # Ожидаем, что комментариев в базе не стало больше, чем было
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author, author_client, news,
                                 comment_form_data,
                                 news_detail_url):
    """Авторизованный пользователь может отправить комментарий."""
    Comment.objects.all().delete()
    # Совершаем запрос через авторизованный клиент.
    response = author_client.post(news_detail_url, data=comment_form_data)
    # Проверяем, что редирект привёл к разделу с комментами.
    assertRedirects(response, f'{news_detail_url}#comments')
    # Считаем количество комментариев.
    # Убеждаемся, что добавлен один комментарий.
    assert Comment.objects.count() == 1
    # Получаем объект комментария из базы.
    comment = Comment.objects.get()
    # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
    assert comment.text == comment_form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(news, author_client,
                                 comment_bad_words_form_data,
                                 news_detail_url):
    """Если комментарий содержит запрещённые слова.

    он не будет опубликован, а форма вернёт ошибку.
    """
    excepted_comment_count = Comment.objects.count()
    # Отправляем запрос через авторизованный клиент.
    response = author_client.post(news_detail_url,
                                  data=comment_bad_words_form_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING)
    # Дополнительно убедимся, что комментарий не был создан.
    assert Comment.objects.count() == excepted_comment_count


def test_author_can_delete_comment(news, author, comment, author_client,
                                   news_delete_url,
                                   news_detail_url):
    """Авторизованный пользователь может удалять свои комментарии."""
    excepted_comment_count = Comment.objects.count() - 1
    # От имени автора комментария отправляем DELETE-запрос на удаление.
    response = author_client.delete(news_delete_url)
    # Проверяем, что редирект привёл к разделу с комментариями.
    assertRedirects(response, news_detail_url + '#comments')
    # Проверяем, что количество комментариев не изменилось.
    assert Comment.objects.count() == excepted_comment_count


def test_user_cant_delete_comment_of_another_user(news, comment,
                                                  not_author_client,
                                                  news_delete_url):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    excepted_comment_count = Comment.objects.count()
    # Выполняем запрос на удаление от пользователя-читателя.
    response = not_author_client.delete(news_delete_url)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Убедимся, что комментарий по-прежнему на месте.
    assert Comment.objects.count() == excepted_comment_count


def test_author_can_edit_comment(author, comment, author_client,
                                 comment_form_data, edited_comment,
                                 news_edit_url):
    """Авторизованный пользователь может редактировать свои комментарии."""
    excepted_comment_count = Comment.objects.count()
    comment_form_data['text'] = edited_comment['comment_edited_text']
    author_client.post(news_edit_url, comment_form_data)
    # Ожидаем, что комментариев больше не стало
    assert Comment.objects.count() == excepted_comment_count
    # Получаем коммент в системе
    edit_comment = Comment.objects.get(pk=comment.id)
    assert edit_comment.text == edited_comment['comment_edited_text']
    assert edit_comment.author == comment.author
    assert edit_comment.news == comment.news
    assert edit_comment.created == comment.created


def test_user_cant_edit_comment_of_another_user(author, comment,
                                                not_author_client,
                                                comment_form_data,
                                                edited_comment,
                                                news_edit_url):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    excepted_comment_count = Comment.objects.count()
    comment_form_data['text'] = edited_comment['comment_edited_text']
    not_author_client.post(news_edit_url, comment_form_data)
    # Ожидаем, что комментариев больше не стало
    assert Comment.objects.count() == excepted_comment_count
    # Получаем коммент в системе
    edit_comment = Comment.objects.get(pk=comment.id)
    assert edit_comment.text == comment.text
    assert edit_comment.author == comment.author
    assert edit_comment.news == comment.news
    assert edit_comment.created == comment.created
