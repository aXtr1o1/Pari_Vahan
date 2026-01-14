import pandas as pd

city_mapping = {
  "ADOOR SRTO": "Pathanamthitta",
  "ALANGUDI UO": "Thanjavur",
  "ALANGULAM UO": "Tirunelveli",
  "ALAPPUZHA RTO": "Alappuzha",
  "ALATHUR SRTO": "Palakkad",
  "ALUVA SRTO": "Ernakulam",
  "AMBASAMUTHIRAM UO": "Tirunelveli",
  "AMBATTUR RTO": "Chennai",
  "AMBUR UO": "Vellore",
  "ANGAMALI SRTO": "Ernakulam",
  "ARAKKONAM UO": "Vellore",
  "ARANI RTO": "Vellore",
  "ARANTHANGI UO": "Thanjavur",
  "ARAVAKURICHI UO": "Salem",
  "ARIYALUR RTO": "Tiruchirapalli",
  "ARUPPUKOTTAI UO": "Madurai",
  "ATHANI ARTO": "Belgaum",
  "ATTINGAL RTO": "Thiruvananthapuram",
  "ATTUR RTO": "Salem",
  "AVINASHI UO": "Coimbatore",
  "BAGALKOT  RTO": "Bijapur",
  "BAHOUR": "Pondicherry",
  "BAILHONGAL  RTO": "Belgaum",
  "BANTWALA ARTO": "Mangalore",
  "BASAVAKALYAN ARTO": "Kalaburagi",
  "BATLAGUNDU UO": "Tiruchirapalli",
  "BELLARY  RTO": "Bellary",
  "BENGALURU CENTRAL  RTO": "Bangalore",
  "BENGALURU EAST  RTO": "Bangalore",
  "BENGALURU NORTH  RTO": "Bangalore",
  "BENGALURU SOUTH  RTO": "Bangalore",
  "BENGALURU WEST  RTO": "Bangalore",
  "BHALKI  ARTO": "Kalaburagi",
  "BHAVANI UO": "Erode",
  "BIDAR  RTO": "Kalaburagi",
  "BIJAPUR  RTO": "Bijapur",
  "CHADAYAMANGALA SRTO": "Kollam",
  "CHALAKKUDY SRTO": "Thrissur",
  "CHAMARAJANAGAR  RTO": "Mysore",
  "CHANDAPURA, BENGALURU RTO": "Bangalore",
  "CHANGANACHERRY SRTO": "Kottayam",
  "CHENGALPATTU RTO": "Chennai",
  "CHENGANNUR SRTO": "Kayamkulam",
  "CHENNAI (CENTRAL) RTO": "Chennai",
  "CHENNAI (EAST) RTO": "Chennai",
  "CHENNAI (NORTH) RTO": "Chennai",
  "CHENNAI (NORTH-EAST) RTO": "Chennai",
  "CHENNAI (SOUTH) RTO": "Chennai",
  "CHENNAI (SOUTH-EAST) RTO": "Chennai",
  "CHENNAI (SOUTH-WEST) RTO": "Chennai",
  "CHENNAI (WEST) RTO": "Chennai",
  "CHERTHALA SRTO": "Alappuzha",
  "CHEYYAR UO": "Vellore",
  "CHICKABALLAPUR  RTO": "Chikkaballapur",
  "CHIDAMBARAM RTO": "Cuddalore",
  "CHIKAMANGLUR RTO": "Mangalore",
  "CHIKKODI  RTO": "Belgaum",
  "CHINTAMANI ARTO": "Chikkaballapur",
  "CHITRADURGA  RTO": "Tumkur",
  "CHITTUR SRTO": "Palakkad",
  "COIMBATORE (CENTRAL) RTO": "Coimbatore",
  "COIMBATORE (NORTH) RTO": "Coimbatore",
  "COIMBATORE (SOUTH) RTO": "Coimbatore",
  "COIMBATORE (WEST) RTO": "Coimbatore",
  "CUDDALORE RTO": "Cuddalore",
  "DANDELI ARTO": "Hubli",
  "DAVANAGERE  RTO": "Davanagere",
  "DEVANAHALLI  ARTO": "Bangalore",
  "DEVIKULAM SRTO": "Ernakulam",
  "DHARAPURAM RTO": "Coimbatore",
  "DHARMAPURI RTO": "Hosur",
  "DHARWAD EAST RTO": "Hubli",
  "DHARWAD WEST RTO": "Hubli",
  "DINDIGUL RTO": "Tiruchirapalli",
  "ELECTRONIC CITY  RTO": "Bangalore",
  "ERNAKULAM RTO": "Ernakulam",
  "ERODE (WEST) RTO": "Erode",
  "ERODE RTO": "Erode",
  "GADAG  RTO": "Hubli",
  "GINGEE UO": "Cuddalore",
  "GOKAK  ARTO": "Belgaum",
  "GOPICHETTIPALAYAM RTO": "Erode",
  "GUDALORE UO": "Coimbatore",
  "GUDIYATHAM UO": "Vellore",
  "GUMMIDIPOONDI UO": "Chennai",
  "GURUVAYUR SRTO": "Thrissur",
  "HARUR UO": "Hosur",
  "HASSAN  RTO": "Hassan",
  "HAVERI  RTO": "Hubli",
  "HONNAVAR  ARTO": "Murudeswar",
  "HOSPET  RTO": "Bellary",
  "HOSUR RTO": "Hosur",
  "HUNSUR  ARTO": "Mysore",
  "IDUKKI RTO": "Ernakulam",
  "ILLUPPUR UO": "Thanjavur",
  "IRINJALAKUDA SRTO": "Thrissur",
  "IRITTY SRTO": "Kannur",
  "JAMKHANDI  ARTO": "Bijapur",
  "JNANABHARATHI  RTO": "Bangalore",
  "K G F  ARTO": "Bangalore",
  "KALABURAGI  RTO": "Kalaburagi",
  "KALLAKURICHI RTO": "Cuddalore",
  "KANCHEEPURAM RTO": "Vellore",
  "KANGEYAM UO": "Coimbatore",
  "KANHANGAD SRTO": "Kannur",
  "KANJIRAPPALLY SRTO": "Kottayam",
  "KANNUR RTO": "Kannur",
  "KARAIKAL": "Pondicherry",
  "KARAIKUDI UO": "Madurai",
  "KARUNAGAPPALLY SRTO": "Kollam",
  "KARUR RTO": "Salem",
  "KARWAR  RTO": "Karwar",
  "KASARGODE RTO": "Kannur",
  "KATTAKADA SRTO": "Thiruvananthapuram",
  "KAYAMKULAM SRTO": "Kayamkulam",
  "KAZHAKUTTOM SRTO": "Thiruvananthapuram",
  "KODUNGALLUR SRTO": "Thrissur",
  "KODUVALLY SRTO": "Kozhikode",
  "KOILANDY SRTO": "Kozhikode",
  "KOLAR  RTO": "Bangalore",
  "KOLLAM RTO": "Kollam",
  "KONDOTTY SRTO": "Malappuram",
  "KONNI SRTO": "Pathanamthitta",
  "KOPPAL  RTO": "Bellary",
  "KOTHAMANGALAM SRTO": "Ernakulam",
  "KOTTARAKKARA SRTO": "Kollam",
  "KOTTAYAM RTO": "Kottayam",
  "KOVILPATTI RTO": "Tirunelveli",
  "KOZHIKODE RTO": "Kozhikode",
  "KRISHNAGIRI RTO": "Hosur",
  "KRISHNARAJAPURAM  RTO": "Bangalore",
  "KULITHALI UO": "Salem",
  "KUMARAPALAYAM RTO": "Salem",
  "KUMBAKONAM RTO": "Thanjavur",
  "KUNDRATHUR RTO": "Chennai",
  "KUNNATHUR SRTO": "Kollam",
  "KUTTANADU SRTO": "Alappuzha",
  "LALKUDI UO": "Tiruchirapalli",
  "MADHUGIRI, TUMAKURU ARTO": "Tumkur",
  "MADIKERI  RTO": "Mysore",
  "MADURAI (CENTRAL) RTO": "Madurai",
  "MADURAI (NORTH) RTO": "Madurai",
  "MADURAI (SOUTH) RTO": "Madurai",
  "MADURANTAGAM UO": "Chennai",
  "MAHE": "Pondicherry",
  "MALAPPURAM RTO": "Malappuram",
  "MALLAPPALLY SRTO": "Pathanamthitta",
  "MANANTHAVADY SRTO": "Wayanad",
  "MANAPARAI UO": "Tiruchirapalli",
  "MANDYA  RTO": "Mysore",
  "MANGALORE  RTO": "Mangalore",
  "MANMANGALAM UO": "Salem",
  "MANNARGHAT SRTO": "Palakkad",
  "MANNARGUDI UO": "Thanjavur",
  "MARTHANDAM RTO": "Nagercoil",
  "MATTANCHERRY SRTO": "Ernakulam",
  "MAVELIKKARA SRTO": "Alappuzha",
  "MAYILADUTHURAI RTO": "Thanjavur",
  "MEENAMBAKKAM RTO": "Chennai",
  "MELUR UO": "Madurai",
  "METTUPALAYAM RTO": "Coimbatore",
  "METTUR RTO": "Salem",
  "MUSURI UO": "Tiruchirapalli",
  "MUVATTUPUZHA RTO": "Ernakulam",
  "MYSURU  EAST  RTO": "Mysore",
  "MYSURU WEST  RTO": "Mysore",
  "NAGAMANGALA  RTO": "Mysore",
  "NAGAPATTINAM RTO": "Thanjavur",
  "NAGERCOIL RTO": "Nagercoil",
  "NAMAKKAL (NORTH) RTO": "Salem",
  "NAMAKKAL (SOUTH) RTO": "Salem",
  "NANMANDA SRTO": "Kozhikode",
  "NATHAM UO": "Tiruchirapalli",
  "NEDUMANGADU SRTO": "Thiruvananthapuram",
  "NELAMANGALA  RTO": "Bangalore",
  "NEYVELI UO": "Cuddalore",
  "NEYYATTINKARA SRTO": "Thiruvananthapuram",
  "NILAMBUR SRTO": "Malappuram",
  "NORTH PARUR SRTO": "Ernakulam",
  "ODDANCHATRAM  UO": "Tiruchirapalli",
  "OMALURE UO": "Salem",
  "OOTY RTO": "Coimbatore",
  "OTTAPPALAM SRTO": "Palakkad",
  "OULGARET": "Pondicherry",
  "PALACODE UO": "Hosur",
  "PALAI SRTO": "Kottayam",
  "PALAKKAD RTO": "Palakkad",
  "PALANI RTO": "Tiruchirapalli",
  "PANRUTI UO": "Cuddalore",
  "PARAMAKUDI UO": "Madurai",
  "PARAMATHI VELLURE UO": "Salem",
  "PARASSALA SRTO": "Thiruvananthapuram",
  "PATHANAMTHITTA RTO": "Pathanamthitta",
  "PATHANAPURAM SRTO": "Kollam",
  "PATTAMBI SRTO": "Palakkad",
  "PATTUKOTTAI UNIT OFFICE": "Thanjavur",
  "PAYYANNUR SRTO": "Kannur",
  "PERAMBALUR RTO": "Tiruchirapalli",
  "PERAMBRA SRTO": "Kozhikode",
  "PERINTHALMANNA SRTO": "Perinthalmana",
  "PERUMBAVUR SRTO": "Ernakulam",
  "PERUNDURAI RTO": "Erode",
  "POLLACHI RTO": "Coimbatore",
  "PONNANI SRTO": "Malappuram",
  "POONAMALLEE RTO": "Chennai",
  "PUDUCHERRY": "Pondicherry",
  "PUDUKOTTAI RTO": "Thanjavur",
  "PUNALUR SRTO": "Kollam",
  "PUTTUR  RTO": "Mangalore",
  "RAICHUR  RTO": "Bellary",
  "RAJAPALAYAM UO": "Madurai",
  "RAMANAGAR  RTO": "Bangalore",
  "RAMANATHAPURAM RTO": "Madurai",
  "RAMANATTUKARA (FEROKE) SRTO": "Kozhikode",
  "RAMDURGA ARTO": "Belgaum",
  "RANIBENNUR ARTO": "Hubli",
  "RANIPET RTO": "Vellore",
  "RANNI SRTO": "Pathanamthitta",
  "RASIPURAM UO": "Salem",
  "REDHILLS RTO": "Chennai",
  "REGIONAL TRANSPORT OFFICE BELAGAVI": "Belgaum",
  "RTO CHENNAI (NORTH WEST)": "Chennai",
  "SAGAR  ARTO": "Shimoga",
  "SAKALESHPURA  ARTO": "Mangalore",
  "SALEM (EAST) RTO": "Salem",
  "SALEM (SOUTH) RTO": "Salem",
  "SALEM (WEST) RTO": "Salem",
  "SANKAGIRI RTO": "Salem",
  "SANKARANKOVIL RTO": "Tirunelveli",
  "SATHYAMANGALAM UO": "Erode",
  "SHIMOGA  RTO": "Shimoga",
  "SHOLINGANALLUR RTO": "Chennai",
  "STU AND AUTORIKSHAW,  SHANTHINAGAR RTO": "Bangalore",
  "SIRKALI UO": "Thanjavur",
  "SIRSI  RTO": "Hubli",
  "SIVAGANGAI RTO": "Madurai",
  "SIVAKASI RTO": "Madurai",
  "SRIPERUMBUDUR RTO": "Chennai",
  "SRIRANGAM RTO": "Tiruchirapalli",
  "SRIVILLIPUTHUR RTO": "Madurai",
  "SULTHANBATHERY SRTO": "Wayanad",
  "SULUR UO": "Coimbatore",
  "TAMBARAM RTO": "Chennai",
  "TARIKERE, CHIKKAMAGALURU ARTO": "Mangalore",
  "TENKASI RTO": "Tirunelveli",
  "THALASSERY SRTO": "Kannur",
  "THALIPARAMBA SRTO": "Kannur",
  "THANJAVUR RTO": "Thanjavur",
  "THENI RTO": "Madurai",
  "THIRUCHENDUR RTO": "Tirunelveli",
  "THIRUKALUKUNTRAM UO": "Chennai",
  "THIRUMANGALAM  UO": "Madurai",
  "THIRUPATTUR RTO": "Vellore",
  "THIRUR SRTO": "Malappuram",
  "THIRURANGADI SRTO": "Malappuram",
  "THIRUTHURAIPOONDI UO": "Thanjavur",
  "THIRUTTANI UO": "Chennai",
  "THIRUVALLA SRTO": "Pathanamthitta",
  "THODUPUZHA SRTO": "Ernakulam",
  "THOOTHUKUDI RTO": "Tirunelveli",
  "THRIPRAYAR SRTO": "Thrissur",
  "THRISSUR RTO": "Thrissur",
  "THURAIYUR UO": "Tiruchirapalli",
  "TINDIVANAM RTO": "Cuddalore",
  "TIPTUR  ARTO": "Tumkur",
  "TIRUCHENGODE RTO": "Salem",
  "TIRUCHI RTO": "Tiruchirapalli",
  "TIRUCHI(EAST) RTO": "Tiruchirapalli",
  "TIRUNELVELI RTO": "Tirunelveli",
  "TIRUPPUR (NORTH) RTO": "Tirupur",
  "TIRUPPUR (SOUTH) RTO": "Tirupur",
  "TIRUVALLUR RTO": "Chennai",
  "TIRUVANNAMALAI RTO": "Vellore",
  "TIRUVARUR RTO": "Thanjavur",
  "TIRUVERANBUR UO": "Tiruchirapalli",
  "TRIPUNITHURA SRTO": "Ernakulam",
  "TRIVANDRUM RTO": "Thiruvananthapuram",
  "TUMKUR  RTO": "Tumkur",
  "UDUMALPET RTO": "Coimbatore",
  "UDUMBANCHOLA SRTO": "Ernakulam",
  "UDUPI  RTO": "Mangalore",
  "ULUNDURPET RTO": "Cuddalore",
  "USILAMPATTI UO": "Madurai",
  "UTHAMAPALAYAM UO": "Madurai",
  "UZHAVOOR SRTO": "Kottayam",
  "VADAKARA RTO": "Kozhikode",
  "VADIPATTI UO": "Madurai",
  "VAIKOM SRTO": "Kottayam",
  "VALAPPADI UO": "Salem",
  "VALLIYUR UO": "Tirunelveli",
  "VALPARAI UO": "Coimbatore",
  "VANDIPERIYAR SRTO": "Ernakulam",
  "VANIYAMBADI RTO": "Vellore",
  "VARKALA SRTO": "Thiruvananthapuram",
  "VEDACHANDUR UO": "Tiruchirapalli",
  "VELLARIKUNDU SRTO": "Kannur",
  "VELLORE RTO": "Vellore",
  "VILLIANUR": "Pondicherry",
  "VILUPPURAM RTO": "Cuddalore",
  "VIRUDHACHALAM UO": "Cuddalore",
  "VIRUDHUNAGAR RTO": "Madurai",
  "WADAKKANCHERRY SRTO": "Thrissur",
  "WAYANAD RTO": "Wayanad",
  "YADGIRI  RTO": "Kalaburagi",
  "YALAHANKA  RTO": "Bangalore",
  "YANAM": "Pondicherry"
}

