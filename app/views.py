from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import time
import random
import requests
from concurrent import futures

# Конфигурация для взаимодействия с основным сервисом
DEFAULT_CALLBACK_TEMPLATE = "http://localhost:8080/api/async/orders/{order_id}/services/{service_id}/subtotal"
ASYNC_SECRET_KEY = "license-async-key"

executor = futures.ThreadPoolExecutor(max_workers=5)


def get_delay_seconds():
    """Возвращает задержку 5-10 секунд для имитации долгой задачи."""
    return random.randint(5, 10)


def calculate_subtotal(order_id, service_id, license_type, base_price, support_level, users, cores, period):
    """
    Имитация долгого расчета sub_total.
    Количество берется по типу лицензии, формула как в основном сервисе.
    """
    delay = get_delay_seconds()
    print(f"[ASYNC] start calc for order={order_id}, service={service_id}, wait {delay}s")
    time.sleep(delay)

    quantity = 1
    if license_type == "per_user":
        quantity = int(users) if users else 0
    elif license_type == "per_core":
        quantity = int(cores) if cores else 0
    elif license_type == "subscription":
        quantity = int(period) if period else 0

    subtotal = float(base_price) * float(quantity) * float(support_level)
    subtotal = round(subtotal, 2)
    print(f"[ASYNC] subtotal={subtotal} for order={order_id}, service={service_id}")

    return subtotal


def send_subtotal_result(task):
    """Колбэк: отправляет рассчитанный sub_total в основной сервис"""
    try:
        result = task.result()
        callback_url = result["callback_url"]
        secret_key = result["secret_key"]

        payload = {"subtotal": result["subtotal"]}
        headers = {
            "Content-Type": "application/json",
            "X-Async-Key": secret_key,
        }

        print(f"[ASYNC] sending result to {callback_url}")
        resp = requests.put(callback_url, json=payload, headers=headers, timeout=10)
        print(f"[ASYNC] callback status: {resp.status_code}, body: {resp.text}")
    except Exception as e:
        print(f"[ASYNC] error sending subtotal: {e}")


@api_view(["POST"])
def start_activation(request):
    """
    Точка входа: принимает задачу на расчет sub_total по услуге заявки.
    Ожидает JSON с полями order_id, service_id, license_type, base_price, support_level,
    users, cores, period, callback_url (необязателен), secret_key.
    """
    required_fields = [
        "order_id",
        "service_id",
        "license_type",
        "base_price",
        "support_level",
        "users",
        "cores",
        "period",
        "secret_key",
    ]
    if not all(field in request.data for field in required_fields):
        return Response(
            {"error": f"Требуются поля: {', '.join(required_fields)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    order_id = request.data["order_id"]
    service_id = request.data["service_id"]
    license_type = request.data["license_type"]
    support_level = request.data["support_level"]
    base_price = request.data["base_price"]
    users = request.data.get("users", 0)
    cores = request.data.get("cores", 0)
    period = request.data.get("period", 0)
    secret_key = request.data.get("secret_key", ASYNC_SECRET_KEY)
    callback_url = request.data.get(
        "callback_url",
        DEFAULT_CALLBACK_TEMPLATE.format(order_id=order_id, service_id=service_id),
    )

    print(
        f"[ASYNC] received task: order={order_id}, service={service_id}, "
        f"type={license_type}, price={base_price}, support={support_level}, users={users}, cores={cores}, period={period}"
    )

    # Планируем задачу в пуле
    task = executor.submit(
        lambda: {
            "order_id": order_id,
            "service_id": service_id,
            "subtotal": calculate_subtotal(
                order_id,
                service_id,
                license_type,
                base_price,
                support_level,
                users,
                cores,
                period,
            ),
            "callback_url": callback_url,
            "secret_key": secret_key,
        }
    )
    task.add_done_callback(send_subtotal_result)

    return Response(
        {
            "message": "Расчет sub_total запущен",
            "order_id": order_id,
            "service_id": service_id,
            "eta": "5-10 секунд",
        },
        status=status.HTTP_202_ACCEPTED,
    )


@api_view(["GET"])
def health_check(request):
    """Проверка здоровья сервиса"""
    return Response(
        {"status": "healthy", "service": "async-license-subtotal"},
        status=status.HTTP_200_OK,
    )
