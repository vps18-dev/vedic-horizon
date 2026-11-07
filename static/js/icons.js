/**
 * Vedic Astrology Iconography & Vector Library
 * References: Flaticon Astrology, Pngtree Vedic Astrology Vectors
 */

const VEDIC_ICONS = {
    ganesha: `
    <svg viewBox="0 0 100 100" class="v-icon v-icon-ganesha" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="46" stroke="currentColor" stroke-width="2" stroke-dasharray="3 3" opacity="0.6"/>
        <path d="M50 14 C40 14 36 22 36 28 C36 34 42 38 42 45 C42 52 38 56 38 64 C38 72 45 78 50 78 C55 78 62 72 62 64 C62 56 58 52 58 45 C58 38 64 34 64 28 C64 22 60 14 50 14 Z" fill="url(#goldGrad)" opacity="0.15"/>
        <path d="M50 18 C43 18 38 23 38 30 C38 37 43 40 46 45 C48 48 49 53 49 60 C49 67 46 72 42 75 C47 77 53 77 57 73 C60 70 61 65 61 58 C61 51 59 47 56 43 C53 39 52 35 52 30 C52 23 48 18 50 18 Z" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
        <!-- Crown / Mukut -->
        <path d="M44 18 L50 8 L56 18 Z" fill="currentColor"/>
        <circle cx="50" cy="7" r="2" fill="currentColor"/>
        <!-- Ears -->
        <path d="M38 26 C30 24 25 30 26 38 C27 45 34 44 38 42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <path d="M62 26 C70 24 75 30 74 38 C73 45 66 44 62 42" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <!-- Tilak -->
        <path d="M47 24 C50 25 50 27 50 29 C50 27 50 25 53 24" stroke="#ef4444" stroke-width="2" stroke-linecap="round"/>
        <circle cx="50" cy="32" r="1.5" fill="#ef4444"/>
        <!-- Tusk & Modak -->
        <path d="M43 48 L37 50" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
        <circle cx="64" cy="62" r="4" fill="url(#goldGrad)" stroke="currentColor" stroke-width="1.5"/>
        <defs>
            <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#ffd700"/>
                <stop offset="100%" stop-color="#d4af37"/>
            </linearGradient>
        </defs>
    </svg>`,

    om: `
    <svg viewBox="0 0 100 100" class="v-icon v-icon-om" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M38 28 C30 28 24 34 24 42 C24 50 30 56 38 56 C32 62 26 70 26 80 C26 90 36 96 48 94 C60 92 68 82 66 70 C65 62 58 56 50 56" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>
        <path d="M40 56 C48 56 56 50 56 42 C56 34 48 28 38 28" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>
        <path d="M50 56 C60 56 72 62 76 72 C80 82 74 92 66 94" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>
        <!-- Chandra-bindu -->
        <path d="M60 26 C66 32 76 32 82 26" stroke="currentColor" stroke-width="3.5" stroke-linecap="round"/>
        <circle cx="71" cy="18" r="3.5" fill="currentColor"/>
    </svg>`,

    kalasha: `
    <svg viewBox="0 0 100 100" class="v-icon v-icon-kalasha" fill="none" xmlns="http://www.w3.org/2000/svg">
        <!-- Pot -->
        <path d="M34 50 C26 56 24 72 32 82 C38 88 62 88 68 82 C76 72 74 56 66 50 Z" fill="currentColor" fill-opacity="0.2" stroke="currentColor" stroke-width="3"/>
        <path d="M34 50 C38 46 62 46 66 50" stroke="currentColor" stroke-width="3"/>
        <path d="M30 84 C38 88 62 88 70 84" stroke="currentColor" stroke-width="3"/>
        <!-- Coconut -->
        <path d="M40 46 C40 34 50 26 50 26 C50 26 60 34 60 46 Z" fill="currentColor" fill-opacity="0.3" stroke="currentColor" stroke-width="2.5"/>
        <!-- Mango leaves -->
        <path d="M30 46 C24 38 32 30 40 40" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <path d="M70 46 C76 38 68 30 60 40" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <path d="M42 34 C36 24 46 20 50 30" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <path d="M58 34 C64 24 54 20 50 30" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        <!-- Swastika on Pot -->
        <path d="M50 62 L50 74 M44 68 L56 68 M50 62 L56 62 M56 68 L56 74 M50 74 L44 74 M44 68 L44 62" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    </svg>`,

    diya: `
    <svg viewBox="0 0 100 100" class="v-icon v-icon-diya" fill="none" xmlns="http://www.w3.org/2000/svg">
        <!-- Base / Lamp Bowl -->
        <path d="M20 62 C26 78 74 78 80 62 C84 54 78 50 70 52 C58 54 42 54 30 52 C22 50 16 54 20 62 Z" fill="currentColor" fill-opacity="0.25" stroke="currentColor" stroke-width="3"/>
        <path d="M36 76 C42 84 58 84 64 76" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
        <!-- Flame -->
        <path d="M50 16 C42 28 40 38 46 48 C48 50 52 50 54 48 C60 38 58 28 50 16 Z" fill="#f59e0b" stroke="#ef4444" stroke-width="2"/>
        <path d="M50 28 C46 34 46 40 49 46 C50 47 51 47 52 46 C55 40 54 34 50 28 Z" fill="#ffd700"/>
    </svg>`,

    kundali_chart: `
    <svg viewBox="0 0 100 100" class="v-icon v-icon-kundali" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="6" y="6" width="88" height="88" stroke="currentColor" stroke-width="2.5" fill="none"/>
        <line x1="6" y1="6" x2="94" y2="94" stroke="currentColor" stroke-width="2"/>
        <line x1="94" y1="6" x2="6" y2="94" stroke="currentColor" stroke-width="2"/>
        <polygon points="50,6 94,50 50,94 6,50" stroke="currentColor" stroke-width="2.5" fill="none"/>
        <circle cx="50" cy="50" r="3" fill="currentColor"/>
    </svg>`,

    swisseph: `
    <svg viewBox="0 0 100 100" class="v-icon v-icon-swe" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="44" stroke="currentColor" stroke-width="2.5"/>
        <ellipse cx="50" cy="50" rx="44" ry="16" stroke="currentColor" stroke-width="2" stroke-dasharray="4 2"/>
        <ellipse cx="50" cy="50" rx="16" ry="44" stroke="currentColor" stroke-width="2" stroke-dasharray="4 2"/>
        <circle cx="50" cy="50" r="8" fill="url(#goldGrad)" stroke="currentColor" stroke-width="2"/>
        <circle cx="78" cy="40" r="4" fill="#38bdf8"/>
        <circle cx="26" cy="62" r="3" fill="#ef4444"/>
    </svg>`
};

