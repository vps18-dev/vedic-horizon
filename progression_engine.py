"""
Transits and Nakshatra Dasa Progression Engine
Based on the seminal research paper by Sri P.V.R. Narasimha Rao (October 12, 2014)
Author of Jagannatha Hora (www.VedicAstrologer.org)

Core Concept:
1. Progress natal Moon through the zodiac as per Vimshottari Dasa (or Yogini Dasa) elapsed time.
2. Rotate the ENTIRE natal chart by the progression angle:
      delta_lon = (progressed_Moon - natal_Moon) mod 360
      progressed_planet = (natal_planet + delta_lon) mod 360
3. Project progressed longitudes into Divisional Charts (D-1, D-9, D-10, D-4, D-7, D-24, D-16, etc.)
4. Correlate with Transits at the time of major life events:
   Close conjunctions and special Vedic aspects (Jupiter 5/9, Saturn 3/10, Mars 4/8, 7th mutual)
   from transiting planets onto progressed planets/lords activate life events.

Dual Language: English and Tamil (Strictly avoiding Hindi / Devanagari)
"""

import math
from datetime import date, datetime
import swisseph as swe
from jhora.panchanga import drik
from jhora import utils, const
from jhora.horoscope.dhasa.graha import vimsottari
from jhora.horoscope.chart import charts
from vedic_constants import RASHIS, GRAHAS, NAKSHATRAS, BHAVAS

EPHE_DIR = "ephe"
swe.set_ephe_path(EPHE_DIR)

AYANAMSA_MAP = {
    "LAHIRI": swe.SIDM_LAHIRI,
    "PUSHYA_PAKSHA": swe.SIDM_TRUE_PUSHYA,
    "KP": swe.SIDM_KRISHNAMURTI,
    "RAMAN": swe.SIDM_RAMAN,
    "YUKTESHWAR": swe.SIDM_YUKTESHWAR,
    "JN_BHASIN": swe.SIDM_JN_BHASIN,
    "SURYASIDDHANTA": swe.SIDM_SURYASIDDHANTA,
    "TROPICAL": -1
}

PLANET_MAP = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE
}

DIVISIONAL_FACTORS = {
    "D-1": (1, "Rasi / ராசி சக்கரம்", "General Physical Life & Personality"),
    "D-9": (9, "Navamsa / நவாம்சம்", "Dharma, Marriage & Life Partner"),
    "D-10": (10, "Dasamsa / தசாம்சம்", "Career, Profession & Social Status"),
    "D-4": (4, "Chaturthamsa / சதுர்த்தாம்சம்", "Residence, Property & Foreign Travel"),
    "D-7": (7, "Saptamsa / சப்தாம்சம்", "Children, Progeny & Lineage"),
    "D-24": (24, "Chaturvimsamsa / சதுர்விம்சாம்சம்", "Higher Learning, Education & Academic Distinction"),
    "D-16": (16, "Shodasamsa / சோடசாம்சம்", "Vehicles, Luxuries, Pleasures & Travel Accidents"),
    "D-2": (2, "Hora / ஹோரை", "Wealth, Finances & Family Assets"),
    "D-3": (3, "Drekkana / திரேக்காணம்", "Siblings, Courage & Initiative"),
    "D-12": (12, "Dwadasamsa / துவாதசாம்சம்", "Parents, Lineage & Ancestry"),
    "D-20": (20, "Vimsamsa / விம்சாம்சம்", "Spiritual Evolution & Upasana"),
    "D-30": (30, "Trimsamsa / திரிம்சாம்சம்", "Adversities, Evils & Misfortunes"),
    "D-60": (60, "Shastiamsa / சஷ்டியாம்சம்", "Root Karma & Destiny")
}

def format_dms(deg_float):
    deg_float = deg_float % 360.0
    d = int(deg_float)
    m = int((deg_float - d) * 60)
    s = int(round((deg_float - d - m / 60.0) * 3600))
    if s >= 60:
        s = 0
        m += 1
    if m >= 60:
        m = 0
        d = (d + 1) % 360
    return f"{d}° {m:02d}’ {s:02d}”"

def format_sign_dms(deg_float):
    deg_in_sign = deg_float % 30.0
    rasi_idx = int((deg_float % 360.0) / 30.0)
    rasi = RASHIS[rasi_idx]
    d = int(deg_in_sign)
    m = int((deg_in_sign - d) * 60)
    s = int(round((deg_in_sign - d - m / 60.0) * 3600))
    if s >= 60:
        s = 0
        m += 1
    if m >= 60:
        m = 0
        d += 1
    return f"{d}° {rasi['name']} {m:02d}’ ({rasi['tamil']})"

def get_nakshatra_info(longitude):
    deg = longitude % 360.0
    nak_float = deg / (360.0 / 27.0)
    nak_idx = int(nak_float) % 27
    pada = int((nak_float - int(nak_float)) * 4) + 1
    nak_data = NAKSHATRAS[nak_idx]
    return {
        "index": nak_idx + 1,
        "name": nak_data["name"],
        "tamil": nak_data["tamil"],
        "pada": pada,
        "lord": nak_data["lord"],
        "lord_tamil": nak_data.get("lord_tamil", ""),
        "symbol": nak_data["symbol"]
    }

