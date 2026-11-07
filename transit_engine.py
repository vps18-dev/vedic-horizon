from datetime import datetime
import swisseph as swe
from vedic_engine import AYANAMSA_MAP, get_nakshatra_info, format_dms, RASHIS, GRAHAS

def calculate_live_transits(natal_moon_rasi: int = 0, natal_lagna_rasi: int = 0, ayanamsa: str = "LAHIRI"):
    now = datetime.now()
    jd_now = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0 + now.second/3600.0)
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    sid_mode = AYANAMSA_MAP.get(ayanamsa.upper(), swe.SIDM_LAHIRI)
    if sid_mode is not None:
        swe.set_sid_mode(sid_mode)
    
    calc_planets = [
        (swe.SUN, "Sun", "சூரியன்", "☉"),
        (swe.MOON, "Moon", "சந்திரன்", "☾"),
        (swe.MARS, "Mars", "செவ்வாய்", "♂"),
        (swe.MERCURY, "Mercury", "புதன்", "☿"),
        (swe.JUPITER, "Jupiter", "குரு", "♃"),
        (swe.VENUS, "Venus", "சுக்கிரன்", "♀"),
        (swe.SATURN, "Saturn", "சனி", "♄"),
        (swe.MEAN_NODE, "Rahu", "ராகு", "☊")
    ]
    transits = []
    for pid, name, tamil_name, sym in calc_planets:
        res, _ = swe.calc_ut(jd_now, pid, flags)
        lon = res[0] % 360
        rasi_id = int(lon / 30)
        deg_in_sign = lon % 30
        is_retro = res[3] < 0 if pid != swe.MEAN_NODE else True
        nak = get_nakshatra_info(lon)
        
        # House from Moon (1 to 12)
        house_from_moon = ((rasi_id - natal_moon_rasi) % 12) + 1
        house_from_lagna = ((rasi_id - natal_lagna_rasi) % 12) + 1
        
        # General benefic transit houses from Moon according to Gochara Phala
        benefic_houses = {
            "Sun": [3, 6, 10, 11],
            "Moon": [1, 3, 6, 7, 10, 11],
            "Mars": [3, 6, 11],
            "Mercury": [2, 4, 6, 8, 10, 11],
            "Jupiter": [2, 5, 7, 9, 11],
            "Venus": [1, 2, 3, 4, 5, 8, 9, 11, 12],
            "Saturn": [3, 6, 11],
            "Rahu": [3, 6, 10, 11]
        }
        is_benefic = house_from_moon in benefic_houses.get(name, [])

        transits.append({
            "planet": name,
            "tamil": tamil_name,
            "sanskrit": tamil_name,
            "symbol": sym,
            "longitude": round(lon, 4),
            "longitude_dms": format_dms(lon),
            "rasi_id": rasi_id,
            "rasi_name": RASHIS[rasi_id]["name"],
            "rasi_tamil": RASHIS[rasi_id].get("tamil", ""),
            "rasi_symbol": RASHIS[rasi_id]["symbol"],
            "deg_in_sign": round(deg_in_sign, 2),
            "deg_in_sign_dms": format_dms(deg_in_sign),
            "is_retrograde": is_retro,
            "nakshatra": nak,
            "house_from_moon": house_from_moon,
            "house_from_lagna": house_from_lagna,
            "is_benefic_transit": is_benefic,
            "effect": "Favorable (சுப பலன்)" if is_benefic else "Sensitive (கவன பலன்)"
        })

    # Ketu
    rahu_t = next(t for t in transits if t["planet"] == "Rahu")
    ketu_lon = (rahu_t["longitude"] + 180.0) % 360
    ketu_rasi = int(ketu_lon / 30)
    ketu_deg = ketu_lon % 30
    h_m_ketu = ((ketu_rasi - natal_moon_rasi) % 12) + 1
    h_l_ketu = ((ketu_rasi - natal_lagna_rasi) % 12) + 1
    transits.append({
        "planet": "Ketu",
        "tamil": "கேது",
        "sanskrit": "கேது",
        "symbol": "☋",
        "longitude": round(ketu_lon, 4),
        "longitude_dms": format_dms(ketu_lon),
        "rasi_id": ketu_rasi,
        "rasi_name": RASHIS[ketu_rasi]["name"],
        "rasi_tamil": RASHIS[ketu_rasi].get("tamil", ""),
        "rasi_symbol": RASHIS[ketu_rasi]["symbol"],
        "deg_in_sign": round(ketu_deg, 2),
        "deg_in_sign_dms": format_dms(ketu_deg),
        "is_retrograde": True,
        "nakshatra": get_nakshatra_info(ketu_lon),
        "house_from_moon": h_m_ketu,
        "house_from_lagna": h_l_ketu,
        "is_benefic_transit": h_m_ketu in [3, 6, 11],
        "effect": "Favorable (சுப பலன்)" if h_m_ketu in [3, 6, 11] else "Spiritual / Detachment (ஆன்மீக நாட்டம்)"
    })

    # Sade Sati Check
    # Saturn's position relative to Moon: 12th, 1st, 2nd
    saturn_t = next(t for t in transits if t["planet"] == "Saturn")
    sat_house = saturn_t["house_from_moon"]
    sade_sati_phase = "None"
    is_sade_sati = False
    if sat_house == 12:
        is_sade_sati = True
        sade_sati_phase = "Rising Phase / விரய சனி (12th from Moon)"
    elif sat_house == 1:
        is_sade_sati = True
        sade_sati_phase = "Peak Phase / ஜென்ம சனி (Over Natal Moon)"
    elif sat_house == 2:
        is_sade_sati = True
        sade_sati_phase = "Setting Phase / பாத சனி (2nd from Moon)"

    return {
        "timestamp": now.isoformat(),
        "transits": transits,
        "sade_sati": {
            "is_active": is_sade_sati,
            "phase": sade_sati_phase,
            "saturn_house_from_moon": sat_house,
            "notes": "Saturn transiting 12th, 1st, or 2nd from natal Moon creates the transformative 7.5-year cycle of disciplined growth and spiritual purification."
        }
    }
