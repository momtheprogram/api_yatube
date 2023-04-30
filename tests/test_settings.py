import pytest
from django.conf import settings


class TestSettings:

    @pytest.mark.parametrize('app', ('rest_framework',
                                     'rest_framework.authtoken'))
    def test_drf_in_installed_apps(self, app):
        assert hasattr(settings, 'INSTALLED_APPS'), (
            'Убедитель, что настройки проекта содержат переменную '
            '`INSTALLED_APPS`.'
        )
        assert app in settings.INSTALLED_APPS, (
            f'`{app}` отсутствует в `INSTALLED_APPS` в настройках '
            'приложения. Убедитесь, что необходимые модули Django '
            'REST Framework добавлены в `INSTALLED_APPS` в настройках проекта.'
        )

    def test_api_in_installed_apps(self):
        assert hasattr(settings, 'INSTALLED_APPS'), (
            'Убедитель, что настройки проекта содержат переменную '
            '`INSTALLED_APPS`.'
        )
        assert {'api', 'api.apps.ApiConfig'}.intersection(
            set(settings.INSTALLED_APPS)
        ), (
            'Убедитесь, что приложение `api` добавлено в `INSTALLED_APPS` в '
            'настройках проекта.'
        )

    def test_auth_settings(self):
        assert hasattr(settings, 'REST_FRAMEWORK'), (
            'Проверьте, что настройка `REST_FRAMEWORK` добавлена в файл '
            '`settings.py`'
        )

        assert 'DEFAULT_AUTHENTICATION_CLASSES' in settings.REST_FRAMEWORK, (
            'Проверьте, что добавили ключ `DEFAULT_AUTHENTICATION_CLASSES` в '
            '`REST_FRAMEWORK` файла `settings.py`'
        )
        assert (
            'rest_framework.authentication.TokenAuthentication' in
            settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']
        ), (
            'Проверьте, что в списке `DEFAULT_AUTHENTICATION_CLASSES` в '
            '`REST_FRAMEWORK` содержится '
            '`rest_framework.authentication.TokenAuthentication`.'
        )
