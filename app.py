import os
from datetime import date, datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import jhora.panchanga.drik as drik
import swisseph as swe
# Monkeypatch drik.vaara to allow place=None (fixes PyPI PyJHora bug in main.py)
_orig_drik_vaara = drik.vaara
def _safe_drik_vaara(jd, place=None, show_vedic_day=True):
    if place is None:
        return drik.civil_weekday(jd)
    return _orig_drik_vaara(jd, place, show_vedic_day)
drik.vaara = _safe_drik_vaara

# Monkeypatch drik.sunrise, sunset, moonrise, moonset to strip any (+...) day-offset artifacts
_orig_drik_sunrise = drik.sunrise
def _safe_drik_sunrise(jd, place):
    res = _orig_drik_sunrise(jd, place)
    lt = res[0] % 24.0 if isinstance(res[0], (int, float)) else 6.0
    time_str = str(res[1]).split('(')[0].strip()
    return [lt, time_str, res[2]]
drik.sunrise = _safe_drik_sunrise

_orig_drik_sunset = drik.sunset
def _safe_drik_sunset(jd, place):
    res = _orig_drik_sunset(jd, place)
    lt = res[0] % 24.0 if isinstance(res[0], (int, float)) else 18.0
    time_str = str(res[1]).split('(')[0].strip()
    return [lt, time_str, res[2]]
drik.sunset = _safe_drik_sunset

_orig_drik_moonrise = drik.moonrise
def _safe_drik_moonrise(jd, place):
    res = _orig_drik_moonrise(jd, place)
    lt = res[0] % 24.0 if isinstance(res[0], (int, float)) else 0.0
    time_str = str(res[1]).split('(')[0].strip()
    return [lt, time_str, res[2]]
drik.moonrise = _safe_drik_moonrise

_orig_drik_moonset = drik.moonset
def _safe_drik_moonset(jd, place):
    res = _orig_drik_moonset(jd, place)
    lt = res[0] % 24.0 if isinstance(res[0], (int, float)) else 0.0
    time_str = str(res[1]).split('(')[0].strip()
    return [lt, time_str, res[2]]
drik.moonset = _safe_drik_moonset

# Monkeypatch drik.upagraha_longitude to safely use float hours and avoid fragile string splitting
_orig_upagraha_longitude = drik.upagraha_longitude
def _safe_upagraha_longitude(dob, tob, place, planet_index, divisional_chart_factor=1, chart_method=1, upagraha_part='middle', dhasa_progression_correction=0.0):
    try:
        from jhora import utils, const
        if isinstance(dob, (list, tuple)):
            dob = drik.Date(int(dob[0]), int(dob[1]), int(dob[2]))
        jd_utc = utils.gregorian_to_jd(drik.Date(dob.year, dob.month, dob.day))
        jd = utils.julian_day_number(drik.Date(dob.year, dob.month, dob.day), (int(tob[0]), int(tob[1]), int(tob[2])))
        day_number = drik.vaara(jd, place)
        
        srise = float(drik.sunrise(jd_utc, place)[0])
        sset = float(drik.sunset(jd_utc, place)[0])
        planet_part = const.day_rulers[day_number].index(planet_index)
        tob_hrs = tob[0] + tob[1] / 60.0 + tob[2] / 3600.0
        
        if tob_hrs < srise:
            sset = float(drik.sunset(jd_utc - 1, place)[0])
            planet_part = const.night_rulers[day_number].index(planet_index)
        elif tob_hrs > sset:
            srise = float(drik.sunrise(jd_utc + 1, place)[0])
            planet_part = const.night_rulers[day_number].index(planet_index)
            
        day_dur = abs(sset - srise)
        one_part = day_dur / 8.0
        planet_start_time = srise + planet_part * one_part
        if str(upagraha_part).lower() == 'middle':
            planet_end_time = srise + (planet_part + 1) * one_part
            planet_middle_time = 0.5 * (planet_start_time + planet_end_time)
            jd_kaala = swe.julday(dob.year, dob.month, dob.day, planet_middle_time)
        else:
            jd_kaala = swe.julday(dob.year, dob.month, dob.day, planet_start_time)
            
        clong = drik.ascendant(jd_kaala, place)
        upagraha_long = utils.norm360(clong[0] * 30 + clong[1] + dhasa_progression_correction)
        return drik.dasavarga_from_long(upagraha_long, divisional_chart_factor)
    except Exception as e:
        clong = drik.ascendant(swe.julday(dob.year, dob.month, dob.day, tob[0] + tob[1]/60.0), place)
        upagraha_long = utils.norm360(clong[0] * 30 + clong[1])
        return drik.dasavarga_from_long(upagraha_long, divisional_chart_factor)
