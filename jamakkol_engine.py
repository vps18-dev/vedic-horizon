"""
Jamakkol Arudam Engine (ஜாமக்கோள் ஆருடம்)
Classical Horary Astrology Engine based on the authoritative Tamil treatise
'Saamakkol Arudam' by S. Vaithyanathan (Paduka Publications).

Calculates:
1. 8 Day and 8 Night Jaamams with exact local Sunrise & Sunset division.
2. Active Jaamam index (1-8) and ruling Jaamam Lord.
3. 8 Jama Grahas placed in the 8 non-fixed signs (Meena, Makara, Dhanus, Thula, Kanni, Kataka, Mithuna, Mesha).
4. The 4 Fundamental Pillars:
   - Udhayam (உதயம் - Sidereal Ascendant)
   - Arudam (ஆருடம் - Horary Querent Sign)
   - Surya Veedhi (சூரிய வீதி - Mesha / Rishaba / Mithuna based on Sun sign)
   - Kavippu (கவிப்பு - Obstruction Point: (Udhayam + Surya Veedhi - Arudam) % 12)
5. Inner Transit Planets (உள்கட்டம்) and Outer Jama Grahas (வெளிக்கட்டம்) dual-ring mandala.
6. Classical predictive rules: Kariya Siddhi (காரிய சித்தி), Dhatu-Moola-Jeeva, Kala Nirnayam timing, and Kavippu affliction.

STRICT CONSTRAINT: 0 Devanagari characters allowed (English + Tamil only).
"""

import math
import datetime
from typing import Dict, List, Any, Optional, Tuple

# 12 Rasis Metadata
RASI_NAMES_EN = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

RASI_NAMES_TA = [
    "மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்",
    "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்",
    "தனுசு", "மகரம்", "கும்பம்", "மீனம்"
]

RASI_LORDS_EN = [
    "Mars", "Venus", "Mercury", "Moon",
    "Sun", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Saturn", "Jupiter"
]

RASI_LORDS_TA = [
    "செவ்வாய்", "சுக்கிரன்", "புதன்", "சந்திரன்",
    "சூரியன்", "புதன்", "சுக்கிரன்", "செவ்வாய்",
    "குரு", "சனி", "சனி", "குரு"
]

# Chara (Movable), Sthira (Fixed), Ubhaya (Common)
RASI_QUALITIES = [
    {"en": "Chara (Movable)", "ta": "சரம்"},
    {"en": "Sthira (Fixed)", "ta": "ஸ்திரம்"},
    {"en": "Ubhaya (Common)", "ta": "உபயம்"},
    {"en": "Chara (Movable)", "ta": "சரம்"},
    {"en": "Sthira (Fixed)", "ta": "ஸ்திரம்"},
    {"en": "Ubhaya (Common)", "ta": "உபயம்"},
    {"en": "Chara (Movable)", "ta": "சரம்"},
    {"en": "Sthira (Fixed)", "ta": "ஸ்திரம்"},
    {"en": "Ubhaya (Common)", "ta": "உபயம்"},
    {"en": "Chara (Movable)", "ta": "சரம்"},
    {"en": "Sthira (Fixed)", "ta": "ஸ்திரம்"},
    {"en": "Ubhaya (Common)", "ta": "உபயம்"}
]

# Dhatu (Mineral/Metal/Inanimate), Moola (Vegetable/Root/Plant), Jeeva (Living Being/Human/Animal)
# Classical assignment: Chara -> Dhatu, Sthira -> Moola, Ubhaya -> Jeeva
RASI_DMJ = [
    {"en": "Dhatu (Mineral/Metal)", "ta": "தாது (பொருள்/உலோகம்)"},
    {"en": "Moola (Plant/Root)", "ta": "மூலம் (தாவரம்/பயிர்)"},
    {"en": "Jeeva (Living Being)", "ta": "ஜீவன் (உயிர்/மனிதர்)"},
    {"en": "Dhatu (Mineral/Metal)", "ta": "தாது (பொருள்/உலோகம்)"},
    {"en": "Moola (Plant/Root)", "ta": "மூலம் (தாவரம்/பயிர்)"},
    {"en": "Jeeva (Living Being)", "ta": "ஜீவன் (உயிர்/மனிதர்)"},
    {"en": "Dhatu (Mineral/Metal)", "ta": "தாது (பொருள்/உலோகம்)"},
    {"en": "Moola (Plant/Root)", "ta": "மூலம் (தாவரம்/பயிர்)"},
    {"en": "Jeeva (Living Being)", "ta": "ஜீவன் (உயிர்/மனிதர்)"},
    {"en": "Dhatu (Mineral/Metal)", "ta": "தாது (பொருள்/உலோகம்)"},
    {"en": "Moola (Plant/Root)", "ta": "மூலம் (தாவரம்/பயிர்)"},
    {"en": "Jeeva (Living Being)", "ta": "ஜீவன் (உயிர்/மனிதர்)"}
]

# Directions of signs from Lesson 6 / 21
RASI_DIRECTIONS = [
    {"en": "East", "ta": "கிழக்கு"},
    {"en": "South", "ta": "தெற்கு"},
    {"en": "West", "ta": "மேற்கு"},
    {"en": "North-East", "ta": "வடகிழக்கு"},
    {"en": "South-East", "ta": "தென்கிழக்கு"},
    {"en": "South-West", "ta": "தென்மேற்கு"},
    {"en": "North-West", "ta": "வடமேற்கு"},
    {"en": "North-East", "ta": "வடகிழக்கு"},
    {"en": "South-East", "ta": "தென்கிழக்கு"},
    {"en": "South-West", "ta": "தென்மேற்கு"},
    {"en": "North-West", "ta": "வடமேற்கு"},
    {"en": "North-East", "ta": "வடகிழக்கு"}
]

