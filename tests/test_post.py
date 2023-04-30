from http import HTTPStatus

import pytest

from posts.models import Post


class TestPostAPI:
    VALID_DATA = {'text': 'Поменяли текст статьи'}

    def test_post_not_found(self, client, post):
        response = client.get('/api/v1/posts/')

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Страница `/api/v1/posts/` не найдена, проверьте этот адрес в '
            '*urls.py*.'
        )

    def test_post_not_auth(self, client, post):
        response = client.get('/api/v1/posts/')

        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что при GET-запросе неавторизованного пользователя к '
            '`/api/v1/posts/` возвращается ответ со статусом 401.'
        )

    def check_post_data(self,
                        response_data,
                        request_method_and_url,
                        db_post=None):
        expected_fields = ('id', 'text', 'author', 'pub_date')
        for field in expected_fields:
            assert field in response_data, (
                'Проверьте, что для авторизованного пользователя ответ на '
                f'{request_method_and_url} содержит поле `{field}` постов.'
            )
        if db_post:
            assert response_data['author'] == db_post.author.username, (
                'Проверьте, что при запросе авторизованного пользователя к '
                f'{request_method_and_url} ответ содержит поле `author` с '
                'именем автора каждого из постов.'
            )
            assert response_data['id'] == db_post.id, (
                'Проверьте, что при запросе авторизованного пользователя к '
                f'{request_method_and_url} в ответе содержится корректный '
                '`id` поста.'
            )

    @pytest.mark.django_db(transaction=True)
    def test_posts_auth_get(self, user_client, post, another_post):
        response = user_client.get('/api/v1/posts/')
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что для авторизованного пользователя GET-запрос к '
            '`/api/v1/posts/` возвращает статус 200.'
        )

        test_data = response.json()
        assert isinstance(test_data, list), (
            'Проверьте, что для авторизованного пользователя GET-запрос к '
            '`/api/v1/posts/` возвращает список.'
        )

        assert len(test_data) == Post.objects.count(), (
            'Проверьте, что для авторизованного пользователя GET-запрос к '
            '`/api/v1/posts/` возвращает список всех постов.'
        )

        db_post = Post.objects.first()
        test_post = test_data[0]
        self.check_post_data(
            test_post,
            'GET-запрос к `/api/v1/posts/`',
            db_post
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_create_auth_with_invalid_data(self, user_client):
        posts_count = Post.objects.count()
        response = user_client.post('/api/v1/posts/', data={})
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что для авторизованного пользователя POST-запрос с '
            'некорректными данными к `/api/v1/posts/` возвращает ответ со '
            'статусом 400.'
        )
        assert posts_count == Post.objects.count(), (
            'Проверьте, что POST-запрос к `/api/v1/posts/` с некорректными '
            'данными не создает новый пост.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_create_auth_with_valid_data(self, user_client, user):
        post_count = Post.objects.count()

        data = {'text': 'Статья номер 3'}
        response = user_client.post('/api/v1/posts/', data=data)
        assert response.status_code == HTTPStatus.CREATED, (
            'Проверьте, что для авторизованного пользователя  POST-запрос с '
            'корректными данными к `/api/v1/posts/` возвращает ответ со '
            'статусом 201.'
        )

        test_data = response.json()
        assert isinstance(test_data, dict), (
            'Проверьте, что для авторизованного пользователя POST-запрос к '
            '`/api/v1/posts/` возвращает ответ, содержащий данные нового '
            'поста в виде словаря.'
        )
        self.check_post_data(test_data, 'POST-запрос к `/api/v1/posts/`')
        assert test_data.get('text') == data['text'], (
            'Проверьте, что для авторизованного пользователя POST-запрос к '
            '`/api/v1/posts/` возвращает ответ, содержащий текст нового '
            'поста в неизменном виде.'
        )
        assert test_data.get('author') == user.username, (
            'Проверьте, что для авторизованного пользователя при создании '
            'поста через POST-запрос к `/api/v1/posts/` ответ содержит поле '
            '`author` с именем пользователя, отправившего запрос.'
        )
        assert post_count + 1 == Post.objects.count(), (
            'Проверьте, что POST-запрос с корректными данными от '
            'авторизованного пользователя к `/api/v1/posts/` создает новый '
            'пост.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_unauth_create(self, client, user, another_user):
        posts_conut = Post.objects.count()

        data = {'author': another_user.id, 'text': 'Статья номер 3'}
        response = client.post('/api/v1/posts/', data=data)
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что POST-запрос неавторизованного пользователя к '
            '`/api/v1/posts/` возвращает ответ со статусом 401.'
        )

        assert posts_conut == Post.objects.count(), (
            'Проверьте, что POST-запрос неавторизованного пользователя к '
            '`/api/v1/posts/` не создает новый пост.'
        )

    def test_post_get_current(self, user_client, post):
        response = user_client.get(f'/api/v1/posts/{post.id}/')

        assert response.status_code == HTTPStatus.OK, (
            'Страница `/api/v1/posts/{id}/` не найдена, проверьте этот адрес '
            'в *urls.py*.'
        )

        test_data = response.json()
        self.check_post_data(
            test_data,
            'GET-запрос к `/api/v1/posts/{id}/`',
            post
        )

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_post_change_auth_with_valid_data(self, user_client, post,
                                              http_method):
        request_func = getattr(user_client, http_method)
        response = request_func(f'/api/v1/posts/{post.id}/',
                                data=self.VALID_DATA)
        http_method = http_method.upper()
        assert response.status_code == HTTPStatus.OK, (
            f'Проверьте, что для авторизованного пользователя {http_method}'
            '-запрос к `/api/v1/posts/{id}/` вернётся ответ со статусом '
            '200.'
        )

        test_post = Post.objects.filter(id=post.id).first()
        assert test_post, (
            f'Проверьте, что {http_method}-запрос авторизованного '
            'пользователя к `/api/v1/posts/{id}/` не удаляет редактируемый '
            'пост.'
        )
        assert test_post.text == self.VALID_DATA['text'], (
            f'Проверьте, что {http_method}-запрос авторизованного '
            'пользователя к `/api/v1/posts/{id}/` вносит изменения в пост.'
        )

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_post_change_not_auth_with_valid_data(self, client, post,
                                                  http_method):
        request_func = getattr(client, http_method)
        response = request_func(f'/api/v1/posts/{post.id}/',
                                data=self.VALID_DATA)
        http_method = http_method.upper()
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            f'Проверьте, что {http_method}-запрос неавторизованного '
            'пользователя к `/api/v1/posts/{id}/` возвращает ответ со '
            'статусом 401.'
        )
        db_post = Post.objects.filter(id=post.id).first()
        assert db_post.text != self.VALID_DATA['text'], (
            f'Проверьте, что {http_method}'
            '-запрос неавторизованного пользователя к `/api/v1/posts/{id}/` '
            'не вносит изменения в пост.'
        )

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_post_change_not_author_with_valid_data(self, user_client,
                                                    another_post, http_method):
        request_func = getattr(user_client, http_method)
        response = request_func(f'/api/v1/posts/{another_post.id}/',
                                data=self.VALID_DATA)
        http_method = http_method.upper()
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            f'Проверьте, что {http_method}'
            '-запрос авторизованного пользователя к `/api/v1/posts/{id}/` '
            'для чужого поста возвращает ответ со статусом 403.'
        )

        db_post = Post.objects.filter(id=another_post.id).first()
        assert db_post.text != self.VALID_DATA['text'], (
            f'Проверьте, что {http_method}'
            '-запрос авторизованного пользователя к `/api/v1/posts/{id}/` '
            'для чужого поста не вносит изменения в пост.'
        )

    @pytest.mark.django_db(transaction=True)
    @pytest.mark.parametrize('http_method', ('put', 'patch'))
    def test_post_patch_auth_with_invalid_data(self, user_client, post,
                                               http_method):
        request_func = getattr(user_client, http_method)
        response = request_func(f'/api/v1/posts/{post.id}/',
                                data={'text': {}},
                                format='json')
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            f'Проверьте, что {http_method}'
            '-запрос с некорректными данными от авторизованного пользователя '
            'к `/api/v1/posts/{id}/` возвращает ответ с кодом 400.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_delete_by_author(self, user_client, post):
        response = user_client.delete(f'/api/v1/posts/{post.id}/')
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Проверьте, что для автора поста DELETE-запрос к '
            ' `/api/v1/posts/{id}/` возвращает ответ со статусом 204.'
        )

        test_post = Post.objects.filter(id=post.id).first()
        assert not test_post, (
            'Проверьте, что DELETE-запрос автора поста к '
            ' `/api/v1/posts/{id}/` удаляет этот пост.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_delete_not_author(self, user_client, another_post):
        response = user_client.delete(f'/api/v1/posts/{another_post.id}/')
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Проверьте, что DELETE-запрос авторизованного пользователя к '
            '`/api/v1/posts/{id}/` чужого поста '
            'вернёт ответ со статусом 403.'
        )

        test_post = Post.objects.filter(id=another_post.id).first()
        assert test_post, (
            'Проверьте, что авторизованный пользователь не может удалить '
            'чужой пост.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_unauth_delete_current(self, client, post):
        response = client.delete(f'/api/v1/posts/{post.id}/')
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что DELETE-запрос неавторизованного пользователя '
            'к `/api/v1/posts/{id}/` вернёт ответ со статусом 401.'
        )
        test_post = Post.objects.filter(id=post.id).first()
        assert test_post, (
            'Проверьте, что DELETE-запрос неавторизованного пользователя '
            'к `/api/v1/posts/{id}/` не удаляет запрошенный пост.'
        )
