"""
Vedic Astrology Engine powered by PyJHora conventions and Swiss Ephemeris.
Supports high-precision JPL ephemeris files (1800-2400 AD).
"""

import os
import math
from datetime import datetime, date
import swisseph as swe
from jhora.panchanga import drik
from jhora import utils
from jhora.horoscope.main import Horoscope
from jhora.horoscope.chart import charts, ashtakavarga, strength, house, dosha, raja_yoga
from jhora.horoscope.dhasa.graha import vimsottari
from jhora.horoscope.match import compatibility
from vedic_constants import RASHIS, GRAHAS, NAKSHATRAS, BHAVAS

# Initialize Swiss Ephemeris path
EPHE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ephe'))
if os.path.exists(EPHE_DIR):
    swe.set_ephe_path(EPHE_DIR)

AYANAMSA_MAP = {
    "LAHIRI": swe.SIDM_LAHIRI,
    "KP": swe.SIDM_KRISHNAMURTI,
    "RAMAN": swe.SIDM_RAMAN,
    "YUKTESHWAR": swe.SIDM_YUKTESHWAR,
    "JN_BHASIN": swe.SIDM_JN_BHASIN,
    "SURYASIDDHANTA": swe.SIDM_SURYASIDDHANTA,
    "TROPICAL": None
}

PLANET_IDS = [
    (swe.SUN, "Sun", "Surya", "☉"),
    (swe.MOON, "Moon", "Chandra", "☾"),
    (swe.MARS, "Mars", "Mangala", "♂"),
    (swe.MERCURY, "Mercury", "Budha", "☿"),
    (swe.JUPITER, "Jupiter", "Guru", "♃"),
    (swe.VENUS, "Venus", "Shukra", "♀"),
    (swe.SATURN, "Saturn", "Shani", "♄"),
    (swe.MEAN_NODE, "Rahu", "Rahu", "☊"),
    (swe.TRUE_NODE, "True Rahu", "True Rahu", "☊"),
    (swe.URANUS, "Uranus", "Arun", "♅"),
    (swe.NEPTUNE, "Neptune", "Varun", "♆"),
    (swe.PLUTO, "Pluto", "Yama", "♇")
]

DIVISIONAL_CHARTS = [
    {"factor": 1, "code": "D-1", "name": "Rasi Chart", "desc": "Physical destiny, health, vitality & general life"},
    {"factor": 9, "code": "D-9", "name": "Navamsa Chart", "desc": "Dharma, marriage, inner self & spiritual fruitfulness"},
    {"factor": 2, "code": "D-2", "name": "Hora Chart", "desc": "Wealth, finances, prosperity & speech"},
    {"factor": 3, "code": "D-3", "name": "Drekkana Chart", "desc": "Siblings, courage, vitality & 22nd drekkana"},
    {"factor": 4, "code": "D-4", "name": "Chaturthamsa Chart", "desc": "Fortune, real estate, property & fixed assets"},
    {"factor": 7, "code": "D-7", "name": "Saptamsa Chart", "desc": "Children, lineage, progeny & grandchildren"},
    {"factor": 10, "code": "D-10", "name": "Dasamsa Chart", "desc": "Career, fame, profession, rank & societal impact"},
    {"factor": 12, "code": "D-12", "name": "Dwadasamsa Chart", "desc": "Parents, ancestral lineage & hereditary karma"},
    {"factor": 16, "code": "D-16", "name": "Shodasamsa Chart", "desc": "Vehicles, conveyances, luxuries & comforts"},
    {"factor": 20, "code": "D-20", "name": "Vimsamsa Chart", "desc": "Spiritual upasana, devotion, mantra siddhi"},
    {"factor": 24, "code": "D-24", "name": "Chaturvimsamsa Chart", "desc": "Higher learning, intellectual prowess & vidya"},
    {"factor": 27, "code": "D-27", "name": "Saptavimsamsa Chart", "desc": "Subtle strengths, weaknesses & bhaga"},
    {"factor": 30, "code": "D-30", "name": "Trimsamsa Chart", "desc": "Evils, misfortunes, adversities & arishta"},
    {"factor": 60, "code": "D-60", "name": "Shastiamsa Chart", "desc": "Past-life root karma, ultimate fine destiny"}
]

CHARA_KARAKA_NAMES = [
    "Atmakaraka (AK)", "Amatyakaraka (AmK)", "Bhratrikaraka (BK)",
    "Matrikaraka (MK)", "Pitrikaraka (PiK)", "Putrakaraka (PK)",
    "Gnatikaraka (GK)", "Darakaraka (DK)"
]

def format_dms(deg_float):
    d = int(deg_float)
    rem = (deg_float - d) * 60
    m = int(rem)
    s = int(round((rem - m) * 60))
    if s >= 60:
        s = 0
        m += 1
    if m >= 60:
        m = 0
        d += 1
    return f"{d}° {m:02d}’ {s:02d}”"

def get_nakshatra_info(longitude):
    deg = longitude % 360
    nak_float = deg / (360.0 / 27.0)
    nak_idx = int(nak_float)
    pada = int((nak_float - nak_idx) * 4) + 1
    nak_data = NAKSHATRAS[nak_idx % 27]
    return {
        "index": nak_idx + 1,
        "name": nak_data["name"],
        "tamil": nak_data.get("tamil", ""),
        "dual": f"{nak_data['name']} / {nak_data.get('tamil', '')}",
        "pada": pada,
        "lord": nak_data["lord"],
        "lord_tamil": nak_data.get("lord_tamil", ""),
        "deity": nak_data["deity"],
        "shakti": nak_data["shakti"],
        "symbol": nak_data["symbol"]
    }

