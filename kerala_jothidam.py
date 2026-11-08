"""
Kerala Vedic Astrology Engine (அகத்தியர் அருளிய மணிகண்ட கேரள சோதிடம்)
Based on classical Tamil astrological rules and manuscripts:
- Mani Kanda Kerala Jothidam (Agasthya Tamil - Shanmugananda Book Depot)
- Classical Tamil Jothidam Principles (Hariram Thejus)
Strictly adheres to dual English + Tamil output with 0 Devanagari characters.
"""

from typing import Dict, List, Any

# Rashi metadata
RASHIS_INFO = [
    {"id": 0, "name": "Aries", "tamil": "மேஷம்", "lord": "Mars", "mobility": "Chara (சரம்)", "element": "Fire (நெருப்பு)"},
    {"id": 1, "name": "Taurus", "tamil": "ரிஷபம்", "lord": "Venus", "mobility": "Sthira (ஸ்திரம்)", "element": "Earth (நிலம்)"},
    {"id": 2, "name": "Gemini", "tamil": "மிதுனம்", "lord": "Mercury", "mobility": "Ubhaya (உபயம்)", "element": "Air (காற்று)"},
    {"id": 3, "name": "Cancer", "tamil": "கடகம்", "lord": "Moon", "mobility": "Chara (சரம்)", "element": "Water (நீர்)"},
    {"id": 4, "name": "Leo", "tamil": "சிம்மம்", "lord": "Sun", "mobility": "Sthira (ஸ்திரம்)", "element": "Fire (நெருப்பு)"},
    {"id": 5, "name": "Virgo", "tamil": "கன்னி", "lord": "Mercury", "mobility": "Ubhaya (உபயம்)", "element": "Earth (நிலம்)"},
    {"id": 6, "name": "Libra", "tamil": "துலாம்", "lord": "Venus", "mobility": "Chara (சரம்)", "element": "Air (காற்று)"},
    {"id": 7, "name": "Scorpio", "tamil": "விருச்சிகம்", "lord": "Mars", "mobility": "Sthira (ஸ்திரம்)", "element": "Water (நீர்)"},
    {"id": 8, "name": "Sagittarius", "tamil": "தனுசு", "lord": "Jupiter", "mobility": "Ubhaya (உபயம்)", "element": "Fire (நெருப்பு)"},
    {"id": 9, "name": "Capricorn", "tamil": "மகரம்", "lord": "Saturn", "mobility": "Chara (சரம்)", "element": "Earth (நிலம்)"},
    {"id": 10, "name": "Aquarius", "tamil": "கும்பம்", "lord": "Saturn", "mobility": "Sthira (ஸ்திரம்)", "element": "Air (காற்று)"},
    {"id": 11, "name": "Pisces", "tamil": "மீனம்", "lord": "Jupiter", "mobility": "Ubhaya (உபயம்)", "element": "Water (நீர்)"}
]

PLANET_TAMIL_NAMES = {
    "Sun": "சூரியன்",
    "Moon": "சந்திரன்",
    "Mars": "செவ்வாய்",
    "Mercury": "புதன்",
    "Jupiter": "குரு",
    "Venus": "சுக்கிரன்",
    "Saturn": "சனி",
    "Rahu": "ராகு",
    "Ketu": "கேது",
    "Ascendant": "லக்னம்"
}