# Vimshottari Progression Constants
DASHA_ORDER = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
DASHA_YEARS = {'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7, 'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17}

def calc_vimsottari_progressed_moon(natal_moon_lon: float, jd_dob_utc: float, jd_target_utc: float):
    """
    Computes exact Vimshottari progressed Moon longitude down to Pratyantardasa arc,
    matching Sri P.V.R. Narasimha Rao's Jagannatha Hora calculations.
    """
    YEAR_DAYS = 365.242199
    elapsed_days = jd_target_utc - jd_dob_utc
    if elapsed_days < 0:
        return natal_moon_lon, 0.0, {"running_dasha": "None", "elapsed_years": 0.0}
    
    elapsed_years = elapsed_days / YEAR_DAYS
    NAK_SPAN = 40.0 / 3.0       # 13° 20' = 800'
    AD_SPAN = NAK_SPAN / 9.0    # 88.8889'
    PD_SPAN = AD_SPAN / 9.0     # 9.8765'
    
    nak_idx = int(natal_moon_lon / NAK_SPAN)
    nak_pos = natal_moon_lon - nak_idx * NAK_SPAN
    lord_idx = nak_idx % 9
    first_lord = DASHA_ORDER[lord_idx]
    first_total_years = DASHA_YEARS[first_lord]
    
    first_elapsed_years = (nak_pos / NAK_SPAN) * first_total_years
    first_rem_years = first_total_years - first_elapsed_years
    
    current_nak_idx = nak_idx
    if elapsed_years < first_rem_years:
        cur_maha_lord = first_lord
        maha_total_years = first_total_years
        maha_elapsed = first_elapsed_years + elapsed_years
    else:
        rem_after_first = elapsed_years - first_rem_years
        current_nak_idx += 1
        lord_pointer = (lord_idx + 1) % 9
        cur_maha_lord = DASHA_ORDER[lord_pointer]
        maha_total_years = DASHA_YEARS[cur_maha_lord]
        
        while rem_after_first >= maha_total_years:
            rem_after_first -= maha_total_years
            current_nak_idx += 1
            lord_pointer = (lord_pointer + 1) % 9
            cur_maha_lord = DASHA_ORDER[lord_pointer]
            maha_total_years = DASHA_YEARS[cur_maha_lord]
        
        maha_elapsed = rem_after_first

    nak_start_deg = (current_nak_idx * NAK_SPAN) % 360.0
    
    # Antardasa
    maha_idx = DASHA_ORDER.index(cur_maha_lord)
    ad_elapsed_acc = 0.0
    cur_ad_lord = cur_maha_lord
    ad_total_years = maha_total_years * (DASHA_YEARS[cur_maha_lord] / 120.0)
    ad_offset_years = 0.0
    ad_idx = 0
    
    for i in range(9):
        ad_lord = DASHA_ORDER[(maha_idx + i) % 9]
        ad_years = maha_total_years * (DASHA_YEARS[ad_lord] / 120.0)
        if ad_elapsed_acc + ad_years > maha_elapsed:
            cur_ad_lord = ad_lord
            ad_total_years = ad_years
            ad_offset_years = maha_elapsed - ad_elapsed_acc
            ad_idx = i
            break
        ad_elapsed_acc += ad_years
        
    # Pratyantardasa
    start_ad_idx = DASHA_ORDER.index(cur_ad_lord)
    pd_elapsed_acc = 0.0
    cur_pd_lord = cur_ad_lord
    pd_total_years = ad_total_years * (DASHA_YEARS[cur_ad_lord] / 120.0)
    pd_offset_years = 0.0
    pd_idx = 0
    
    for j in range(9):
        pd_lord = DASHA_ORDER[(start_ad_idx + j) % 9]
        pd_years = ad_total_years * (DASHA_YEARS[pd_lord] / 120.0)
        if pd_elapsed_acc + pd_years > pd_offset_years:
            cur_pd_lord = pd_lord
            pd_total_years = pd_years
            pd_offset_years = pd_offset_years - pd_elapsed_acc
            pd_idx = j
            break
        pd_elapsed_acc += pd_years
        
    pd_fraction = pd_offset_years / pd_total_years if pd_total_years > 0 else 0.0
    
    progressed_moon_lon = (nak_start_deg + ad_idx * AD_SPAN + pd_idx * PD_SPAN + pd_fraction * PD_SPAN) % 360.0
    prog_angle = (progressed_moon_lon - natal_moon_lon) % 360.0
    dasha_str = f"{cur_maha_lord}-{cur_ad_lord}-{cur_pd_lord}"
    
    return progressed_moon_lon, prog_angle, {
        "running_dasha": dasha_str,
        "maha_lord": cur_maha_lord,
        "antar_lord": cur_ad_lord,
        "prat_lord": cur_pd_lord,
        "elapsed_years": round(elapsed_years, 2)
    }