def get_dignity(planet_name, rasi_idx, deg_in_sign):
    # Exaltation & Debilitation definitions
    exalt_deb = {
        "Sun": {"exalt": (0, 10), "deb": (6, 10), "own": [4], "mool": (4, 0, 20)},
        "Moon": {"exalt": (1, 3), "deb": (7, 3), "own": [3], "mool": (1, 3, 30)},
        "Mars": {"exalt": (9, 28), "deb": (3, 28), "own": [0, 7], "mool": (0, 0, 12)},
        "Mercury": {"exalt": (5, 15), "deb": (11, 15), "own": [2, 5], "mool": (5, 15, 20)},
        "Jupiter": {"exalt": (3, 5), "deb": (9, 5), "own": [8, 11], "mool": (8, 0, 10)},
        "Venus": {"exalt": (11, 27), "deb": (5, 27), "own": [1, 6], "mool": (6, 0, 15)},
        "Saturn": {"exalt": (6, 20), "deb": (0, 20), "own": [9, 10], "mool": (10, 0, 20)},
        "Rahu": {"exalt": (1, 15), "deb": (7, 15), "own": [10], "mool": (1, 0, 30)},
        "Ketu": {"exalt": (7, 15), "deb": (1, 15), "own": [7], "mool": (7, 0, 30)}
    }
    info = exalt_deb.get(planet_name)
    if not info:
        return "Neutral"
    if rasi_idx == info["exalt"][0]:
        return "Exalted (உச்சம்)"
    if rasi_idx == info["deb"][0]:
        return "Debilitated (நீசம்)"
    if rasi_idx == info["mool"][0] and info["mool"][1] <= deg_in_sign <= info["mool"][2]:
        return "Moolatrikona (மூலத்திரிகோணம்)"
    if rasi_idx in info["own"]:
        return "Own Sign (ஆட்சி)"
    # Friends / Enemies relative to sign lord
    sign_lord = RASHIS[rasi_idx]["lord"].split(" ")[0]
    friends_map = {
        "Sun": {"friends": ["Moon", "Mars", "Jupiter"], "enemies": ["Venus", "Saturn"]},
        "Moon": {"friends": ["Sun", "Mercury"], "enemies": []},
        "Mars": {"friends": ["Sun", "Moon", "Jupiter"], "enemies": ["Mercury"]},
        "Mercury": {"friends": ["Sun", "Venus"], "enemies": ["Moon"]},
        "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "enemies": ["Mercury", "Venus"]},
        "Venus": {"friends": ["Mercury", "Saturn"], "enemies": ["Sun", "Moon"]},
        "Saturn": {"friends": ["Mercury", "Venus"], "enemies": ["Sun", "Moon", "Mars"]}
    }
    p_rel = friends_map.get(planet_name)
    if p_rel:
        if sign_lord in p_rel["friends"]:
            return "Friendly Sign (நட்பு)"
        if sign_lord in p_rel["enemies"]:
            return "Enemy Sign (பகை)"
    return "Neutral Sign (சமம்)"