# 12 Bhava Metadata based on Mani Kanda Kerala Jothidam Chapters
BHAVA_CHAPTER_NAMES = [
    {
        "house": 1,
        "name": "Tanu Bhava (1st House)",
        "tamil": "லக்ன பாவகம் (உடல், அறிவு, கம்பீரம்)",
        "chapter": "உயிர் & கல்ப காண்டம்",
        "significations": "Vitality, appearance, mental acumen, longevity and self-realization (உடல் ஆரோக்கியம், குணம், சுயமுயற்சி, ஆயுள் பலம்)."
    },
    {
        "house": 2,
        "name": "Dhana Bhava (2nd House)",
        "tamil": "தன பாவகம் (தனலாபம், குடும்பம், வாக்கு)",
        "chapter": "தனக்காண்டம் (அத்தியாயம் 49 & 55)",
        "significations": "Accumulated wealth, financial assets, speech eloquence, and family peace (தனலாபம், சொத்து சேருதல், இனிய வாக்கு, குடும்ப ஐஸ்வர்யம்)."
    },
    {
        "house": 3,
        "name": "Sahodara Bhava (3rd House)",
        "tamil": "சகோதர பாவகம் (தைரியம், வெற்றி, முயற்சி)",
        "chapter": "சகோதரகாண்டம் (அத்தியாயம் 58)",
        "significations": "Courage, valor, younger siblings, artistic skills and triumphant effort (தைரிய வீரியம், இளைய சகோதரன், தகவல் தொடர்பு, கலை ஈடுபாடு)."
    },
    {
        "house": 4,
        "name": "Mathru & Sukha Bhava (4th House)",
        "tamil": "மாதுரு & சுக பாவகம் (தாய், பூமி, வாகனம், சுகம்)",
        "chapter": "மாதுருகாண்டம் (அத்தியாயம் 59)",
        "significations": "Mother's blessings, real estate, luxurious conveyances, domestic happiness and education (தாய் அன்பு, மனை யோகம், வாகன வசதி, கல்வி)."
    },
    {
        "house": 5,
        "name": "Putra & Purva Punya Bhava (5th House)",
        "tamil": "புத்திர & பூர்வ புண்ணிய பாவகம் (குழந்தைகள், அறிவு, தெய்வ அருள்)",
        "chapter": "வெகுபுத்திர காண்டம் (அத்தியாயம் 56)",
        "significations": "Progeny vitality, past-life merits, creative intellect, mantra siddhi and divine grace (புத்திர பாக்கியம், பூர்வ புண்ணியம், தெய்வ பக்தி, ஆழ்ந்த புத்தி)."
    },
    {
        "house": 6,
        "name": "Roga & Satru Bhava (6th House)",
        "tamil": "ரோக & சத்ரு பாவகம் (நோய் எதிர்ப்பு, கடன் வெற்றி, பணி)",
        "chapter": "ரோககாண்டம் (அத்தியாயம் 51 & 54)",
        "significations": "Immunity, overcoming debts, triumph over competitors and professional diligence (ரோகமின்மை, எதிரிகள் வீழ்ச்சி, கடன் நீங்குதல், விடாமுயற்சி)."
    },
    {
        "house": 7,
        "name": "Kalathra Bhava (7th House)",
        "tamil": "களத்திர பாவகம் (வாழ்க்கை துணை, தாம்பத்தியம், கூட்டு)",
        "chapter": "களத்திர காண்டம் (அத்தியாயம் 61)",
        "significations": "Spousal compatibility, marital bliss, public prestige, partnerships and travel (வாழ்க்கைத் துணை, தாம்பத்திய ஒற்றுமை, நற்பெயர், கூட்டுத் தொழில்)."
    },
    {
        "house": 8,
        "name": "Ayur & Randhra Bhava (8th House)",
        "tamil": "ஆயுள் பாவகம் (தீர்க்காயுள், திடீர் அதிர்ஷ்டம், மறைபொருள்)",
        "chapter": "ஆயுள் காண்டம் (அத்தியாயம் 42 & 44)",
        "significations": "Life span, unexpected windfalls, occult insights, resilience and transformation (தீர்க்காயுள், எதிர்பாராத தனலாபம், ஆன்மீக ஞானம், ஆபத்து விலகுதல்)."
    },
    {
        "house": 9,
        "name": "Bhagya & Pithru Bhava (9th House)",
        "tamil": "பாக்கிய & பிதுரு பாவகம் (தந்தை, பாக்கிய யோகம், தர்மம்)",
        "chapter": "பிதுருகாண்டம் (அத்தியாயம் 60)",
        "significations": "Father's guidance, dharma, righteous fortune, pilgrimage and spiritual blessings (தந்தை வழி ஆசி, பாக்கிய பலம், அறநெறி, ஆன்மீக மேன்மை)."
    },
    {
        "house": 10,
        "name": "Karma & Jeevana Bhava (10th House)",
        "tamil": "ஜீவன & கர்ம பாவகம் (தொழில் மேன்மை, அரசு மரியாதை, அதிகாரம்)",
        "chapter": "தானாதி பலக்காண்டம் (அத்தியாயம் 62)",
        "significations": "Career zenith, leadership rank, government honor, professional renown and executive mastery (தொழில் வெற்றி, அரசு கௌரவம், ஆளுமை, சமூக அந்தஸ்து)."
    },
    {
        "house": 11,
        "name": "Labha Bhava (11th House)",
        "tamil": "லாப பாவகம் (சர்வ லாபம், ஆசை நிறைவேறுதல், மூத்த சகோதரன்)",
        "chapter": "தனலாப காண்டம் (அத்தியாயம் 50)",
        "significations": "All-round financial profits, realization of ambitions, influential elder siblings and network gains (அனைத்து காரியங்களிலும் லாபம், அபரிமித வரவு, செல்வாக்கு)."
    },
    {
        "house": 12,
        "name": "Moksha & Vraya Bhava (12th House)",
        "tamil": "விரய & மோட்ச பாவகம் (சுப விரயம், தூர தேச யோகம், மோட்சம்)",
        "chapter": "மோட்ச காண்டம்",
        "significations": "Auspicious expenditures, foreign voyages, philanthropic generosity, tranquil sleep and ultimate liberation (சுப விரயம், கடல் கடந்த வெற்றி, நிம்மதியான தூக்கம், மோட்சம்)."
    }
]