def calc_yogini_progressed_moon(natal_moon_lon: float, jd_dob_utc: float, jd_target_utc: float):
    """
    Computes Yogini Dasa progression (36-year cycle) per Sri PVR Narasimha Rao's paper (Pages 27-30).
    """
    YEAR_DAYS = 365.242199
    elapsed_days = jd_target_utc - jd_dob_utc
    if elapsed_days < 0:
        return natal_moon_lon, 0.0, {"running_dasha": "None", "elapsed_years": 0.0}
        
    elapsed_years = elapsed_days / YEAR_DAYS
    YOGINI_NAMES = ["Mangala (Moon)", "Pingala (Sun)", "Dhanya (Jupiter)", "Bhramari (Mars)", "Bhadrika (Mercury)", "Ulka (Saturn)", "Siddha (Venus)", "Sankata (Rahu)"]
    YOGINI_YEARS = [1, 2, 3, 4, 5, 6, 7, 8] # Total 36 years
    
    NAK_SPAN = 40.0 / 3.0
    nak_idx = int(natal_moon_lon / NAK_SPAN)
    nak_pos = natal_moon_lon - nak_idx * NAK_SPAN
    
    first_y_idx = (nak_idx + 3) % 8
    first_y_years = YOGINI_YEARS[first_y_idx]
    
    first_elapsed = (nak_pos / NAK_SPAN) * first_y_years
    first_rem = first_y_years - first_elapsed
    
    current_nak_idx = nak_idx
    y_idx = first_y_idx
    
    if elapsed_years < first_rem:
        cur_y_years = first_y_years
        cur_y_elapsed = first_elapsed + elapsed_years
    else:
        rem_after = elapsed_years - first_rem
        current_nak_idx += 1
        y_idx = (y_idx + 1) % 8
        cur_y_years = YOGINI_YEARS[y_idx]
        
        while rem_after >= cur_y_years:
            rem_after -= cur_y_years
            current_nak_idx += 1
            y_idx = (y_idx + 1) % 8
            cur_y_years = YOGINI_YEARS[y_idx]
            
        cur_y_elapsed = rem_after
        
    frac = cur_y_elapsed / cur_y_years if cur_y_years > 0 else 0.0
    nak_start_deg = (current_nak_idx * NAK_SPAN) % 360.0
    progressed_moon_lon = (nak_start_deg + frac * NAK_SPAN) % 360.0
    prog_angle = (progressed_moon_lon - natal_moon_lon) % 360.0
    
    return progressed_moon_lon, prog_angle, {
        "running_dasha": YOGINI_NAMES[y_idx],
        "cycle_years": 36,
        "elapsed_years": round(elapsed_years, 2)
    }

def project_to_divisional(abs_long: float, factor: int) -> float:
    """
    Standard Parashari Divisional Chart projection (D-1 through D-60)
    returning exact absolute longitude (0-360) within the divisional chart.
    """
    if factor == 1:
        return abs_long % 360.0
    deg_in_sign = abs_long % 30.0
    sign_idx = int(abs_long / 30.0)
    part_span = 30.0 / float(factor)
    part_idx = int(deg_in_sign / part_span)

    if factor == 9: # Navamsa
        element_offset = [0, 8, 4][sign_idx % 3] # Movable=0, Fixed=8, Dual=4
        d_sign = (element_offset + part_idx) % 12
        sub_deg = (deg_in_sign - part_idx * part_span) * factor
        return (d_sign * 30.0 + sub_deg) % 360.0
    elif factor == 10: # Dasamsa
        is_odd = (sign_idx % 2 == 0)
        start_sign = sign_idx if is_odd else (sign_idx + 8) % 12
        d_sign = (start_sign + part_idx) % 12
        sub_deg = (deg_in_sign - part_idx * part_span) * factor
        return (d_sign * 30.0 + sub_deg) % 360.0
    elif factor == 4: # Chaturthamsa
        d_sign = (sign_idx + part_idx * 3) % 12
        sub_deg = (deg_in_sign - part_idx * part_span) * factor
        return (d_sign * 30.0 + sub_deg) % 360.0
    elif factor == 7: # Saptamsa
        is_odd = (sign_idx % 2 == 0)
        start_sign = sign_idx if is_odd else (sign_idx + 6) % 12
        d_sign = (start_sign + part_idx) % 12
        sub_deg = (deg_in_sign - part_idx * part_span) * factor
        return (d_sign * 30.0 + sub_deg) % 360.0
    elif factor == 24: # Chaturvimsamsa / Siddhamsa (Parasara with Even Sign Reversal per JHora)
        is_odd = (sign_idx % 2 == 0)
        if is_odd:
            d_sign = (4 + part_idx) % 12
            sub_deg = (deg_in_sign - part_idx * part_span) * factor
        else:
            d_sign = (3 - part_idx) % 12
            sub_deg = 30.0 - (deg_in_sign - part_idx * part_span) * factor
        return (d_sign * 30.0 + sub_deg) % 360.0
    elif factor == 16: # Shodasamsa
        modality = sign_idx % 3
        start_sign = 0 if modality == 0 else (4 if modality == 1 else 8)
        d_sign = (start_sign + part_idx) % 12
        sub_deg = (deg_in_sign - part_idx * part_span) * factor
        return (d_sign * 30.0 + sub_deg) % 360.0
    else:
        d_sign = (sign_idx * factor + part_idx) % 12
        sub_deg = (deg_in_sign - part_idx * part_span) * factor
        return (d_sign * 30.0 + sub_deg) % 360.0