# The 8 Jamakkol non-fixed houses in anti-clockwise order starting from Meena
# 11: Meena, 9: Makara, 8: Dhanus, 6: Thula, 5: Kanni, 3: Kataka, 2: Mithuna, 0: Mesha
HOUSES_ANTI = [11, 9, 8, 6, 5, 3, 2, 0]
FIXED_HOUSES = [1, 4, 7, 10]  # Rishaba, Simha, Vrischika, Kumbha

# The 8 Jama Grahas in classical order:
# 1. Kadir (Sun), 2. Sei (Mars), 3. Pon (Jupiter), 4. Maal (Mercury),
# 5. Pugar (Venus), 6. Mandhan (Saturn), 7. Madhi (Moon), 8. Paambu (Rahu)
JAMA_GRAHAS = [
    {"key": "Sun", "name_en": "Sun (Kadir)", "name_ta": "சூரியன் (கதிர்)", "short_ta": "கதிர்", "opposite_idx": 4},
    {"key": "Mars", "name_en": "Mars (Sei)", "name_ta": "செவ்வாய் (சேய்)", "short_ta": "சேய்", "opposite_idx": 5},
    {"key": "Jupiter", "name_en": "Jupiter (Pon)", "name_ta": "குரு (பொன்)", "short_ta": "பொன்", "opposite_idx": 6},
    {"key": "Mercury", "name_en": "Mercury (Maal)", "name_ta": "புதன் (மால்)", "short_ta": "மால்", "opposite_idx": 7},
    {"key": "Venus", "name_en": "Venus (Pugar)", "name_ta": "சுக்கிரன் (புகார்)", "short_ta": "புகார்", "opposite_idx": 0},
    {"key": "Saturn", "name_en": "Saturn (Mandhan)", "name_ta": "சனி (மந்தன்)", "short_ta": "மந்தன்", "opposite_idx": 1},
    {"key": "Moon", "name_en": "Moon (Madhi)", "name_ta": "சந்திரன் (மதி)", "short_ta": "மதி", "opposite_idx": 2},
    {"key": "Rahu", "name_en": "Snake/Rahu (Paambu)", "name_ta": "ராகு (பாம்பு)", "short_ta": "பாம்பு", "opposite_idx": 3}
]

# Weekday Lord mapping to planet index:
# Sunday (6 in python weekday or 0 depending on convention; python Monday=0, Sunday=6)
# Standard Vedic vaara:
# 0: Sunday -> Sun (0)
# 1: Monday -> Moon (6)
# 2: Tuesday -> Mars (1)
# 3: Wednesday -> Mercury (3)
# 4: Thursday -> Jupiter (2)
# 5: Friday -> Venus (4)
# 6: Saturday -> Saturn (5)
WEEKDAY_LORDS = {
    0: {"name_en": "Sunday", "name_ta": "ஞாயிறு", "planet_idx": 0},
    1: {"name_en": "Monday", "name_ta": "திங்கள்", "planet_idx": 6},
    2: {"name_en": "Tuesday", "name_ta": "செவ்வாய்", "planet_idx": 1},
    3: {"name_en": "Wednesday", "name_ta": "புதன்", "planet_idx": 3},
    4: {"name_en": "Thursday", "name_ta": "வியாழன்", "planet_idx": 2},
    5: {"name_en": "Friday", "name_ta": "வெள்ளி", "planet_idx": 4},
    6: {"name_en": "Saturday", "name_ta": "சனி", "planet_idx": 5}
}

# Kala Nirnayam Time Periods (Lesson 10)
PLANET_TIME_UNITS = {
    "Sun": {"en": "6 Months (1 Ayanam)", "ta": "6 மாதங்கள் (ஒரு அயனம்)"},
    "Moon": {"en": "1 Muhurtham (48 minutes to 2 days)", "ta": "1 முகூர்த்தம் (48 நிமிடம் - 2 நாட்கள்)"},
    "Mars": {"en": "1 Day", "ta": "1 தினம் (ஒரு நாள்)"},
    "Mercury": {"en": "2 Months (1 Ritu)", "ta": "2 மாதங்கள் (ஒரு ருது)"},
    "Jupiter": {"en": "1 Month", "ta": "1 மாதம்"},
    "Venus": {"en": "15 Days (1 Paksham / Fortnight)", "ta": "15 நாட்கள் (ஒரு பட்சம்)"},
    "Saturn": {"en": "1 Year", "ta": "1 ஆண்டு (ஒரு வருடம்)"},
    "Rahu": {"en": "1 Year or more", "ta": "1 ஆண்டு அல்லது அதற்கு மேல்"},
    "Ketu": {"en": "3 Months", "ta": "3 மாதங்கள்"}
}


