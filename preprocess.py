import pandas as pd

# 1) Read
df = pd.read_csv("final_master.csv")

# 2) Drop scrape_timestamp
df = df.drop(columns=["scrape_timestamp"], errors="ignore")

# 3) Define the fixed columns you want to keep
id_cols = ["timestamp", "state", "RTO", "rto_number", "vehicle_type", "district", "Maker"]

# 4) All other columns are fuel columns (including TOTAL right now)
fuel_cols = [c for c in df.columns if c not in id_cols]

# Optional: If you do NOT want the final TOTAL column from your source file as a “FuelType”
fuel_cols = [c for c in fuel_cols if c != "TOTAL"]

# 5) Melt fuel columns -> FuelType + Total
out = df.melt(
    id_vars=id_cols,
    value_vars=fuel_cols,
    var_name="FuelType",
    value_name="Total"
)

# 6) Clean + filter
out["Total"] = pd.to_numeric(out["Total"], errors="coerce").fillna(0)

# Keep only actual registrations (recommended)
out = out[out["Total"] > 0].reset_index(drop=True)

# 7) Save
out.to_csv("master_preprocessed.csv", index=False)

print("Saved:", out.shape, "-> master_preprocessed.csv")
