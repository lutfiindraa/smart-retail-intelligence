from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = PROJECT_ROOT / "data" / "synthetic"
OUTPUT_PATH = OUTPUT_DIR / "calendar.csv"


def generate_calendar(
    start_date: str,
    end_date: str,
) -> pd.DataFrame:

    dates = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D",
    )

    calendar = pd.DataFrame({
        "date": dates,
    })

    calendar["year"] = calendar["date"].dt.year
    calendar["month"] = calendar["date"].dt.month
    calendar["month_name"] = calendar["date"].dt.month_name()
    calendar["day"] = calendar["date"].dt.day
    calendar["day_of_week"] = calendar["date"].dt.dayofweek
    calendar["day_name"] = calendar["date"].dt.day_name()
    calendar["week_of_year"] = calendar["date"].dt.isocalendar().week
    calendar["is_weekend"] = (
        calendar["day_of_week"] >= 5
    )

    return calendar


def main():

    calendar = generate_calendar(
        start_date="2023-01-01",
        end_date="2023-07-31",
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    calendar.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("=" * 60)
    print("CALENDAR DATA GENERATED")
    print("=" * 60)

    print(f"Rows : {len(calendar):,}")
    print(f"Saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()