def get_surya_veedhi(sun_sign_idx: int) -> Dict[str, Any]:
    """
    Determines Surya Veedhi based on the Sun's transit sign:
    - Mesha Veedhi (0): Sun in Taurus (1), Gemini (2), Cancer (3), Leo (4) [Vaikasi, Aani, Aadi, Aavani]
    - Rishaba Veedhi (1): Sun in Virgo (5), Libra (6), Pisces (11), Aries (0) [Purattasi, Aippasi, Panguni, Chithirai]
    - Mithuna Veedhi (2): Sun in Scorpio (7), Sagittarius (8), Capricorn (9), Aquarius (10) [Karthigai, Margazhi, Thai, Maasi]
    """
    if sun_sign_idx in [1, 2, 3, 4]:
        veedhi_sign = 0  # Mesha
        name_en = "Mesha Veedhi (Northern Path / Deva Veedhi)"
        name_ta = "மேஷ வீதி (உத்தராயணம் / தேவ வீதி)"
    elif sun_sign_idx in [5, 6, 11, 0]:
        veedhi_sign = 1  # Rishaba
        name_en = "Rishaba Veedhi (Central Path / Madhya Veedhi)"
        name_ta = "ரிஷப வீதி (மத்திய வீதி)"
    else:
        veedhi_sign = 2  # Mithuna
        name_en = "Mithuna Veedhi (Southern Path / Yama Veedhi)"
        name_ta = "மிதுன வீதி (தக்ஷிணாயனம் / யம வீதி)"

    return {
        "veedhi_sign": veedhi_sign,
        "veedhi_sign_name_en": RASI_NAMES_EN[veedhi_sign],
        "veedhi_sign_name_ta": RASI_NAMES_TA[veedhi_sign],
        "name_en": name_en,
        "name_ta": name_ta,
        "sun_sign_idx": sun_sign_idx,
        "sun_sign_name_en": RASI_NAMES_EN[sun_sign_idx],
        "sun_sign_name_ta": RASI_NAMES_TA[sun_sign_idx]
    }


def calculate_kavippu(udhayam_sign: int, arudam_sign: int, surya_veedhi_sign: int) -> int:
    """
    Calculates Kavippu (Obstruction point):
    Count from Arudam to Surya Veedhi inclusive = N.
    Count N from Udhayam inclusive.
    Formula: (Udhayam + Surya Veedhi - Arudam) % 12
    """
    return (udhayam_sign + surya_veedhi_sign - arudam_sign) % 12


def calculate_jaamams(
    sunrise_dt: datetime.datetime,
    sunset_dt: datetime.datetime,
    next_sunrise_dt: datetime.datetime,
    query_dt: datetime.datetime,
    weekday_idx: int
) -> Dict[str, Any]:
    """
    Divides Day into 8 Jaamams (Sunrise to Sunset) and Night into 8 Jaamams (Sunset to Next Sunrise).
    Determines active Jaamam (1-8), day/night flag, and Jaamam lord.
    """
    is_night = False
    if query_dt < sunrise_dt:
        # Before sunrise: belongs to previous day's night Jaamams
        is_night = True
        # Shift back to previous sunset
        prev_sunset_dt = sunset_dt - datetime.timedelta(days=1)
        night_duration = (sunrise_dt - prev_sunset_dt).total_seconds()
        jaamam_duration = night_duration / 8.0
        elapsed = (query_dt - prev_sunset_dt).total_seconds()
        active_idx = min(7, max(0, int(elapsed / jaamam_duration)))
        # Shift weekday to previous day
        active_weekday = (weekday_idx - 1) % 7
        base_start = prev_sunset_dt
        base_dur = jaamam_duration
    elif query_dt >= sunset_dt:
        # After sunset: current night
        is_night = True
        night_duration = (next_sunrise_dt - sunset_dt).total_seconds()
        jaamam_duration = night_duration / 8.0
        elapsed = (query_dt - sunset_dt).total_seconds()
        active_idx = min(7, max(0, int(elapsed / jaamam_duration)))
        active_weekday = weekday_idx
        base_start = sunset_dt
        base_dur = jaamam_duration
    else:
        # Daytime
        is_night = False
        day_duration = (sunset_dt - sunrise_dt).total_seconds()
        jaamam_duration = day_duration / 8.0
        elapsed = (query_dt - sunrise_dt).total_seconds()
        active_idx = min(7, max(0, int(elapsed / jaamam_duration)))
        active_weekday = weekday_idx
        base_start = sunrise_dt
        base_dur = jaamam_duration

    # Active Jaamam start and end
    active_start_dt = base_start + datetime.timedelta(seconds=active_idx * base_dur)
    active_end_dt = active_start_dt + datetime.timedelta(seconds=base_dur)

    # Generate full timeline of 8 day or night Jaamams
    jaamam_list = []
    day_lord_idx = WEEKDAY_LORDS[active_weekday]["planet_idx"]

    # In Jamakkol, the jaamam lord sequence for the day follows the cyclic order:
    # 1st Jaamam lord is Day Lord; each successive Jaamam rotates through the sequence of 8 planets
    for j in range(8):
        j_start = base_start + datetime.timedelta(seconds=j * base_dur)
        j_end = j_start + datetime.timedelta(seconds=base_dur)
        # Jaamam Lord planet index
        lord_p_idx = (day_lord_idx + j) % 8
        lord_planet = JAMA_GRAHAS[lord_p_idx]

        jaamam_list.append({
            "jaamam_number": j + 1,
            "start_time": j_start.strftime("%H:%M:%S"),
            "end_time": j_end.strftime("%H:%M:%S"),
            "duration_minutes": round(base_dur / 60.0, 1),
            "is_active": (j == active_idx),
            "lord_planet_key": lord_planet["key"],
            "lord_name_en": lord_planet["name_en"],
            "lord_name_ta": lord_planet["name_ta"],
            "lord_short_ta": lord_planet["short_ta"]
        })

    active_jaamam_lord = jaamam_list[active_idx]

    return {
        "is_night": is_night,
        "active_jaamam_number": active_idx + 1,  # 1-indexed (1 to 8)
        "active_jaamam_index": active_idx,      # 0-indexed (0 to 7)
        "active_weekday_name_en": WEEKDAY_LORDS[active_weekday]["name_en"],
        "active_weekday_name_ta": WEEKDAY_LORDS[active_weekday]["name_ta"],
        "day_lord_planet_idx": day_lord_idx,
        "active_jaamam_start": active_start_dt.strftime("%H:%M:%S"),
        "active_jaamam_end": active_end_dt.strftime("%H:%M:%S"),
        "jaamam_duration_minutes": round(base_dur / 60.0, 1),
        "jaamam_duration_seconds": base_dur,
        "elapsed_in_jaamam_seconds": (query_dt - active_start_dt).total_seconds(),
        "active_jaamam_lord": active_jaamam_lord,
        "all_jaamams": jaamam_list
    }


