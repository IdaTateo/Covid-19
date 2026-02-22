#!/usr/bin/env python3
"""
Build region-level (CCAA) cumulative COVID-19 cases & deaths for Spain, year 2020.

Source: Datadista, file: ccaa_covid19_datos_sanidad_nueva_serie.csv
Raw URL: https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_datos_sanidad_nueva_serie.csv

Output:
  1) spain_ccaa_covid19_2020_cumulative_long.csv  (long/tidy: date, region, cum_cases, cum_deaths)
  2) spain_ccaa_covid19_2020_cumulative_wide_cases.csv   (wide: dates x regions for cumulative cases)
  3) spain_ccaa_covid19_2020_cumulative_wide_deaths.csv  (wide: dates x regions for cumulative deaths)
"""

import io
import sys
import pandas as pd

RAW_URL = "https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_datos_sanidad_nueva_serie.csv"

def main():
    # Load
    df = pd.read_csv(RAW_URL, parse_dates=["Fecha"])

    # Select relevant columns and standardize names
    cols = ["Fecha", "CCAA", "Casos", "Fallecidos"]
    for c in cols:
        if c not in df.columns:
            raise ValueError(f"Column '{c}' not found in source CSV. Columns present: {list(df.columns)}")

    df = df[cols].rename(columns={"Fecha":"date",
                                  "CCAA":"region",
                                  "Casos":"new_cases",
                                  "Fallecidos":"new_deaths"})

    # Sort to ensure cumulative sums are correct
    df = df.sort_values(["region", "date"])

    # Filter to 2020
    df = df[df["date"].dt.year == 2020].copy()

    # Some series might contain corrections (negative daily values). We keep them as-is so cum sums reflect revisions.
    # Compute cumulative by region
    df["cum_cases"] = df.groupby("region", sort=False)["new_cases"].cumsum()
    df["cum_deaths"] = df.groupby("region", sort=False)["new_deaths"].cumsum()

    # Long/tidy output
    out_long = df[["date", "region", "cum_cases", "cum_deaths"]].copy()
    out_long.to_csv("spain_ccaa_covid19_2020_cumulative_long.csv", index=False)

    # Wide outputs (cases / deaths)
    wide_cases = out_long.pivot(index="date", columns="region", values="cum_cases").sort_index()
    wide_deaths = out_long.pivot(index="date", columns="region", values="cum_deaths").sort_index()

    wide_cases.to_csv("spain_ccaa_covid19_2020_cumulative_wide_cases.csv")
    wide_deaths.to_csv("spain_ccaa_covid19_2020_cumulative_wide_deaths.csv")

    print("✅ Wrote:")
    print(" - spain_ccaa_covid19_2020_cumulative_long.csv")
    print(" - spain_ccaa_covid19_2020_cumulative_wide_cases.csv")
    print(" - spain_ccaa_covid19_2020_cumulative_wide_deaths.csv")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