const PLANET_SVG = {
    Sun: `<svg viewBox="0 0 36 36" class="planet-svg planet-sun"><circle cx="18" cy="18" r="7" fill="#f59e0b" stroke="#d97706" stroke-width="1.5"/><circle cx="18" cy="18" r="1.5" fill="#ffffff"/><g stroke="#f59e0b" stroke-width="2" stroke-linecap="round"><line x1="18" y1="4" x2="18" y2="8"/><line x1="18" y1="28" x2="18" y2="32"/><line x1="4" y1="18" x2="8" y2="18"/><line x1="28" y1="18" x2="32" y2="18"/><line x1="8" y1="8" x2="11" y2="11"/><line x1="25" y1="25" x2="28" y2="28"/><line x1="8" y1="28" x2="11" y2="25"/><line x1="25" y1="11" x2="28" y2="8"/></g></svg>`,
    Moon: `<svg viewBox="0 0 36 36" class="planet-svg planet-moon"><path d="M22 6 C13 6 8 13 8 20 C8 27 13 32 20 32 C23 32 26 31 28 29 C21 28 17 22 17 16 C17 11 20 8 22 6 Z" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1.5"/><circle cx="14" cy="18" r="1.5" fill="#cbd5e1"/></svg>`,
    Mars: `<svg viewBox="0 0 36 36" class="planet-svg planet-mars"><circle cx="16" cy="20" r="9" fill="#ef4444" stroke="#b91c1c" stroke-width="2"/><line x1="22" y1="14" x2="30" y2="6" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round"/><polyline points="23,6 30,6 30,13" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round"/></svg>`,
    Mercury: `<svg viewBox="0 0 36 36" class="planet-svg planet-mercury"><circle cx="18" cy="17" r="7" fill="#10b981" stroke="#059669" stroke-width="2"/><path d="M12 9 C14 5 22 5 24 9" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round"/><line x1="18" y1="24" x2="18" y2="33" stroke="#10b981" stroke-width="2.5"/><line x1="13" y1="28" x2="23" y2="28" stroke="#10b981" stroke-width="2.5"/></svg>`,
    Jupiter: `<svg viewBox="0 0 36 36" class="planet-svg planet-jupiter"><path d="M14 6 L14 30 M24 16 L6 16 M24 6 C18 6 12 12 12 18 C12 24 18 26 24 26" fill="none" stroke="#eab308" stroke-width="2.5" stroke-linecap="round"/></svg>`,
    Venus: `<svg viewBox="0 0 36 36" class="planet-svg planet-venus"><circle cx="18" cy="13" r="8" fill="#f472b6" stroke="#db2777" stroke-width="2"/><line x1="18" y1="21" x2="18" y2="33" stroke="#db2777" stroke-width="2.5"/><line x1="12" y1="27" x2="24" y2="27" stroke="#db2777" stroke-width="2.5"/></svg>`,
    Saturn: `<svg viewBox="0 0 36 36" class="planet-svg planet-saturn"><ellipse cx="18" cy="18" rx="14" ry="5" fill="none" stroke="#60a5fa" stroke-width="2" transform="rotate(-25 18 18)"/><circle cx="18" cy="18" r="7" fill="#3b82f6" stroke="#1d4ed8" stroke-width="1.5"/><ellipse cx="18" cy="18" rx="14" ry="5" fill="none" stroke="#93c5fd" stroke-width="1.5" stroke-dasharray="14 18" transform="rotate(-25 18 18)"/></svg>`,
    Rahu: `<svg viewBox="0 0 36 36" class="planet-svg planet-rahu"><path d="M10 26 C10 16 14 10 18 10 C22 10 26 16 26 26 C26 29 23 31 20 30 C18 29 16 27 15 25" fill="none" stroke="#818cf8" stroke-width="2.5" stroke-linecap="round"/><circle cx="12" cy="27" r="3" fill="#6366f1"/><circle cx="24" cy="27" r="3" fill="#6366f1"/></svg>`,
    Ketu: `<svg viewBox="0 0 36 36" class="planet-svg planet-ketu"><path d="M10 10 C10 20 14 26 18 26 C22 26 26 20 26 10 C26 7 23 5 20 6 C18 7 16 9 15 11" fill="none" stroke="#a78bfa" stroke-width="2.5" stroke-linecap="round"/><circle cx="12" cy="9" r="3" fill="#8b5cf6"/><circle cx="24" cy="9" r="3" fill="#8b5cf6"/></svg>`,
    Uranus: `<svg viewBox="0 0 36 36" class="planet-svg planet-uranus"><circle cx="18" cy="22" r="6" fill="#38bdf8" stroke="#0284c7" stroke-width="1.5"/><line x1="18" y1="16" x2="18" y2="6" stroke="#38bdf8" stroke-width="2"/><circle cx="18" cy="6" r="2" fill="#38bdf8"/><line x1="11" y1="10" x2="11" y2="20" stroke="#38bdf8" stroke-width="1.5"/><line x1="25" y1="10" x2="25" y2="20" stroke="#38bdf8" stroke-width="1.5"/><line x1="11" y1="15" x2="25" y2="15" stroke="#38bdf8" stroke-width="1.5"/></svg>`,
    Neptune: `<svg viewBox="0 0 36 36" class="planet-svg planet-neptune"><path d="M11 8 L11 18 C11 22 25 22 25 18 L25 8" fill="none" stroke="#06b6d4" stroke-width="2" stroke-linecap="round"/><line x1="18" y1="6" x2="18" y2="30" stroke="#06b6d4" stroke-width="2.5"/><line x1="13" y1="24" x2="23" y2="24" stroke="#06b6d4" stroke-width="2"/><polygon points="18,5 16,8 20,8" fill="#06b6d4"/></svg>`,
    Pluto: `<svg viewBox="0 0 36 36" class="planet-svg planet-pluto"><circle cx="18" cy="10" r="4" fill="#a855f7"/><path d="M11 14 C11 22 25 22 25 14" fill="none" stroke="#a855f7" stroke-width="2"/><line x1="18" y1="21" x2="18" y2="32" stroke="#a855f7" stroke-width="2.5"/><line x1="13" y1="27" x2="23" y2="27" stroke="#a855f7" stroke-width="2"/></svg>`
};