def calculate_jama_grahas(weekday_idx: int, jaamam_idx: int) -> Dict[str, Any]:
    """
    Places the 8 Jama Grahas in the 8 non-fixed houses according to classical rules:
    house_idx = (p - day_lord_planet_idx + jaamam_idx) % 8
    sign = HOUSES_ANTI[house_idx]
    """
    day_lord_idx = WEEKDAY_LORDS[weekday_idx]["planet_idx"]

    planet_positions = {}
    sign_to_planets = {s: [] for s in range(12)}

    for p_idx, p in enumerate(JAMA_GRAHAS):
        h_idx = (p_idx - day_lord_idx + jaamam_idx) % 8
        sign_idx = HOUSES_ANTI[h_idx]
        pos_info = {
            "key": p["key"],
            "name_en": p["name_en"],
            "name_ta": p["name_ta"],
            "short_ta": p["short_ta"],
            "sign_idx": sign_idx,
            "sign_name_en": RASI_NAMES_EN[sign_idx],
            "sign_name_ta": RASI_NAMES_TA[sign_idx],
            "house_idx_8": h_idx,
            "is_fixed_sign": False
        }
        planet_positions[p["key"]] = pos_info
        sign_to_planets[sign_idx].append(pos_info)

    return {
        "planet_positions": planet_positions,
        "sign_to_jama_planets": sign_to_planets,
        "fixed_signs": [
            {"sign_idx": s, "sign_name_en": RASI_NAMES_EN[s], "sign_name_ta": RASI_NAMES_TA[s]}
            for s in FIXED_HOUSES
        ]
    }


def calculate_auto_arudam(
    udhayam_sign: int,
    elapsed_in_jaamam_seconds: float,
    jaamam_duration_seconds: float
) -> int:
    """
    Calculates dynamic 5-minute / time-division Arudam progression:
    The 12 signs traverse during 1 Jaamam.
    Each sign takes (jaamam_duration / 12) seconds (approx 7.5 mins).
    """
    sign_duration = jaamam_duration_seconds / 12.0
    steps = int(max(0, elapsed_in_jaamam_seconds) / sign_duration) % 12
    # Progressing from Udhayam
    return (udhayam_sign + steps) % 12


