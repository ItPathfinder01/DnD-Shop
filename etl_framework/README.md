# DnD Shop — Test Framework

Фреймворк для автоматизированного тестирования REST API сервиса [DnD Shop](http://localhost:8000/docs).  
Покрывает авторизацию, персонажей, магазин и инвентарь.

---

## Архитектура

```
config/settings.py      ← URL, таймаут, креды суперадмина
        │
api/                    ← HTTP-клиенты (ООП, токен передаётся один раз)
  base.py               ← BaseClient: _url(), headers, timeout
  auth.py               ← AuthClient
  characters.py         ← CharacterClient
  shop.py               ← ShopClient
  inventory.py          ← InventoryClient
  admin.py              ← AdminClient (удаление юзеров)
        │
fixtures/               ← pytest-фикстуры с setup/teardown
  auth.py               ← user_credentials, auth_token, api_client, admin_token
  character.py          ← character, second_character
        │
tests/                  ← только бизнес-логика и assert'ы
  test_auth.py
  test_characters.py
  test_shop.py
  test_inventory.py
```

---

## Требования

- Python 3.11+
- Запущенный DnD Shop backend (`http://localhost:8000`)
- Аккаунт суперадмина в базе данных

---

## Установка

```bash
cd etl_framework
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

---

## Конфигурация

Настройки находятся в `config/settings.py`. Можно переопределить через переменные окружения:

| Переменная          | По умолчанию            | Описание                        |
|---------------------|-------------------------|---------------------------------|
| `API_BASE_URL`      | `http://localhost:8000` | Базовый URL API                 |
| `API_TIMEOUT`       | `10`                    | Таймаут запросов (секунды)      |
| `SUPERADMIN_EMAIL`  | `demiurg@test.com`      | Email суперадмина для teardown  |
| `SUPERADMIN_PASSWORD` | `demiurg`             | Пароль суперадмина              |

---

## Запуск тестов

```bash
# Все тесты
pytest

# Только smoke-тесты
pytest -m smoke

# Только regression-тесты
pytest -m regression

# Конкретный файл
pytest tests/test_auth.py

# С Allure-отчётом
pytest --alluredir=allure-results
allure serve allure-results
```

---

## Маркеры

| Маркер        | Описание                                      |
|---------------|-----------------------------------------------|
| `smoke`       | Быстрые проверки — API отвечает и базовые сценарии работают |
| `regression`  | Детальные проверки бизнес-логики и edge-cases |
| `integration` | Тесты с реальным API DnD Shop                 |

---

## Teardown и очистка базы данных

Фикстуры используют `yield` — после каждого теста созданные пользователи удаляются через `DELETE /admin/users/{id}` с токеном суперадмина.

Фикстуры с teardown:

| Фикстура           | Что создаёт                    | Что удаляет        |
|--------------------|--------------------------------|--------------------|
| `smoke_user`       | `smoke_...@dndtest.com`        | пользователя       |
| `auth_token`       | `test_...@dndtest.com`         | пользователя       |
| `second_auth_token`| `test2_...@dndtest.com`        | пользователя       |

---

## Настройка суперадмина

Если суперадмин ещё не создан:

```bash
# 1. Зарегистрировать аккаунт
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"demiurg@test.com","password":"demiurg"}'

# 2. Выдать права суперадмина
curl -X POST "http://localhost:8000/admin/init-superadmin?email=demiurg@test.com"
```
