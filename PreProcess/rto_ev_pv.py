import pandas as pd
import re
from difflib import get_close_matches

# --- Load CSV ---

def Preprocessingev_pv(csv_path="month_main_table.csv"):
    df = pd.read_csv(csv_path)

    # --- District Map ---
    district_map = {
        "Chennai": [
            "AMBATTUR","CHENGALPATTU","CHENNAI CENTRAL","CHENNAI EAST","CHENNAI","CHENNAI NORTH",
            "CHENNAI NORTH EAST","CHENNAI SOUTH","CHENNAI SOUTH EAST","CHENNAI SOUTH WEST",
            "CHENNAI WEST","GUMMIDIPOONDI","KUNDRATHUR","MADURANTAGAM","MEENAMBAKKAM",
            "POONAMALLEE","REDHILLS","CHENNAI NORTH WEST","SHOLINGANALLUR",
            "SRIPERUMBUDUR","TAMBARAM","THIRUKALUKUNTRAM","THIRUTHANI","THIRUVALLUR"
        ],
        "Coimbatore": [
            "AVINASHI","COIMBATORE CENTRAL","COIMBATORE NORTH","COIMBATORE SOUTH",
            "COIMBATORE WEST","DHARAPURAM","KANGEYAM","METTUPALAYAM","OOTY","POLLACHI",
            "SULUR","TIRUPPUR NORTH","TIRUPPUR SOUTH","UDUMALPET","VALPARAI"
        ],
        "Cuddalore": [
            "CHIDAMBARAM","CUDDALORE","GINGEE","KALLAKKURICHI","NEYVELI",
            "PANRUTI","TINDIVANAM","ULUNDURPETTAI","VILUPPURAM","VIRUDHACHALAM"
        ],
        "DERIK": [
            "AMBASAMUDRAM","KOVILPATTI","MARTHANDAM","NAGERCOIL","SANKARANKOIL",
            "TENKASI","THOOTHUKUDI","TIRUCHENDUR","TIRUNELVELI","VALLIYUR","ALANGULAM"
        ],
        "Madurai": [
            "ARUPPUKKOTTAI","KARAIKKUDI","MADURAI CENTRAL","MADURAI NORTH","MADURAI SOUTH",
            "MELUR","PARAMAKUDI","RAMANATHAPURAM","SIVAGANGA","SIVAKASI","SRIVILLIPUTHUR",
            "THENI","THIRUMANAGALAM","USILAMPATTI","UTHAMAPALAYAM","VADIPATTI",
            "VIRUDHUNAGAR","RAJAPALAYAM"
        ],
        "Pondicherry": [
            "BAHOUR","KARAIKAL","OULGARET","PUDUCHERRY","VILLIANUR"
        ],
        "Thanjavur": [
            "ALANGUDI","ARANTHANGI","ILLUPPUR","KUMBAKONAM","MANNARGUDI",
            "MAYILADUTHURAI","NAGAPATTINAM","PATTUKOTTAI","PUDUKKOTTAI","SIRKALI",
            "THANJAVUR","THIRUTHURAIPOONDI","TIRUVARUR"
        ],
        "Tiruchirappalli": [
            "ARIYALUR","BATLAGUNDU","DINDIGUL","LALGUDI","MANAPARAI","MUSURI","NATHAM",
            "ODDANCHATRAM","PALANI","PERAMBALUR","SRIRANGAM","THIRUVERUMBUR","THURAIYUR",
            "TIRUCHI","TIRUCHI EAST","VEDACHANDUR"
        ],
        "Hosur": [
            "DHARMAPURI","HARUR","HOSUR","KRISHNAGIRI","PALACODE"
        ],
        "Salem": [
            "ARAVAKURICHI","ATTUR","KARUR","KULITHALAI","MANMANGALAM","METTUR",
            "NAMAKKAL","NAMAKKAL SOUTH","OMALUR","PARAMATHI VELLUR","RASIPURAM",
            "SANKAGIRI","TIRUCHENGODE","VALAPPADI"
        ],
        "Vellore": [
            "AMBUR","ARAKONAM","ARANI","CHEYYAR","GUDIYATHAM","KANCHEEPURAM","RANIPET",
            "THIRUPATTUR","TIRUVANNAMALAI","VANIYAMBADI","VELLORE"
        ]
    }

    # --- Build Reverse Map ---
    rto_to_district = {rto.upper(): d for d, rtos in district_map.items() for rto in rtos}
    known_rtos = list(rto_to_district.keys())

    # --- Normalize Function ---
    def normalize_rto_name(name):
        name = str(name).upper().strip()
        name = re.sub(r"RTO|DISTRICT|REGIONAL|OFFICE|\(.*?\)", "", name)
        name = re.sub(r"[^A-Z ]", "", name)
        name = re.sub(r"\s+", " ", name).strip()
        return name

    # --- Apply normalization ---
    df["RTO_CLEAN"] = df["RTO"].apply(normalize_rto_name)

    # --- Fuzzy match ---
    def map_to_district(clean_name):
        if clean_name in rto_to_district:
            return rto_to_district[clean_name]
        match = get_close_matches(clean_name, known_rtos, n=1, cutoff=0.8)
        return rto_to_district[match[0]] if match else "Other"

    df["District"] = df["RTO_CLEAN"].apply(map_to_district)

    # --- Group totals ---



    df["OEM_UPPER"] = df["OEM"].str.upper()

    # --- Define brand groups ---
    brand_groups = {
        "MARUTI SUZUKI INDIA LTD": ["MARUTI SUZUKI INDIA LTD"],
        "HYUNDAI MOTOR INDIA LTD": ["HYUNDAI MOTOR INDIA LTD"],
        "Tata Motors": [
            "TATA MOTORS LTD",
            "TATA MOTORS PASSENGER VEHICLES LTD",
            "TATA PASSENGER ELECTRIC MOBILITY LTD"
        ],
        "HONDA CARS INDIA LTD": ["HONDA CARS INDIA LTD"],
        "KIA MOTORS INDIA PVT LTD": ["KIA MOTORS INDIA PVT LTD"],
        "RENAULT INDIA PVT LTD": ["RENAULT INDIA PVT LTD"],
        "TOYOTA KIRLOSKAR MOTOR PVT LTD": ["TOYOTA KIRLOSKAR MOTOR PVT LTD"],
        "MAHINDRA & MAHINDRA LIMITED": ["MAHINDRA & MAHINDRA LIMITED","MAHINDRA ELECTRIC AUTOMOBILE LTD"],
        "SKODA AUTO VOLKSWAGEN INDIA PVT LTD": ["SKODA AUTO VOLKSWAGEN INDIA PVT LTD"],
        "JSW MG MOTOR INDIA PVT LTD": ["JSW MG MOTOR INDIA PVT LTD"],
        "NISSAN MOTOR INDIA PVT LTD": ["NISSAN MOTOR INDIA PVT LTD"],
        "PCA AUTOMOBILES INDIA PVT LTD": ["PCA AUTOMOBILES INDIA PVT LTD"],
        "BYD INDIA PRIVATE LIMITED": ["BYD INDIA PRIVATE LIMITED"],
    }

    # --- Compute total per RTO ---
    rto_totals = (
        df.groupby(["District", "RTO_CLEAN"])["Total"]
        .sum()
        .reset_index()
        .rename(columns={"Total": "Total"})
    )

    # --- Compute totals for each brand ---
    brand_dfs = []
    for brand_name, oem_list in brand_groups.items():
        temp = (
            df[df["OEM_UPPER"].isin(oem_list)]
            .groupby(["District", "RTO_CLEAN"])["Total"]
            .sum()
            .reset_index()
            .rename(columns={"Total": brand_name})
        )
        brand_dfs.append(temp)




    oem_cols = [
        "MARUTI SUZUKI INDIA LTD",
        "HYUNDAI MOTOR INDIA LTD",
        "Tata Motors",
        "HONDA CARS INDIA LTD",
        "KIA MOTORS INDIA PVT LTD",
        "RENAULT INDIA PVT LTD",
        "TOYOTA KIRLOSKAR MOTOR PVT LTD",
        "MAHINDRA & MAHINDRA LIMITED",
        "SKODA AUTO VOLKSWAGEN INDIA PVT LTD",
        "JSW MG MOTOR INDIA PVT LTD",
        "NISSAN MOTOR INDIA PVT LTD",
        "PCA AUTOMOBILES INDIA PVT LTD",
        "BYD INDIA PRIVATE LIMITED"
    ]

    # Rank Tata Motors among all OEMs for each row


    merged = rto_totals.copy()
    for temp in brand_dfs:
        merged = merged.merge(temp, on=["District", "RTO_CLEAN"], how="left")
    for col in merged.columns:
        if col not in ["District", "RTO_CLEAN"]:
            merged[col] = merged[col].fillna(0).astype(int)
    merged["MS"] = (merged["Tata Motors"] / merged["Total"] * 100).round(2)
    final_cols = [
        "RTO_CLEAN", "District",
        "MARUTI SUZUKI INDIA LTD", "HYUNDAI MOTOR INDIA LTD", "Tata Motors",
        "HONDA CARS INDIA LTD", "KIA MOTORS INDIA PVT LTD", "RENAULT INDIA PVT LTD",
        "TOYOTA KIRLOSKAR MOTOR PVT LTD", "MAHINDRA & MAHINDRA LIMITED",
        "SKODA AUTO VOLKSWAGEN INDIA PVT LTD", "JSW MG MOTOR INDIA PVT LTD",
        "NISSAN MOTOR INDIA PVT LTD", "PCA AUTOMOBILES INDIA PVT LTD",
        "BYD INDIA PRIVATE LIMITED", "Total", "MS","Rank_Tata"
    ]
    merged["Rank_Tata"] = merged[oem_cols].rank(axis=1, ascending=False)["Tata Motors"].astype(int)
    merged = merged[final_cols].rename(columns={"RTO_CLEAN": "RTO"})
    print(merged)




    from datetime import datetime

    # Optional: align column names you want in the CSV
    out = merged.rename(columns={
        "District": "district",
        "RTO_CLEAN": "rto",
        "Total": "total",
        "TATA_Total": "tata_total",
        "MS": "ms",
        "Rank_Tata": "rank_tata"
    })

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    csv_path = f"rto_tata_ms_{ts}.csv"
    out.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"CSV written -> {csv_path}")


    import os
    from supabase import create_client
    import dotenv
    from datetime import datetime, timezone
    dotenv.load_dotenv()
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Missing SUPABASE_URL or SUPABASE_KEY env vars.")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    payload = (
        out.assign(created_at=datetime.now(timezone.utc).isoformat())
        .to_dict(orient="records")
    )


    res = supabase.table("rto_pv_and_ev").upsert(payload).execute()
    print("Inserted/updated rows:", len(payload))