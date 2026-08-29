from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT_ROOT / "data" / "synthetic"
OUTPUT_PATH = OUTPUT_DIR / "weather.csv"

RANDOM_SEED = 42


def generate_weather() -> pd.DataFrame:

    rng = np.random.default_rng(RANDOM_SEED)

    dates = pd.date_range(
        "2023-01-01",
        "2023-06-30",
        freq="D",
    )

    locations = [
        "Astoria",
        "Lower Manhattan",
        "Hell's Kitchen",
    ]

    rows = []

    for date in dates:

        month = date.month

        # Temperature seasonal sederhana
        if month <= 2:
            base_temp = 5
        elif month <= 4:
            base_temp = 12
        else:
            base_temp = 20

        for location in locations:

            temperature = (
                base_temp
                + rng.normal(0, 3)
            )

            rainfall = max(
                0,
                rng.normal(3, 5)
            )

            if rainfall >= 8:
                condition = "Rain"
            elif rainfall >= 2:
                condition = "Cloudy"
            else:
                condition = "Clear"

            rows.append({
                "date": date.date(),
                "location": location,
                "temperature": round(
                    temperature,
                    2,
                ),
                "rainfall_mm": round(
                    rainfall,
                    2,
                ),
                "weather_condition": condition,
            })

    return pd.DataFrame(rows)


def validate_weather(
    weather: pd.DataFrame,
) -> None:

    if weather.isna().any().any():
        raise ValueError(
            "Missing value ditemukan."
        )

    if (
        weather["rainfall_mm"] < 0
    ).any():
        raise ValueError(
            "Rainfall tidak boleh negatif."
        )

    if not weather["weather_condition"].isin(
        ["Clear", "Cloudy", "Rain"]
    ).all():
        raise ValueError(
            "Weather condition tidak valid."
        )


def main():

    print("=" * 60)
    print("GENERATE SYNTHETIC WEATHER DATA")
    print("=" * 60)

    weather = generate_weather()

    validate_weather(
        weather
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    weather.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        f"✓ Rows : {len(weather):,}"
    )

    print(
        f"✓ Locations : "
        f"{weather['location'].nunique()}"
    )

    print(
        f"✓ Saved : {OUTPUT_PATH}"
    )

    print("=" * 60)
    print("WEATHER GENERATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()