def calculate_dasa_progression(
    birth_date: date,
    birth_time_str: str,
    lat: float,
    lon: float,
    tz: float,
    target_date: date,
    target_time_str: str = "12:00:00",
    ayanamsa: str = "LAHIRI",
    progression_type: str = "rasi_vimsottari",
    div_chart_code: str = "D-1"
):
    """
    Computes PVR Narasimha Rao's Dasa Progression and Transit Correlations.
    """
    # 1. Setup Swiss Ephemeris
    ay_code = AYANAMSA_MAP.get(ayanamsa, swe.SIDM_LAHIRI)
    if ay_code >= 0:
        swe.set_sid_mode(ay_code)
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    else:
        flags = swe.FLG_SPEED

    # 2. Parse Birth Date and Time -> JD
    b_parts = [int(p) for p in birth_time_str.split(":")]
    b_hour = b_parts[0] + b_parts[1] / 60.0 + (b_parts[2] if len(b_parts) > 2 else 0) / 3600.0
    jd_dob_local = swe.julday(birth_date.year, birth_date.month, birth_date.day, b_hour)
    jd_dob_utc = jd_dob_local - (tz / 24.0)

    # 3. Parse Target Date and Time -> JD
    t_parts = [int(p) for p in target_time_str.split(":")]
    t_hour = t_parts[0] + t_parts[1] / 60.0 + (t_parts[2] if len(t_parts) > 2 else 0) / 3600.0
    jd_target_local = swe.julday(target_date.year, target_date.month, target_date.day, t_hour)
    jd_target_utc = jd_target_local - (tz / 24.0)

    # 4. Calculate Natal Planets & Lagna
    natal_planets = {}
    for p_name, p_id in PLANET_MAP.items():
        res, _ = swe.calc_ut(jd_dob_utc, p_id, flags)
        natal_planets[p_name] = res[0] % 360.0

    # Ketu = Rahu + 180
    natal_planets["Ketu"] = (natal_planets["Rahu"] + 180.0) % 360.0

    # Natal Lagna
    cusps, ascmc = swe.houses_ex(jd_dob_utc, lat, lon, b'P', flags)
    natal_planets["Lagna"] = ascmc[0] % 360.0

    natal_moon_lon = natal_planets["Moon"]

    # 5. Calculate Progression
    # We support Method 1 (Rasi Vimshottari progression rotated into D-charts),
    # Method 2 (Divisional Vimshottari progression), and Yogini Progression.
    dcf_tuple = DIVISIONAL_FACTORS.get(div_chart_code, (1, "Rasi", "Physical"))
    dcf = dcf_tuple[0]

    if progression_type == "divisional_vimsottari" and dcf > 1:
        # Method 2: Progress Moon of Divisional Chart directly
        div_moon_lon = project_to_divisional(natal_moon_lon, dcf)
        progressed_moon_lon, progression_angle, active_dasha_info = calc_vimsottari_progressed_moon(
            div_moon_lon, jd_dob_utc, jd_target_utc
        )
    elif progression_type == "yogini":
        # Yogini Dasa Progression (36 year cycle)
        progressed_moon_lon, progression_angle, active_dasha_info = calc_yogini_progressed_moon(
            natal_moon_lon, jd_dob_utc, jd_target_utc
        )
    else:
        # Method 1 (Standard): Rasi Vimshottari Progression
        progressed_moon_lon, progression_angle, active_dasha_info = calc_vimsottari_progressed_moon(
            natal_moon_lon, jd_dob_utc, jd_target_utc
        )

    # 6. Rotate All Natal Planets by Progression Angle
    progressed_planets_rasi = {}
    for p_name, natal_lon in natal_planets.items():
        progressed_planets_rasi[p_name] = (natal_lon + progression_angle) % 360.0

    # 7. Project Natal & Progressed Planets into the Selected Divisional Chart
    natal_div_positions = {}
    progressed_div_positions = {}
    for p_name, r_lon in natal_planets.items():
        natal_div_positions[p_name] = project_to_divisional(r_lon, dcf)

    for p_name, r_lon in progressed_planets_rasi.items():
        if progression_type == "divisional_vimsottari" and dcf > 1:
            # In Method 2, progress the divisional positions directly
            progressed_div_positions[p_name] = (natal_div_positions[p_name] + progression_angle) % 360.0
        else:
            # In Method 1, project progressed rasi longitudes into the D-chart
            progressed_div_positions[p_name] = project_to_divisional(r_lon, dcf)

    # 8. Calculate Transit Positions at Event Date (JPL Precision)
    transit_planets = {}
    for p_name, p_id in PLANET_MAP.items():
        res, _ = swe.calc_ut(jd_target_utc, p_id, flags)
        transit_planets[p_name] = res[0] % 360.0

    transit_planets["Ketu"] = (transit_planets["Rahu"] + 180.0) % 360.0

    # Transit Lagna at Target Location
    _, t_ascmc = swe.houses_ex(jd_target_utc, lat, lon, b'P', flags)
    transit_planets["Lagna"] = t_ascmc[0] % 360.0

    # 9. PVR Rao Transit-to-Progression Activation & Correlation Engine
    # Analyzes close conjunctions and Vedic special aspects
    activations = []
    
    # Planets to check for transit triggers (Jupiter, Saturn, Rahu, Ketu, Mars, Sun)
    trigger_planets = ["Jupiter", "Saturn", "Mars", "Rahu", "Ketu", "Sun"]

    for t_name in trigger_planets:
        t_lon = transit_planets[t_name]

        # Check against both Progressed D-Chart and Progressed Rasi
        targets = [
            ("Progressed in " + div_chart_code, progressed_div_positions),
            ("Progressed in D-1 (Rasi)", progressed_planets_rasi)
        ]

        for target_label, p_dict in targets:
            for p_name, p_lon in p_dict.items():
                # Forward angle from Transit Planet to Progressed Planet
                forward_angle = (p_lon - t_lon) % 360.0
                
                aspect_type = None
                ideal_angle = 0.0

                # 1. Conjunction (0 deg)
                diff_0 = forward_angle if forward_angle <= 180 else 360.0 - forward_angle
                if diff_0 <= 5.5:
                    aspect_type = "Conjunction / சேர்க்கை (0°)"
                    ideal_angle = 0.0

                # 2. 7th Aspect (180 deg - All planets)
                diff_180 = abs(forward_angle - 180.0)
                if diff_180 <= 5.5:
                    aspect_type = "7th Mutual Aspect / சமசப்தம பார்வை (180°)"
                    ideal_angle = 180.0

                # 3. Special Aspects:
                # Jupiter: 5th (120°) & 9th (240°) trine aspects
                if t_name == "Jupiter":
                    if abs(forward_angle - 120.0) <= 5.5:
                        aspect_type = "5th Trine Aspect / 5-ஆம் பார்வை (120°)"
                        ideal_angle = 120.0
                    elif abs(forward_angle - 240.0) <= 5.5:
                        aspect_type = "9th Trine Aspect / 9-ஆம் பார்வை (240°)"
                        ideal_angle = 240.0

                # Saturn: 3rd (60°) & 10th (270°) aspects
                if t_name == "Saturn":
                    if abs(forward_angle - 60.0) <= 5.5:
                        aspect_type = "3rd Special Aspect / 3-ஆம் பார்வை (60°)"
                        ideal_angle = 60.0
                    elif abs(forward_angle - 270.0) <= 5.5:
                        aspect_type = "10th Special Aspect / 10-ஆம் பார்வை (270°)"
                        ideal_angle = 270.0

                # Mars: 4th (90°) & 8th (210°) aspects
                if t_name == "Mars":
                    if abs(forward_angle - 90.0) <= 5.5:
                        aspect_type = "4th Special Aspect / 4-ஆம் பார்வை (90°)"
                        ideal_angle = 90.0
                    elif abs(forward_angle - 210.0) <= 5.5:
                        aspect_type = "8th Special Aspect / 8-ஆம் பார்வை (210°)"
                        ideal_angle = 210.0

                # Rahu / Ketu: 5th (120°) & 9th (240°) aspects
                if t_name in ["Rahu", "Ketu"]:
                    if abs(forward_angle - 120.0) <= 5.5:
                        aspect_type = "5th Trine Aspect / 5-ஆம் பார்வை (120°)"
                        ideal_angle = 120.0
                    elif abs(forward_angle - 240.0) <= 5.5:
                        aspect_type = "9th Trine Aspect / 9-ஆம் பார்வை (240°)"
                        ideal_angle = 240.0

                if aspect_type:
                    orb = abs(forward_angle - ideal_angle)
                    if orb > 180:
                        orb = abs(orb - 360)

                    # House lords in selected D-chart
                    d_lagna_sign = int(natal_div_positions["Lagna"] / 30.0)
                    p_sign = int(natal_div_positions.get(p_name, 0) / 30.0)
                    house_from_d_lagna = ((p_sign - d_lagna_sign) % 12) + 1

                    # Astrological interpretation
                    category = "Benefic / சுப நிகழ்வு" if t_name == "Jupiter" else ("Karmic / சவாலான நிகழ்வு" if t_name == "Saturn" else "Dynamic / தீவிர மாற்றம்")
                    
                    event_indicator = "General Activation / பொதுச் சுழற்சி"
                    if div_chart_code == "D-9":
                        event_indicator = "Marriage, Love & Relationship / திருமணம் & வாழ்க்கைத்துணை" if (p_name in ["Venus", "Mars"] or house_from_d_lagna in [1, 7, 5, 8]) else "Relationship Alignment / களத்திர அமைப்பு"
                    elif div_chart_code == "D-10":
                        event_indicator = "Career Elevation, Job Change or Recognition / தொழில் & உத்தியோக மாற்றம்" if (house_from_d_lagna in [1, 5, 10, 6, 7] or p_name in ["Sun", "Jupiter", "Saturn", "Mars"]) else "Professional Milestone / கர்ம விபரம்"
                    elif div_chart_code == "D-4":
                        event_indicator = "Foreign Travel, Relocation & Residence / வெளிநாட்டு பயணம் & குடியிருப்பு" if (house_from_d_lagna in [9, 12, 4, 1] or p_name in ["Mars", "Saturn", "Rahu", "Venus"]) else "Property & Land / பூமி & சொத்து"
                    elif div_chart_code == "D-7":
                        event_indicator = "Childbirth & Progeny Fortune / குழந்தை பாக்கியம் & புத்திர யோகம்" if (house_from_d_lagna in [5, 9, 1] or p_name in ["Jupiter", "Sun", "Mars"]) else "Progeny Matter / புத்திர காரகம்"
                    elif div_chart_code == "D-24":
                        event_indicator = "Academic Distinction, Rank & Admission / கல்வி சாதனை & உயர்கல்வி சேர்க்கை" if (house_from_d_lagna in [4, 9, 1, 5] or p_name in ["Jupiter", "Mercury", "Venus", "Sun"]) else "Learning Milestone / கல்வி விபரம்"
                    elif div_chart_code in ["D-1", "D-16"]:
                        event_indicator = "Vehicular Matter, Sudden Event or Caution / வாகனம், விபத்து எச்சரிக்கை அல்லது மாற்றம்" if (house_from_d_lagna in [6, 8, 4] or t_name in ["Saturn", "Rahu", "Mars"]) else "Vital Energy & Health / உடல் நலம் & சக்தி"

                    activations.append({
                        "transit_planet": t_name,
                        "transit_lon_dms": format_sign_dms(t_lon),
                        "aspect_type": aspect_type,
                        "target_planet": p_name,
                        "target_context": target_label,
                        "progressed_lon_dms": format_sign_dms(p_lon),
                        "orb_deg": round(orb, 2),
                        "orb_dms": format_dms(orb),
                        "is_tight": orb <= 2.0,
                        "category": category,
                        "event_indicator": event_indicator,
                        "explanation": f"Transit {t_name} at {format_sign_dms(t_lon)} forms {aspect_type} with {p_name} ({target_label}) at {format_sign_dms(p_lon)} with tight orb of {format_dms(orb)}."
                    })

    # Sort activations: tightest orb first
    activations.sort(key=lambda x: x["orb_deg"])

    TAMIL_GRAHA_MAP = {
        "Sun": "சூரியன்", "Moon": "சந்திரன்", "Mars": "செவ்வாய்",
        "Mercury": "புதன்", "Jupiter": "குரு", "Venus": "சுக்கிரன்",
        "Saturn": "சனி", "Rahu": "ராகு", "Ketu": "கேது", "Lagna": "லக்னம்"
    }

    # Build Structured Planetary Tables for Frontend
    def build_chart_elements(positions_dict):
        result = []
        for p_name, lon_val in positions_dict.items():
            r_idx = int((lon_val % 360.0) / 30.0)
            deg_in_sign = lon_val % 30.0
            r_info = RASHIS[r_idx]
            nak_info = get_nakshatra_info(lon_val)
            tamil_n = TAMIL_GRAHA_MAP.get(p_name, p_name)
            result.append({
                "key": p_name,
                "name": p_name,
                "tamil": tamil_n,
                "name_dual": f"{p_name} / {tamil_n}",
                "longitude": round(lon_val, 4),
                "longitude_dms": format_dms(lon_val),
                "sign_dms": format_sign_dms(lon_val),
                "deg_in_sign": round(deg_in_sign, 2),
                "deg_in_sign_dms": format_dms(deg_in_sign),
                "rasi_id": r_idx,
                "rasi_name": r_info["name"],
                "rasi_tamil": r_info["tamil"],
                "rasi_symbol": r_info["symbol"],
                "nakshatra": nak_info
            })
        return result

    # Chart Structure formatted for VedicChartRenderer (North & South Indian)
    def build_chart_render_data(positions_dict, chart_code):
        lagna_lon = positions_dict.get("Lagna", 0.0)
        lagna_sign = int((lagna_lon % 360.0) / 30.0)
        
        # North Indian: 12 Houses from Lagna (House 1 to 12)
        north_indian_houses = []
        for h in range(1, 13):
            sign_for_house = (lagna_sign + h - 1) % 12
            r_info = RASHIS[sign_for_house]
            occupants = []
            for p_name, lon_val in positions_dict.items():
                if int((lon_val % 360.0) / 30.0) == sign_for_house:
                    deg_s = lon_val % 30.0
                    nak_info = get_nakshatra_info(lon_val)
                    occupants.append({
                        "id": p_name,
                        "name": p_name,
                        "short": "ASC" if p_name == "Lagna" else p_name[:2],
                        "label": f"{p_name[:2]} {format_dms(deg_s).split(' ')[0]}",
                        "deg": round(deg_s, 2),
                        "deg_dms": format_dms(deg_s),
                        "full_name": p_name,
                        "tamil": TAMIL_GRAHA_MAP.get(p_name, p_name),
                        "nakshatra": nak_info["name"],
                        "nakshatra_tamil": nak_info["tamil"],
                        "pada": nak_info["pada"],
                        "nak_pada": f"{nak_info['name']} {nak_info['pada']}",
                        "nak_pada_tamil": f"{nak_info['tamil']}-{nak_info['pada']}"
                    })
            north_indian_houses.append({
                "house": h,
                "rasi_id": sign_for_house,
                "rasi_name": r_info["name"],
                "rasi_tamil": r_info["tamil"],
                "rasi_dual": f"{r_info['name']} / {r_info['tamil']}",
                "rasi_sanskrit": r_info["tamil"],
                "rasi_symbol": r_info["symbol"],
                "planets": occupants
            })

        # South Indian: 12 Fixed Signs (Aries to Pisces, 0 to 11)
        south_indian_signs = []
        for r_idx in range(12):
            is_asc = (r_idx == lagna_sign)
            house_num = ((r_idx - lagna_sign) % 12) + 1
            r_info = RASHIS[r_idx]
            occupants = []
            for p_name, lon_val in positions_dict.items():
                if int((lon_val % 360.0) / 30.0) == r_idx:
                    deg_s = lon_val % 30.0
                    nak_info = get_nakshatra_info(lon_val)
                    occupants.append({
                        "id": p_name,
                        "name": p_name,
                        "short": "ASC" if p_name == "Lagna" else p_name[:2],
                        "label": f"{p_name[:2]} {format_dms(deg_s).split(' ')[0]}",
                        "deg": round(deg_s, 2),
                        "deg_dms": format_dms(deg_s),
                        "full_name": p_name,
                        "tamil": TAMIL_GRAHA_MAP.get(p_name, p_name),
                        "nakshatra": nak_info["name"],
                        "nakshatra_tamil": nak_info["tamil"],
                        "pada": nak_info["pada"],
                        "nak_pada": f"{nak_info['name']} {nak_info['pada']}",
                        "nak_pada_tamil": f"{nak_info['tamil']}-{nak_info['pada']}"
                    })
            south_indian_signs.append({
                "rasi_id": r_idx,
                "rasi_name": r_info["name"],
                "rasi_tamil": r_info["tamil"],
                "rasi_dual": f"{r_info['name']} / {r_info['tamil']}",
                "rasi_sanskrit": r_info["tamil"],
                "rasi_symbol": r_info["symbol"],
                "house_num": house_num,
                "is_ascendant": is_asc,
                "planets": occupants
            })

        return {
            "code": chart_code,
            "ascendant_rasi": lagna_sign,
            "ascendant_rasi_name": RASHIS[lagna_sign]["name"],
            "ascendant_rasi_tamil": RASHIS[lagna_sign]["tamil"],
            "ascendant_rasi_dual": f"{RASHIS[lagna_sign]['name']} / {RASHIS[lagna_sign]['tamil']}",
            "north_indian": north_indian_houses,
            "south_indian": south_indian_signs,
            "houses": north_indian_houses
        }

    return {
        "success": True,
        "meta": {
            "birth_date": birth_date.isoformat(),
            "birth_time": birth_time_str,
            "target_date": target_date.isoformat(),
            "target_time": target_time_str,
            "ayanamsa": ayanamsa,
            "progression_type": progression_type,
            "divisional_chart": div_chart_code,
            "divisional_chart_name": dcf_tuple[1],
            "divisional_signification": dcf_tuple[2]
        },
        "progression_summary": {
            "natal_moon_dms": format_sign_dms(natal_moon_lon),
            "progressed_moon_dms": format_sign_dms(progressed_moon_lon),
            "progression_angle_deg": round(progression_angle, 4),
            "progression_angle_dms": format_dms(progression_angle),
            "active_dasha_info": active_dasha_info
        },
        "activations_count": len(activations),
        "activations": activations,
        "natal_planets": build_chart_elements(natal_div_positions),
        "progressed_planets": build_chart_elements(progressed_div_positions),
        "transit_planets": build_chart_elements(transit_planets),
        "progressed_chart_render": build_chart_render_data(progressed_div_positions, f"Progressed {div_chart_code}"),
        "transit_chart_render": build_chart_render_data(transit_planets, "Transits / கோச்சாரம்")
    }


