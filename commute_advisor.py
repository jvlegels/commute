#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, time


@dataclass
class TrainStatus:
    departure_time: str
    delay_minutes: int
    cancelled: bool
    message: str


@dataclass
class OptionEstimate:
    mode: str
    morning_minutes: int
    evening_minutes: int
    comfort_score: float
    reliability_score: float
    total_score: float
    notes: list[str]


BELGIUM_SCHOOL_HOLIDAYS_2026 = {
    (date(2026, 1, 1), date(2026, 1, 4)),
    (date(2026, 2, 16), date(2026, 2, 22)),
    (date(2026, 4, 6), date(2026, 4, 19)),
    (date(2026, 5, 14), date(2026, 5, 17)),
    (date(2026, 7, 1), date(2026, 8, 31)),
    (date(2026, 11, 2), date(2026, 11, 8)),
    (date(2026, 12, 21), date(2027, 1, 3)),
}


def is_school_holiday(today: date) -> bool:
    return any(start <= today <= end for start, end in BELGIUM_SCHOOL_HOLIDAYS_2026)


def fetch_json(url: str) -> dict | None:
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


def fetch_weather_factor() -> tuple[float, str]:
    # Gentbrugge weather proxy.
    url = (
        "https://api.open-meteo.com/v1/forecast?latitude=51.04&longitude=3.77"
        "&current=temperature_2m,precipitation,rain,wind_speed_10m"
    )
    data = fetch_json(url)
    if not data or "current" not in data:
        return 0.0, "Weather data unavailable."

    cur = data["current"]
    rain = float(cur.get("rain", 0.0)) + float(cur.get("precipitation", 0.0))
    wind = float(cur.get("wind_speed_10m", 0.0))

    penalty = 0.0
    reasons = []
    if rain >= 1.0:
        penalty += 0.8
        reasons.append("rain")
    elif rain > 0.0:
        penalty += 0.4
        reasons.append("light rain")
    if wind >= 30:
        penalty += 0.4
        reasons.append("windy")

    if reasons:
        return penalty, f"Weather currently: {', '.join(reasons)}."
    return penalty, "Weather currently mild."


def fetch_train_status() -> TrainStatus:
    today = datetime.now().strftime("%d%m%y")
    q = urllib.parse.urlencode(
        {
            "from": "Gentbrugge",
            "to": "Brussel-Centraal",
            "date": today,
            "time": "0750",
            "timesel": "departure",
            "format": "json",
            "lang": "en",
        }
    )
    url = f"https://api.irail.be/connections/?{q}"
    data = fetch_json(url)
    if not data or "connection" not in data or not data["connection"]:
        return TrainStatus("07:50", 0, False, "Live train data unavailable.")

    conn = data["connection"][0]
    dep = conn.get("departure", {})
    delay_minutes = int(round(float(dep.get("delay", 0)) / 60))
    cancelled = dep.get("canceled", "0") == "1"
    dep_time = datetime.fromtimestamp(int(dep.get("time", 0))).strftime("%H:%M") if dep.get("time") else "07:50"

    msg = "On time"
    if cancelled:
        msg = "Cancelled"
    elif delay_minutes > 0:
        msg = f"Delayed by {delay_minutes} min"

    return TrainStatus(dep_time, delay_minutes, cancelled, msg)


def traffic_multiplier(now: datetime, evening_leave: time) -> tuple[float, float, list[str]]:
    weekday = now.weekday()  # 0 Mon
    holiday = is_school_holiday(now.date())

    morning = 1.0
    evening = 1.0
    notes = []

    if weekday < 5:
        morning += 0.35
        evening += 0.2
        notes.append("weekday baseline traffic")
    if weekday in (1, 2, 3):
        morning += 0.1
        notes.append("midweek pressure")
    if holiday:
        morning -= 0.2
        evening -= 0.15
        notes.append("school holiday relief")

    if evening_leave >= time(17, 0):
        evening += 0.25
        notes.append("peak evening departure")
    elif evening_leave <= time(16, 0):
        evening -= 0.1
        notes.append("early departure")

    return max(0.7, morning), max(0.75, evening), notes


def estimate_options(evening_leave: time) -> tuple[OptionEstimate, OptionEstimate, TrainStatus]:
    now = datetime.now()
    morning_mult, evening_mult, traffic_notes = traffic_multiplier(now, evening_leave)
    weather_penalty, weather_note = fetch_weather_factor()
    train = fetch_train_status()

    # Base minutes approximations.
    car_morning = round(52 * morning_mult)
    car_evening = round(44 * evening_mult)

    train_morning = 63 + max(0, train.delay_minutes)
    train_evening = 58

    if evening_leave >= time(17, 30):
        train_evening += 5

    car = OptionEstimate(
        mode="Car",
        morning_minutes=car_morning,
        evening_minutes=car_evening,
        comfort_score=8.4 + weather_penalty,
        reliability_score=6.2 - (morning_mult - 1.0) * 1.5,
        total_score=0.0,
        notes=[weather_note] + traffic_notes,
    )

    train_reliability = 6.8
    train_notes = [train.message, "7:50 Gentbrugge train monitored."]
    if train.cancelled:
        train_reliability -= 3.5
        train_notes.append("Cancellation detected for your regular train.")
    elif train.delay_minutes >= 10:
        train_reliability -= 1.8
        train_notes.append("Major morning delay on the selected train.")
    elif train.delay_minutes > 0:
        train_reliability -= 0.8

    train_opt = OptionEstimate(
        mode="Train + metro",
        morning_minutes=train_morning,
        evening_minutes=train_evening,
        comfort_score=6.0 - weather_penalty,
        reliability_score=train_reliability,
        total_score=0.0,
        notes=train_notes,
    )

    for opt in (car, train_opt):
        total_time = opt.morning_minutes + opt.evening_minutes
        opt.total_score = (10 - total_time / 20) * 0.55 + opt.comfort_score * 0.2 + opt.reliability_score * 0.25

    return car, train_opt, train


def print_report(evening_leave: time) -> None:
    car, train_opt, train = estimate_options(evening_leave)

    print("\n=== Commute advisor: Gentbrugge ↔ Schuman ===")
    print(f"Live train check (target train around 07:50): {train.message}")

    for opt in (car, train_opt):
        total = opt.morning_minutes + opt.evening_minutes
        print(f"\n{opt.mode}")
        print(f"  Morning: {opt.morning_minutes} min")
        print(f"  Evening: {opt.evening_minutes} min")
        print(f"  Daily total: {total} min")
        print(f"  Comfort: {opt.comfort_score:.1f}/10")
        print(f"  Reliability: {opt.reliability_score:.1f}/10")
        print(f"  Combined score: {opt.total_score:.2f}")
        print("  Notes:")
        for note in opt.notes:
            print(f"   - {note}")

    recommended = car if car.total_score >= train_opt.total_score else train_opt
    other = train_opt if recommended is car else car
    diff = abs(car.total_score - train_opt.total_score)

    print("\nRecommendation")
    print(f"  Use: {recommended.mode}")
    print(f"  Reason: score advantage of {diff:.2f} points versus {other.mode}.")


if __name__ == "__main__":
    raw = input("What time do you expect to leave the office today? (HH:MM) ").strip()
    try:
        h, m = map(int, raw.split(":"))
        leave = time(h, m)
    except Exception:
        print("Invalid time format. Please use HH:MM, for example 17:30.")
        raise SystemExit(1)

    print_report(leave)