rto_ao_mapping = {
  "ATHANI ARTO": "RO South1",
  "BAGALKOT  RTO": "RO South1",
  "BANTWALA ARTO": "Mangalore",
  "BASAVAKALYAN ARTO": "RO South1",
  "BELLARY  RTO": "RO South1",
  "BENGALURU CENTRAL  RTO": "RO South1",
  "BENGALURU EAST  RTO": "RO South1",
  "BENGALURU NORTH  RTO": "RO South1",
  "BENGALURU SOUTH  RTO": "RO South1",
  "BENGALURU WEST  RTO": "RO South1",
  "BHALKI  ARTO": "RO South1",
  "BIDAR  RTO": "RO South1",
  "BIJAPUR  RTO": "RO South1",
  "CHAMARAJANAGAR  RTO": "RO South1",
  "CHANDAPURA, BENGALURU RTO": "RO South1",
  "CHICKABALLAPUR  RTO": "RO South1",
  "CHIKAMANGLUR RTO": "Mangalore",
  "CHIKKODI  RTO": "RO South1",
  "CHITRADURGA  RTO": "RO South1",
  "DAVANAGERE  RTO": "RO South1",
  "DEVANAHALLI  ARTO": "RO South1",
  "DHARWAD EAST RTO": "RO South1",
  "DHARWAD WEST RTO": "RO South1",
  "ELECTRONIC CITY  RTO": "RO South1",
  "GADAG  RTO": "RO South1",
  "GOKAK  ARTO": "RO South1",
  "HASSAN  RTO": "Mangalore",
  "HAVERI  RTO": "RO South1",
  "HONNAVAR  ARTO": "RO South1",
  "HOSPET  RTO": "RO South1",
  "HUNSUR  ARTO": "RO South1",
  "JNANABHARATHI  RTO": "RO South1",
  "K G F  ARTO": "RO South1",
  "KALABURAGI  RTO": "RO South1",
  "KARWAR  RTO": "RO South1",
  "KOLAR  RTO": "RO South1",
  "KOPPAL  RTO": "RO South1",
  "KRISHNARAJAPURAM  RTO": "RO South1",
  "MADIKERI  RTO": "RO South1",
  "MANDYA  RTO": "RO South1",
  "MANGALORE  RTO": "Mangalore",
  "MYSURU  EAST  RTO": "RO South1",
  "MYSURU WEST  RTO": "RO South1",
  "NELAMANGALA  RTO": "RO South1",
  "PUTTUR  RTO": "Mangalore",
  "RAICHUR  RTO": "RO South1",
  "RAMANAGAR  RTO": "RO South1",
  "SHIMOGA  RTO": "RO South1",
  "SIRSI  RTO": "RO South1",
  "TIPTUR  ARTO": "RO South1",
  "TUMKUR  RTO": "RO South1",
  "UDUPI  RTO": "Mangalore",
  "YADGIRI  RTO": "RO South1",
  "YALAHANKA  RTO": "RO South1",
  "STU AND AUTORIKSHAW,  SHANTHINAGAR RTO": "RO South1",

  "ALUVA SRTO": "RO South3",
  "ANGAMALI SRTO": "RO South3",
  "ATTINGAL RTO": "RO South3",
  "CHALAKKUDY SRTO": "RO South3",
  "ERNAKULAM RTO": "RO South3",
  "GURUVAYUR SRTO": "RO South3",
  "KOLLAM RTO": "RO South3",
  "KOTTAYAM RTO": "RO South3",
  "MALAPPURAM RTO": "RO South3",
  "PALAKKAD RTO": "RO South3",
  "PATHANAMTHITTA RTO": "RO South3",
  "THRISSUR RTO": "RO South3",
  "TRIVANDRUM RTO": "RO South3",

  "IRITTY SRTO": "Kannur",
  "KANNUR RTO": "Kannur",
  "KASARGODE RTO": "Kannur",
  "PAYYANNUR SRTO": "Kannur",
  "THALASSERY SRTO": "Kannur",
  "THALIPARAMBA SRTO": "Kannur",

  "KOZHIKODE RTO": "Kozhikode",
  "VADAKARA RTO": "Kozhikode",
  "WAYANAD RTO": "Kozhikode",

  "PUDUCHERRY": "RO South2",
  "KARAIKAL": "RO South2",
  "MAHE": "RO South2",
  "YANAM": "RO South2",

  "CHENNAI (CENTRAL) RTO": "RO South2",
  "CHENNAI (NORTH) RTO": "RO South2",
  "CHENNAI (SOUTH) RTO": "RO South2",
  "CHENNAI (WEST) RTO": "RO South2",
  "AMBATTUR RTO": "RO South2",
  "TAMBARAM RTO": "RO South2",
  "VELLORE RTO": "RO South2",
  "SALEM (EAST) RTO": "RO South2",
  "SALEM (WEST) RTO": "RO South2",
  "ERODE RTO": "RO South2",

  "COIMBATORE (CENTRAL) RTO": "Coimbatore",
  "COIMBATORE (NORTH) RTO": "Coimbatore",
  "COIMBATORE (SOUTH) RTO": "Coimbatore",
  "TIRUPPUR (NORTH) RTO": "Coimbatore",
  "TIRUPPUR (SOUTH) RTO": "Coimbatore",

  "MADURAI (CENTRAL) RTO": "Madurai",
  "MADURAI (NORTH) RTO": "Madurai",
  "MADURAI (SOUTH) RTO": "Madurai",

  "TIRUNELVELI RTO": "Tirunelveli",
  "TENKASI RTO": "Tirunelveli",
  "THOOTHUKUDI RTO": "Tirunelveli",

  "THANJAVUR RTO": "Thanjavur",
  "KUMBAKONAM RTO": "Thanjavur",
  "NAGAPATTINAM RTO": "Thanjavur",

  "TIRUCHI RTO": "Tiruchirappalli",
  "SRIRANGAM RTO": "Tiruchirappalli",
  "DINDIGUL RTO": "Tiruchirappalli"
}