def analyze_kerala_jothidam(full_analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes Agastya Mani Kanda Kerala Jothidam Yogas, 12 Bhava Predictions,
    and Longevity/Dosha assessments directly from chart positions.
    """
    planets_list = full_analysis_data.get("planets", [])
    div_charts = full_analysis_data.get("divisional_charts", {})
    
    # Map planets by key
    planets_by_key = {}
    for p in planets_list:
        key = p.get("key") or p.get("name")
        planets_by_key[key] = p
        
    asc_info = planets_by_key.get("Ascendant") or planets_by_key.get("Lagna")
    if not asc_info:
        return {}

    lagna_rasi = asc_info.get("rasi_id", 0)

    # 1. Compute houses (1-12) for all planets
    planet_houses = {}
    planet_rasis = {}
    for k, p in planets_by_key.items():
        r_id = p.get("rasi_id", 0)
        h_num = ((r_id - lagna_rasi) % 12) + 1
        planet_houses[k] = h_num
        planet_rasis[k] = r_id

    # 2. Compute 12 Bhavas and their Lords
    bhavas_prediction = []
    house_planets = {h: [] for h in range(1, 13)}
    for k, h in planet_houses.items():
        if k not in ("Ascendant", "Lagna", "Uranus", "Neptune", "Pluto"):
            house_planets[h].append(k)

    for bhava_meta in BHAVA_CHAPTER_NAMES:
        h_num = bhava_meta["house"]
        h_rasi_id = (lagna_rasi + h_num - 1) % 12
        r_info = RASHIS_INFO[h_rasi_id]
        lord_name = r_info["lord"]
        lord_house = planet_houses.get(lord_name, 1)
        lord_planet_obj = planets_by_key.get(lord_name, {})
        lord_dignity = lord_planet_obj.get("dignity", "Neutral")
        
        # Placed planets in this house
        occupants = house_planets.get(h_num, [])
        occupants_tamil = [f"{p} ({PLANET_TAMIL_NAMES.get(p, p)})" for p in occupants]
        
        # Interpretive verse based on lord placement & dignity
        prediction_text = generate_kerala_bhava_verse(
            h_num, lord_name, lord_house, lord_dignity, occupants
        )

        bhavas_prediction.append({
            "house_number": h_num,
            "bhava_name": bhava_meta["name"],
            "bhava_tamil": bhava_meta["tamil"],
            "chapter": bhava_meta["chapter"],
            "sign_name": r_info["name"],
            "sign_tamil": r_info["tamil"],
            "lord_name": lord_name,
            "lord_tamil": PLANET_TAMIL_NAMES.get(lord_name, lord_name),
            "lord_placed_house": lord_house,
            "lord_dignity": lord_dignity,
            "occupants": occupants_tamil,
            "significations": bhava_meta["significations"],
            "prediction": prediction_text
        })

    # 3. Detect Rare Kerala Yogas (அகத்தியர் அருளிய மணிகண்ட கேரள யோகங்கள்)
    kerala_yogas = detect_kerala_yogas(
        planet_houses, planet_rasis, planets_by_key, lagna_rasi, div_charts
    )

    # 4. Longevity, Badhaka, Maraka & Dosha Nivarthi (ஆயுள் & தோஷ கணிதம்)
    longevity_dosha = evaluate_longevity_and_maraka(
        lagna_rasi, planet_houses, planet_rasis, planets_by_key
    )

    return {
        "source": "Mani Kanda Kerala Jothidam (அகத்தியர் அருளிய மணிகண்ட கேரள சோதிடம்)",
        "kerala_yogas": kerala_yogas,
        "bhava_predictions": bhavas_prediction,
        "longevity_and_dosha": longevity_dosha
    }


def generate_kerala_bhava_verse(house_num: int, lord_name: str, lord_house: int,
                                lord_dignity: str, occupants: List[str]) -> Dict[str, str]:
    """Generates Tamil and English classical predictive commentary according to Mani Kanda Kerala Jothidam."""
    lord_tamil = PLANET_TAMIL_NAMES.get(lord_name, lord_name)
    is_kendra = lord_house in (1, 4, 7, 10)
    is_trikona = lord_house in (1, 5, 9)
    is_dusthana = lord_house in (6, 8, 12)
    is_upachaya = lord_house in (3, 6, 10, 11)

    # General strength assessment
    if is_kendra or is_trikona or "Own" in lord_dignity or "Exalted" in lord_dignity:
        strength_en = "Highly Auspicious (சுப பலம்)"
        tamil_verse = f"{house_num}-ஆம் பாவாதிபதி {lord_tamil} {lord_house}-ஆம் இடத்தில் பலம் பெற்று அமர்ந்துள்ளார். மணிகண்ட கேரள விதிகளின்படி, இந்த பாவகத்தின் காரகத்துவங்கள் சிறந்து விளங்கி நற்பலன்களையும் மேன்மைகளையும் வழங்கும்."
        english_desc = f"Lord of {house_num}th house ({lord_name}) is strongly disposed in {lord_house}th house ({lord_dignity}). Promises auspicious expansion, prosperity, and fulfillment in this sphere of life."
    elif is_dusthana:
        strength_en = "Mixed / Overcoming Trials (சுமாரான பலன் - விடாமுயற்சி தேவை)"
        tamil_verse = f"{house_num}-ஆம் பாவாதிபதி {lord_tamil} {lord_house}-ஆம் மறைவு ஸ்தானத்தில் அமர்ந்துள்ளார். ஆரம்பத்தில் சில சவால்கள் ஏற்பட்டாலும், பின்னர் தகுந்த உழைப்பாலும் இறை வழிபாட்டினாலும் சுப யோகமாக மாறும்."
        english_desc = f"Lord of {house_num}th house ({lord_name}) occupies a dusthana ({lord_house}th house). Initial efforts face hurdles before yielding stability."
    else:
        strength_en = "Favorable (நன்மையான பலன்)"
        tamil_verse = f"{house_num}-ஆம் பாவாதிபதி {lord_tamil} {lord_house}-ஆம் வீட்டில் அமர்ந்துள்ளார். சுப கிரகங்களின் ஆசியுடன் நற்பலன்கள் கிட்டும்."
        english_desc = f"Lord of {house_num}th house ({lord_name}) is located in {lord_house}th house, indicating progressive gains and favorable developments."

    # Specific verse enhancements for key chapters
    if house_num == 1:
        tamil_detail = "மணிகண்ட கேரள உயிர் காண்டம்: லக்னாதிபதி பலத்தால் திடமான உடல்வாகு, நீண்ட ஆயுள், எதிலும் அஞ்சாத மனோபலம் உண்டாகும்."
    elif house_num == 2:
        tamil_detail = "தனக்காண்டம் (அத்தியாயம் 49): தன ஸ்தான பலத்தால் செல்வச் சேர்க்கை, வாக்கு நாணயம், தொழில் மூலம் சீரான வரவு கிட்டும்."
    elif house_num == 3:
        tamil_detail = "சகோதரகாண்டம் (அத்தியாயம் 58): விடாமுயற்சி, தைரியம், புதிய முயற்சிகளில் வெற்றி காணும் ஆற்றல் அமையும்."
    elif house_num == 4:
        tamil_detail = "மாதுருகாண்டம் (அத்தியாயம் 59): மாதுரு ஆசி, மனை, பூமி யோகம் மற்றும் வசதியான வாகன சேர்க்கை உண்டாகும்."
    elif house_num == 5:
        tamil_detail = "வெகுபுத்திர காண்டம் (அத்தியாயம் 56): பூர்வ புண்ணிய பலம், நுண்ணிய அறிவு, சமுதாயத்தில் நற்பெயர் கிட்டும்."
    elif house_num == 6:
        tamil_detail = "ரோககாண்டம் (அத்தியாயம் 51): நோய் எதிர்ப்பு சக்தி, கடன் மற்றும் எதிரிகளை நேர்மையால் வெல்லும் பலம்."
    elif house_num == 7:
        tamil_detail = "களத்திர காண்டம் (அத்தியாயம் 61): நற்குணமுள்ள வாழ்க்கை துணை, இல்லறத்தில் இணக்கமான தாம்பத்திய அமைதி."
    elif house_num == 8:
        tamil_detail = "ஆயுள் காண்டம் (அத்தியாயம் 44): தீர்க்காயுள் அனுகூலம், மறைமுக ஆபத்துகளில் இருந்து இறை பாதுகாப்பு."
    elif house_num == 9:
        tamil_detail = "பிதுருகாண்டம் (அத்தியாயம் 60): தந்தை வழி பெருமை, தர்ம சிந்தனை, குரு மற்றும் பெரியோர்களின் மேலான ஆசிகள்."
    elif house_num == 10:
        tamil_detail = "தானாதி பலக்காண்டம் (அத்தியாயம் 62): தொழில் உயர்வு, அரசு / நிர்வாக மரியாதை, தலைமைப் பண்புகள்."
    elif house_num == 11:
        tamil_detail = "தனலாப காண்டம் (அத்தியாயம் 50): அனைத்து முயற்சிகளிலும் தொடர் லாபம், நன்மைகள் அபரிமிதமாக சேரும்."
    else:
        tamil_detail = "மோட்ச காண்டம்: ஆன்மீக நாட்டமும் சுப காரியங்களுக்கான செலவுகளும் அமையும்."

    return {
        "strength": strength_en,
        "tamil": f"{tamil_verse} {tamil_detail}",
        "english": english_desc
    }


def detect_kerala_yogas(planet_houses: Dict[str, int], planet_rasis: Dict[str, int],
                        planets_by_key: Dict[str, Any], lagna_rasi: int,
                        div_charts: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Detects classical Yogas from Mani Kanda Kerala Jothidam."""
    detected = []

    h_sun = planet_houses.get("Sun", 0)
    h_moon = planet_houses.get("Moon", 0)
    h_mars = planet_houses.get("Mars", 0)
    h_merc = planet_houses.get("Mercury", 0)
    h_jup = planet_houses.get("Jupiter", 0)
    h_ven = planet_houses.get("Venus", 0)
    h_sat = planet_houses.get("Saturn", 0)

    r_sun = planet_rasis.get("Sun", 0)
    r_moon = planet_rasis.get("Moon", 0)
    r_jup = planet_rasis.get("Jupiter", 0)
    r_ven = planet_rasis.get("Venus", 0)

    # Lagna Lord
    lagna_lord_name = RASHIS_INFO[lagna_rasi]["lord"]
    h_lagna_lord = planet_houses.get(lagna_lord_name, 0)
    
    # 9th Lord
    ninth_rasi = (lagna_rasi + 8) % 12
    ninth_lord_name = RASHIS_INFO[ninth_rasi]["lord"]
    h_ninth_lord = planet_houses.get(ninth_lord_name, 0)

    # 1. Bheri Yoga (பேரியோகம் - Chapter 18)
    # Jupiter, Venus and Lagna Lord in Kendras/Trikonas, and 9th lord strong
    if (h_jup in (1, 4, 5, 7, 9, 10) and
        h_ven in (1, 4, 5, 7, 9, 10) and
        h_lagna_lord in (1, 4, 5, 7, 9, 10) and
        h_ninth_lord in (1, 4, 5, 7, 9, 10, 11)):
        detected.append({
            "name": "Bheri Yoga (பேரியோகம்)",
            "category": "Kerala Royal Yoga (ராஜயோகம்)",
            "tamil_name": "பேரியோகம் (மணிகண்ட கேரளம் அத்தியாயம் 18)",
            "description": "Jupiter, Venus, and Lagna Lord in quadrants/trines with a strong 9th lord. Bestows royal honors, widespread fame, enduring wealth, and profound joy (பேரியோகமுடையோன் பெரும் செல்வந்தன், நற்குணவான், மன்னன் போல் வாழ்வான்).",
            "is_present": True
        })

    # 2. Gaja Yoga (கெஜயோகம் / கஜயோகம் - Chapter 20)
    # 9th lord in 9th, or Moon and Jupiter in mutually auspicious angles
    rel_moon_jup = ((planet_rasis.get("Jupiter", 0) - planet_rasis.get("Moon", 0)) % 12) + 1
    if (h_ninth_lord == 9 or rel_moon_jup in (1, 4, 5, 7, 9, 10)):
        detected.append({
            "name": "Gaja Yoga (கெஜயோகம்)",
            "category": "Kerala Sovereign Yoga (வெற்றி யோகம்)",
            "tamil_name": "கெஜயோகம் (மணிகண்ட கேரளம் அத்தியாயம் 20)",
            "description": "Auspicious mutual alignment of Jupiter and Moon or fortified 9th house. Grants commanding authority, executive victory over adversaries, and noble esteem (யானைப்படை கொண்ட மன்னனைப்போல எதிலும் வெற்றி பெறுவார்).",
            "is_present": True
        })

    # 3. Samrajya Yoga (சாம்ப்ராஜ்யயோகம் - Chapter 21)
    # 2nd, 9th, 10th or 11th lord exalted or in own house, with Lagna lord in Kendra
    second_rasi = (lagna_rasi + 1) % 12
    second_lord = RASHIS_INFO[second_rasi]["lord"]
    tenth_rasi = (lagna_rasi + 9) % 12
    tenth_lord = RASHIS_INFO[tenth_rasi]["lord"]
    eleventh_rasi = (lagna_rasi + 10) % 12
    eleventh_lord = RASHIS_INFO[eleventh_rasi]["lord"]

    lords_to_check = [second_lord, ninth_lord_name, tenth_lord, eleventh_lord]
    has_exalted_or_own = any(
        "Own" in planets_by_key.get(l, {}).get("dignity", "") or
        "Exalted" in planets_by_key.get(l, {}).get("dignity", "")
        for l in lords_to_check
    )
    if h_lagna_lord in (1, 4, 7, 10) and has_exalted_or_own:
        detected.append({
            "name": "Samrajya Yoga (சாம்ப்ராஜ்யயோகம்)",
            "category": "Imperial Sovereignty Yoga",
            "tamil_name": "சாம்ப்ராஜ்யயோகம் (மணிகண்ட கேரளம் அத்தியாயம் 21)",
            "description": "Lagna lord in quadrant while wealth or fortune lords are fortified. Bestows immense leadership, empire-building abilities, and continuous societal respect (சாம்ப்ராஜ்ய யோகத்தால் பெரும் ஆளுமை, செல்வம், சமூக மதிப்பு கிட்டும்).",
            "is_present": True
        })

    # 4. Sivikai Yoga (சிவிகையோகம் / Palanquin & Vehicle Yoga - Chapter 39)
    # Benefics in 4th, 5th, or 9th houses
    benefics_in_comfort = sum(1 for h in [h_jup, h_ven, h_merc] if h in (4, 5, 9))
    if benefics_in_comfort >= 2 or h_lagna_lord == 4:
        detected.append({
            "name": "Sivikai Yoga (சிவிகையோகம்)",
            "category": "Luxury & Vehicle Yoga (சுகபோக யோகம்)",
            "tamil_name": "சிவிகையோகம் (மணிகண்ட கேரளம் அத்தியாயம் 39)",
            "description": "Benefics occupying 4th/5th/9th houses or Lagna lord in 4th. Grants comfortable conveyances, luxury vehicles, stately residences, and peaceful contentment (சிவிகை ஏறும் பாக்கியம், நவீன வாகன யோகம், மனை சுகம்).",
            "is_present": True
        })

    # 5. Sakata Yoga (சகடயோகம் - Chapter 33)
    # Moon in 6th, 8th or 12th from Jupiter (and not in Kendra from Lagna)
    rel_pos_jup_moon = ((r_moon - r_jup) % 12) + 1
    if rel_pos_jup_moon in (6, 8, 12) and h_moon not in (1, 4, 7, 10):
        detected.append({
            "name": "Sakata Yoga (சகடயோகம்)",
            "category": "Cyclical Growth Yoga (சக்கர யோகம்)",
            "tamil_name": "சகடயோகம் (மணிகண்ட கேரளம் அத்தியாயம் 33)",
            "description": "Moon placed 6th, 8th or 12th from Jupiter. Fortunes oscillate like a turning wheel; builds great psychological tenacity and late enduring triumph (வாழ்க்கையில் சக்கரத்தைப்போல ஏற்ற இறக்கங்கள் வந்து பின்னர் திடமான நிலை பெறுவர்).",
            "is_present": True
        })

    # 6. Maha Parivartana Yoga (மகா பரிவர்த்தனை யோகம்)
    # Check mutual exchange of house lords between Kendra/Trikona houses (1, 2, 4, 5, 7, 9, 10, 11)
    kendra_trikona_houses = [1, 2, 4, 5, 7, 9, 10, 11]
    for h1 in kendra_trikona_houses:
        h1_rasi = (lagna_rasi + h1 - 1) % 12
        l1 = RASHIS_INFO[h1_rasi]["lord"]
        l1_house = planet_houses.get(l1, 0)
        if l1_house in kendra_trikona_houses and l1_house > h1:
            h2 = l1_house
            h2_rasi = (lagna_rasi + h2 - 1) % 12
            l2 = RASHIS_INFO[h2_rasi]["lord"]
            l2_house = planet_houses.get(l2, 0)
            if l2_house == h1 and l1 != l2:
                detected.append({
                    "name": f"Maha Parivartana Yoga ({l1} & {l2})",
                    "category": "Planetary Mutual Exchange (மகா பரிவர்த்தனை)",
                    "tamil_name": f"மகா பரிவர்த்தனை யோகம் ({PLANET_TAMIL_NAMES.get(l1, l1)} & {PLANET_TAMIL_NAMES.get(l2, l2)})",
                    "description": f"Mutual exchange of signs between lord of house {h1} ({l1}) and lord of house {h2} ({l2}). Mutual reinforcement dramatically uplifts life status and prosperity (இரு சுப வீடுகளின் அதிபதிகள் பரிவர்த்தனை ஆவதால் பெரும் உயர்வும் யோகமும் உண்டாகும்).",
                    "is_present": True
                })

    # 7. Vargottama Planets (வர்கோத்தம யோகம்)
    d1_chart = div_charts.get("D-1", {})
    d9_chart = div_charts.get("D-9", {})
    vargottama_planets = []
    
    if d1_chart and d9_chart:
        d1_south = d1_chart.get("south_indian", [])
        d9_south = d9_chart.get("south_indian", [])
        if len(d1_south) == 12 and len(d9_south) == 12:
            # Map planet to D-1 rasi
            p_d1 = {}
            p_d9 = {}
            for r_idx, box in enumerate(d1_south):
                for p_item in box.get("planets", []):
                    p_d1[p_item.get("key") or p_item.get("name")] = r_idx
            for r_idx, box in enumerate(d9_south):
                for p_item in box.get("planets", []):
                    p_d9[p_item.get("key") or p_item.get("name")] = r_idx

            for p_k in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Ascendant"):
                if p_k in p_d1 and p_k in p_d9 and p_d1[p_k] == p_d9[p_k]:
                    rasi_name = RASHIS_INFO[p_d1[p_k]]["name"]
                    rasi_tamil = RASHIS_INFO[p_d1[p_k]]["tamil"]
                    p_tamil = PLANET_TAMIL_NAMES.get(p_k, p_k)
                    vargottama_planets.append(f"{p_k} ({p_tamil}) in {rasi_name} / {rasi_tamil}")

    if vargottama_planets:
        detected.append({
            "name": f"Vargottama Yoga ({len(vargottama_planets)} Placements)",
            "category": "Navamsa Stability Yoga (வர்கோத்தமம்)",
            "tamil_name": "வர்கோத்தம யோகம் (ராசி & நவாம்ச பலம்)",
            "description": f"Planets occupying identical signs in D-1 (Rasi) and D-9 (Navamsa): {', '.join(vargottama_planets)}. Endows these planets with supreme stability and double auspicious results in their Dasha-Bhuktis (வர்கோத்தமம் பெற்ற கிரகம் இரு மடங்கு சுப பலன்களை வழங்கும்).",
            "is_present": True
        })

    # 8. Subha Kartari Yoga (சுபகர்த்தாரி யோகம்)
    # Lagna 12th house and 2nd house occupied by natural benefics (Jupiter, Venus, Mercury)
    benefics = ("Jupiter", "Venus", "Mercury")
    h2_planets = [k for k, h in planet_houses.items() if h == 2]
    h12_planets = [k for k, h in planet_houses.items() if h == 12]
    has_h2_benefic = any(b in h2_planets for b in benefics)
    has_h12_benefic = any(b in h12_planets for b in benefics)
    if has_h2_benefic and has_h12_benefic:
        detected.append({
            "name": "Subha Kartari Yoga (Lagna)",
            "category": "Divine Shield Yoga (சுபகர்த்தாரி)",
            "tamil_name": "சுபகர்த்தாரி யோகம் (லக்னம் சுப கிரகங்களால் சூழப்படுதல்)",
            "description": "Lagna is hemmed between natural benefics in 12th and 2nd houses. Serves as a divine armor shielding the native from accidents, ill health, and adverse reversals (லக்னம் சுப கிரகங்களுக்கு இடையில் அமைவதால் ஆபத்துகளில் இருந்து காக்கும் தெய்வீக கவசம் உண்டாகும்).",
            "is_present": True
        })

    # 9. Kumuda Yoga & Murasa Yoga (குமுத யோகம் & முரச யோகம் - Chapter 31 & 32)
    # Benefics in odd Kendra/Trikona houses (1, 5, 9)
    if h_jup in (1, 5, 9) or (h_ven in (1, 5, 9) and h_merc in (1, 4, 10)):
        detected.append({
            "name": "Kumuda Yoga (குமுதயோகம்)",
            "category": "Agastya Wisdom & Charisma Yoga",
            "tamil_name": "குமுதயோகம் (மணிகண்ட கேரளம் அத்தியாயம் 31)",
            "description": "Benefics placed in auspicious trines and angles. Bestows deep poetic eloquence, pleasant speech, academic honors, and widespread admiration (குமுத யோகத்தால் சொல்வாக்கு, கலைஞானம், நற்குணம், புகழ் உண்டாகும்).",
            "is_present": True
        })

    return detected


def evaluate_longevity_and_maraka(lagna_rasi: int, planet_houses: Dict[str, int],
                                  planet_rasis: Dict[str, int],
                                  planets_by_key: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates Ayul Kandam (Longevity) and Maraka/Badhaka according to Mani Kanda Kerala Jothidam.
    """
    lagna_info = RASHIS_INFO[lagna_rasi]
    mobility = lagna_info["mobility"]  # Chara, Sthira, Ubhaya

    # 1. Determine Badhaka Sthanam and Badhaka Lord
    # Chara (சரம்): 11th house is Badhaka
    # Sthira (ஸ்திரம்): 9th house is Badhaka
    # Ubhaya (உபயம்): 7th house is Badhaka
    if "Chara" in mobility:
        badhaka_house = 11
        badhaka_rule = "Chara Lagna (சரம்): 11-ஆம் வீடு பாதக ஸ்தானம்"
    elif "Sthira" in mobility:
        badhaka_house = 9
        badhaka_rule = "Sthira Lagna (ஸ்திரம்): 9-ஆம் வீடு பாதக ஸ்தானம்"
    else:
        badhaka_house = 7
        badhaka_rule = "Ubhaya Lagna (உபயம்): 7-ஆம் வீடு பாதக ஸ்தானம்"

    badhaka_rasi_id = (lagna_rasi + badhaka_house - 1) % 12
    badhaka_lord = RASHIS_INFO[badhaka_rasi_id]["lord"]
    badhaka_lord_house = planet_houses.get(badhaka_lord, 1)

    # 2. Determine Maraka Lords (2nd & 7th Lords)
    maraka_2_rasi = (lagna_rasi + 1) % 12
    maraka_2_lord = RASHIS_INFO[maraka_2_rasi]["lord"]
    maraka_7_rasi = (lagna_rasi + 6) % 12
    maraka_7_lord = RASHIS_INFO[maraka_7_rasi]["lord"]

    # 3. Determine Longevity Category (Ayul Kandam - Chapter 42 & 44)
    # Check strengths of: Lagna Lord (1st), 8th Lord (Ayur), and Saturn (Ayushkaraka)
    eighth_rasi = (lagna_rasi + 7) % 12
    eighth_lord = RASHIS_INFO[eighth_rasi]["lord"]
    lagna_lord = lagna_info["lord"]

    h_lagna_lord = planet_houses.get(lagna_lord, 1)
    h_eighth_lord = planet_houses.get(eighth_lord, 1)
    h_saturn = planet_houses.get("Saturn", 1)

    # Count auspicious placements (Kendra/Trikona or 11th or Own/Exalted)
    ausp_count = 0
    for l_name, h_pos in [(lagna_lord, h_lagna_lord), (eighth_lord, h_eighth_lord), ("Saturn", h_saturn)]:
        p_obj = planets_by_key.get(l_name, {})
        dignity = p_obj.get("dignity", "")
        if h_pos in (1, 4, 5, 7, 9, 10, 11) or "Own" in dignity or "Exalted" in dignity:
            ausp_count += 1

    if ausp_count >= 2:
        longevity_class = "Deergayu (தீர்க்காயுள் - Full Longevity 75+ Years)"
        longevity_tamil = "தீர்க்காயுள் (மணிகண்ட கேரளம் அத்தியாயம் 44): லக்னாதிபதி மற்றும் 8-ஆம் அதிபதி, ஆயுள்காரகன் சனி சுப பலம் பெற்றுள்ளதால் நீண்ட ஆயுள், ஆரோக்கியம், தெய்வ பாதுகாப்பு அமையும்."
    elif ausp_count == 1:
        longevity_class = "Madhyayu (மத்தியாயுள் - Medium Longevity 50-75 Years)"
        longevity_tamil = "மத்தியாயுள்: கிரக நிலைகள் சம பலத்துடன் உள்ளதால் தகுந்த ஆரோக்கிய பராமரிப்பு மற்றும் இறை வழிபாட்டின் மூலம் நீண்ட ஆயுள் கிட்டும்."
    else:
        longevity_class = "Alpayu / Arishta Nivarthi Required (அற்பாயுள் - தோஷ நிவர்த்தி)"
        longevity_tamil = "அற்பாயுள் / தோஷ நிவர்த்தி: சுப கிரக பார்வைகள் மற்றும் பரிகாரங்களின் மூலம் ஆயுள் பலம் வலுப்பெறும்."

    # 4. Dosha Nivarthi (Protective Factors - குரு பார்வை & சுப கிரக அருள்)
    # Check if Jupiter aspects Lagna or Moon (5th, 7th, 9th aspect)
    r_jup = planet_rasis.get("Jupiter", 0)
    r_moon = planet_rasis.get("Moon", 0)
    
    jup_aspects_lagna = ((lagna_rasi - r_jup) % 12) in (4, 6, 8)  # 5, 7, 9 houses
    jup_aspects_moon = ((r_moon - r_jup) % 12) in (4, 6, 8) or r_jup == r_moon
    
    protective_factors = []
    if jup_aspects_lagna:
        protective_factors.append("Jupiter aspects Lagna (குரு பார்வை லக்னத்தின் மீது விழுந்து சகல தோஷங்களையும் நீக்குகிறது).")
    if jup_aspects_moon:
        protective_factors.append("Jupiter aspects / conjuncts Moon (குரு பகவான் சந்திரனைப் பார்த்து மன அமைதியையும் ஆயுள் பலத்தையும் கூட்டுகிறார்).")
    if h_lagna_lord in (1, 4, 5, 7, 9, 10):
        protective_factors.append(f"Lagna Lord {lagna_lord} ({PLANET_TAMIL_NAMES.get(lagna_lord)}) sits strongly in Kendra/Trikona (லக்னாதிபதி பலம் பெற்று நிற்பது பெரும் அரணாகும்).")

    if not protective_factors:
        protective_factors.append("Regular recitation of Shiva & Vishnu Mantras or performing temple archana enhances protective shielding (இறை வழிபாடு ஆயுள் பலத்தையும் நற்பலன்களையும் கூட்டும்).")

    return {
        "longevity_classification": longevity_class,
        "longevity_tamil": longevity_tamil,
        "lagna_mobility": mobility,
        "badhaka_house": badhaka_house,
        "badhaka_rule": badhaka_rule,
        "badhaka_sign": RASHIS_INFO[badhaka_rasi_id]["name"],
        "badhaka_sign_tamil": RASHIS_INFO[badhaka_rasi_id]["tamil"],
        "badhaka_lord": f"{badhaka_lord} ({PLANET_TAMIL_NAMES.get(badhaka_lord)}) in House {badhaka_lord_house}",
        "maraka_lords": [
            f"2nd Lord: {maraka_2_lord} ({PLANET_TAMIL_NAMES.get(maraka_2_lord)})",
            f"7th Lord: {maraka_7_lord} ({PLANET_TAMIL_NAMES.get(maraka_7_lord)})"
        ],
        "dosha_nivarthi": protective_factors
    }
