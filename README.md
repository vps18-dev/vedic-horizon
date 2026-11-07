# Vedic Horizon (ज्योतिष) — Vedic Astrology Web Application

A full-featured, aesthetic Vedic astrology web application powered by **PyJHora** conventions and **Swiss Ephemeris** high-precision JPL numerical integration.

---

## 🌟 Key Features

### 1. Interactive Dual-Style Kundali Charts
- **North Indian Style (Parashari Diamond Layout)**: House-centric interactive SVG with dynamic sign placement and click-to-inspect house drawer.
- **South Indian Style (4x4 Fixed-Sign Perimeter Grid)**: Sign-centric interactive SVG highlighting Ascendant and house numbers.
- **14 Divisional Charts (Vargas)**:
  - **D-1 (Rasi)**: Physical destiny, general life & Lagna
  - **D-9 (Navamsa)**: Dharma, marriage, inner self & spiritual fruitfulness
  - **D-10 (Dasamsa)**: Career, profession, public status & rank
  - **D-2 (Hora)**: Wealth, prosperity & speech
  - **D-3 (Drekkana)**: Siblings, courage & 22nd drekkana
  - **D-4 (Chaturthamsa)**: Fixed assets, lands & fortune
  - **D-7 (Saptamsa)**: Children, lineage & progeny
  - **D-12 (Dwadasamsa)**: Parents & ancestral heritage
  - **D-16 (Shodasamsa)**: Vehicles & conveyances
  - **D-20 (Vimsamsa)**: Spiritual practice & upasana
  - **D-24 (Chaturvimsamsa)**: Higher learning & vidya
  - **D-27 (Saptavimsamsa)**: Subtle strengths & bhaga
  - **D-30 (Trimsamsa)**: Evils, adversities & misfortunes
  - **D-60 (Shastiamsa)**: Past-life root karma
- **Interactive House Inspection Modal**: Click any house in either chart style to view primary Karaka, Significations, Occupants, and Aspects.

### 2. Comprehensive Planetary Details
- 9 Vedic Grahas (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu) + Modern Planets (Uranus, Neptune, Pluto).
- Exact longitudes in Degrees, Minutes, Seconds (DMS).
- Direct vs Retrograde (℞) motion and daily planetary speeds.
- Combustion detection from Sun proximity.
- Dignities: Exalted, Moolatrikona, Own Sign, Great Friend, Friend, Neutral, Enemy, Great Enemy, Debilitated.
- Nakshatras & Padas (1-4) with ruling deities and shakti.
- 7 Chara Karakas (Atmakaraka AK, Amatyakaraka AmK, BK, MK, PiK, PK, GK, DK).
- Special Lagnas & Upagrahas: Bhava Lagna (BL), Hora Lagna (HL), Ghati Lagna (GL), Sree Lagna (SL), Arudha Lagna (AL), Upapada Lagna (UL), Gulika, Mandi, Pranapada, Indu Lagna, Bhrigu Bindu.

### 3. Complete Panchanga & Muhurta Dashboard
- **Five Limbs of Time**: Tithi (with paksha & % balance), Vaara (sunrise-to-sunrise Vedic day with ruling lord), Nakshatra, Yoga, and Karana.
- **Auspicious & Inauspicious Windows**:
  - Abhijit Muhurta (Supreme midday auspicious window)
  - Rahu Kalam (Avoided for auspicious beginnings)
  - Yamagandam & Gulika Kalam
  - Sunrise, Sunset, Moonrise, Moonset
- **Vedic Calendar**: Lunar Samvatsara (60-year cycle), Solar Month, Kali Yuga, Vikrama Samvat, Saka Samvat.

### 4. Vimshottari Dasha Explorer
- Balance of Dasha at birth.
- Active Running Mahadasha and Antardasha with elapsed progress indicators.
- 120-year hierarchical timeline of all 9 Mahadashas and their 81 Antardashas.

### 5. Ashtakavarga & Live Planetary Transits (Gochara)
- **Sarvashtakavarga (SAV)**: 12-house matrix scoring (Parashara 337 total baseline) with color-coded heatmap (>28 benefic, 25-28 average, <25 sensitive).
- **Bhinnashtakavarga (BAV)**: Detailed breakdown for Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn.
- **Live Transits (Gochara)**: Real-time planetary positions evaluated against natal Moon and Lagna.
- **Sade Sati Tracker**: Identifies Rising, Peak, or Setting phase of Saturn's 7.5-year transit.

### 6. Sixfold Planetary Strength (Shadbala)
- Sthana Bala (Positional)
- Dig Bala (Directional)
- Kaala Bala (Temporal)
- Cheshta Bala (Motional)
- Naisargika Bala (Natural)
- Drik Bala (Aspectual)
- Total Rupas vs Parashara minimum requirement, strength ratios, and power rankings.

### 7. Yogas & Doshas Analysis
- Classical Auspicious Yogas: Pancha Mahapurusha (Ruchaka, Bhadra, Hamsa, Malavya, Sasa), Gajakesari, Budhaditya, Amala, Adhi Yoga, Neechabhanga Raja Yoga, Viparita Raja Yoga.
- Dosha Diagnostics: Manglik (Chevvai) Dosha with South/North cancellation exceptions, Kaalsarp Dosha, Pitru Dosha, Guru Chandal, Shrapit, and Ganda Moola Dosha.

### 8. Kundali Milan (Horoscope Matching)
- **North Indian Ashtakoota (36 Gunas)**: Varna (1), Vashya (2), Tara (3), Yoni (4), Graha Maitri (5), Gana (6), Bhakoot (7), Nadi (8).
- **South Indian Dasa Porutham**: Dina, Gana, Mahendra, Stree Deergha, Yoni, Rasi, Rasi Adhipathi, Vasiya, Rajju, Vedha.
- Matrimonial compatibility score, percentage, and verdict.

### 9. Ephemeris & Technical Conventions Reference
- High-precision compressed JPL binary ephemeris files (`sepl_18.se1`, `semo_18.se1`, `seas_18.se1`, `sefstars.txt`) active.
- Multiple Ayanamsa options: Lahiri (Chitra Paksha), KP, Raman, Yukteshwar, JN Bhasin, Surya Siddhanta, Sayana (Tropical).
- House systems: Sripathi, Placidus (KP), Equal House, Whole Sign.
- Handcrafted vector iconography library for Grahas, Rashis, Ganesha, Om, Kalasha, Diya, and Yantras.

---

## 🚀 Running the Web Application

The application runs locally on **`http://127.0.0.1:5000`**.

To launch manually:
```cmd
run.bat
```
or
```cmd
"C:\Users\Panther\Python311\python.exe" app.py
```

---

## 📚 References & Source Citations
- **PyJHora**: [naturalstupid/PyJHora](https://github.com/naturalstupid/PyJHora.git)
- **Swiss Ephemeris**: [aloistr/swisseph](https://github.com/aloistr/swisseph.git)
- **Vedic Astrology Vectors**: [Pngtree Vedic Astrology Vectors](https://pngtree.com/free-png-vectors/vedic-astrology-vector)
- **Astrology Icons**: [Flaticon Astrology Icons](https://www.flaticon.com/free-icons/astrology?word=astrology&color=color)