maker_short_mapping = {
  "MARUTI SUZUKI INDIA LTD": "Maruti",
  "HONDA CARS INDIA LTD": "Honda",
  "HYUNDAI MOTOR INDIA LTD": "Hyundai",
  "JSW MG MOTOR INDIA PVT LTD": "MG",
  "KIA INDIA PRIVATE LIMITED": "KIA",
  "MAHINDRA & MAHINDRA LIMITED": "Mahindra",
  "NISSAN MOTOR INDIA PVT LTD": "Nissan",
  "SKODA AUTO VOLKSWAGEN INDIA PVT LTD": "Skoda",
  "TATA MOTORS PASSENGER VEHICLES LTD": "Tata",
  "TATA PASSENGER ELECTRIC MOBILITY LTD": "Tata",
  "TOYOTA KIRLOSKAR MOTOR PVT LTD": "Toyota",
  "RENAULT INDIA PVT LTD": "Renault",
  "MAHINDRA ELECTRIC AUTOMOBILE LTD": "Mahindra",
  "STELLANTIS AUTOMOBILES INDIA PVT LTD": "PCA",
  "STELLANTIS INDIA PVT LTD": "Fiat",
  "BYD INDIA PRIVATE LIMITED": "BYD",
  "VINFAST AUTO INDIA PVT LTD": "Vinfast",
  "VOLKSWAGEN AG": "VW",
  "TATA MOTORS LTD": "Tata",
  "SKODA AUTO AS": "Skoda"
}