const ZODIAC_SVG = {
    0: `<svg viewBox="0 0 36 36" class="zodiac-svg"><path d="M7 14 C7 9 12 7 18 16 C24 7 29 9 29 14 C29 19 24 24 18 31 L18 16" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round"/></svg>`,
    1: `<svg viewBox="0 0 36 36" class="zodiac-svg"><circle cx="18" cy="22" r="8" fill="none" stroke="#10b981" stroke-width="2.5"/><path d="M8 8 C12 14 24 14 28 8" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round"/></svg>`,
    2: `<svg viewBox="0 0 36 36" class="zodiac-svg"><line x1="13" y1="8" x2="13" y2="28" stroke="#f59e0b" stroke-width="2.5"/><line x1="23" y1="8" x2="23" y2="28" stroke="#f59e0b" stroke-width="2.5"/><path d="M8 9 C18 13 28 9 28 9" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round"/><path d="M8 27 C18 23 28 27 28 27" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round"/></svg>`,
    3: `<svg viewBox="0 0 36 36" class="zodiac-svg"><circle cx="13" cy="14" r="5" fill="none" stroke="#06b6d4" stroke-width="2.5"/><path d="M13 9 C22 9 26 18 24 24" fill="none" stroke="#06b6d4" stroke-width="2.5" stroke-linecap="round"/><circle cx="23" cy="22" r="5" fill="none" stroke="#06b6d4" stroke-width="2.5"/><path d="M23 27 C14 27 10 18 12 12" fill="none" stroke="#06b6d4" stroke-width="2.5" stroke-linecap="round"/></svg>`,
    4: `<svg viewBox="0 0 36 36" class="zodiac-svg"><circle cx="12" cy="19" r="4.5" fill="none" stroke="#f97316" stroke-width="2.5"/><path d="M16 17 C16 9 24 9 24 16 C24 23 18 27 23 29 C26 30 28 27 28 24" fill="none" stroke="#f97316" stroke-width="2.5" stroke-linecap="round"/></svg>`,
    5: `<svg viewBox="0 0 36 36" class="zodiac-svg"><path d="M8 12 C8 24 8 28 8 28 M8 15 C11 11 15 11 15 19 L15 28 M15 15 C18 11 22 11 22 19 L22 28 C22 32 26 32 28 26 L26 21" fill="none" stroke="#84cc16" stroke-width="2.5" stroke-linecap="round"/></svg>`,
    6: `<svg viewBox="0 0 36 36" class="zodiac-svg"><line x1="6" y1="28" x2="30" y2="28" stroke="#ec4899" stroke-width="2.5"/><line x1="6" y1="22" x2="13" y2="22" stroke="#ec4899" stroke-width="2.5"/><line x1="23" y1="22" x2="30" y2="22" stroke="#ec4899" stroke-width="2.5"/><path d="M13 22 C13 14 23 14 23 22" fill="none" stroke="#ec4899" stroke-width="2.5"/></svg>`,
    7: `<svg viewBox="0 0 36 36" class="zodiac-svg"><path d="M8 12 C8 24 8 28 8 28 M8 15 C11 11 15 11 15 19 L15 28 M15 15 C18 11 22 11 22 19 L22 28 C22 30 25 30 28 28 L30 30" fill="none" stroke="#b91c1c" stroke-width="2.5" stroke-linecap="round"/><polyline points="26,30 30,30 30,26" fill="none" stroke="#b91c1c" stroke-width="2.5" stroke-linecap="round"/></svg>`,
    8: `<svg viewBox="0 0 36 36" class="zodiac-svg"><line x1="8" y1="28" x2="28" y2="8" stroke="#8b5cf6" stroke-width="2.5" stroke-linecap="round"/><polyline points="18,8 28,8 28,18" fill="none" stroke="#8b5cf6" stroke-width="2.5" stroke-linecap="round"/><line x1="12" y1="20" x2="20" y2="28" stroke="#8b5cf6" stroke-width="2.5" stroke-linecap="round"/></svg>`,
    9: `<svg viewBox="0 0 36 36" class="zodiac-svg"><path d="M8 10 L8 24 C8 27 12 28 15 25 L21 16 C22 14 24 14 25 16 C26 20 23 28 27 28 C29 28 30 26 30 23" fill="none" stroke="#64748b" stroke-width="2.5" stroke-linecap="round"/></svg>`,
    10: `<svg viewBox="0 0 36 36" class="zodiac-svg"><path d="M6 14 L11 10 L16 14 L21 10 L26 14 L30 10" fill="none" stroke="#0ea5e9" stroke-width="2.5" stroke-linecap="round"/><path d="M6 22 L11 18 L16 22 L21 18 L26 22 L30 18" fill="none" stroke="#0ea5e9" stroke-width="2.5" stroke-linecap="round"/></svg>`,
    11: `<svg viewBox="0 0 36 36" class="zodiac-svg"><path d="M10 8 C15 18 15 22 10 30" fill="none" stroke="#a855f7" stroke-width="2.5" stroke-linecap="round"/><path d="M26 8 C21 18 21 22 26 30" fill="none" stroke="#a855f7" stroke-width="2.5" stroke-linecap="round"/><line x1="7" y1="19" x2="29" y2="19" stroke="#a855f7" stroke-width="2.5"/></svg>`
};
