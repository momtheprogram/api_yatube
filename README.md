# api_yatube
В проекте api_yatube реализовано API для всех моделей приложения.

API должен доступен только аутентифицированным пользователям. В проекте использована аутентификация по токену TokenAuthentication.
Аутентифицированный пользователь авторизован на изменение и удаление своего контента; в остальных случаях доступ предоставляется только для чтения. При попытке изменить чужие данные, вернётся код ответа 403 Forbidden.
Для взаимодействия с ресурсами настроены такие эндпоинты:
api/v1/api-token-auth/ (POST): передаём логин и пароль, получаем токен.
api/v1/posts/ (GET, POST): получаем список всех постов или создаём новый пост.
api/v1/posts/{post_id}/ (GET, PUT, PATCH, DELETE): получаем, редактируем или удаляем пост по id.
api/v1/groups/ (GET): получаем список всех групп.
api/v1/groups/{group_id}/ (GET): получаем информацию о группе по id.
api/v1/posts/{post_id}/comments/ (GET, POST): получаем список всех комментариев поста с id=post_id или создаём новый, указав id поста, который хотим прокомментировать.
api/v1/posts/{post_id}/comments/{comment_id}/ (GET, PUT, PATCH, DELETE): получаем, редактируем или удаляем комментарий по id у поста с id=post_id.

В ответ на запросы POST, PUT и PATCH API возвращает объект, который был добавлен или изменён.

Для модели Post использован ModelViewSet. 

***Примеры запросов***
Пример POST-запроса с токеном Антона Чехова: добавление нового поста.
POST .../api/v1/posts/
{
    "text": "Вечером собрались в редакции «Русской мысли», чтобы поговорить о народном театре. Проект Шехтеля всем нравится.",
    "group": 1
} 
Пример ответа:
{
    "id": 14,
    "text": "Вечером собрались в редакции «Русской мысли», чтобы поговорить о народном театре. Проект Шехтеля всем нравится.",
    "author": "anton",
    "image": null,
    "group": 1,
    "pub_date": "2021-06-01T08:47:11.084589Z"
} 
Пример POST-запроса с токеном Антона Чехова: отправляем новый комментарий к посту с id=14.
POST .../api/v1/posts/14/comments/
{
    "text": "тест тест"
} 
Пример ответа:
{
    "id": 4,
    "author": "anton",
    "post": 14,
    "text": "тест тест",
    "created": "2021-06-01T10:14:51.388932Z"
} 
Пример GET-запроса с токеном Антона Чехова: получаем информацию о группе.
GET .../api/v1/groups/2/
Пример ответа:
{
    "id": 2,
    "title": "Математика",
    "slug": "math",
    "description": "Посты на тему математики"
} 
