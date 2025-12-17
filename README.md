# Web-backend-async — ЛР8

Асинхронный сервис на Django/DRF для расчета `sub_total` по услугам (м-м). Сервис принимает задачу на расчет, делает «долгий» расчет 5–10 сек в пуле потоков и по завершении шлет PUT в основной Go-бэкенд по колбэку `/api/async/orders/{order_id}/services/{service_id}/subtotal` с заголовком `X-Async-Key`.

## Эндпоинты

- `POST /api/license-activation` — запускает расчет `sub_total`. Тело:
  ```json
  {
    "order_id": 1,
    "service_id": 2,
    "license_type": "per_user",
    "base_price": 1000,
    "support_level": 1.2,
    "users": 10,
    "cores": 0,
    "period": 1,
    "callback_url": "http://localhost:8080/api/async/orders/1/services/2/subtotal",
    "secret_key": "license-async-key"
  }
  ```
  Возвращает `202 Accepted`.
- `GET /api/health/` — проверка здоровья.

## Как запустить

```bash
cd Web-backend-async
python -m venv env
. env/bin/activate
pip install -r requirements.txt
python manage.py runserver 0.0.0.0:8001
```

По умолчанию сервис стучится в основной бэкенд на `http://localhost:8080`, ключ — `license-async-key` (совпадает с ключом в Go API).
