"""
Comprehensive Global Places Search Service
1. Instant SQLite search over 68,520 world cities & 310,554 aliases from GeoNames.
2. Multi-word matching (City + State + Country).
3. Live OpenStreetMap / Nominatim fallback for small towns, villages, and exact addresses.
4. Automatic astronomical timezone offset calculation using TimezoneFinder & pytz.
"""

import os
import re
import sqlite3
import unicodedata
from datetime import datetime
import requests
from timezonefinder import TimezoneFinder
import pytz

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "geonames_places_5k.db")

# Fallback path if in site-packages
if not os.path.exists(DB_PATH):
    alt_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Python", "geonames_places_5k.db")
    if os.path.exists(alt_path):
        DB_PATH = alt_path

tz_finder = TimezoneFinder()
_SEARCH_CACHE = {}

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def get_tz_offset(lat: float, lon: float) -> float:
    try:
        tz_name = tz_finder.timezone_at(lng=lon, lat=lat)
        if not tz_name:
            # Fallback approximation from longitude
            return round(lon / 15.0 * 2) / 2
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        offset_sec = now.utcoffset().total_seconds()
        return round(offset_sec / 3600.0, 2)
    except Exception:
        return round(lon / 15.0 * 2) / 2

def search_local_db(query: str, limit: int = 25):
    if not os.path.exists(DB_PATH):
        return []

    norm_q = normalize_text(query)
    if not norm_q:
        return []

    tokens = norm_q.split()
    results = []
    seen_ids = set()

    try:
        con = sqlite3.connect(DB_PATH, timeout=5)
        cur = con.cursor()

        # 1. Exact alias match (e.g. "bangalore" -> Bengaluru, "calcutta" -> Kolkata)
        cur.execute("""
            SELECT p.id, p.place_name, p.state, p.country, p.display_label, p.latitude, p.longitude, p.timezone_hours
            FROM aliases a
            JOIN places p ON a.place_id = p.id
            WHERE a.alias_norm = ?
            LIMIT 5;
        """, (norm_q,))
        for row in cur.fetchall():
            if row[0] not in seen_ids:
                seen_ids.add(row[0])
                results.append({
                    "name": row[4],
                    "city": row[1],
                    "state": row[2],
                    "country": row[3],
                    "lat": row[5],
                    "lon": row[6],
                    "tz": row[7],
                    "source": "database_exact"
                })

        # 2. Prefix match on place name (e.g. "chen" -> Chennai)
        if len(results) < limit:
            cur.execute("""
                SELECT id, place_name, state, country, display_label, latitude, longitude, timezone_hours
                FROM places
                WHERE display_label_norm LIKE ?
                ORDER BY length(display_label) ASC
                LIMIT ?;
            """, (f"{norm_q}%", limit - len(results)))
            for row in cur.fetchall():
                if row[0] not in seen_ids:
                    seen_ids.add(row[0])
                    results.append({
                        "name": row[4],
                        "city": row[1],
                        "state": row[2],
                        "country": row[3],
                        "lat": row[5],
                        "lon": row[6],
                        "tz": row[7],
                        "source": "database"
                    })

        # 3. Multi-word search (e.g. "pune maharashtra", "salem tamil nadu", "austin texas")
        if len(results) < limit:
            sql_clauses = ["display_label_norm LIKE ?" for _ in tokens]
            params = [f"%{tok}%" for tok in tokens]
            params.append(limit - len(results))
            sql = f"""
                SELECT id, place_name, state, country, display_label, latitude, longitude, timezone_hours
                FROM places
                WHERE {' AND '.join(sql_clauses)}
                ORDER BY length(display_label) ASC
                LIMIT ?;
            """
            cur.execute(sql, tuple(params))
            for row in cur.fetchall():
                if row[0] not in seen_ids:
                    seen_ids.add(row[0])
                    results.append({
                        "name": row[4],
                        "city": row[1],
                        "state": row[2],
                        "country": row[3],
                        "lat": row[5],
                        "lon": row[6],
                        "tz": row[7],
                        "source": "database"
                    })

        # 4. Substring search if still under limit
        if len(results) < 5 and len(norm_q) >= 3:
            cur.execute("""
                SELECT id, place_name, state, country, display_label, latitude, longitude, timezone_hours
                FROM places
                WHERE display_label_norm LIKE ?
                LIMIT ?;
            """, (f"%{norm_q}%", limit - len(results)))
            for row in cur.fetchall():
                if row[0] not in seen_ids:
                    seen_ids.add(row[0])
                    results.append({
                        "name": row[4],
                        "city": row[1],
                        "state": row[2],
                        "country": row[3],
                        "lat": row[5],
                        "lon": row[6],
                        "tz": row[7],
                        "source": "database"
                    })

        con.close()
    except Exception as e:
        print("SQLite place search error:", e)

    return results

def search_nominatim(query: str, limit: int = 5):
    clean_q = query.strip()
    if not clean_q or len(clean_q) < 2:
        return []

    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": clean_q,
            "format": "json",
            "limit": limit,
            "addressdetails": 1
        }
        headers = {
            "User-Agent": "VedicHorizonAstrologyApp/2.0 (contact: support@vedichorizon.local)"
        }
        resp = requests.get(url, params=params, headers=headers, timeout=4)
        if resp.status_code != 200:
            return []

        items = resp.json()
        results = []
        for it in items:
            lat = float(it["lat"])
            lon = float(it["lon"])
            tz = get_tz_offset(lat, lon)
            addr = it.get("address", {})

            # Construct clean city / state / country label
            city_part = (
                addr.get("city") or addr.get("town") or addr.get("village") or
                addr.get("suburb") or addr.get("county") or it.get("name") or ""
            )
            state_part = addr.get("state") or addr.get("region") or ""
            country_part = addr.get("country") or ""

            parts = [p for p in [city_part, state_part, country_part] if p]
            display_name = ", ".join(parts) if parts else it.get("display_name", clean_q)

            results.append({
                "name": display_name,
                "city": city_part,
                "state": state_part,
                "country": country_part,
                "lat": round(lat, 4),
                "lon": round(lon, 4),
                "tz": tz,
                "source": "global_osm"
            })

        return results
    except Exception as e:
        print("Nominatim search error:", e)
        return []

def search_all_places(query: str, limit: int = 15):
    q_key = query.strip().lower()
    if not q_key:
        # Default top major cities if query is empty
        return search_local_db("India", limit=limit)

    if q_key in _SEARCH_CACHE:
        return _SEARCH_CACHE[q_key]

    # 1. First search local database (68,520 cities, 310k aliases)
    local_results = search_local_db(q_key, limit=limit)

    # 2. If we found 5 or more matches, return immediately (sub-millisecond speed)
    if len(local_results) >= 5:
        _SEARCH_CACHE[q_key] = local_results[:limit]
        return local_results[:limit]

    # 3. If fewer than 5 matches, enhance with live Nominatim global search
    online_results = search_nominatim(q_key, limit=limit - len(local_results))
    
    # Merge, deduplicating by normalized name
    seen_names = set()
    combined = []
    for item in local_results + online_results:
        norm = normalize_text(item["name"])
        if norm not in seen_names:
            seen_names.add(norm)
            combined.append(item)

    _SEARCH_CACHE[q_key] = combined[:limit]
    return combined[:limit]