def analyze_jamakkol_prasna(
    udhayam_sign: int,
    arudam_sign: int,
    kavippu_sign: int,
    surya_veedhi_info: Dict[str, Any],
    jama_grahas_info: Dict[str, Any],
    inner_planets: List[Dict[str, Any]],
    jaamam_info: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Synthesizes deep classical predictions based on Vaithyanatha Deekshithar's treatise:
    1. Kariya Siddhi (காரிய சித்தி - Outcome & Success Probability)
    2. Kavippu affliction analysis (கவிப்பு தடைகள்)
    3. Dhatu, Moola, Jeeva analysis (தாம்பூல / கேள்வி நிர்ணயம்)
    4. Kala Nirnayam timing (கால நிர்ணயம்)
    5. Inner vs. Outer Graha conjunctions
    """
    # 1. Bhava from Udhayam to Arudam
    # Inclusive count: 1 to 12
    bhava_arudam = ((arudam_sign - udhayam_sign) % 12) + 1
    # Bhava from Udhayam to Kavippu
    bhava_kavippu = ((kavippu_sign - udhayam_sign) % 12) + 1
    # Bhava from Arudam to Kavippu
    bhava_kavippu_from_arudam = ((kavippu_sign - arudam_sign) % 12) + 1

    # Udhayam & Arudam lords
    udhayam_lord_en = RASI_LORDS_EN[udhayam_sign]
    udhayam_lord_ta = RASI_LORDS_TA[udhayam_sign]
    arudam_lord_en = RASI_LORDS_EN[arudam_sign]
    arudam_lord_ta = RASI_LORDS_TA[arudam_sign]
    kavippu_lord_en = RASI_LORDS_EN[kavippu_sign]
    kavippu_lord_ta = RASI_LORDS_TA[kavippu_sign]

    # Check Grahas in Udhayam, Arudam, Kavippu
    sign_to_inner = {s: [] for s in range(12)}
    for p in inner_planets:
        s_id = p.get("rasi_id", 0)
        sign_to_inner[s_id].append(p)

    sign_to_jama = jama_grahas_info["sign_to_jama_planets"]

    udhayam_inner = sign_to_inner[udhayam_sign]
    udhayam_jama = sign_to_jama[udhayam_sign]
    arudam_inner = sign_to_inner[arudam_sign]
    arudam_jama = sign_to_jama[arudam_sign]
    kavippu_inner = sign_to_inner[kavippu_sign]
    kavippu_jama = sign_to_jama[kavippu_sign]

    # --- Kariya Siddhi Evaluation ---
    score = 50
    reasons_en = []
    reasons_ta = []

    # Bhava evaluation
    if bhava_arudam in [1, 2, 4, 5, 7, 9, 10, 11]:
        if bhava_arudam in [1, 5, 9, 11]:
            score += 25
            reasons_en.append(f"Arudam falls in the highly auspicious {bhava_arudam}th house (Trikona/Labha) from Udhayam.")
            reasons_ta.append(f"ஆருடம் உதயத்திற்கு அதி உன்னதமான {bhava_arudam}ம் வீட்டில் (திரிகோணம்/லாபம்) விழுந்துள்ளது. முழு வெற்றி.")
        elif bhava_arudam in [4, 7, 10]:
            score += 20
            reasons_en.append(f"Arudam falls in Kendra ({bhava_arudam}th house) from Udhayam, indicating strength and achievement.")
            reasons_ta.append(f"ஆருடம் உதயத்திற்கு கேந்திர ஸ்தானத்தில் ({bhava_arudam}ம் வீடு) அமர்ந்து காரிய பலத்தை அளிக்கிறது.")
        else:  # 2nd
            score += 15
            reasons_en.append("Arudam falls in the 2nd house (Dhana Bhava) from Udhayam, indicating wealth and material gains.")
            reasons_ta.append("ஆருடம் உதயத்திற்கு 2ம் வீட்டில் (தன ஸ்தானம்) அமர்ந்து தன லாபத்தை சுட்டிக்காட்டுகிறது.")
    elif bhava_arudam == 3:
        score += 5
        reasons_en.append("Arudam falls in the 3rd house (Bhratru/Virya Bhava) - requires courageous initiative and travel to succeed.")
        reasons_ta.append("ஆருடம் உதயத்திற்கு 3ம் வீட்டில் (தைரிய ஸ்தானம்) உள்ளது. தீவிர முயற்சியும் பிரயாணமும் தேவைப்படும்.")
    else:  # 6, 8, 12
        score -= 25
        if bhava_arudam == 6:
            reasons_en.append("Arudam falls in the 6th house (Rina/Roga/Shatru) from Udhayam - indicates disputes, debts, or obstacles.")
            reasons_ta.append("ஆருடம் உதயத்திற்கு 6ம் வீட்டில் (சத்ரு/ரோக ஸ்தானம்) உள்ளது. வழக்குகளும், எதிர்ப்புகளும் காணப்படும்.")
        elif bhava_arudam == 8:
            reasons_en.append("Arudam falls in the 8th house (Ashtama) from Udhayam - severe delays, sudden anxiety, or peril.")
            reasons_ta.append("ஆருடம் உதயத்திற்கு 8ம் வீட்டில் (அஷ்டம ஸ்தானம்) உள்ளது. எதிர்பாராத தடையையும் மனவேதனையையும் குறிக்கும்.")
        else:  # 12
            score -= 20
            reasons_en.append("Arudam falls in the 12th house (Vyaya) from Udhayam - high expenses, wastage of effort, or relocation.")
            reasons_ta.append("ஆருடம் உதயத்திற்கு 12ம் வீட்டில் (விரய ஸ்தானம்) உள்ளது. அலைச்சலும் விரயங்களும் ஏற்படும்.")

    # Kavippu affliction
    if kavippu_sign == udhayam_sign:
        score -= 25
        reasons_en.append("Kavippu falls directly on Udhayam! Querent faces personal confusion, health weakness, or clouded judgment.")
        reasons_ta.append("கவிப்பு நேரடியாக உதயத்தின் மீது கவிழ்ந்துள்ளது! ஜாதகருக்கு மனக்குழப்பம் மற்றும் சுய தடைகள் உண்டாகும்.")
    elif kavippu_sign == arudam_sign:
        score -= 30
        reasons_en.append("Kavippu falls directly on Arudam! The intended venture or lost item is completely veiled/obstructed.")
        reasons_ta.append("கவிப்பு நேரடியாக ஆருடத்தின் மீது கவிழ்ந்துள்ளது! கேட்கப்பட்ட காரியம் மறைக்கப்பட்டோ பெரும் தடையிலோ சிக்கியுள்ளது.")
    elif bhava_kavippu in [2, 7, 8]:
        score -= 10
        reasons_en.append(f"Kavippu is in the sensitive {bhava_kavippu}th house from Udhayam, affecting finance/partnerships.")
        reasons_ta.append(f"கவிப்பு உதயத்திற்கு {bhava_kavippu}ம் வீட்டில் விழுந்து பொருளாதார/கூட்டாளி தடைகளை ஏற்படுத்துகிறது.")
    else:
        score += 10
        reasons_en.append("Kavippu is clear from Udhayam and Arudam, minimizing hidden obstructions.")
        reasons_ta.append("கவிப்பு உதயம் மற்றும் ஆருடத்தை பாதிக்காமல் விலகி நிற்பதால் மறைமுக தடைகள் குறைவு.")

    # Benefics in Udhayam / Arudam
    benefic_keys = ["Jupiter", "Venus", "Mercury"]
    malefic_keys = ["Saturn", "Mars", "Rahu"]

    udhayam_has_benefic = any(p["key"] in benefic_keys for p in (udhayam_inner + udhayam_jama))
    udhayam_has_malefic = any(p["key"] in malefic_keys for p in (udhayam_inner + udhayam_jama))
    arudam_has_benefic = any(p["key"] in benefic_keys for p in (arudam_inner + arudam_jama))
    arudam_has_malefic = any(p["key"] in malefic_keys for p in (arudam_inner + arudam_jama))

    if udhayam_has_benefic:
        score += 15
        reasons_en.append("Benefic planets grace Udhayam, providing divine protection and auspicious support.")
        reasons_ta.append("சுப கிரகங்கள் உதயத்தில் அமர்ந்து நற்காட்சியும் தெய்வீக பாதுகாப்பும் அளிக்கின்றன.")
    if arudam_has_benefic:
        score += 15
        reasons_en.append("Benefic planets occupy Arudam, ensuring profitable and pleasing culmination of the question.")
        reasons_ta.append("சுப கிரகங்கள் ஆருடத்தில் கூடி காரியத்தின் இனிய நிறைவேற்றத்தை உறுதி செய்கின்றன.")

    if udhayam_has_malefic and not udhayam_has_benefic:
        score -= 10
        reasons_en.append("Malefic energy on Udhayam indicates mental agitation or hostility.")
        reasons_ta.append("அசுப கோள்கள் உதயத்தில் உள்ளதால் மன அமைதியின்மையும் விரோதமும் உண்டாகலாம்.")
    if arudam_has_malefic and not arudam_has_benefic:
        score -= 15
        reasons_en.append("Malefic influence on Arudam denotes friction, resistance, or aggressive challenges.")
        reasons_ta.append("ஆருடத்தில் பாபக் கிரகங்களின் தாக்கம் காரியத்தில் வாக்குவாதங்களையும் சவால்களையும் காட்டும்.")

    score = max(5, min(95, score))

    if score >= 75:
        verdict_en = "Highly Auspicious (Kariya Siddhi Confirmed)"
        verdict_ta = "உறுதியான காரிய சித்தி (முழு வெற்றி நற்பலன்)"
        color_badge = "success"
    elif score >= 55:
        verdict_en = "Favorable with Effort (Success After Overcoming Minor Delays)"
        verdict_ta = "முயற்சியினால் வெற்றி (சிறிய தாமதத்திற்குப் பின் சாதகம்)"
        color_badge = "info"
    elif score >= 40:
        verdict_en = "Mixed / Challenging (Compromise or Strong Perseverance Required)"
        verdict_ta = "மிதமான பலன் (போராட்டமும் சமரசமும் தேவை)"
        color_badge = "warning"
    else:
        verdict_en = "Obstruction / Inauspicious (Postpone Venture or Apply Remedial Action)"
        verdict_ta = "காரியத் தடை / எச்சரிக்கை (தள்ளிப்போடுதல் அல்லது பரிகாரம் தேவை)"
        color_badge = "danger"

    # --- Dhatu / Moola / Jeeva Analysis (Lessons 13-14) ---
    udhayam_dmj = RASI_DMJ[udhayam_sign]
    arudam_dmj = RASI_DMJ[arudam_sign]
    kavippu_dmj = RASI_DMJ[kavippu_sign]

    dmj_summary_en = f"Udhayam is {udhayam_dmj['en']}, Arudam is {arudam_dmj['en']}."
    dmj_summary_ta = f"உதயம் {udhayam_dmj['ta']}, ஆருடம் {arudam_dmj['ta']}."

    # --- Kala Nirnayam (Timing of Event - Lesson 10) ---
    # Method 1: Moon distance to Udhayam
    # Find Moon sign in inner planets
    moon_sign = udhayam_sign
    for p in inner_planets:
        if p.get("key") == "Moon":
            moon_sign = p.get("rasi_id", udhayam_sign)
            break

    dist_moon_to_udhayam = ((udhayam_sign - moon_sign) % 12) + 1
    # Each sign is approx 2.25 days of Moon transit
    moon_days = round(dist_moon_to_udhayam * 2.25, 1)

    # Method 2: Planetary Karakatva unit of Arudam Lord
    arudam_lord_unit = PLANET_TIME_UNITS.get(arudam_lord_en, {"en": "1 Month", "ta": "1 மாதம்"})

    # Auspicious Direction (Lesson 6 & 21)
    auspicious_dir_en = RASI_DIRECTIONS[arudam_sign]["en"]
    auspicious_dir_ta = RASI_DIRECTIONS[arudam_sign]["ta"]

    return {
        "kariya_siddhi_score": score,
        "kariya_siddhi_verdict_en": verdict_en,
        "kariya_siddhi_verdict_ta": verdict_ta,
        "color_badge": color_badge,
        "reasons_en": reasons_en,
        "reasons_ta": reasons_ta,
        "bhava_arudam_from_udhayam": bhava_arudam,
        "bhava_kavippu_from_udhayam": bhava_kavippu,
        "bhava_kavippu_from_arudam": bhava_kavippu_from_arudam,
        "udhayam_dmj": udhayam_dmj,
        "arudam_dmj": arudam_dmj,
        "kavippu_dmj": kavippu_dmj,
        "dmj_summary_en": dmj_summary_en,
        "dmj_summary_ta": dmj_summary_ta,
        "timing_analysis": {
            "moon_distance_houses": dist_moon_to_udhayam,
            "estimated_days": moon_days,
            "arudam_lord_time_unit_en": arudam_lord_unit["en"],
            "arudam_lord_time_unit_ta": arudam_lord_unit["ta"],
            "summary_en": f"Expected realization in {int(moon_days)} to {int(moon_days + 4)} days (based on Moon-Udhayam transit) or within {arudam_lord_unit['en']} (Lord of Arudam).",
            "summary_ta": f"சந்திரன்-உதய இடைவெளியின்படி {int(moon_days)} முதல் {int(moon_days + 4)} நாட்களுக்குள் அல்லது ஆருடாதிபதி சுட்டும் காலமான {arudam_lord_unit['ta']}க்குள் காரியம் பலிதமாகும்."
        },
        "auspicious_direction_en": auspicious_dir_en,
        "auspicious_direction_ta": auspicious_dir_ta,
        "afflicted_by_kavippu": {
            "inner_planets": [p.get("name") for p in kavippu_inner],
            "jama_planets": [p["name_en"] for p in kavippu_jama]
        }
    }


def calculate_jamakkol_chart(
    query_date: datetime.date,
    query_time_str: str,
    place_name: str,
    lat: float,
    lon: float,
    tz: float,
    arudam_override: Optional[int] = None
) -> Dict[str, Any]:
    """
    Master Jamakkol Calculation Function:
    Calculates astronomical positions via VedicHoroscopeEngine,
    generates 8 Jaamams, places 8 Jama Grahas, computes 4 Pillars,
    and returns rich dual-language horoscope data.
    """
    # Import VedicHoroscopeEngine dynamically to prevent potential circularity
    from vedic_engine import VedicHoroscopeEngine

    engine = VedicHoroscopeEngine(
        birth_date=query_date,
        birth_time_str=query_time_str,
        place_name=place_name,
        lat=lat,
        lon=lon,
        tz=tz,
        ayanamsa="LAHIRI"
    )

    # 1. Ephemeris & Panchanga calculation
    planets_and_lagna = engine.calculate_planets_and_lagna()
    panchanga = engine.calculate_panchanga()

    # Ascendant (Udhayam) is item 0
    lagna_item = planets_and_lagna[0]
    udhayam_sign = lagna_item["rasi_id"]
    udhayam_deg_in_sign = lagna_item["deg_in_sign"]

    # Sun position
    sun_item = next((p for p in planets_and_lagna if p["key"] == "Sun"), None)
    sun_sign = sun_item["rasi_id"] if sun_item else 0

    # Parse query datetime
    h, m, s = [int(x) for x in query_time_str.split(":")]
    query_dt = datetime.datetime(query_date.year, query_date.month, query_date.day, h, m, s)

    # Parse Sunrise and Sunset
    sr_str = panchanga.get("sunrise", "06:00:00")
    ss_str = panchanga.get("sunset", "18:00:00")
    sr_h, sr_m, sr_s = [int(x) for x in sr_str.split(":")]
    ss_h, ss_m, ss_s = [int(x) for x in ss_str.split(":")]

    sunrise_dt = datetime.datetime(query_date.year, query_date.month, query_date.day, sr_h, sr_m, sr_s)
    sunset_dt = datetime.datetime(query_date.year, query_date.month, query_date.day, ss_h, ss_m, ss_s)
    next_sunrise_dt = sunrise_dt + datetime.timedelta(days=1)

    # Weekday determination:
    # Python weekday(): Monday=0, Sunday=6
    # Vedic weekday: Sunday=0, Monday=1, ..., Saturday=6
    py_weekday = query_dt.weekday()
    vedic_weekday = (py_weekday + 1) % 7

    # 2. Calculate 8 Jaamams
    jaamam_info = calculate_jaamams(sunrise_dt, sunset_dt, next_sunrise_dt, query_dt, vedic_weekday)

    # 3. Calculate 8 Jama Grahas
    jama_grahas_info = calculate_jama_grahas(vedic_weekday, jaamam_info["active_jaamam_index"])

    # 4. Determine Surya Veedhi
    surya_veedhi_info = get_surya_veedhi(sun_sign)

    # 5. Determine Arudam
    if arudam_override is not None and 0 <= arudam_override <= 11:
        arudam_sign = arudam_override
        arudam_mode = "Custom Querent Selection"
    else:
        arudam_sign = calculate_auto_arudam(
            udhayam_sign=udhayam_sign,
            elapsed_in_jaamam_seconds=jaamam_info["elapsed_in_jaamam_seconds"],
            jaamam_duration_seconds=jaamam_info["jaamam_duration_seconds"]
        )
        arudam_mode = "Automatic (Time-Division Progression)"

    # 6. Calculate Kavippu
    kavippu_sign = calculate_kavippu(udhayam_sign, arudam_sign, surya_veedhi_info["veedhi_sign"])

    # Filter real transit planets (excluding Lagna)
    transit_planets = [p for p in planets_and_lagna if p["key"] != "Lagna"]

    # 7. Synthesize Classical Horary Predictions
    prediction_analysis = analyze_jamakkol_prasna(
        udhayam_sign=udhayam_sign,
        arudam_sign=arudam_sign,
        kavippu_sign=kavippu_sign,
        surya_veedhi_info=surya_veedhi_info,
        jama_grahas_info=jama_grahas_info,
        inner_planets=transit_planets,
        jaamam_info=jaamam_info
    )

    # 8. Build 12-Rasi Grid Data for Dual-Ring Visual Mandala
    signs_grid = []
    for s_idx in range(12):
        inner_in_sign = [
            {
                "key": p["key"],
                "name_en": p["name"],
                "name_ta": p.get("tamil", p["name"]),
                "symbol": p.get("symbol", ""),
                "deg_in_sign_dms": p.get("deg_in_sign_dms", ""),
                "is_retrograde": p.get("is_retrograde", False)
            }
            for p in transit_planets if p.get("rasi_id") == s_idx
        ]

        jama_in_sign = jama_grahas_info["sign_to_jama_planets"][s_idx]

        # Markers in this sign
        markers = []
        if s_idx == udhayam_sign:
            markers.append({"key": "UDH", "name_en": "Udhayam", "name_ta": "உதயம்", "color": "#f59e0b"})
        if s_idx == arudam_sign:
            markers.append({"key": "ARU", "name_en": "Arudam", "name_ta": "ஆருடம்", "color": "#10b981"})
        if s_idx == kavippu_sign:
            markers.append({"key": "KAV", "name_en": "Kavippu", "name_ta": "கவிப்பு", "color": "#ef4444"})
        if s_idx == surya_veedhi_info["veedhi_sign"]:
            markers.append({"key": "SV", "name_en": "Surya Veedhi Anchor", "name_ta": "சூரிய வீதி", "color": "#6366f1"})

        signs_grid.append({
            "sign_idx": s_idx,
            "sign_name_en": RASI_NAMES_EN[s_idx],
            "sign_name_ta": RASI_NAMES_TA[s_idx],
            "lord_en": RASI_LORDS_EN[s_idx],
            "lord_ta": RASI_LORDS_TA[s_idx],
            "quality": RASI_QUALITIES[s_idx],
            "dmj": RASI_DMJ[s_idx],
            "direction": RASI_DIRECTIONS[s_idx],
            "is_fixed_sign": s_idx in FIXED_HOUSES,
            "inner_planets": inner_in_sign,
            "jama_planets": jama_in_sign,
            "markers": markers
        })

    # 4 Pillars Summary Object
    pillars = {
        "udhayam": {
            "sign_idx": udhayam_sign,
            "sign_name_en": RASI_NAMES_EN[udhayam_sign],
            "sign_name_ta": RASI_NAMES_TA[udhayam_sign],
            "deg_dms": lagna_item.get("deg_in_sign_dms", ""),
            "longitude_dms": lagna_item.get("longitude_dms", ""),
            "nakshatra": lagna_item.get("nakshatra", {}).get("name", ""),
            "pada": lagna_item.get("nakshatra", {}).get("pada", 1),
            "lord_en": RASI_LORDS_EN[udhayam_sign],
            "lord_ta": RASI_LORDS_TA[udhayam_sign],
            "quality": RASI_QUALITIES[udhayam_sign],
            "dmj": RASI_DMJ[udhayam_sign],
            "direction": RASI_DIRECTIONS[udhayam_sign],
            "description_en": "The Ascendant representing the querent, present situation, and physical body.",
            "description_ta": "கேட்பவர், அவரது தற்போதைய சூழ்நிலை, உடல்நிலை மற்றும் மனநிலையைக் குறிக்கும் லக்னம்."
        },
        "arudam": {
            "sign_idx": arudam_sign,
            "sign_name_en": RASI_NAMES_EN[arudam_sign],
            "sign_name_ta": RASI_NAMES_TA[arudam_sign],
            "mode": arudam_mode,
            "lord_en": RASI_LORDS_EN[arudam_sign],
            "lord_ta": RASI_LORDS_TA[arudam_sign],
            "quality": RASI_QUALITIES[arudam_sign],
            "dmj": RASI_DMJ[arudam_sign],
            "direction": RASI_DIRECTIONS[arudam_sign],
            "bhava_from_udhayam": prediction_analysis["bhava_arudam_from_udhayam"],
            "description_en": "The query anchor point representing the core question, object, or person sought.",
            "description_ta": "கேட்கப்பட்ட விஷயம், நபர் அல்லது தேடப்படும் பொருளைக் குறிக்கும் மைய ஆருடம்."
        },
        "surya_veedhi": surya_veedhi_info,
        "kavippu": {
            "sign_idx": kavippu_sign,
            "sign_name_en": RASI_NAMES_EN[kavippu_sign],
            "sign_name_ta": RASI_NAMES_TA[kavippu_sign],
            "lord_en": RASI_LORDS_EN[kavippu_sign],
            "lord_ta": RASI_LORDS_TA[kavippu_sign],
            "quality": RASI_QUALITIES[kavippu_sign],
            "dmj": RASI_DMJ[kavippu_sign],
            "bhava_from_udhayam": prediction_analysis["bhava_kavippu_from_udhayam"],
            "bhava_from_arudam": prediction_analysis["bhava_kavippu_from_arudam"],
            "formula_en": "(Udhayam + Surya Veedhi - Arudam) mod 12",
            "formula_ta": "(உதயம் + சூரிய வீதி - ஆருடம்) mod 12",
            "description_en": "The obstruction/veil point indicating hidden blockages, secret pitfalls, or lost items.",
            "description_ta": "மறைக்கப்பட்ட தடைகள், கண்களுக்குத் தெரியாத ஆபத்துக்கள், மற்றும் இழப்புகளைக் காட்டும் கவிப்பு புள்ளி."
        }
    }

    return {
        "status": "success",
        "system": "Jamakkol Arudam (ஜாமக்கோள் ஆருடம்)",
        "treatise_reference": "Saamakkol Arudam by S. Vaithyanathan (ஜாமக்கோள் ஆருடம் - எஸ். வைத்தியநாதன்)",
        "query_metadata": {
            "date": query_date.strftime("%Y-%m-%d"),
            "time": query_time_str,
            "place": place_name,
            "lat": lat,
            "lon": lon,
            "tz": tz,
            "sunrise": sr_str,
            "sunset": ss_str
        },
        "jaamam_info": jaamam_info,
        "pillars": pillars,
        "jama_grahas": jama_grahas_info["planet_positions"],
        "signs_grid": signs_grid,
        "predictions": prediction_analysis
    }
