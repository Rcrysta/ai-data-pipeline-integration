import pandas as pd
import requests
from datetime import datetime
from dateutil.relativedelta import relativedelta
api_key = "enter api key secret"

monthly_series = {
    "cpi_core": "CPILFESL",
    "cpi_sticky": "CORESTICKM159SFRBATL",
    "cpi_median": "MEDCPIM158SFRBCLE",
    "bank_prime_rate": "MPRIME",
    "fed_funds_rate": "FEDFUNDS",
    "unemployment_rate": "UNRATE",
    "median_weeks_unemployed": "UEMPMED",
    "avg_weeks_unemployed": "UEMPMEAN",
    "housing_starts": "MSACSR",
    "freight_transport_index": "TSIFRGHTC",
    "freight_truck_tonnage": "TRUCKD11",
    "freight_ppi_industry": "PCU484484",
    "freight_ppi_dist": "PCU484121484121",
    "freight_ppi_trans_warehouse": "PCUATRNWRATRNWR",
    "diesel_ppi": "WPS057303",
    "oecd_leading_indicator": "USALOLITOAASTSAM",
    "labor_participation": "CIVPART",
    "employment_population_ratio": "EMRATIO",
    "labor_avg_hourly_earn": "CES0500000003",
    "labor_truck_transport": "CES4348400001",
    "labor_ware_storage": "CES4349300001",
    "case_shiller_hpi": "CSUSHPISA",
    "diesel_price_padd_1": "GASDESECW",
    "diesel_price_padd_2": "GASDESMWW",
    "diesel_price_padd_3": "GASDESGCW",
    "diesel_price_padd_4": "GASDESRMW",
    "diesel_price_padd_5": "GASDESWCW",
    "indu_prod_all": "INDPRO",
    "indu_prod_goods": "IPDCONGD",
    "indu_prod_food_bev_tobacco": "IPG311A2S",
    "indu_prod_plastic_rubber": "IPG326S",
    "indu_prod_non-durable_goods": "IPNCONGD",
    "bank_fin_con_loan_72mth": "RIFLPBCIANM72NM",
    "bank_fin_con_loan_60mth": "RIFLPBCIANM60NM",
    "bank_fin_con_loan_48mth": "TERMCBAUTO48NS",
    "com_bank_int_rate_cc": "TERMCBCCALLNS",
    "com_bank_fin_rate_24mths": "TERMCBPER24NS",
    "mortgage_rate_fix_15yr": "MORTGAGE15US",
    "mortgage_rate_fix_30yr": "MORTGAGE30US",

}
# 2. CALCULATE NORMALIZED ROLLING 36-MONTH WINDOW
# ---------------------------------------------------------
today = datetime.today()

# always use first day of prior month
end_date = (today.replace(day=1) - relativedelta(months=1)).replace(day=1)
start_date = end_date - relativedelta(months=35)

start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")

# 3. FETCH MONTHLY FRED SERIES
# ---------------------------------------------------------
def fetch_fred_series(series_id, start_date, end_date, api_key):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
        "observation_end": end_date,
        "frequency": "m",
    }

    r = requests.get(url, params=params)
    if r.status_code != 200:
        print(f"Failed: {series_id}")
        return None

    df = pd.DataFrame(r.json()["observations"])
    df["date"] = pd.to_datetime(df["date"])

    # force YYYY-MM-01
    df["date"] = df["date"].dt.to_period("M").dt.to_timestamp()

    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df[["date", "value"]]

# ---------------------------------------------------------
# 4. MERGE ALL SERIES INTO ONE DATAFRAME
# ---------------------------------------------------------
combined = None
api_key

for name, sid in monthly_series.items():
    df = fetch_fred_series(sid, start_date_str, end_date_str, api_key)
    if df is None:
        continue

    df.rename(columns={"value": name}, inplace=True)

    combined = df if combined is None else combined.merge(df, on="date", how="outer")

combined.sort_values("date", inplace=True)
combined.set_index("date", inplace=True)
combined = combined.ffill()

display(combined)
