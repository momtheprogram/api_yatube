from http import HTTPStatus

import pytest

from posts.models import Comment


class TestCommentAPI:
    TEXT_FOR_COMMENT = 'Новый комментарий'

    def test_comments_not_found(self, user_client, post):
        response = user_client.get(f'/api/v1/posts/{post.id}/comments/')
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Страница `/api/v1/posts/{post.id}/comments/` не найдена, '
            'проверьте этот адрес в *urls.py*.'
        )

    def test_comments_get_unauth(self, client, post, comment_1_post):
        response = client.get(f'/api/v1/posts/{post.id}/comments/')
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что GET-запрос от неавторизованного пользователя к '
            '`/api/v1/posts/{post.id}/comments/` возвращает ответ со '
            'статусом 401.'
        )

    def check_comment_data(self,
                           response_data,
                           request_method_and_url,
                           db_comment=None):
        expected_fields = ('id', 'text', 'author', 'post', 'created')
        for field in expected_fields:
            assert field in response_data, (
                'Проверьте, что при запросе авторизованного пользователя к '
                f'{request_method_and_url} в ответе содержится поле '
                f'комментария `{field}`.'
            )
        if db_comment:
            assert response_data['author'] == db_comment.author.username, (
                'Проверьте, что при запросе авторизованного пользователя к '
                f'{request_method_and_url} в ответе содержится поле '
                'комментария `author`, в котором указан `username` автора.'
            )
            assert response_data['id'] == db_comment.id, (
                'Проверьте, что при запросе авторизованного пользователя на '
                f'{request_method_and_url} в ответе содержится корректный '
                '`id` комментария.'
            )

    @pytest.mark.django_db(transaction=True)
    def test_comments_get(self, user_client, post, comment_1_post,
                          comment_2_post, comment_1_another_post):
        response = user_client.get(f'/api/v1/posts/{post.id}/comments/')
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что при GET-запросе авторизованного пользователя к '
            '`/api/v1/posts/{post.id}/comments/` возвращается ответ со '
            'статусом 200.'
        )
        test_data = response.json()
        assert isinstance(test_data, list), (
            'Проверьте, что при GET-запросе авторизованного пользователя к '
            '`/api/v1/posts/{post.id}/comments/` возвращаются данные в виде '
            'списка.'
        )
        assert len(test_data) == Comment.objects.filter(post=post).count(), (
            'Проверьте, что при GET-запросе авторизованного пользователя к '
            '`/api/v1/posts/{post.id}/comments/` возвращаются данные обо '
            'всех комментариях к посту.'
        )

        comment = Comment.objects.filter(post=post).first()
        test_comment = test_data[0]
        self.check_comment_data(
            test_comment,
            'GET-запрос к `/api/v1/posts/{post.id}/comments/`',
            db_comment=comment
        )

    @pytest.mark.django_db(transaction=True)
    def test_comments_post_auth_with_valid_data(self, user_client, post,
                                                user, another_user):
        comments_count = Comment.objects.count()
        data = {
            'text': self.TEXT_FOR_COMMENT,
        }
        response = user_client.post(
            f'/api/v1/posts/{post.id}/comments/',
            data=data
        )
        assert response.status_code == HTTPStatus.CREATED, (
            'Проверьте, что POST-запрос с корректными данными от '
            'авторизованного пользователя к '
            '`/api/v1/posts/{post.id}/comments/` возвращает ответ со '
            'статусом 201.'
        )

        test_data = response.json()
        assert isinstance(test_data, dict), (
            'Проверьте, что POST-запрос авторизованного пользователя к '
            '`/api/v1/posts/{post.id}/comments/` возвращает ответ, '
            'содержащий данные нового комментария в виде словаря.'
        )
        assert test_data.get('text') == data['text'], (
            'Проверьте, что POST-запрос авторизованного пользователя к '
            '`/api/v1/posts/{post.id}/comments/` возвращает ответ, '
            'содержащий текст нового комментария в неизменном виде.'
        )
        self.check_comment_data(
            test_data,
            'POST-запрос к `/api/v1/posts/{post.id}/comments/`'
        )

        assert test_data.get('author') == user.username, (
            'Проверьте, что при создании '
            'комментария через POST-запрос к '
            '`/api/v1/posts/{post.id}/comments/` авторизованный пользователь '
            'получит ответ, в котором будет поле `author` с именем '
            'пользователя, отправившего запрос.'
        )
        assert comments_count + 1 == Comment.objects.count(), (
            'Проверьте, что POST-запрос авторизованного пользователя к '
            '`/api/v1/posts/{post.id}/comments/` создает новый комментарий.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_comments_auth_post_with_invalid_data(self, user_client, post):
        comments_count = Comment.objects.count()

        response = user_client.post(
            f'/api/v1/posts/{post.id}/comments/',
            data={}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что POST-запрос с некорректными данными от '
            'авторизованного пользователя к '
            '`/api/v1/posts/{post.id}/comments/` возвращает ответ со '
            'статусом 400.'
        )
        assert comments_count == Comment.objects.count(), (
            'Проверьте, что при POST-запросе с некорректными данными к '
            '`/api/v1/posts/{post.id}/comments/` новый комментарий не '
            'создаётся.'
        )

    def test_comment_author_and_post_are_read_only(self, user_client, post):
        response = user_client.post(
            f'/api/v1/posts/{post.id}/comments/',
            data={}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что POST-запрос с некорректными данными от '
            'авторизованного пользователя к '
            '`/api/v1/posts/{post.id}/comments/` возвращает ответ со '
            'статусом 400.'
        )
        data = set(response.json())
        assert not {'author', 'post'}.intersection(data), (
            'Проверьте, что для эндпоинта '
            '`/api/v1/posts/{post.id}/comments/` для полей `author` и `post` '
            'установлен свойство "Только для чтения"'
        )


    def test_comments_id_available(self, user_client, post, comment_1_post):
        response = user_client.get(
            f'/api/v1/posts/{post.id}/comments/{comment_1_post.id}/'
        )
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Страница `/api/v1/posts/{post.id}/comments/{comment.id}/` '
            'не найдена, проверьте этот адрес в *urls.py*.'
        )

    def test_comments_id_unauth_get(self, client, post, comment_1_post):
        response = client.get(
            f'/api/v1/posts/{post.id}/comments/{comment_1_post.id}/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что для неавторизованного пользователя GET-запрос на '
            '`/api/v1/posts/{post.id}/comments/{comment.id}/` возвращает '
            'ответ со статусом 401.'
        )

    def test_comment_id_auth_get(self, user_client, post,
                                 comment_1_post, user):
        response = user_client.get(
            f'/api/v1/posts/{post.id}/comments/{comment_1_post.id}/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Страница `/api/v1/posts/{post.id}/comments/{comment.id}/` не '
            'найдена, проверьте этот адрес в *urls.py*.'
        )

        test_data = response.json()
        assert test_data.get('text') == comment_1_post.text, (
            'Проверьте, что для авторизованного пользователя GET-запрос к '
            '`/api/v1/posts/{post.id}/comments/{comment.id}/` возвращает '
            'ответ, содержащий текст комментария.'
        )
        assert test_data.get('author') == user.username, (
            'Проверьте, что для авторизованного пользователя GET-запрос к '
            '`/api/v1/posts/{post.id}/comments/{comment.id}/` возвращает '
            'ответ, содержащий `username` автора комментария.'
        )
        assert test_data.get('post') == post.id, (
            'Проверьте, что для авторизованного пользователя GET-запрос к '
            '`/api/v1/posts/{post.id}/comments/{comment.id}/` возвращает '
            'ответ, содержащий `id` поста.'
        )

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_comment_change_by_auth_with_valid_data(self,
                                                    user_client,
                                                    post,
                                                    comment_1_post,
                                                    comment_2_post,
                                                    http_method):
        request_func = getattr(user_client, http_method)
        response = request_func(
            f'/api/v1/posts/{post.id}/comments/{comment_1_post.id}/',
            data={'text': self.TEXT_FOR_COMMENT}
        )
        http_method = http_method.upper()
        assert response.status_code == HTTPStatus.OK, (
            f'Проверьте, что для авторизованного пользователя {http_method}'
            '-запрос к `/api/v1/posts/{post.id}/comments/{comment.id}/` '
            'возвращает ответ со статусом 200.'
        )

        db_comment = Comment.objects.filter(id=comment_1_post.id).first()
        assert db_comment, (
            f'Проверьте, что для авторизованного пользователя {http_method}'
            '-запрос к `/api/v1/posts/{post.id}/comments/{comment.id}/` не '
            'удаляет редактируемый комментарий.'
        )
        assert db_comment.text == self.TEXT_FOR_COMMENT, (
            f'Проверьте, что для авторизованного пользователя {http_method}'
            '-запрос к `/api/v1/posts/{post.id}/comments/{comment.id}/` '
            'вносит изменения в комментарий.'
        )
        response_data = response.json()
        self.check_comment_data(
            response_data,
            request_method_and_url=(
                f'{http_method} -запрос к '
                '`/api/v1/posts/{post.id}/comments/{comment.id}/`'
            ),
            db_comment=db_comment
        )

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_comment_change_by_not_author_with_valid_data(self,
                                                          user_client,
                                                          post,
                                                          comment_2_post,
                                                          http_method):
        request_func = getattr(user_client, http_method)
        response = request_func(
            f'/api/v1/posts/{post.id}/comments/{comment_2_post.id}/',
            data={'text': self.TEXT_FOR_COMMENT}
        )
        http_method = http_method.upper()
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            f'Проверьте, что для авторизованного пользователя {http_method}'
            '-запрос к `/api/v1/posts/{post.id}/comments/{comment.id}/` для '
            'чужого комментария возвращает ответ со статусом 403.'
        )

        db_comment = Comment.objects.filter(id=comment_2_post.id).first()
        assert db_comment.text != self.TEXT_FOR_COMMENT, (
            f'Проверьте, что для авторизованного пользователя {http_method}'
            '-запрос к `/api/v1/posts/{post.id}/comments/{comment.id}/` для '
            'чужого комментария не вносит изменения в комментарий.'
        )

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_comment_change_not_auth_with_valid_data(self,
                                                     client,
                                                     post,
                                                     comment_1_post,
                                                     http_method):
        request_func = getattr(client, http_method)
        response = request_func(
            f'/api/v1/posts/{post.id}/comments/{comment_1_post.id}/',
            data={'text': self.TEXT_FOR_COMMENT}
        )
        http_method = http_method.upper()
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            f'Проверьте, что для неавторизованного пользователя {http_method}'
            '-запрос к `/api/v1/posts/{post.id}/comments/{comment.id}/` '
            'возвращает ответ со статусом 401.'
        )
        db_comment = Comment.objects.filter(id=comment_1_post.id).first()
        assert db_comment.text != self.TEXT_FOR_COMMENT, (
            f'Проверьте, что для неавторизованного пользователя {http_method}'
            '-запрос к `/api/v1/posts/{post.id}/comments/{comment.id}/` не '
            'вносит изменения в комментарий.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_comment_delete_by_author(self, user_client,
                                      post, comment_1_post):
        response = user_client.delete(
            f'/api/v1/posts/{post.id}/comments/{comment_1_post.id}/'
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что для автора комментария DELETE-запрос к '
            '`/api/v1/posts/{post.id}/comments/{comment.id}/` возвращает '
            'ответ со статусом 204.'
        )

        test_comment = Comment.objects.filter(id=post.id).first()
        assert not test_comment, (
            'Проверьте, что DELETE-запрос автора комментария к '
            '`/api/v1/posts/{post.id}/comments/{comment.id}/` удаляет '
            'комментарий.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_comment_delete_by_author(self, user_client,
                                      post, comment_2_post):
        response = user_client.delete(
            f'/api/v1/posts/{post.id}/comments/{comment_2_post.id}/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Проверьте, что DELETE-запрос авторизованного пользователя к '
            '`/api/v1/posts/{post.id}/comments/{comment.id}/` чужого '
            'комментария возвращает ответ со статусом 403.'
        )
        db_comment = Comment.objects.filter(id=comment_2_post.id).first()
        assert db_comment, (
            'Проверьте, что для авторизованного пользователя DELETE-запрос к '
            '`/api/v1/posts/{post.id}/comments/{comment.id}/` для чужого '
            'комментария не удаляет комментарий.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_comment_delete_by_unauth(self, client, post, comment_1_post):
        response = client.delete(
            f'/api/v1/posts/{post.id}/comments/{comment_1_post.id}/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что для неавторизованного пользователя DELETE-запрос '
            'к `/api/v1/posts/{post.id}/comments/{comment.id}/` возвращает '
            'ответ со статусом 401.'
        )
        db_comment = Comment.objects.filter(id=comment_1_post.id).first()
        assert db_comment, (
            'Проверьте, что для неавторизованного пользователя DELETE-запрос '
            'к `/api/v1/posts/{post.id}/comments/{comment.id}/` не удаляет '
            'комментарий.'
        )