class VedicHoroscopeEngine:
    def __init__(self, birth_date: date, birth_time_str: str,
                 place_name: str, lat: float, lon: float, tz: float,
                 ayanamsa: str = "LAHIRI", house_system: str = "SRIPATHI"):
        self.birth_date = birth_date
        self.birth_time_str = birth_time_str
        self.place_name = place_name
        self.lat = lat
        self.lon = lon
        self.tz = tz
        self.ayanamsa = ayanamsa.upper()
        self.house_system = house_system.upper()

        # Swiss Ephemeris configuration
        swe.set_ephe_path(EPHE_DIR)
        sid_mode = AYANAMSA_MAP.get(self.ayanamsa, swe.SIDM_LAHIRI)
        if sid_mode is not None:
            swe.set_sid_mode(sid_mode)
        
        # Parse time
        parts = [int(p) for p in birth_time_str.split(':')]
        h = parts[0]
        m = parts[1] if len(parts) > 1 else 0
        s = parts[2] if len(parts) > 2 else 0
        self.time_tuple = (h, m, s)
        self.hour_float = h + m / 60.0 + s / 3600.0

        # Julian Day Numbers
        self.jd_utc = swe.julday(birth_date.year, birth_date.month, birth_date.day, self.hour_float - self.tz)
        self.jd_local = swe.julday(birth_date.year, birth_date.month, birth_date.day, self.hour_float)

        self.dob = drik.Date(birth_date.year, birth_date.month, birth_date.day)
        self.place = drik.Place(place_name, lat, lon, tz)

        # PyJHora Horoscope object
        self.jhora_h = Horoscope(
            place_with_country_code=place_name,
            latitude=lat, longitude=lon, timezone_offset=tz,
            date_in=self.dob, birth_time=f"{h}:{m:02d}:{s:02d}"
        )

    def calculate_ephemeris_status(self):
        ephe_files = []
        if os.path.exists(EPHE_DIR):
            ephe_files = os.listdir(EPHE_DIR)
        ayanamsa_val = swe.get_ayanamsa_ut(self.jd_utc)
        return {
            "swiss_eph_version": swe.version,
            "ephe_path": EPHE_DIR,
            "ephe_files": ephe_files,
            "is_jpl_precision": any(f.endswith('.se1') for f in ephe_files),
            "ayanamsa_name": self.ayanamsa,
            "ayanamsa_value_dms": format_dms(ayanamsa_val),
            "ayanamsa_degrees": round(ayanamsa_val, 6),
            "julian_day_utc": round(self.jd_utc, 6),
            "julian_day_local": round(self.jd_local, 6)
        }

    def calculate_planets_and_lagna(self):
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        if self.ayanamsa == "TROPICAL":
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED

        # 1. Ascendant (Lagna)
        houses, ascmc = swe.houses_ex(self.jd_utc, self.lat, self.lon, b'P', flags)
        lagna_deg = ascmc[0] % 360
        lagna_rasi = int(lagna_deg / 30)
        lagna_deg_in_sign = lagna_deg % 30
        lagna_nak = get_nakshatra_info(lagna_deg)

        planets_data = []

        # Lagna Entry
        planets_data.append({
            "key": "Lagna",
            "name": "Ascendant / Lagna",
            "sanskrit": "Lagna / லக்னம்",
            "tamil": "லக்னம்",
            "symbol": "ASC",
            "longitude": round(lagna_deg, 4),
            "longitude_dms": format_dms(lagna_deg),
            "rasi_id": lagna_rasi,
            "rasi_name": RASHIS[lagna_rasi]["name"],
            "rasi_tamil": RASHIS[lagna_rasi].get("tamil", ""),
            "rasi_sanskrit": RASHIS[lagna_rasi]["sanskrit"],
            "rasi_symbol": RASHIS[lagna_rasi]["symbol"],
            "deg_in_sign": round(lagna_deg_in_sign, 4),
            "deg_in_sign_dms": format_dms(lagna_deg_in_sign),
            "speed": 0.0,
            "is_retrograde": False,
            "is_combust": False,
            "dignity": "Ascendant / லக்னம்",
            "nakshatra": lagna_nak,
            "chara_karaka": "Lagna"
        })

        # Calculate Sun first to compute combustion
        sun_res, _ = swe.calc_ut(self.jd_utc, swe.SUN, flags)
        sun_lon = sun_res[0] % 360

        # Calculate Planets
        calc_planets = [
            (swe.SUN, "Sun", "Surya", "☉", 0),
            (swe.MOON, "Moon", "Chandra", "☾", 1),
            (swe.MARS, "Mars", "Mangala", "♂", 2),
            (swe.MERCURY, "Mercury", "Budha", "☿", 3),
            (swe.JUPITER, "Jupiter", "Guru", "♃", 4),
            (swe.VENUS, "Venus", "Shukra", "♀", 5),
            (swe.SATURN, "Saturn", "Shani", "♄", 6),
            (swe.MEAN_NODE, "Rahu", "Rahu", "☊", 7)
        ]

        # Combustion limits from Sun in degrees
        combust_limits = {
            "Moon": 12.0, "Mars": 17.0, "Mercury": 14.0,
            "Jupiter": 11.0, "Venus": 10.0, "Saturn": 15.0
        }

        temp_planets = []

        for pid, name, sanskrit, sym, g_idx in calc_planets:
            res, _ = swe.calc_ut(self.jd_utc, pid, flags)
            lon = res[0] % 360
            speed = res[3]
            is_retro = speed < 0 if pid != swe.MEAN_NODE else True
            
            # Distance to Sun
            dist_to_sun = abs(lon - sun_lon)
            if dist_to_sun > 180:
                dist_to_sun = 360 - dist_to_sun
            is_combust = False
            if name in combust_limits and dist_to_sun <= combust_limits[name]:
                is_combust = True

            rasi_id = int(lon / 30)
            deg_in_sign = lon % 30
            nak = get_nakshatra_info(lon)
            dignity = get_dignity(name, rasi_id, deg_in_sign)

            p_entry = {
                "key": name,
                "name": name,
                "sanskrit": f"{sanskrit} ({GRAHAS[g_idx]['sanskrit']})",
                "symbol": sym,
                "longitude": round(lon, 4),
                "longitude_dms": format_dms(lon),
                "rasi_id": rasi_id,
                "rasi_name": RASHIS[rasi_id]["name"],
                "rasi_sanskrit": RASHIS[rasi_id]["sanskrit"],
                "rasi_symbol": RASHIS[rasi_id]["symbol"],
                "deg_in_sign": round(deg_in_sign, 4),
                "deg_in_sign_dms": format_dms(deg_in_sign),
                "speed": round(speed, 6),
                "is_retrograde": is_retro,
                "is_combust": is_combust,
                "dignity": dignity,
                "nakshatra": nak,
                "gemstone": GRAHAS[g_idx]["gemstone"],
                "color": GRAHAS[g_idx]["color"]
            }
            temp_planets.append((name, deg_in_sign, p_entry))

        # Compute Ketu (opposite to Rahu by exactly 180 degrees)
        rahu_entry = next(p[2] for p in temp_planets if p[0] == "Rahu")
        ketu_lon = (rahu_entry["longitude"] + 180.0) % 360
        ketu_rasi = int(ketu_lon / 30)
        ketu_deg_in_sign = ketu_lon % 30
        ketu_nak = get_nakshatra_info(ketu_lon)
        ketu_entry = {
            "key": "Ketu",
            "name": "Ketu",
            "sanskrit": "Ketu / கேது",
            "tamil": "கேது",
            "symbol": "☋",
            "longitude": round(ketu_lon, 4),
            "longitude_dms": format_dms(ketu_lon),
            "rasi_id": ketu_rasi,
            "rasi_name": RASHIS[ketu_rasi]["name"],
            "rasi_tamil": RASHIS[ketu_rasi].get("tamil", ""),
            "rasi_sanskrit": RASHIS[ketu_rasi]["sanskrit"],
            "rasi_symbol": RASHIS[ketu_rasi]["symbol"],
            "deg_in_sign": round(ketu_deg_in_sign, 4),
            "deg_in_sign_dms": format_dms(ketu_deg_in_sign),
            "speed": rahu_entry["speed"],
            "is_retrograde": True,
            "is_combust": False,
            "dignity": get_dignity("Ketu", ketu_rasi, ketu_deg_in_sign),
            "nakshatra": ketu_nak,
            "gemstone": GRAHAS[8]["gemstone"],
            "color": GRAHAS[8]["color"]
        }
        temp_planets.append(("Ketu", ketu_deg_in_sign, ketu_entry))

        # Compute 7 Chara Karakas (Sun to Saturn, by descending degree in sign)
        seven_grahas = [p for p in temp_planets if p[0] in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]]
        seven_grahas.sort(key=lambda x: x[1], reverse=True)
        for idx, item in enumerate(seven_grahas):
            item[2]["chara_karaka"] = CHARA_KARAKA_NAMES[idx]

        rahu_entry["chara_karaka"] = "Upagraha"
        ketu_entry["chara_karaka"] = "Mokshakaraka"

        # Outer planets (Uranus, Neptune, Pluto)
        outer_planets = [
            (swe.URANUS, "Uranus", "Arun", "♅"),
            (swe.NEPTUNE, "Neptune", "Varun", "♆"),
            (swe.PLUTO, "Pluto", "Yama", "♇")
        ]
        outer_entries = []
        for pid, name, sanskrit, sym in outer_planets:
            res, _ = swe.calc_ut(self.jd_utc, pid, flags)
            lon = res[0] % 360
            rasi_id = int(lon / 30)
            deg_in_sign = lon % 30
            nak = get_nakshatra_info(lon)
            outer_entries.append({
                "key": name,
                "name": name,
                "sanskrit": sanskrit,
                "symbol": sym,
                "longitude": round(lon, 4),
                "longitude_dms": format_dms(lon),
                "rasi_id": rasi_id,
                "rasi_name": RASHIS[rasi_id]["name"],
                "rasi_sanskrit": RASHIS[rasi_id]["sanskrit"],
                "rasi_symbol": RASHIS[rasi_id]["symbol"],
                "deg_in_sign": round(deg_in_sign, 4),
                "deg_in_sign_dms": format_dms(deg_in_sign),
                "speed": round(res[3], 6),
                "is_retrograde": res[3] < 0,
                "is_combust": False,
                "dignity": "Modern Graha",
                "nakshatra": nak,
                "chara_karaka": "-"
            })

        for p in temp_planets:
            planets_data.append(p[2])
        for p in outer_entries:
            planets_data.append(p)

        return planets_data

    def calculate_divisional_charts(self):
        div_charts_dict = {}
        for d in DIVISIONAL_CHARTS:
            factor = d["factor"]
            code = d["code"]
            try:
                # Use charts.divisional_chart from PyJHora
                chart_pos = charts.divisional_chart(self.jd_local, self.place, divisional_chart_factor=factor)
                # chart_pos: [['L', (rasi, deg)], [0, (rasi, deg)], ... [8, (rasi, deg)]]
                houses_planets = [[] for _ in range(12)]
                planet_key_map = {
                    'L': 'Lagna (ASC)', 0: 'Sun ☉', 1: 'Moon ☾', 2: 'Mars ♂',
                    3: 'Mercury ☿', 4: 'Jupiter ♃', 5: 'Venus ♀', 6: 'Saturn ♄',
                    7: 'Rahu ☊', 8: 'Ketu ☋'
                }
                planet_tamil_map = {
                    'L': 'லக்னம்', 0: 'சூரியன்', 1: 'சந்திரன்', 2: 'செவ்வாய்',
                    3: 'புதன்', 4: 'குரு', 5: 'சுக்கிரன்', 6: 'சனி',
                    7: 'ராகு', 8: 'கேது'
                }
                planet_short_map = {
                    'L': 'ASC', 0: 'Su', 1: 'Mo', 2: 'Ma',
                    3: 'Me', 4: 'Ju', 5: 'Ve', 6: 'Sa',
                    7: 'Ra', 8: 'Ke'
                }
                asc_rasi = 0
                for item in chart_pos:
                    p_id = item[0]
                    r_id = item[1][0]
                    deg = item[1][1]
                    p_label = planet_key_map.get(p_id, str(p_id))
                    abs_lon = (r_id * 30.0 + deg) % 360.0
                    nak_info = get_nakshatra_info(abs_lon)
                    houses_planets[r_id].append({
                        "id": p_id,
                        "name": p_label.split(' ')[0],
                        "short": planet_short_map.get(p_id, str(p_id)),
                        "label": p_label,
                        "tamil": planet_tamil_map.get(p_id, ""),
                        "deg": round(deg, 2),
                        "deg_dms": format_dms(deg),
                        "nakshatra": nak_info["name"],
                        "nakshatra_tamil": nak_info["tamil"],
                        "pada": nak_info["pada"],
                        "nak_pada": f"{nak_info['name']} {nak_info['pada']}",
                        "nak_pada_tamil": f"{nak_info['tamil']}-{nak_info['pada']}"
                    })
                    if p_id == 'L':
                        asc_rasi = r_id

                # Structure for North Indian (House-centric: House 1 to 12)
                # House 1 = asc_rasi, House 2 = (asc_rasi + 1)%12, etc.
                north_indian_houses = []
                for h in range(1, 13):
                    cur_rasi = (asc_rasi + (h - 1)) % 12
                    north_indian_houses.append({
                        "house": h,
                        "rasi_id": cur_rasi,
                        "rasi_name": RASHIS[cur_rasi]["name"],
                        "rasi_tamil": RASHIS[cur_rasi]["tamil"],
                        "rasi_dual": f"{RASHIS[cur_rasi]['name']} / {RASHIS[cur_rasi]['tamil']}",
                        "rasi_sanskrit": RASHIS[cur_rasi]["sanskrit"],
                        "rasi_symbol": RASHIS[cur_rasi]["symbol"],
                        "planets": houses_planets[cur_rasi]
                    })

                # Structure for South Indian (Sign-centric: fixed 12 signs)
                south_indian_signs = []
                for r_idx in range(12):
                    is_asc = (r_idx == asc_rasi)
                    house_num = ((r_idx - asc_rasi) % 12) + 1
                    south_indian_signs.append({
                        "rasi_id": r_idx,
                        "rasi_name": RASHIS[r_idx]["name"],
                        "rasi_tamil": RASHIS[r_idx]["tamil"],
                        "rasi_dual": f"{RASHIS[r_idx]['name']} / {RASHIS[r_idx]['tamil']}",
                        "rasi_sanskrit": RASHIS[r_idx]["sanskrit"],
                        "rasi_symbol": RASHIS[r_idx]["symbol"],
                        "house_num": house_num,
                        "is_ascendant": is_asc,
                        "planets": houses_planets[r_idx]
                    })

                div_charts_dict[code] = {
                    "code": code,
                    "factor": factor,
                    "name": d["name"],
                    "description": d["desc"],
                    "ascendant_rasi": asc_rasi,
                    "ascendant_rasi_name": RASHIS[asc_rasi]["name"],
                    "ascendant_rasi_tamil": RASHIS[asc_rasi]["tamil"],
                    "ascendant_rasi_dual": f"{RASHIS[asc_rasi]['name']} / {RASHIS[asc_rasi]['tamil']}",
                    "north_indian": north_indian_houses,
                    "south_indian": south_indian_signs
                }
            except Exception as e:
                print(f"Error computing chart {code}: {e}")

        return div_charts_dict

    def calculate_special_lagnas_and_arudhas(self):
        try:
            d1_info = self.jhora_h.get_horoscope_information_for_chart(chart_index=0)
            raw_dict = d1_info[0]
            arudhas = []
            special_lagnas = []
            upagrahas = []

            for k, v in raw_dict.items():
                if "Arudha" in k or "Pada" in k or "Upapada" in k:
                    arudhas.append({"point": k.replace("D-1-", ""), "position": v})
                elif "Lagna" in k and "D-1-" not in k:
                    special_lagnas.append({"point": k.replace("Custom Kundali (Dn)-", ""), "position": v})
                elif any(u in k.lower() for u in ['gulika', 'maandi', 'dhuma', 'vyatipaata', 'kaala', 'mrityu', 'yama']):
                    upagrahas.append({"point": k.replace("Custom Kundali (Dn)-", ""), "position": v})

            return {
                "arudha_padas": arudhas,
                "special_lagnas": special_lagnas,
                "upagrahas": upagrahas
            }
        except Exception as e:
            print("Error computing special lagnas:", e)
            return {"arudha_padas": [], "special_lagnas": [], "upagrahas": []}

    def calculate_panchanga(self):
        cal = self.jhora_h.calendar_info
        cal_clean = {}
        for k, v in cal.items():
            clean_k = k.replace(":", "").strip()
            cal_clean[clean_k] = str(v).strip()

        # Build clean structured panchanga elements
        tithi_str = cal_clean.get("Tithi", "")
        nak_str = cal_clean.get("Nakshatram", "")
        yoga_str = cal_clean.get("Yoga", "")
        karana_str = cal_clean.get("Karana", "")
        vaara_str = cal_clean.get("Day", "")

        return {
            "raw": cal_clean,
            "vaara": {
                "day": vaara_str,
                "lord": {"Sunday": "Sun ☉", "Monday": "Moon ☾", "Tuesday": "Mars ♂",
                         "Wednesday": "Mercury ☿", "Thursday": "Jupiter ♃", "Friday": "Venus ♀",
                         "Saturday": "Saturn ♄"}.get(vaara_str, "Sun ☉")
            },
            "tithi": tithi_str,
            "nakshatra": nak_str,
            "yoga": yoga_str,
            "karana": karana_str,
            "sunrise": cal_clean.get("Sun Rise", ""),
            "sunset": cal_clean.get("Sun Set", ""),
            "moonrise": cal_clean.get("Moon Rise", ""),
            "moonset": cal_clean.get("Moon Set", ""),
            "rahu_kalam": cal_clean.get("Raagu Kaalam", ""),
            "yamagandam": cal_clean.get("Yamagandam", ""),
            "gulika_kalam": cal_clean.get("KuLigai", ""),
            "abhijit_muhurta": cal_clean.get("Abhijit", ""),
            "dur_muhurtham": cal_clean.get("Dhur Muhurtham", ""),
            "samvatsara": cal_clean.get("Lunar Year/Month", ""),
            "solar_month": cal_clean.get("Solar Month", ""),
            "kali_year": cal_clean.get("Kali Year", ""),
            "vikram_year": cal_clean.get("Vikarama Year", ""),
            "saka_year": cal_clean.get("Saka Year", "")
        }

    def calculate_vimshottari_dasha(self, target_date: date = None):
        if target_date is None:
            target_date = date.today()

        jd = self.jd_local
        bal, db = vimsottari.get_vimsottari_dhasa_bhukthi(jd, self.place)
        # bal: (balance_years, balance_months, balance_days)
        # db: [[(dhasa_lord, bhukthi_lord), (y, m, d_frac), duration_years], ...]
        
        balance_str = f"{bal[0]} Years, {bal[1]} Months, {bal[2]} Days"

        dasha_hierarchy = []
        current_mahadasha = None
        current_antardasha = None

        planet_names = ["Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus"]
        # Mahadasha order in Vimshottari
        # Group by Mahadasha lord
        maha_dict = {}
        for row in db:
            (dl_idx, bl_idx) = row[0] if isinstance(row[0], (list, tuple)) else (row[0], row[1])
            start_date_tuple = row[1]
            dur = row[2]
            
            dl_name = GRAHAS[dl_idx]["name"]
            bl_name = GRAHAS[bl_idx]["name"]

            dt_start = date(int(start_date_tuple[0]), int(start_date_tuple[1]), int(start_date_tuple[2]))

            if dl_name not in maha_dict:
                maha_dict[dl_name] = {
                    "lord": dl_name,
                    "sanskrit": GRAHAS[dl_idx]["sanskrit"],
                    "symbol": GRAHAS[dl_idx]["symbol"],
                    "color": GRAHAS[dl_idx]["color"],
                    "start_date": dt_start.isoformat(),
                    "antardashas": []
                }
            
            maha_dict[dl_name]["antardashas"].append({
                "sub_lord": bl_name,
                "sanskrit": GRAHAS[bl_idx]["sanskrit"],
                "symbol": GRAHAS[bl_idx]["symbol"],
                "start_date": dt_start.isoformat(),
                "duration_years": round(dur, 2)
            })

        dasha_list = list(maha_dict.values())
        
        # Calculate end dates & find active dasha
        for m_idx, m in enumerate(dasha_list):
            if m_idx + 1 < len(dasha_list):
                m["end_date"] = dasha_list[m_idx + 1]["start_date"]
            else:
                last_start = datetime.fromisoformat(m["start_date"])
                m["end_date"] = date(last_start.year + 20, last_start.month, last_start.day).isoformat()

            # Antardasha end dates
            for a_idx, a in enumerate(m["antardashas"]):
                if a_idx + 1 < len(m["antardashas"]):
                    a["end_date"] = m["antardashas"][a_idx + 1]["start_date"]
                else:
                    a["end_date"] = m["end_date"]

                a_start = date.fromisoformat(a["start_date"])
                a_end = date.fromisoformat(a["end_date"])
                if a_start <= target_date <= a_end:
                    current_mahadasha = m["lord"]
                    current_antardasha = a["sub_lord"]
                    a["is_active"] = True
                    m["is_active"] = True
                else:
                    a["is_active"] = False

            m["is_active"] = (current_mahadasha == m["lord"])

        return {
            "balance_at_birth": balance_str,
            "target_date": target_date.isoformat(),
            "active_mahadasha": current_mahadasha,
            "active_antardasha": current_antardasha,
            "dashas": dasha_list
        }

    def calculate_shadbala(self):
        try:
            sb = self.jhora_h._get_shad_bala(self.dob, self.time_tuple, self.place)
            # sb format: 9 rows x 7 planets
            # 0: Sthana Bala
            # 1: Dig Bala
            # 2: Kaala Bala
            # 3: Cheshta Bala
            # 4: Naisargika Bala
            # 5: Drik Bala
            # 6: Total Shadbala (Shashtiamsas)
            # 7: Total Rupas
            # 8: Strength Ratio
            planets_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
            min_req_rupas = {"Sun": 6.5, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0, "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0}

            shadbala_result = []
            for col_idx, p_name in enumerate(planets_7):
                sthana = sb[0][col_idx]
                dig = sb[1][col_idx]
                kaala = sb[2][col_idx]
                cheshta = sb[3][col_idx]
                naisargika = sb[4][col_idx]
                drik_val = sb[5][col_idx]
                total = sb[6][col_idx]
                rupas = sb[7][col_idx]
                ratio = sb[8][col_idx]
                req = min_req_rupas.get(p_name, 6.0)
                is_strong = rupas >= req

                shadbala_result.append({
                    "planet": p_name,
                    "symbol": GRAHAS[col_idx]["symbol"],
                    "sthana_bala": round(sthana, 2),
                    "dig_bala": round(dig, 2),
                    "kaala_bala": round(kaala, 2),
                    "cheshta_bala": round(cheshta, 2),
                    "naisargika_bala": round(naisargika, 2),
                    "drik_bala": round(drik_val, 2),
                    "total_shashtiamsa": round(total, 2),
                    "total_rupas": round(rupas, 2),
                    "min_required_rupas": req,
                    "strength_ratio": round(ratio, 2),
                    "is_strong": is_strong,
                    "power_percentage": round((rupas / req) * 100, 1)
                })

            # Sort by strength ratio for ranking
            shadbala_result.sort(key=lambda x: x["strength_ratio"], reverse=True)
            for rank, item in enumerate(shadbala_result, 1):
                item["rank"] = rank

            return shadbala_result
        except Exception as e:
            print("Error calculating Shadbala:", e)
            return []

    def calculate_ashtakavarga(self):
        try:
            d1_chart = charts.divisional_chart(self.jd_local, self.place, divisional_chart_factor=1)
            h_to_p = utils.get_house_planet_list_from_planet_positions(d1_chart)
            bav_raw, sav_raw, pav_raw = ashtakavarga.get_ashtaka_varga(h_to_p)

            sav_list = []
            for r_idx in range(12):
                pts = int(sav_raw[r_idx])
                sav_list.append({
                    "rasi_id": r_idx,
                    "rasi_name": RASHIS[r_idx]["name"],
                    "rasi_sanskrit": RASHIS[r_idx]["sanskrit"],
                    "rasi_symbol": RASHIS[r_idx]["symbol"],
                    "points": pts,
                    "strength": "High (Benefic)" if pts >= 30 else ("Medium (Average)" if pts >= 25 else "Low (Sensitive)"),
                    "color": "#10b981" if pts >= 30 else ("#f59e0b" if pts >= 25 else "#ef4444")
                })

            # BAV breakdown per planet (0=Sun, 1=Moon, 2=Mars, 3=Mercury, 4=Jupiter, 5=Venus, 6=Saturn, 7=Lagna)
            bav_dict = {}
            planet_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Lagna"]
            for idx, p_name in enumerate(planet_names):
                if idx < len(bav_raw):
                    bav_dict[p_name] = [int(pt) for pt in bav_raw[idx]]

            return {
                "sarvashtakavarga": sav_list,
                "total_points": sum(s["points"] for s in sav_list),
                "bhinnashtakavarga": bav_dict
            }
        except Exception as e:
            print("Error calculating Ashtakavarga:", e)
            return {"sarvashtakavarga": [], "total_points": 337, "bhinnashtakavarga": {}}

    def calculate_yogas_and_doshas(self):
        # 1. Doshas
        try:
            doshas_dict = dosha.get_dosha_details(self.jd_local, self.place)
        except Exception as e:
            print("Error in get_dosha_details:", e)
            doshas_dict = {}

        clean_doshas = []
        for name, desc in doshas_dict.items():
            # Clean HTML tags from jhora output
            clean_desc = desc.replace("<html>", "").replace("</html>", "").replace("<br>", "\n").strip()
            is_present = not ("no " in clean_desc.lower() and "dosha" in clean_desc.lower())
            clean_doshas.append({
                "name": name,
                "is_present": is_present,
                "description": clean_desc,
                "status": "Present (உள்ளது - Active)" if is_present else "Not Present (இல்லை - Nil)"
            })

        # 2. Key Yogas
        d1_chart = charts.divisional_chart(self.jd_local, self.place, divisional_chart_factor=1)
        detected_yogas = []

        # Check Pancha Mahapurusha & major auspicious yogas
        yoga_checks = [
            ("Gajakesari Yoga", "gaja_kesari_yoga_from_planet_positions",
             "Jupiter in a quadrant (1, 4, 7, 10) from Moon. Bestows virtue, royal honor, lasting fame, prosperity and intellect. (கஜகேசரி யோகம்: புகழ், செல்வம், அறிவு)"),
            ("Budhaditya Yoga", "budha_aditya_yoga_from_planet_positions" if hasattr(raja_yoga, "budha_aditya_yoga_from_planet_positions") else None,
             "Conjunction of Sun and Mercury. Sharp intellect, eloquence, analytical brilliance, leadership and professional success. (புதாதித்ய யோகம்: கூர்மையான அறிவு, கல்வி மேன்மை)"),
            ("Ruchaka Yoga (Mahapurusha)", "ruchaka_yoga_from_planet_positions" if hasattr(raja_yoga, "ruchaka_yoga_from_planet_positions") else None,
             "Mars in own sign or exaltation in a Kendra. Bestows valor, military prowess, executive leadership, property and physical vigor. (ருச்சக யோகம்: தலைமை, வீரம், பூமி லாபம்)"),
            ("Bhadra Yoga (Mahapurusha)", "bhadra_yoga_from_planet_positions" if hasattr(raja_yoga, "bhadra_yoga_from_planet_positions") else None,
             "Mercury exalted or in own sign in a Kendra. High intelligence, sharp commerce, longevity, scholarly renown and speech. (பத்ர யோகம்: கல்வி, வியாபாரம், வாக்கு வன்மை)"),
            ("Hamsa Yoga (Mahapurusha)", "hamsa_yoga_from_planet_positions" if hasattr(raja_yoga, "hamsa_yoga_from_planet_positions") else None,
             "Jupiter exalted or in own sign in a Kendra. Righteousness, profound wisdom, purity of character, divine grace and honor. (ஹம்ச யோகம்: தெய்வீக அருள், நற்குணம், மேன்மை)"),
            ("Malavya Yoga (Mahapurusha)", "malavya_yoga_from_planet_positions" if hasattr(raja_yoga, "malavya_yoga_from_planet_positions") else None,
             "Venus exalted or in own sign in a Kendra. Refinement, artistic elegance, luxurious conveyances, aesthetic charm and marital bliss. (மாளவ்ய யோகம்: கலை ஆர்வம், வாகனம், சுகபோகம்)"),
            ("Sasa Yoga (Mahapurusha)", "sasa_yoga_from_planet_positions" if hasattr(raja_yoga, "sasa_yoga_from_planet_positions") else None,
             "Saturn exalted or in own sign in a Kendra. Authority over masses, commanding discipline, enduring longevity and tenacity. (சச யோகம்: மக்கள் ஆதரவு, அதிகாரம், நீண்ட ஆயுள்)"),
            ("Amala Yoga", "amala_yoga_from_planet_positions" if hasattr(raja_yoga, "amala_yoga_from_planet_positions") else None,
             "Benefic occupying the 10th house from Lagna or Moon. Spotless reputation, philanthropic disposition and enduring career success. (அமல யோகம்: நற்பெயர், தொழில் வெற்றி)"),
            ("Adhi Yoga", "adhi_yoga_from_planet_positions" if hasattr(raja_yoga, "adhi_yoga_from_planet_positions") else None,
             "Benefics in 6th, 7th, 8th from Moon or Lagna. Overcoming competitors, victory, joy and prosperity. (அதி யோகம்: தடைகள் நீங்குதல், வெற்றி, சுப வாழ்வு)")
        ]

        from jhora.horoscope.chart import yoga as y_mod
        for y_name, fn_name, desc in yoga_checks:
            try:
                fn = getattr(y_mod, fn_name, None) or getattr(raja_yoga, fn_name, None)
                if fn:
                    is_active = fn(d1_chart)
                    if is_active:
                        detected_yogas.append({
                            "name": y_name,
                            "type": "Auspicious Yoga (சுப யோகம்)",
                            "description": desc,
                            "is_present": True
                        })
            except Exception:
                pass

        # Check Neechabhanga Raja Yoga
        try:
            nb = raja_yoga.neecha_bhanga_raja_yoga(d1_chart)
            if nb:
                detected_yogas.append({
                    "name": "Neechabhanga Raja Yoga",
                    "type": "Raja Yoga (ராஜ யோகம்)",
                    "description": "Cancellation of planetary debilitation turning into a powerful rise in life after overcoming early trials. (நீசபங்க ராஜ யோகம்: தடைகளை வென்று பெரும் வெற்றி)",
                    "is_present": True
                })
        except Exception:
            pass

        # Check Viparita Raja Yoga
        try:
            vip = raja_yoga.vipareetha_raja_yoga(d1_chart)
            if vip:
                detected_yogas.append({
                    "name": "Viparita Raja Yoga (Harsha / Sarala / Vimala)",
                    "type": "Viparita Raja Yoga (விபரீத ராஜ யோகம்)",
                    "description": "Lords of dusthanas (6, 8, 12) placed in other dusthanas. Bestows unexpected sudden elevation and triumph over adversaries. (விபரீத ராஜ யோகம்: எதிர்பாராத திடீர் உயர்வும் யோகமும்)",
                    "is_present": True
                })
        except Exception:
            pass

        return {
            "yogas": detected_yogas,
            "doshas": clean_doshas
        }

    def get_full_analysis(self):
        ephe_status = self.calculate_ephemeris_status()
        planets = self.calculate_planets_and_lagna()
        div_charts = self.calculate_divisional_charts()
        special_pts = self.calculate_special_lagnas_and_arudhas()
        panchanga = self.calculate_panchanga()
        dasha = self.calculate_vimshottari_dasha()
        shadbala = self.calculate_shadbala()
        ashtakavarga_data = self.calculate_ashtakavarga()
        yogas_doshas = self.calculate_yogas_and_doshas()

        return {
            "meta": {
                "name": self.place_name,
                "birth_date": self.birth_date.isoformat(),
                "birth_time": self.birth_time_str,
                "latitude": self.lat,
                "longitude": self.lon,
                "timezone": self.tz,
                "ayanamsa": self.ayanamsa,
                "house_system": self.house_system
            },
            "ephemeris_status": ephe_status,
            "planets": planets,
            "divisional_charts": div_charts,
            "special_points": special_pts,
            "panchanga": panchanga,
            "dasha": dasha,
            "shadbala": shadbala,
            "ashtakavarga": ashtakavarga_data,
            "yogas_and_doshas": yogas_doshas
        }

def calculate_kundali_matching(boy_nakshatra_num: int, boy_pada: int,
                               girl_nakshatra_num: int, girl_pada: int):
    # North Indian Ashtakoota
    match_north = compatibility.Ashtakoota(
        boy_nakshatra_number=boy_nakshatra_num, boy_paadham_number=boy_pada,
        girl_nakshatra_number=girl_nakshatra_num, girl_paadham_number=girl_pada,
        method='North'
    )
    score_list = match_north.compatibility_score()
    # score_list: [varna, vasiya, tara, yoni, graha_maitri, gana, bhakoot, nadi, total, ...]
    
    kootas_north = [
        {"name": "Varna Koota (Work & Ego alignment)", "score": score_list[0], "max": 1, "desc": "Assesses spiritual, intellectual and ego compatibility"},
        {"name": "Vashya Koota (Mutual Attraction & Control)", "score": score_list[1], "max": 2, "desc": "Evaluates magnetism, mutual devotion and dominance balance"},
        {"name": "Tara Koota (Destiny, Health & Longevity)", "score": score_list[2], "max": 3, "desc": "Calculates birth star auspiciousness and vitality"},
        {"name": "Yoni Koota (Biological & Sexual Harmony)", "score": score_list[3], "max": 4, "desc": "Analyzes innate animal instincts and intimate compatibility"},
        {"name": "Graha Maitri Koota (Mental & Psychological Affection)", "score": score_list[4], "max": 5, "desc": "Measures planetary friendship of Moon lords"},
        {"name": "Gana Koota (Temperamental Harmonization)", "score": score_list[5], "max": 6, "desc": "Harmonizes Deva (Divine), Manushya (Human), and Rakshasa (Fiery) temperaments"},
        {"name": "Bhakoot Koota (Emotional Prosperity & Family Welfare)", "score": score_list[6], "max": 7, "desc": "Assesses Moon sign relative placements (avoiding 6-8 and 2-12 doshas)"},
        {"name": "Nadi Koota (Genetic Health & Nervous Resonance)", "score": score_list[7], "max": 8, "desc": "Ensures physiological health, bloodline continuity and progeny vitality"}
    ]

    total_score = score_list[8]
    verdict = "Excellent Match (மிக உத்தமம் - Excellent)" if total_score >= 28 else (
        "Good Match (உத்தமம் - Good)" if total_score >= 21 else (
            "Average / Acceptable Match (மத்திமம் - Average)" if total_score >= 18 else "Incompatible Match (பொருத்தமில்லை - Not Recommended)"
        )
    )

    # South Indian 10 Dasa Poruthams
    match_south = compatibility.Ashtakoota(
        boy_nakshatra_number=boy_nakshatra_num, boy_paadham_number=boy_pada,
        girl_nakshatra_number=girl_nakshatra_num, girl_paadham_number=girl_pada,
        method='South'
    )
    
    south_kootas = [
        {"name": "Dina Porutham / தினப் பொருத்தம் (Health & Longevity)", "status": match_south.dina_porutham_south()},
        {"name": "Gana Porutham / கணப் பொருத்தம் (Temperament & Character)", "status": match_south.gana_porutham_south()},
        {"name": "Mahendra Porutham / மகேந்திரப் பொருத்தம் (Progeny & Lineage Growth)", "status": match_south.mahendra_porutham_south()},
        {"name": "Stree Deergha / ஸ்திரீ தீர்க்கப் பொருத்தம் (Prosperity & Longevity)", "status": match_south.sthree_dheerga_porutham_south()},
        {"name": "Yoni Porutham / யோனிப் பொருத்தம் (Physical & Intimate Harmony)", "status": match_south.yoni_porutham_south()},
        {"name": "Rasi Porutham / ராசிப் பொருத்தம் (Family Harmony & Happiness)", "status": match_south.raasi_porutham_south()},
        {"name": "Rasi Adhipathi / ராசி அதிபதிப் பொருத்தம் (Lord Friendship & Unity)", "status": match_south.raasi_adhipathi_porutham_south()},
        {"name": "Vasiya Porutham / வசியப் பொருத்தம் (Mutual Love & Attraction)", "status": match_south.vasiya_porutham_south()},
        {"name": "Rajju Porutham / ரஜ்ஜுப் பொருத்தம் (Mangalya Strength & Long Life)", "status": match_south.rajju_porutham_south()},
        {"name": "Vedha Porutham / வேதைப் பொருத்தம் (Affliction-Free Partnership)", "status": match_south.vedha_porutham_south()}
    ]

    return {
        "ashtakoota_north": {
            "total_score": total_score,
            "max_score": 36,
            "percentage": round((total_score / 36.0) * 100, 1),
            "verdict": verdict,
            "kootas": kootas_north
        },
        "dasa_porutham_south": {
            "poruthams": south_kootas,
            "favorable_count": sum(1 for p in south_kootas if p["status"])
        }
    }
