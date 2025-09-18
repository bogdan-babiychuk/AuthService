# AuthService

Небольшой сервис аутентификации/авторизации на FastAPI + SQLAlchemy (async) + SQLite.

## Требования
- Python 3.12+
- Poetry 1.6+

## Установка и запуск (Poetry)

1) Клонирование и установка зависимостей
```bash
poetry install
```

2) (Опционально) Установка dev-зависимостей, если они будут добавлены в проект
```bash
poetry install --with dev
```

3) Настройка окружения
Создайте файл `.env` в корне проекта (на уровне с `src/`) и перенесите в него переменные из .env.example
```env
JWT_SECRET_KEY=super_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_PASSWORD=123
```

4) Запуск приложения
```bash
poetry run uvicorn main:create --factory --reload
```

Документация Swagger: http://localhost:8000/api/docs

Первый запуск автоматически создаст таблицы в SQLite (`./test.db`).

## Архитектура кратко
- `src/api` – схемы (Pydantic), обработчики, зависимости
- `src/api/services` – бизнес-логика (например, `UserService`)
- `src/auth` – утилиты для JWT и паролей
- `src/db` – движок БД, модели, UoW, роли
- `src/infra/repositories` – слой доступа к данным (репозитории)

## Эндпоинты
Базовый префикс: `/api/v1/users`

- POST `/` – Регистрация нового пользователя
  - Тело: `CreateUserSchema {name, last_name, surname, email, password, confirm_password}`
  - 201: `{201: "Пользватель успешно зарегистрирован"}`

- POST `/login` – Аутентификация пользователя
  - Тело: `LoginUserSchema {email, password}`
  - Возвращает JWT-токен и устанавливает cookie `access_token`

- POST `/logout` – Выход из системы
  - Удаляет cookie `access_token`

- DELETE `/` – Мягкое удаление (деактивация) текущего пользователя
  - Требуется cookie `access_token`
  - Тело: `UserDeleteScheme {email}`
  - 200: `{200: "Аккаунт <email> успешно удален"}`

- PATCH `/password` – Смена пароля текущего пользователя
  - Требуется cookie `access_token`
  - Тело: `ChangePasswordUserSchema {recent_password, new_password, confirm_new_password}`
  - 200: `{200: "Пароль пользователя успешно изменён"}`

- PATCH `/me` – Обновление профиля текущего пользователя
  - Требуется cookie `access_token`
  - Тело: `UserUpdateSchema {name?, last_name?, surname?}`
  - 200: `{ "message": "Профиль успешно обновлён" }`

- PATCH `/admin` – Выдать себе роль ADMIN при знании админ-пароля
  - Тело/параметр: `password`
  - 200: `{200: "Админка успешно добавлена! В аккаунт необходимо зайти заново"}`
  
Админские ручки (требуется роль ADMIN):

- PATCH `/{user_oid}/role` – Изменить роль указанного пользователя (только админ)
  - Параметр пути: `user_oid` – UUID пользователя
  - Query/body: `role` – одно из: `admin`, `simple_user`
  - 200: `{200: "Роль пользователя успешно изменена, роль будет активна когда пользователь перезайдёт в аккаунт"}`

- DELETE `/` – Перманентное удаление пользователя (только админ)
  - Тело: `UserDeleteScheme {email}`
  - 200: `{200: "Пользователь <email> успешно удалён"}`

- POST `/admin/joke` – Возвращает случайную шутку (только админ)
  - 200: `{ "message": "..." }`


### Mock-эндпоинты
Базовый префикс: `/api/v1/mock` (таблицы в БД не требуются, данные в памяти)

- GET `/products` – Список товаров (требуется аутентификация)
  - Ответ: `Product[]`

- GET `/orders` – Список заказов (только ADMIN)
  - Ответ: `Order[]`
  - Если пользователь не ADMIN → 403