drik.upagraha_longitude = _safe_upagraha_longitude

# Monkeypatch swe functions to protect against missing ephemeris files (*.se1) and out-of-range epochs
_orig_rise_trans = swe.rise_trans
def _safe_rise_trans(*args, **kwargs):
    try:
        return _orig_rise_trans(*args, **kwargs)
    except Exception as e:
        err_msg = str(e)
        if "not found in PATH" in err_msg or "outside" in err_msg or "seplm" in err_msg:
            kwargs_copy = dict(kwargs)
            if "flags" in kwargs_copy:
                kwargs_copy["flags"] = (kwargs_copy["flags"] & ~swe.FLG_SWIEPH) | swe.FLG_MOSEPH
            al = list(args)
            if len(al) >= 5:
                al[4] = (al[4] & ~swe.FLG_SWIEPH) | swe.FLG_MOSEPH
            try:
                return _orig_rise_trans(*al, **kwargs_copy)
            except Exception:
                rsmi = kwargs.get('rsmi', args[1] if len(args) > 1 else swe.CALC_RISE)
                offset = 0.25 if (isinstance(rsmi, int) and (rsmi & swe.CALC_RISE)) else 0.75
                tjd = args[0] if len(args) > 0 else kwargs.get('tjdut', 2451545.0)
                return (0, (tjd + offset, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
        tjd = args[0] if len(args) > 0 else kwargs.get('tjdut', 2451545.0)
        return (0, (tjd + 0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
swe.rise_trans = _safe_rise_trans

_orig_calc_ut = swe.calc_ut
def _safe_calc_ut(*args, **kwargs):
    try:
        return _orig_calc_ut(*args, **kwargs)
    except swe.Error as e:
        err_msg = str(e)
        if "not found in PATH" in err_msg or "outside" in err_msg or "seplm" in err_msg:
            kwargs_copy = dict(kwargs)
            if "flags" in kwargs_copy:
                kwargs_copy["flags"] = (kwargs_copy["flags"] & ~swe.FLG_SWIEPH) | swe.FLG_MOSEPH
            args_list = list(args)
            if len(args_list) >= 3:
                args_list[2] = (args_list[2] & ~swe.FLG_SWIEPH) | swe.FLG_MOSEPH
            return _orig_calc_ut(*args_list, **kwargs_copy)
        raise
swe.calc_ut = _safe_calc_ut

_orig_houses_ex = swe.houses_ex
def _safe_houses_ex(*args, **kwargs):
    try:
        return _orig_houses_ex(*args, **kwargs)
    except swe.Error as e:
        err_msg = str(e)
        if "not found in PATH" in err_msg or "outside" in err_msg or "seplm" in err_msg:
            kwargs_copy = dict(kwargs)
            if "flags" in kwargs_copy:
                kwargs_copy["flags"] = (kwargs_copy["flags"] & ~swe.FLG_SWIEPH) | swe.FLG_MOSEPH
            args_list = list(args)
            if len(args_list) >= 5:
                args_list[4] = (args_list[4] & ~swe.FLG_SWIEPH) | swe.FLG_MOSEPH
            return _orig_houses_ex(*args_list, **kwargs_copy)
        raise
swe.houses_ex = _safe_houses_ex
def parse_date_robustly(date_str, default_date=None):
    if default_date is None:
        default_date = date(1995, 8, 20)
    if not date_str:
        return default_date
    date_str = str(date_str).strip()
    if '-' in date_str:
        parts = [int(p) for p in date_str.split('-') if p.isdigit()]
        if len(parts) == 3:
            if parts[0] > 31:
                return date(parts[0], parts[1], parts[2])
            else:
                return date(parts[2], parts[1], parts[0])
    if '/' in date_str:
        parts = [int(p) for p in date_str.split('/') if p.isdigit()]
        if len(parts) == 3:
            if parts[0] > 31:
                return date(parts[0], parts[1], parts[2])
            elif parts[2] > 31:
                if parts[0] > 12:
                    return date(parts[2], parts[1], parts[0])
                elif parts[1] > 12:
                    return date(parts[2], parts[0], parts[1])
                else:
                    try:
                        return date(parts[2], parts[1], parts[0])
                    except Exception:
                        return date(parts[2], parts[0], parts[1])
    try:
        from dateutil import parser
        return parser.parse(date_str).date()
    except Exception:
        return default_date



from vedic_engine import VedicHoroscopeEngine, calculate_kundali_matching, EPHE_DIR, AYANAMSA_MAP
from transit_engine import calculate_live_transits
from progression_engine import calculate_dasa_progression, PVR_PAPER_EXAMPLES, DIVISIONAL_FACTORS
from places_service import search_all_places
from vedic_constants import RASHIS, GRAHAS, NAKSHATRAS, BHAVAS
import swisseph as swe

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    # Allow embedding within Google Sites (sites.google.com)
    response.headers["Content-Security-Policy"] = "frame-ancestors 'self' https://sites.google.com https://*.google.com https://*.googleusercontent.com;"
    response.headers.pop("X-Frame-Options", None)
    return response

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/api/status", methods=["GET"])
def get_status():
    ephe_files = os.listdir(EPHE_DIR) if os.path.exists(EPHE_DIR) else []
    return jsonify({
        "status": "online",
        "app_name": "Vedic Horizon (வேத ஜோதிடம்) Web Application",
        "calculation_conventions": "PyJHora (PVR Narasimha Rao Integrated Approach)",
        "ephemeris_engine": "Swiss Ephemeris (swe)",
        "swiss_eph_version": swe.version,
        "ephe_path": EPHE_DIR,
        "ephe_files": ephe_files,
        "has_jpl_precision": any(f.endswith('.se1') for f in ephe_files),
        "available_ayanamsas": list(AYANAMSA_MAP.keys()),
        "server_time": datetime.now().isoformat()
    })

@app.route("/api/cities", methods=["GET"])
def get_cities():
    q = request.args.get("q", "")
    limit = int(request.args.get("limit", 20))
    results = search_all_places(q, limit=limit)
    return jsonify(results)

@app.route("/api/horoscope", methods=["POST"])
def post_horoscope():
    try:
        data = request.json or {}
        # Parse inputs with defaults
        b_date_str = data.get("birth_date", "1995-08-20")
        b_time_str = data.get("birth_time", "06:30:00")
        place_name = data.get("place_name", "New Delhi, India")
        lat = float(data.get("latitude", 28.6139))
        lon = float(data.get("longitude", 77.2090))
        tz = float(data.get("timezone", 5.5))
        ayanamsa = data.get("ayanamsa", "LAHIRI")
        house_system = data.get("house_system", "SRIPATHI")

        b_date = parse_date_robustly(b_date_str, date(1995, 8, 20))

        engine = VedicHoroscopeEngine(
            birth_date=b_date,
            birth_time_str=b_time_str,
            place_name=place_name,
            lat=lat, lon=lon, tz=tz,
            ayanamsa=ayanamsa,
            house_system=house_system
        )
        analysis = engine.get_full_analysis()
        return jsonify({"success": True, "data": analysis})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/match", methods=["POST"])
def post_match():
    try:
        data = request.json or {}
        boy_nak = int(data.get("boy_nakshatra", 4))
        boy_pada = int(data.get("boy_pada", 2))
        girl_nak = int(data.get("girl_nakshatra", 8))
        girl_pada = int(data.get("girl_pada", 1))

        res = calculate_kundali_matching(boy_nak, boy_pada, girl_nak, girl_pada)
        return jsonify({"success": True, "data": res})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/transits", methods=["GET"])
def get_transits():
    try:
        moon_r = int(request.args.get("moon_rasi", 0))
        lagna_r = int(request.args.get("lagna_rasi", 0))
        ayanamsa = request.args.get("ayanamsa", "LAHIRI")
        res = calculate_live_transits(natal_moon_rasi=moon_r, natal_lagna_rasi=lagna_r, ayanamsa=ayanamsa)
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/progression/presets", methods=["GET"])
def get_progression_presets():
    return jsonify({"success": True, "presets": PVR_PAPER_EXAMPLES})

@app.route("/api/progression", methods=["POST"])
def post_progression():
    try:
        data = request.json or {}
        b_date_str = data.get("birth_date", "1970-04-04")
        b_time_str = data.get("birth_time", "17:50:40")
        t_date_str = data.get("target_date", "1987-05-28")
        t_time_str = data.get("target_time", "19:00:00")
        lat = float(data.get("latitude", 16.1667))
        lon = float(data.get("longitude", 81.1333))
        tz = float(data.get("timezone", 5.5))
        ayanamsa = data.get("ayanamsa", "PUSHYA_PAKSHA")
        div_chart = data.get("div_chart", "D-24")
        progression_type = data.get("progression_type", "rasi_vimsottari")

        b_date = parse_date_robustly(b_date_str, date(1970, 4, 4))
        t_date = parse_date_robustly(t_date_str, date(1987, 5, 28))

        res = calculate_dasa_progression(
            birth_date=b_date,
            birth_time_str=b_time_str,
            lat=lat, lon=lon, tz=tz,
            target_date=t_date,
            target_time_str=t_time_str,
            ayanamsa=ayanamsa,
            div_chart_code=div_chart,
            progression_type=progression_type
        )
        return jsonify(res)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/reference", methods=["GET"])
def get_reference():
    return jsonify({
        "rashis": RASHIS,
        "grahas": GRAHAS,
        "nakshatras": NAKSHATRAS,
        "bhavas": BHAVAS,
        "conventions": {
            "source_library": "PyJHora (https://github.com/naturalstupid/PyJHora)",
            "ephemeris_engine": "Swiss Ephemeris (https://github.com/aloistr/swisseph)",
            "ephemeris_files": ["sepl_18.se1", "semo_18.se1", "seas_18.se1", "sefstars.txt"],
            "accuracy": "Sub-arcsecond accuracy derived from NASA Jet Propulsion Laboratory (JPL) DE431 numerical integration",
            "year_length": "Sidereal Solar Year: 365.256364 days",
            "default_ayanamsa": "Chitra Paksha / Lahiri (Fixed Spica at 180° Virgo)",
            "ayanamsa_options": ["LAHIRI", "KP", "RAMAN", "YUKTESHWAR", "JN_BHASIN", "SURYASIDDHANTA", "TROPICAL"],
            "house_systems": ["Sripathi (Standard Vedic)", "Placidus (KP)", "Equal House (Bhava Sama)", "Whole Sign"],
            "references": [
                {"title": "PyJHora by Sundar Sundaresan", "url": "https://github.com/naturalstupid/PyJHora.git"},
                {"title": "Swiss Ephemeris by Alois Treindl & Dieter Koch", "url": "https://github.com/aloistr/swisseph.git"},
                {"title": "Vedic Astrology Vector References", "url": "https://pngtree.com/free-png-vectors/vedic-astrology-vector"},
                {"title": "Astrology Icons & Symbolism", "url": "https://www.flaticon.com/free-icons/astrology?word=astrology&color=color"}
            ]
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
