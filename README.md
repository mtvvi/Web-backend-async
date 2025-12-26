# Web-backend-async — ЛР8

Асинхронный сервис на Django/DRF для расчета `sub_total` по услугам (м-м). Сервис принимает задачу на расчет, делает «долгий» расчет 5–10 сек в пуле потоков и по завершении шлет PUT в основной Go-бэкенд по колбэку `/api/async/licenseCalculationRequests/{licenseCalculationRequest_id}/services/{service_id}/subtotal` с заголовком `X-Async-Key`.
