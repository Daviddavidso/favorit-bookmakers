#!/usr/bin/env python3
"""
Big Bet — обновление данных сайта.

Запуск: автоматически по расписанию (GitHub Actions, см.
.github/workflows/update-data.yml) или вручную: `python scripts/update_data.py`.

СЕЙЧАС — демо-режим: обновляет метку времени и слегка варьирует
коэффициенты, чтобы было видно, что данные «живые».

ДЛЯ БОЕВОГО РЕЖИМА: замените тело fetch_predictions() / fetch_bookmakers()
на реальный сбор данных с источника — его API (предпочтительно) или парсинг
страницы. Функции должны вернуть список словарей того же формата.
"""
import json
import random
import datetime
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def save(name: str, obj: dict) -> None:
    (DATA / name).write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def fetch_predictions(current: dict) -> list:
    """ДЕМО: текущие прогнозы со слегка изменёнными коэффициентами.

    Боевой режим: получить данные с источника и вернуть список вида
    [{"a": team1, "b": team2, "t": "HH:MM", "d": "5 июн",
      "bet": "П1", "odd": "1.90"}, ...].
    Пример с API:
        import urllib.request
        raw = urllib.request.urlopen("https://API_ИСТОЧНИКА/...").read()
        data = json.loads(raw)
        return [ ...маппинг под наш формат... ]
    """
    items = current.get("items", [])
    for it in items:
        try:
            base = float(it["odd"])
            it["odd"] = f"{max(1.05, base + random.uniform(-0.12, 0.12)):.2f}"
        except (KeyError, ValueError):
            pass
    return items


def fetch_bookmakers(current: dict) -> list:
    """ДЕМО: список БК и бонусы меняются редко — отдаём как есть.

    Боевой режим: подтянуть актуальные суммы фрибетов / условия с источника.
    """
    return current.get("items", [])


def main() -> None:
    pred = load("predictions.json")
    pred["items"] = fetch_predictions(pred)
    pred["updated"] = now_iso()
    save("predictions.json", pred)

    bk = load("bookmakers.json")
    bk["items"] = fetch_bookmakers(bk)
    bk["updated"] = now_iso()
    save("bookmakers.json", bk)

    print("data updated:", pred["updated"])


if __name__ == "__main__":
    main()
