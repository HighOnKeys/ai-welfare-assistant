def get_eligible_schemes(user):
    schemes = []
    notes = {}  # store assumptions/caveats per scheme for transparency

    # PM-KISAN: real rule = owns farmland in own name.
    # Proxy used here: occupation = Farmer. Documented as a simplification.
    if user["occupation"] == "Farmer":
        schemes.append("PM-KISAN")
        notes["PM-KISAN"] = "Based on occupation=Farmer. Final eligibility also requires land ownership records."

    # Ayushman Bharat: two real paths -
    # (1) age 70+ -> eligible regardless of income (2024 update)
    # (2) SECC-2011 deprivation / BPL category (rural/urban)
    # Income alone is NOT the real criterion - using BPL card + age as proxies.
    if user["age"] >= 70:
        schemes.append("Ayushman Bharat")
        notes["Ayushman Bharat"] = "Eligible under age 70+ universal coverage (2024 update)."
    elif user["bpl_card"] == "Yes":
        schemes.append("Ayushman Bharat")
        notes["Ayushman Bharat"] = "Based on BPL/priority household card. Final eligibility checked via SECC-2011 database."

    # PMAY: applicant must not own a pucca house, and falls in EWS/LIG/MIG income band.
    if user["house"] == "No" and user["income"] <= 1800000:
        schemes.append("PMAY")
        notes["PMAY"] = "No pucca house owned + income within EWS/LIG/MIG band."

    # Ujjwala: women from BPL/priority households, not all women.
    if user["gender"] == "Female" and user["bpl_card"] == "Yes":
        schemes.append("Ujjwala")
        notes["Ujjwala"] = "Female + BPL/priority household card."

    # MGNREGA: adult member (18+) of a rural household willing to do manual work.
    if user["rural"] == "Yes" and user["age"] >= 18:
        schemes.append("MGNREGA")
        notes["MGNREGA"] = "Rural household, age 18+."

    # Sukanya Samriddhi: girl child under 10 (account must open before age 10).
    if user["girl_child"] == "Yes":
        schemes.append("Sukanya Samriddhi")
        notes["Sukanya Samriddhi"] = "Girl child under 10 years."

    # PM Shram Yogi Maandhan: unorganised worker, age 18-40, income <= 15,000/month (~1.8L/year).
    if user["occupation"] == "Unorganised Worker" and 18 <= user["age"] <= 40 and user["income"] <= 180000:
        schemes.append("PM Shram Yogi Maandhan")
        notes["PM Shram Yogi Maandhan"] = "Unorganised worker, age 18-40, income <= Rs.15,000/month."

    # PMJJBY: life insurance, age 18-50, requires a bank account (assumed yes).
    if 18 <= user["age"] <= 50:
        schemes.append("PMJJBY")
        notes["PMJJBY"] = "Age 18-50 (assumes applicant has a bank account)."

    return schemes, notes
