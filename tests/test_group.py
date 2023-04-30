from http import HTTPStatus

import pytest

from posts.models import Group, Post


class TestGroupAPI:

    @pytest.mark.django_db(transaction=True)
    def test_group_not_found(self, client, group_1):
        response = client.get('/api/v1/groups/')

        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Страница `/api/v1/groups/` не найдена, проверьте этот адрес в '
            '*urls.py*.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_not_auth(self, client, group_1):
        response = client.get('/api/v1/groups/')
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что `/api/v1/groups/` при запросе от '
            'неавторизованного пользователя возвращаете ответ со статусом '
            '401.'
        )

    def check_group_info(self, group_info, url):
        assert 'id' in group_info, (
            f'Ответ на GET-запрос к `{url}` содержит неполную информацию о '
            'группе. Проверьте, что поле `id` добавлено в список полей '
            '`fields` сериализатора модели `Group`.'
        )
        assert 'title' in group_info, (
            f'Ответ на GET-запрос к `{url}` содержит неполную информацию о '
            'группе. Проверьте, что поле `title` добавлено в список полей '
            '`fields` сериализатора модели `Group`.'
        )
        assert 'slug' in group_info, (
            f'Ответ на GET-запрос к `{url}` содержит неполную информацию о '
            'группе. Проверьте, что поле `slug` добавлено в список полей '
            '`fields` сериализатора модели `Group`.'
        )
        assert 'description' in group_info, (
            f'Ответ на GET-запрос к `{url}` содержит неполную информацию о '
            'группе. Проверьте, что поле `description` добавлено в список '
            'полей `fields` сериализатора модели `Group`.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_auth_get(self, user_client, group_1, group_2):
        response = user_client.get('/api/v1/groups/')
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что для авторизованного пользователя GET-запрос к '
            '`/api/v1/groups/` возвращает ответ со статусом 200.'
        )

        test_data = response.json()
        assert isinstance(test_data, list), (
            'Проверьте, что для авторизованного пользователя '
            'GET-запрос к `/api/v1/groups/` возвращает информацию о группах '
            'в виде списка.'
        )
        assert len(test_data) == Group.objects.count(), (
            'Проверьте, что для авторизованного пользователя GET-запрос к '
            '`/api/v1/groups/` возвращает информацию обо всех существующих '
            'группах.'
        )

        test_group = test_data[0]
        self.check_group_info(test_group, '/api/v1/groups/')

    @pytest.mark.django_db(transaction=True)
    def test_group_create(self, user_client, group_1, group_2):
        data = {'title': 'Группа  номер 3'}
        response = user_client.post('/api/v1/groups/', data=data)
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED, (
            'Убедитесь, что группу можно создавать только через админку, '
            'а при попытке создать ее через API возвращается статус 405.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_get_post(self, user_client, post_2):
        response = user_client.get('/api/v1/posts/')
        assert response.status_code == HTTPStatus.OK, (
            'Страница `/api/v1/posts/` не найдена, проверьте этот адрес в '
            '*urls.py*.'
        )

        test_data = response.json()
        assert len(test_data) == Post.objects.count(), (
            'Проверьте, что при GET-запросе к `/api/v1/posts/` '
            'в возвращаются и посты, принадлежащие группам.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_page_not_found(self, client, group_1):
        response = client.get(f'/api/v1/groups/{group_1.id}/')
        assert response.status_code != 404, (
            'Страница `/api/v1/groups/{group_id}` не найдена, проверьте этот '
            'адрес в *urls.py*.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_page_not_auth(self, client, group_1):
        response = client.get(f'/api/v1/groups/{group_1.id}/')
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Проверьте, что при запросе от неавторизованного пользователя к '
            '`/api/v1/groups/{group_id}/` возвращается ответ со статусом '
            '401.'
        )

    @pytest.mark.django_db(transaction=True)
    def test_group_page_auth_get(self, user_client, group_1):
        response = user_client.get(f'/api/v1/groups/{group_1.id}/')
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что при GET-запросе авторизованного пользователя к '
            '`/api/v1/groups/{group_id}/` возвращается ответ со статусом 200.'
        )

        test_data = response.json()
        assert isinstance(test_data, dict), (
            'Проверьте, что при GET-запросе авторизованного пользователя к '
            '`/api/v1/groups/{group_id}/` информация о группе возвращается в '
            'виде словаря.'
        )
        self.check_group_info(test_data, '/api/v1/groups/{group_id}/')