FUEL_GROUP_MAP = {
    "CNG": [
        "CNG ONLY",
        "PETROL/CNG",
        "PETROL(E20)/CNG"
    ],

    "Diesel": [
        "DIESEL"
    ],

    "Petrol": [
        "PETROL",
        "PETROL/ETHANOL"
    ],

    "EV": [
        "ELECTRIC(BOV)",
        "PURE EV"
    ],

    "Petrol-Hybrid": [
        "PETROL/HYBRID",
        "PETROL(E20)/HYBRID"
    ],

    "Diesel-Hybrid": [
        "DIESEL/HYBRID"
    ],

    "Strong-Hybrid": [
        "STRONG HYBRID EV"
    ]
}

fuel_lookup = {
    fuel: group
    for group, fuels in FUEL_GROUP_MAP.items()
    for fuel in fuels
}

def get_financial_year(date):
    if date.month >= 4:
        return f"{date.year}-{str(date.year + 1)[-2:]}"
    else:
        return f"{date.year - 1}-{str(date.year)[-2:]}"
    


def get_financial_quarter(date):
    if date.month in [4, 5, 6]:
        return "Q1"
    elif date.month in [7, 8, 9]:
        return "Q2"
    elif date.month in [10, 11, 12]:
        return "Q3"
    else:
        return "Q4"
