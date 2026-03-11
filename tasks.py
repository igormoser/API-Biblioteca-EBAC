import time
from celery_app import celery_app


@celery_app.task(name="tasks.calcular_soma")
def calcular_soma(a: int, b: int) -> dict:
    time.sleep(5)

    return {
        "operacao": "soma",
        "a": a,
        "b": b,
        "resultado": a + b,
    }


@celery_app.task(name="tasks.calcular_fatorial")
def calcular_fatorial(n: int) -> dict:
    time.sleep(5)

    if n < 0:
        raise ValueError("O número deve ser maior ou igual a zero.")

    resultado = 1
    for i in range(1, n + 1):
        resultado *= i

    return {
        "operacao": "fatorial",
        "n": n,
        "resultado": resultado,
    }