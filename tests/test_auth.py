from http import HTTPStatus


class TestAuthAPI:

    def test_auth(self, client, user, password):
        response = client.post(
            '/api/v1/api-token-auth/',
            data={'username': user.username, 'password': password}
        )
        assert response.status_code != HTTPStatus.NOT_FOUND, (
            'Страница `/api/v1/api-token-auth/` не найдена, проверьте этот '
            'адрес в *urls.py*.'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Проверьте, что POST-запрос к `/api/v1/api-token-auth/` '
            'возвращает ответ с кодом 200.'
        )

        auth_data = response.json()
        assert 'token' in auth_data, (
            'Проверьте, что ответ на POST-запрос с валидными данными к '
            '`/api/v1/api-token-auth/` содержит токен.'
        )

    def test_auth_with_invalid_data(self, client, user):
        response = client.post('/api/v1/api-token-auth/', data={})
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Проверьте, что POST-запрос к `/api/v1/api-token-auth/` '
            'с некорректными данными возвращает ответ со статусовм 400.'
        )