# ==============================================================================
# Presets from P.V.R. Narasimha Rao's Research Paper
# ==============================================================================
PVR_PAPER_EXAMPLES = [
    {
        "id": "pvr_ex1",
        "title": "Example 1: Academic Distinction (1987 May 28)",
        "tamil_title": "உதாரணம் 1: மாநில அளவில் முதலிடம் & IIT சேர்க்கை (1987)",
        "category": "Education / கல்வி",
        "birth_date": "1970-04-04",
        "birth_time": "17:50:40",
        "place": "Machilipatnam, India",
        "lat": 16.1667, "lon": 81.1333, "tz": 5.5,
        "target_date": "1987-05-28",
        "target_time": "19:00:00",
        "ayanamsa": "PUSHYA_PAKSHA",
        "div_chart": "D-24",
        "progression_type": "rasi_vimsottari",
        "highlight": "Transit Jupiter at 27° Pi aspects Progressed Moon at 26° Vi (9th lord in D-24) & Progressed Sun at 27° Sc!"
    },
    {
        "id": "pvr_ex2",
        "title": "Example 2: Foreign Travel to USA (1991 Aug 15)",
        "tamil_title": "உதாரணம் 2: அமெரிக்கா உயர் படிப்பு பயணம் (1991)",
        "category": "Travel / வெளிநாடு",
        "birth_date": "1970-04-04",
        "birth_time": "17:50:40",
        "place": "Machilipatnam, India",
        "lat": 16.1667, "lon": 81.1333, "tz": 5.5,
        "target_date": "1991-08-15",
        "target_time": "03:00:00",
        "ayanamsa": "PUSHYA_PAKSHA",
        "div_chart": "D-4",
        "progression_type": "rasi_vimsottari",
        "highlight": "Transit Mars at 26° Le (9th lord in D-4) & Rahu at 25° Sg (12th lord) activate Progressed Mars at 24° Le!"
    },
    {
        "id": "pvr_ex6",
        "title": "Example 6: Childbirth (1996 Feb 19)",
        "tamil_title": "உதாரணம் 6: குழந்தை பிறப்பு (1996)",
        "category": "Children / புத்திரம்",
        "birth_date": "1970-04-04",
        "birth_time": "17:50:40",
        "place": "Machilipatnam, India",
        "lat": 16.1667, "lon": 81.1333, "tz": 5.5,
        "target_date": "1996-02-19",
        "target_time": "19:00:00",
        "ayanamsa": "PUSHYA_PAKSHA",
        "div_chart": "D-7",
        "progression_type": "rasi_vimsottari",
        "highlight": "Transit Jupiter (D-7 Lagna lord) at 17° Sg aspects Progressed Sun (exalted 9th lord in 5th) at 14° Ge!"
    },
    {
        "id": "pvr_ex10",
        "title": "Example 10: Love Marriage (1991 Aug 29)",
        "tamil_title": "உதாரணம் 10: காதல் திருமணம் (1991)",
        "category": "Marriage / திருமணம்",
        "birth_date": "1963-08-07",
        "birth_time": "21:14:34",
        "place": "Sambalpur, India",
        "lat": 21.4500, "lon": 83.9667, "tz": 5.5,
        "target_date": "1991-08-29",
        "target_time": "07:00:00",
        "ayanamsa": "PUSHYA_PAKSHA",
        "div_chart": "D-9",
        "progression_type": "rasi_vimsottari",
        "highlight": "Transit Jupiter (5th lord) at 4° Le aspects Progressed Mars (Lagna lord in 7th) at 3° Sg in Navamsa!"
    },
    {
        "id": "pvr_ex13",
        "title": "Example 13: Barack Obama Marriage (1992 Oct 3)",
        "tamil_title": "உதாரணம் 13: பராக் ஒபாமா திருமணம் (1992)",
        "category": "Marriage / திருமணம்",
        "birth_date": "1961-08-04",
        "birth_time": "19:24:20",
        "place": "Honolulu, Hawaii, USA",
        "lat": 21.3069, "lon": -157.8583, "tz": -10.0,
        "target_date": "1992-10-03",
        "target_time": "10:30:00",
        "ayanamsa": "PUSHYA_PAKSHA",
        "div_chart": "D-9",
        "progression_type": "rasi_vimsottari",
        "highlight": "Transit Rahu (exalted 7th lord of D-9) at 2° Sg closely aspects its own progressed D-9 position at 3° Ar!"
    },
    {
        "id": "pvr_ex14",
        "title": "Example 14: Christopher Reeve Accident (1995 May 27)",
        "tamil_title": "உதாரணம் 14: நடிகர் கிறிஸ்டோபர் ரீவ் குதிரையேற்ற விபத்து (1995)",
        "category": "Accident / விபத்து",
        "birth_date": "1952-09-25",
        "birth_time": "03:12:00",
        "place": "Manhattan, NY, USA",
        "lat": 40.7833, "lon": -73.9667, "tz": -4.0,
        "target_date": "1995-05-27",
        "target_time": "10:30:00",
        "ayanamsa": "PUSHYA_PAKSHA",
        "div_chart": "D-1",
        "progression_type": "rasi_vimsottari",
        "highlight": "Transit Rahu at 12° Li aspects Progressed Jupiter (6th lord of accidents) at 13° Ge! Transit Jupiter at 18° Sc conjoins Progressed Venus at 19° Sc!"
    },
    {
        "id": "pvr_ex18",
        "title": "Example 18: First Job Joined (1993 Dec 10)",
        "tamil_title": "உதாரணம் 18: முதல் உத்தியோகம் சேர்ந்த நாள் (1993)",
        "category": "Career / உத்தியோகம்",
        "birth_date": "1970-04-04",
        "birth_time": "17:50:40",
        "place": "Machilipatnam, India",
        "lat": 16.1667, "lon": 81.1333, "tz": 5.5,
        "target_date": "1993-12-10",
        "target_time": "20:42:00",
        "ayanamsa": "PUSHYA_PAKSHA",
        "div_chart": "D-10",
        "progression_type": "divisional_vimsottari",
        "highlight": "Transit Jupiter at 13° Li closely aspects its own progressed D-10 position at 14° Aq!"
    },
    {
        "id": "pvr_ex20",
        "title": "Example 20: Career Promotion (2008 Sep 28)",
        "tamil_title": "உதாரணம் 20: உத்தியோக பதவி உயர்வு (2008)",
        "category": "Career / உத்தியோகம்",
        "birth_date": "1970-04-04",
        "birth_time": "17:50:40",
        "place": "Machilipatnam, India",
        "lat": 16.1667, "lon": 81.1333, "tz": 5.5,
        "target_date": "2008-09-28",
        "target_time": "20:42:00",
        "ayanamsa": "PUSHYA_PAKSHA",
        "div_chart": "D-10",
        "progression_type": "divisional_vimsottari",
        "highlight": "Transit Jupiter at 20° Sg aspects Progressed D-10 Venus (10th lord of career) at 16° Le!"
    }
]