def preprocess_master():
    df = pd.read_csv("final_master.csv")

    df = df.drop(columns=["scrape_timestamp"], errors="ignore")


    df = df.rename(columns={
        "Maker": "OEM",
        "district": "cluster",
        "timestamp": "Date"
    })

    if "cluster" not in df.columns:
        district_col = next((c for c in df.columns if c.strip().lower() == "district"), None)
        if district_col:
            df["cluster"] = df[district_col]
        else:
            df["cluster"] = pd.NA


    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, format="mixed",errors="raise")

    # Add city column using city_mapping
    df["city"] = df["RTO"].map(city_mapping)

    # Add AO column using rto_ao_mapping
    df["AO"] = df["RTO"].map(rto_ao_mapping)

    # Add maker_short column using maker_short_mapping
    df["maker_short"] = df["OEM"].map(maker_short_mapping)

    id_cols = [
        "Date", "state","cluster","city","AO","RTO",
        "rto_number", "vehicle_type",
         "OEM", "maker_short"
    ]

    fuel_cols = [c for c in df.columns if c not in id_cols and c != "TOTAL"]


    out = df.melt(
        id_vars=id_cols,
        value_vars=fuel_cols,
        var_name="FuelType",
        value_name="Regn Vol"
    )

    out["Regn Vol"] = pd.to_numeric(out["Regn Vol"], errors="coerce").fillna(0)
    out = out[out["Regn Vol"] > 0]


    out["FuelGroup"] = out["FuelType"].map(fuel_lookup)
    out = out.dropna(subset=["FuelGroup"])


    grouped = (
        out
        .groupby(id_cols + ["FuelGroup"], as_index=False)["Regn Vol"]
        .sum()
    )

    grouped["Zone"] = grouped["state"].map({
        "Karnataka": "S1",
        "Tamil Nadu": "S2",
        "Puducherry": "S2",
        "Kerala": "S3"
    })

    # Financial Year
    grouped["FY"] = grouped["Date"].apply(get_financial_year)

    # Month name
    grouped["month"] = grouped["Date"].dt.strftime("%B")

    # Financial Quarter
    grouped["Qtr"] = grouped["Date"].apply(get_financial_quarter)

    grouped.to_csv("master_preprocessed.csv", index=False)

    print("Saved:", grouped.shape, "-> master_preprocessed.csv")

if __name__ == "__main__":

    preprocess_master()
    print("\nDone!")