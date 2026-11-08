/**
 * Main Application Logic for Vedic Horizon Web App
 */

let chartRenderer = null;
let d9ChartRenderer = null;
let progChartRenderer = null;
let transitChartRenderer = null;
let currentHoroscopeData = null;
let currentProgressionData = null;
let pvrPresetsList = [];
let progCurrentStyle = "south";
let activeDivChartCode = "D-1";
let activeD9ChartCode = "D-9";

document.addEventListener("DOMContentLoaded", () => {
    // Initialize Theme first
    initTheme();
    initViewMode();

    // Inject brand icon
    const brandIconBox = document.getElementById("brandIcon");
    if (brandIconBox && VEDIC_ICONS.ganesha) {
        brandIconBox.innerHTML = VEDIC_ICONS.ganesha;
    }

    // Initialize Horoscope Chart Renderer (Left)
    chartRenderer = new VedicChartRenderer("chartContainer");
    window.chartRenderer = chartRenderer;
    chartRenderer.onHouseClick((hNum, hData) => {
        openHouseModal(hNum, hData);
    });

    // Initialize D-9 Navamsa Chart Renderer (Right)
    d9ChartRenderer = new VedicChartRenderer("chartD9Container");
    window.d9ChartRenderer = d9ChartRenderer;
    d9ChartRenderer.onHouseClick((hNum, hData) => {
        openHouseModal(hNum, hData);
    });

    // Initialize Dual Progression & Transit Chart Renderers
    progChartRenderer = new VedicChartRenderer("chartProgContainer");
    transitChartRenderer = new VedicChartRenderer("chartTransitContainer");
    window.progChartRenderer = progChartRenderer;
    window.transitChartRenderer = transitChartRenderer;

    // Start Clock
    updateClock();
    setInterval(updateClock, 1000);

    // Fetch Ephemeris Status
    fetchEphemerisStatus();

    // Populate Milan Nakshatras dropdowns
    populateMilanSelects();


    // City Autocomplete setup
    setupCityAutocomplete();

    // Fetch PVR Rao Research Paper Presets
    fetchPvrPresets();

    // Default to Sky Right Now / கோச்சார நிலை (Transit) on initial home page load
    loadPreset('now');
});

function updateClock() {
    const clockEl = document.getElementById("headerClock");
    if (clockEl) {
        const now = new Date();
        clockEl.textContent = `UTC: ${now.toUTCString().slice(17, 25)} | Local: ${now.toLocaleTimeString()}`;
    }
}

async function fetchEphemerisStatus() {
    try {
        const res = await fetch("/api/status");
        const data = await res.json();
    } catch (e) {
        console.error("Status fetch error:", e);
    }
}

function setupCityAutocomplete() {
    const inputPlace = document.getElementById("inputPlace");
    const autoList = document.getElementById("autocompleteList");
    if (!inputPlace || !autoList) return;

    let debounceTimer = null;
    let selectedIndex = -1;

    async function doSearch(query) {
        if (!query || query.trim().length === 0) {
            autoList.style.display = "none";
            return;
        }

        autoList.innerHTML = `
            <div style="padding:10px 14px; font-size:0.82rem; color:var(--text-secondary); display:flex; align-items:center; gap:8px;">
                <span class="pulse-dot"></span> Searching 68,000+ cities & global coordinates...
            </div>
        `;
        autoList.style.display = "block";

        try {
            const res = await fetch(`/api/cities?q=${encodeURIComponent(query.trim())}&limit=20`);
            const places = await res.json();
            autoList.innerHTML = "";
            selectedIndex = -1;

            if (!places || places.length === 0) {
                autoList.innerHTML = `
                    <div style="padding:10px 14px; font-size:0.82rem; color:var(--text-secondary);">
                        No matches found. You can enter custom coordinates manually below.
                    </div>
                `;
                return;
            }

            places.forEach((p, idx) => {
                const item = document.createElement("div");
                item.className = "autocomplete-item";
                item.dataset.index = idx;

                const tzSign = p.tz >= 0 ? "+" : "";
                const srcBadge = p.source === "global_osm" 
                    ? `<span style="font-size:0.7rem; background:rgba(6,182,212,0.15); color:#38bdf8; padding:2px 6px; border-radius:4px; margin-left:6px;">Global Map</span>`
                    : `<span style="font-size:0.7rem; background:rgba(212,175,55,0.15); color:var(--gold-bright); padding:2px 6px; border-radius:4px; margin-left:6px;">City DB</span>`;

                item.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:600; color:var(--text-primary); font-size:0.9rem;">
                            📍 ${p.name}
                        </span>
                        ${srcBadge}
                    </div>
                    <div style="font-size:0.78rem; color:var(--text-secondary); margin-top:3px; display:flex; gap:12px;">
                        <span>Lat: <strong>${p.lat.toFixed(4)}°</strong></span>
                        <span>Lon: <strong>${p.lon.toFixed(4)}°</strong></span>
                        <span style="color:var(--gold-light);">TZ: <strong>UTC ${tzSign}${p.tz}</strong></span>
                    </div>
                `;

                item.addEventListener("click", () => {
                    selectPlace(p);
                });

                autoList.appendChild(item);
            });
            autoList.style.display = "block";
        } catch (e) {
            console.error("Place search error:", e);
            autoList.style.display = "none";
        }
    }

    function selectPlace(p) {
        inputPlace.value = p.name;
        const latInput = document.getElementById("inputLat");
        const lonInput = document.getElementById("inputLon");
        const tzInput = document.getElementById("inputTz");

        if (latInput) {
            latInput.value = p.lat;
            highlightField(latInput);
        }
        if (lonInput) {
            lonInput.value = p.lon;
            highlightField(lonInput);
        }
        if (tzInput) {
            tzInput.value = p.tz;
            highlightField(tzInput);
        }

        autoList.style.display = "none";
    }

    function highlightField(field) {
        field.style.borderColor = "#10b981";
        field.style.boxShadow = "0 0 10px rgba(16, 185, 129, 0.4)";
        setTimeout(() => {
            field.style.borderColor = "";
            field.style.boxShadow = "";
        }, 1200);
    }

    inputPlace.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        const query = inputPlace.value;
        debounceTimer = setTimeout(() => doSearch(query), 200);
    });

    inputPlace.addEventListener("focus", () => {
        if (inputPlace.value.trim().length >= 2) {
            doSearch(inputPlace.value);
        }
    });

    // Keyboard navigation
    inputPlace.addEventListener("keydown", (e) => {
        const items = autoList.querySelectorAll(".autocomplete-item");
        if (!items || items.length === 0 || autoList.style.display === "none") return;

        if (e.key === "ArrowDown") {
            e.preventDefault();
            selectedIndex = (selectedIndex + 1) % items.length;
            updateSelection(items);
        } else if (e.key === "ArrowUp") {
            e.preventDefault();
            selectedIndex = (selectedIndex - 1 + items.length) % items.length;
            updateSelection(items);
        } else if (e.key === "Enter") {
            if (selectedIndex >= 0 && selectedIndex < items.length) {
                e.preventDefault();
                items[selectedIndex].click();
            }
        } else if (e.key === "Escape") {
            autoList.style.display = "none";
        }
    });

    function updateSelection(items) {
        items.forEach((it, idx) => {
            if (idx === selectedIndex) {
                it.classList.add("active-item");
                it.scrollIntoView({ block: "nearest" });
            } else {
                it.classList.remove("active-item");
            }
        });
    }

    document.addEventListener("click", (e) => {
        if (!inputPlace.contains(e.target) && !autoList.contains(e.target)) {
            autoList.style.display = "none";
        }
    });
}

let currentViewMode = "single-page";

function initViewMode() {
    let saved = null;
    try {
        saved = localStorage.getItem("vedic_view_mode");
    } catch (e) {}
    const mode = saved || "single-page";
    setViewMode(mode);
    setupScrollObserver();
}

function setViewMode(mode) {
    currentViewMode = mode;
    try {
        localStorage.setItem("vedic_view_mode", mode);
    } catch (e) {}

    const isSingle = (mode === "single-page");
    if (isSingle) {
        document.body.classList.add("single-page-mode");
    } else {
        document.body.classList.remove("single-page-mode");
    }

    const btnSingle = document.getElementById("btnViewSingle");
    const btnTabs = document.getElementById("btnViewTabs");
    if (btnSingle) btnSingle.classList.toggle("active", isSingle);
    if (btnTabs) btnTabs.classList.toggle("active", !isSingle);

    if (!isSingle) {
        const activeTab = document.querySelector(".tab-pane.active") || document.getElementById("tabCharts");
        if (activeTab) {
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
            activeTab.classList.add("active");
        }
    }
}

function setupScrollObserver() {
    if (!('IntersectionObserver' in window)) return;
    const panes = document.querySelectorAll(".tab-pane");
    const observer = new IntersectionObserver((entries) => {
        if (!document.body.classList.contains("single-page-mode")) return;
        entries.forEach(entry => {
            if (entry.isIntersecting && entry.intersectionRatio >= 0.2) {
                const id = entry.target.id;
                document.querySelectorAll(".tab-btn").forEach(btn => {
                    btn.classList.toggle("active", !!btn.getAttribute("onclick")?.includes(id));
                });
            }
        });
    }, { threshold: [0.2, 0.4] });

    panes.forEach(pane => observer.observe(pane));
}

function switchTab(tabId) {
    const isSingle = document.body.classList.contains("single-page-mode");

    document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
    const clickedBtn = Array.from(document.querySelectorAll(".tab-btn")).find(b => b.getAttribute("onclick")?.includes(tabId));
    if (clickedBtn) clickedBtn.classList.add("active");

    const targetPane = document.getElementById(tabId);
    if (targetPane) {
        if (!isSingle) {
            document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));
            targetPane.classList.add("active");
        } else {
            targetPane.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    if (tabId === "tabProgression" && !currentProgressionData) {
        calculateProgression();
    }
    if (tabId === "tabJamakkol" && !currentJamakkolData) {
        loadJamakkolNow();
    }
}

function setChartStyle(style) {
    document.getElementById("btnNorthStyle")?.classList.toggle("active", style === "north");
    document.getElementById("btnSouthStyle")?.classList.toggle("active", style === "south");
    if (chartRenderer) {
        chartRenderer.setStyle(style);
    }
    if (d9ChartRenderer) {
        d9ChartRenderer.setStyle(style);
    }
}

function onDivChartChange(code) {
    activeDivChartCode = code;
    if (currentHoroscopeData && currentHoroscopeData.divisional_charts[code]) {
        chartRenderer.setChartData(currentHoroscopeData.divisional_charts[code]);
    }
}

function onD9DivChartChange(code) {
    activeD9ChartCode = code;
    if (currentHoroscopeData && currentHoroscopeData.divisional_charts[code]) {
        d9ChartRenderer.setChartData(currentHoroscopeData.divisional_charts[code]);
    }
}

async function calculateHoroscope() {
    const btn = document.getElementById("btnSubmit");
    const originalText = btn.innerHTML;
    btn.innerHTML = `<span>⏳</span> Calculating Ephemeris & Horoscope... / ஜாதகம் கணிக்கப்படுகிறது...`;
    btn.disabled = true;

    const payload = {
        name: document.getElementById("inputName").value,
        birth_date: document.getElementById("inputDate").value,
        birth_time: document.getElementById("inputTime").value,
        place_name: document.getElementById("inputPlace").value,
        latitude: parseFloat(document.getElementById("inputLat").value),
        longitude: parseFloat(document.getElementById("inputLon").value),
        timezone: parseFloat(document.getElementById("inputTz").value),
        ayanamsa: document.getElementById("selectAyanamsa").value,
        house_system: document.getElementById("selectHouseSystem").value
    };

    try {
        const res = await fetch("/api/horoscope", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const json = await res.json();
        if (json.success) {
            currentHoroscopeData = json.data;
            renderAllSections(currentHoroscopeData);
        } else {
            alert("Calculation Error: " + json.error);
        }
    } catch (e) {
        console.error("Horoscope error:", e);
        alert("Failed to compute horoscope. See console for details.");
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function renderAllSections(data) {
    // 1. Chart Tab: Render Left (D-1 Rasi or selected) and Right (D-9 Navamsa or selected)
    if (data.divisional_charts) {
        if (data.divisional_charts[activeDivChartCode]) {
            chartRenderer.setChartData(data.divisional_charts[activeDivChartCode]);
        }
        const rightCode = activeD9ChartCode || "D-9";
        if (data.divisional_charts[rightCode] && d9ChartRenderer) {
            d9ChartRenderer.setChartData(data.divisional_charts[rightCode]);
        }
    }

    // 2. Planets Table
    renderPlanetsTable(data.planets);
    renderSpecialPoints(data.special_points);

    // 3. Panchanga
    renderPanchanga(data.panchanga);

    // 4. Vimshottari Dasha
    renderDasha(data.dasha);

    // 5. Ashtakavarga & Gochara
    renderAshtakavarga(data.ashtakavarga);
    fetchLiveTransits(data.planets);

    // 6. Shadbala
    renderShadbala(data.shadbala);

    // 7. Yogas & Doshas
    renderYogasAndDoshas(data.yogas_and_doshas);
        if (data.kerala_jothidam) {
            renderKeralaJothidam(data.kerala_jothidam);
        }
        if (data.jamakkol_arudam && data.jamakkol_arudam.status === 'success') {
            currentJamakkolData = data.jamakkol_arudam;
            renderJamakkol(data.jamakkol_arudam);
        }

        const urlParams = new URLSearchParams(window.location.search);
        const initTab = urlParams.get('tab');
        if (initTab) {
            switchTab(initTab);
        }
}

function updateChartSidebar(chartData) {
    const lagnaTitle = document.getElementById("sideLagnaTitle");
    const lagnaDesc = document.getElementById("sideLagnaDesc");
    if (lagnaTitle && lagnaDesc) {
        lagnaTitle.textContent = `${chartData.name} (${chartData.code})`;
        lagnaDesc.textContent = `Ascendant Sign: ${chartData.ascendant_rasi_name} • ${chartData.description}`;
    }
}

function renderPlanetsTable(planets) {
    const tbody = document.getElementById("planetsTableBody");
    if (!tbody) return;
    tbody.innerHTML = "";

    planets.forEach(p => {
        const tr = document.createElement("tr");

        let dignityBadge = "";
        if (p.dignity.includes("Exalted")) dignityBadge = `<span class="badge badge-exalted">↑ ${p.dignity}</span>`;
        else if (p.dignity.includes("Debilitated")) dignityBadge = `<span class="badge badge-debilitated">↓ ${p.dignity}</span>`;
        else if (p.dignity.includes("Own Sign")) dignityBadge = `<span class="badge badge-own">⌂ ${p.dignity}</span>`;
        else dignityBadge = `<span style="font-size:0.85rem; color:var(--text-secondary);">${p.dignity}</span>`;

        let motionBadge = `<span style="color:#34d399;">Direct (${p.speed > 0 ? '+' : ''}${p.speed.toFixed(3)}°)</span>`;
        if (p.is_retrograde) {
            motionBadge = `<span class="badge badge-retro">℞ Retro (${p.speed.toFixed(3)}°)</span>`;
        }
        if (p.is_combust) {
            motionBadge += ` <span class="badge badge-combust">🔥 Combust</span>`;
        }

        const iconSvg = PLANET_SVG[p.key] || "";

        tr.innerHTML = `
            <td>
                <div class="planet-cell">
                    <span style="display:inline-block; width:26px; height:26px;">${iconSvg}</span>
                    <div>
                        <div style="font-weight:600;">${p.name} <span style="font-size:0.85rem; opacity:0.8;">${p.symbol}</span></div>
                        <div style="font-size:0.75rem; color:var(--text-muted);">${p.sanskrit}</div>
                    </div>
                </div>
            </td>
            <td>
                <span style="font-weight:600; color:var(--gold-light);">${p.rasi_name}</span> ${p.rasi_symbol}
                <div style="font-size:0.75rem; color:var(--text-muted);">${p.deg_in_sign_dms}</div>
            </td>
            <td>
                <strong>${p.longitude_dms}</strong>
                <div style="font-size:0.75rem; color:var(--text-muted);">${p.longitude.toFixed(2)}°</div>
            </td>
            <td>${motionBadge}</td>
            <td>
                <strong>${p.nakshatra.name}</strong> (Pada ${p.nakshatra.pada})
                <div style="font-size:0.75rem; color:var(--text-muted);">Lord: ${p.nakshatra.lord} • ${p.nakshatra.shakti}</div>
            </td>
            <td>${dignityBadge}</td>
            <td>
                <span style="font-weight:600; color:${p.chara_karaka.includes('AK') ? 'var(--gold-bright)' : 'var(--text-primary)'};">
                    ${p.chara_karaka}
                </span>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderSpecialPoints(special) {
    const grid = document.getElementById("specialPointsGrid");
    if (!grid || !special) return;
    grid.innerHTML = "";

    const allPts = [
        ...(special.arudha_padas || []),
        ...(special.special_lagnas || []),
        ...(special.upagrahas || [])
    ];

    if (allPts.length === 0) {
        grid.innerHTML = `<div style="color:var(--text-secondary);">No special points calculated.</div>`;
        return;
    }

    allPts.slice(0, 16).forEach(pt => {
        const box = document.createElement("div");
        box.className = "house-info-card";
        box.innerHTML = `
            <div style="font-weight:700; color:var(--gold-bright); font-size:0.88rem;">
                ${pt.point}
            </div>
            <div style="font-size:0.9rem; color:var(--text-primary); margin-top:4px;">
                ${pt.position}
            </div>
        `;
        grid.appendChild(box);
    });
}

function renderPanchanga(panchanga) {
    const angasGrid = document.getElementById("panchangaAngasGrid");
    if (!angasGrid || !panchanga) return;

    angasGrid.innerHTML = `
        <div class="panchanga-card">
            <div class="panchanga-anga-name">TITHI / திதி (Lunar Phase)</div>
            <div class="panchanga-val">${panchanga.tithi || '--'}</div>
            <div class="panchanga-sub">Moon-Sun angle illumination phase • சந்திர-சூரிய பாகை தூரம்</div>
        </div>
        <div class="panchanga-card">
            <div class="panchanga-anga-name">VAARA / வாரம் (Vedic Day / கிழமை)</div>
            <div class="panchanga-val">${panchanga.vaara.day} ${panchanga.vaara.day_tamil ? '/ ' + panchanga.vaara.day_tamil : ''} (${panchanga.vaara.lord})</div>
            <div class="panchanga-sub">Vedic day from true sunrise • சூரிய உதயம் முதல் கணக்கீடு</div>
        </div>
        <div class="panchanga-card">
            <div class="panchanga-anga-name">NAKSHATRA / நட்சத்திரம் (Lunar Mansion)</div>
            <div class="panchanga-val">${panchanga.nakshatra || '--'}</div>
            <div class="panchanga-sub">Stellar asterism traversed by Moon • சந்திரன் சஞ்சரிக்கும் விண்மீன்</div>
        </div>
        <div class="panchanga-card">
            <div class="panchanga-anga-name">YOGA / யோகம் (Soli-Lunar Union)</div>
            <div class="panchanga-val">${panchanga.yoga || '--'}</div>
            <div class="panchanga-sub">Sum of Sun & Moon sidereal longitudes • சூரிய-சந்திர ஸ்புட கூட்டுத்தொகை</div>
        </div>
        <div class="panchanga-card">
            <div class="panchanga-anga-name">KARANA / கரணம் (Half-Tithi)</div>
            <div class="panchanga-val">${panchanga.karana || '--'}</div>
            <div class="panchanga-sub">Half-interval of the active tithi • திதியின் பாதிப் பகுதி</div>
        </div>
    `;

    // Muhurta windows
    const muhurtaGrid = document.getElementById("muhurtaWindowsGrid");
    if (muhurtaGrid) {
        muhurtaGrid.innerHTML = `
            <div class="muhurta-card is-auspicious">
                <div style="font-size:2rem;">☀️</div>
                <div>
                    <div style="font-size:0.82rem; color:#34d399; font-weight:700;">ABHIJIT MUHURTHA / அபிஜித் முகூர்த்தம்</div>
                    <div style="font-size:1.05rem; font-weight:700; color:var(--text-primary);">${panchanga.abhijit_muhurta || 'Midday Window'}</div>
                    <div style="font-size:0.75rem; color:var(--text-secondary);">Supreme midday auspicious window for all major endeavors • உச்ச சுப முகூர்த்த நேரம்</div>
                </div>
            </div>
            <div class="muhurta-card">
                <div style="font-size:2rem;">🌅</div>
                <div>
                    <div style="font-size:0.82rem; color:var(--gold-light); font-weight:700;">SUNRISE & SUNSET / சூரிய உதயம் & அஸ்தமனம்</div>
                    <div style="font-size:1.05rem; font-weight:700; color:var(--text-primary);">Rise: ${panchanga.sunrise} • Set: ${panchanga.sunset}</div>
                    <div style="font-size:0.75rem; color:var(--text-secondary);">Moonrise: ${panchanga.moonrise} • Moonset: ${panchanga.moonset}</div>
                </div>
            </div>
            <div class="muhurta-card is-inauspicious">
                <div style="font-size:2rem;">⚡</div>
                <div>
                    <div style="font-size:0.82rem; color:#f87171; font-weight:700;">RAHU KALAM / இராகு காலம்</div>
                    <div style="font-size:1.05rem; font-weight:700; color:var(--text-primary);">${panchanga.rahu_kalam || 'Avoid for new starts'}</div>
                    <div style="font-size:0.75rem; color:var(--text-secondary);">Sensitive inauspicious window; avoid inaugurations • சுப காரியங்கள் தவிர்க்க வேண்டிய நேரம்</div>
                </div>
            </div>
            <div class="muhurta-card is-inauspicious">
                <div style="font-size:2rem;">⚠️</div>
                <div>
                    <div style="font-size:0.82rem; color:#f87171; font-weight:700;">YAMAGANDAM & GULIKA / எமகண்டம் & குளிகை</div>
                    <div style="font-size:1.05rem; font-weight:700; color:var(--text-primary);">Yama: ${panchanga.yamagandam}</div>
                    <div style="font-size:0.75rem; color:var(--text-secondary);">Gulika Kalam: ${panchanga.gulika_kalam}</div>
                </div>
            </div>
        `;
    }

    // Traditional Calendar Eras
    const erasGrid = document.getElementById("calendarErasGrid");
    if (erasGrid) {
        erasGrid.innerHTML = `
            <div class="house-info-card">
                <div style="color:var(--gold-bright); font-size:0.82rem; font-weight:600;">LUNAR SAMVATSARA / தமிழ் ஆண்டு</div>
                <div style="font-size:1rem; font-weight:700; margin-top:2px;">${panchanga.samvatsara || '--'}</div>
            </div>
            <div class="house-info-card">
                <div style="color:var(--gold-bright); font-size:0.82rem; font-weight:600;">SOLAR MONTH / சூரிய மாதம் (தமிழ் மாதம்)</div>
                <div style="font-size:1rem; font-weight:700; margin-top:2px;">${panchanga.solar_month || '--'}</div>
            </div>
            <div class="house-info-card">
                <div style="color:var(--gold-bright); font-size:0.82rem; font-weight:600;">KALI YUGA YEAR / கலியுக ஆண்டு</div>
                <div style="font-size:1rem; font-weight:700; margin-top:2px;">${panchanga.kali_year || '--'}</div>
            </div>
            <div class="house-info-card">
                <div style="color:var(--gold-bright); font-size:0.82rem; font-weight:600;">VIKRAMA & SAKA / விக்கிரம & சாலிவாகன சகாப்தம்</div>
                <div style="font-size:1rem; font-weight:700; margin-top:2px;">Vikram: ${panchanga.vikram_year} • Saka: ${panchanga.saka_year}</div>
            </div>
        `;
    }
}

function renderDasha(dasha) {
    if (!dasha) return;

    const PLANET_TAMIL = {
        'Sun': 'சூரியன்',
        'Moon': 'சந்திரன்',
        'Mars': 'செவ்வாய்',
        'Mercury': 'புதன்',
        'Jupiter': 'குரு',
        'Venus': 'சுக்கிரன்',
        'Saturn': 'சனி',
        'Rahu': 'ராகு',
        'Ketu': 'கேது'
    };

    const activeDashaText = document.getElementById("activeDashaText");
    const dashaBalanceText = document.getElementById("dashaBalanceText");
    if (activeDashaText) {
        const mahaTa = PLANET_TAMIL[dasha.active_mahadasha] || '';
        const antarTa = PLANET_TAMIL[dasha.active_antardasha] || '';
        activeDashaText.innerHTML = `<strong>${dasha.active_mahadasha || 'Active'} (${mahaTa})</strong> Mahadasha • <strong>${dasha.active_antardasha || ''} (${antarTa})</strong> Antardasha`;
    }
    if (dashaBalanceText) {
        dashaBalanceText.textContent = `Balance of Dasha at Birth: ${dasha.balance_at_birth}`;
    }

    // Chart Header Live Dasha Badge next to South / தெற்கு
    const chartHeaderDasha = document.getElementById("chartHeaderDasha");
    if (chartHeaderDasha) {
        const mahaEn = dasha.active_mahadasha || 'Active';
        const mahaTa = PLANET_TAMIL[mahaEn] || mahaEn;
        const antarEn = dasha.active_antardasha || '';
        const antarTa = PLANET_TAMIL[antarEn] || antarEn;

        chartHeaderDasha.innerHTML = `
            <div class="dasha-line">
                <span class="dasha-label">Mahadasha / மகாதிசை:</span> 
                <strong class="dasha-val">${mahaEn} / ${mahaTa}</strong>
            </div>
            <div class="dasha-line">
                <span class="dasha-label">Antardasha / அந்தர்திசை:</span> 
                <strong class="dasha-val">${antarEn} / ${antarTa}</strong>
            </div>
        `;
    }

    const accordion = document.getElementById("dashaAccordion");
    if (!accordion) return;
    accordion.innerHTML = "";

    dasha.dashas.forEach(m => {
        const card = document.createElement("div");
        card.className = `dasha-card ${m.is_active ? 'is-running open' : ''}`;

        const header = document.createElement("div");
        header.className = "dasha-header";
        header.onclick = () => card.classList.toggle("open");

        const iconSvg = PLANET_SVG[m.lord] || "";
        const mahaTamil = PLANET_TAMIL[m.lord] || m.lord;

        header.innerHTML = `
            <div style="display:flex; align-items:center; gap:12px;">
                <span style="display:inline-block; width:28px; height:28px;">${iconSvg}</span>
                <div>
                    <span style="font-family:var(--font-serif); font-size:1.08rem; font-weight:700; color:var(--gold-bright);">
                        ${m.lord} / ${mahaTamil}
                    </span>
                    <span style="font-size:0.82rem; color:var(--text-secondary); margin-left:8px; font-weight:600;">
                        ${m.start_date} to ${m.end_date}
                    </span>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                ${m.is_active ? '<span class="badge" style="background:#059669; color:#ffffff; font-weight:800; padding:4px 10px; border-radius:6px; font-size:0.75rem;">CURRENT • தற்போதைய தசை</span>' : ''}
                <span style="color:var(--text-secondary); font-size:0.9rem;">▼</span>
            </div>
        `;

        const body = document.createElement("div");
        body.className = "dasha-body";

        const antGrid = document.createElement("div");
        antGrid.className = "antardasha-grid";

        m.antardashas.forEach(a => {
            const box = document.createElement("div");
            box.className = `antardasha-box ${a.is_active ? 'active' : ''}`;
            const subTamil = PLANET_TAMIL[a.sub_lord] || a.sub_lord;

            box.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
                    <div style="font-weight:700; font-size:0.92rem; color:${a.is_active ? '#047857' : 'var(--gold-bright)'};">
                        ${a.sub_lord} ${a.symbol} <span style="font-size:0.78rem; color:var(--text-secondary); font-weight:600;">/ ${subTamil}</span>
                    </div>
                    ${a.is_active ? '<span class="badge" style="background:#059669; color:#ffffff; font-size:0.65rem; padding:1px 6px; font-weight:800; border-radius:4px;">ACTIVE</span>' : ''}
                </div>
                <div style="font-size:0.76rem; color:var(--text-secondary); line-height:1.4;">
                    From: <strong style="color:var(--text-primary); font-weight:700;">${a.start_date}</strong>
                </div>
                <div style="font-size:0.76rem; color:var(--text-secondary); line-height:1.4;">
                    To: <strong style="color:var(--text-primary); font-weight:700;">${a.end_date}</strong>
                </div>
            `;
            antGrid.appendChild(box);
        });

        body.appendChild(antGrid);
        card.appendChild(header);
        card.appendChild(body);
        accordion.appendChild(card);
    });
}

function recalculateDasha(targetDateStr) {
    if (!currentHoroscopeData) return;
    // Client side or fetch
    console.log("Recalculate dasha for date:", targetDateStr);
}

function renderAshtakavarga(av) {
    if (!av) return;

    // 1. Render Single Visual Ashtakavarga Chart (South Indian 4x4 Grid)
    renderAshtakavargaChart(av);

    // 2. Render Non-Scrolling Bhinnashtakavarga Table (Fits 100% into card)
    const bavBody = document.getElementById("bavTableBody");
    if (bavBody && av.bhinnashtakavarga) {
        bavBody.innerHTML = "";
        const themeName = document.body.getAttribute("data-theme") || "human-crafted";
        const isLight = (themeName === "palm-leaf" || themeName === "pleasant-vedic" || !themeName || themeName === "default");

        const PLANET_ROW_META = {
            'Jupiter': { glyph: '♃', ta: 'குரு' },
            'Lagna':   { glyph: '★', ta: 'லக்னம்' },
            'Mars':    { glyph: '♂', ta: 'செவ்வாய்' },
            'Mercury': { glyph: '☿', ta: 'புதன்' },
            'Moon':    { glyph: '☾', ta: 'சந்திரன்' },
            'Saturn':  { glyph: '♄', ta: 'சனி' },
            'Sun':     { glyph: '☉', ta: 'சூரியன்' },
            'Venus':   { glyph: '♀', ta: 'சுக்கிரன்' }
        };

        const planetsOrder = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Lagna'];
        const pKeys = Object.keys(av.bhinnashtakavarga);
        pKeys.sort((a, b) => {
            const idxA = planetsOrder.indexOf(a);
            const idxB = planetsOrder.indexOf(b);
            return (idxA !== -1 ? idxA : 99) - (idxB !== -1 ? idxB : 99);
        });

        pKeys.forEach(pName => {
            const pts = av.bhinnashtakavarga[pName];
            const sumPts = pts.reduce((a, b) => a + b, 0);
            const tr = document.createElement("tr");
            const meta = PLANET_ROW_META[pName] || { glyph: '🪐', ta: pName };

            let tds = `<td><span style="font-weight:700;">${meta.glyph} ${pName}</span> <span style="font-size:0.75rem; color:var(--text-secondary);">/ ${meta.ta}</span></td>`;
            pts.forEach(pt => {
                const color = pt >= 5 ? (isLight ? '#047857' : '#34d399') : (pt <= 3 ? (isLight ? '#b91c1c' : '#f87171') : 'var(--text-primary)');
                tds += `<td style="color:${color}; font-weight:700; text-align:center;">${pt}</td>`;
            });
            tds += `<td style="font-weight:800; color:var(--gold-bright); text-align:center;">${sumPts}</td>`;

            tr.innerHTML = tds;
            bavBody.appendChild(tr);
        });

        // 3. Add SAV Total Summary Row at bottom of table
        if (av.sarvashtakavarga) {
            const totalTr = document.createElement("tr");
            totalTr.className = "bav-total-row";
            let totalTds = `<td><strong>Total (SAV) / மொத்தம்</strong></td>`;
            let grandTotal = 0;
            av.sarvashtakavarga.forEach(s => {
                const pt = s.points;
                grandTotal += pt;
                const color = pt >= 28 ? (isLight ? '#047857' : '#34d399') : (isLight ? '#b91c1c' : '#f87171');
                totalTds += `<td style="color:${color}; font-weight:800; text-align:center;">${pt}</td>`;
            });
            totalTds += `<td style="font-weight:900; color:var(--gold-bright); text-align:center;">${grandTotal}</td>`;
            totalTr.innerHTML = totalTds;
            bavBody.appendChild(totalTr);
        }
    }
}

function renderAshtakavargaChart(av) {
    const container = document.getElementById("ashtakavargaChartContainer");
    if (!container || !av || !av.sarvashtakavarga) return;
    container.innerHTML = "";

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 680 680");
    svg.setAttribute("class", "vedic-chart-svg south-chart modern-south-chart");

    const compStyle = getComputedStyle(document.body);
    const goldBright = compStyle.getPropertyValue('--gold-bright').trim() || '#ffd700';
    const goldPrimary = compStyle.getPropertyValue('--gold-primary').trim() || '#d4af37';
    const bgDark = compStyle.getPropertyValue('--bg-dark').trim() || '#070a13';
    const borderGold = compStyle.getPropertyValue('--border-gold').trim() || 'rgba(212, 175, 55, 0.4)';
    const textPrimary = compStyle.getPropertyValue('--text-primary').trim() || '#f8fafc';
    const textSecondary = compStyle.getPropertyValue('--text-secondary').trim() || '#94a3b8';

    const themeName = document.body.getAttribute("data-theme") || "human-crafted";
    const isLight = (themeName === "palm-leaf" || themeName === "pleasant-vedic" || !themeName || themeName === "default");

    const cPalette = isLight ? {
        chartBg: "#fbf8ef",
        chartBorder: "#b45309",
        cellBg: "#f5eedf",
        cellBorder: "rgba(180, 83, 9, 0.45)",
        centerBg: "#f7f1e4",
        centerBorder: "#b45309",
        omColor: "rgba(180, 83, 9, 0.13)",
        titleColor: "#78350f",
        subtitleColor: "#1c1917",
        badgeBg: "rgba(180, 83, 9, 0.12)",
        badgeBorder: "#b45309",
        badgeText: "#78350f",
        epheColor: "#57534e",
        rasiEnColor: "#78350f",
        rasiTaColor: "#92400e",
        highScoreBg: "rgba(5, 150, 105, 0.16)",
        highScoreBorder: "#059669",
        highScoreText: "#065f46",
        lowScoreBg: "rgba(220, 38, 38, 0.12)",
        lowScoreBorder: "#dc2626",
        lowScoreText: "#991b1b",
        rekhaColor: "#292524"
    } : {
        chartBg: bgDark,
        chartBorder: goldPrimary,
        cellBg: "rgba(255, 255, 255, 0.04)",
        cellBorder: borderGold,
        centerBg: "rgba(10, 15, 26, 0.95)",
        centerBorder: goldBright,
        omColor: "rgba(212, 175, 55, 0.16)",
        titleColor: goldBright,
        subtitleColor: "#f8fafc",
        badgeBg: "rgba(212, 175, 55, 0.18)",
        badgeBorder: goldBright,
        badgeText: goldBright,
        epheColor: textSecondary,
        rasiEnColor: goldBright,
        rasiTaColor: "#facc15",
        highScoreBg: "rgba(16, 185, 129, 0.22)",
        highScoreBorder: "#10b981",
        highScoreText: "#6ee7b7",
        lowScoreBg: "rgba(239, 68, 68, 0.18)",
        lowScoreBorder: "#ef4444",
        lowScoreText: "#fca5a5",
        rekhaColor: "#f8fafc"
    };

    const RASHI_DATA = [
        { id: 0, en: "Aries", ta: "மேஷம்", symbol: "♈" },
        { id: 1, en: "Taurus", ta: "ரிஷபம்", symbol: "♉" },
        { id: 2, en: "Gemini", ta: "மிதுனம்", symbol: "♊" },
        { id: 3, en: "Cancer", ta: "கடகம்", symbol: "♋" },
        { id: 4, en: "Leo", ta: "சிம்மம்", symbol: "♌" },
        { id: 5, en: "Virgo", ta: "கன்னி", symbol: "♍" },
        { id: 6, en: "Libra", ta: "துலாம்", symbol: "♎" },
        { id: 7, en: "Scorpio", ta: "விருச்சிகம்", symbol: "♏" },
        { id: 8, en: "Sagittarius", ta: "தனுசு", symbol: "♐" },
        { id: 9, en: "Capricorn", ta: "மகரம்", symbol: "♑" },
        { id: 10, en: "Aquarius", ta: "கும்பம்", symbol: "♒" },
        { id: 11, en: "Pisces", ta: "மீனம்", symbol: "♓" }
    ];

    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    defs.innerHTML = `
        <linearGradient id="goldBorderGradAV" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="${goldBright}"/>
            <stop offset="50%" stop-color="${goldPrimary}"/>
            <stop offset="100%" stop-color="${goldPrimary}"/>
        </linearGradient>
    `;
    svg.appendChild(defs);

    // Chart Outer Background Card
    const bg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    bg.setAttribute("x", "8");
    bg.setAttribute("y", "8");
    bg.setAttribute("width", "664");
    bg.setAttribute("height", "664");
    bg.setAttribute("rx", "16");
    bg.setAttribute("fill", cPalette.chartBg);
    bg.setAttribute("stroke", isLight ? cPalette.chartBorder : "url(#goldBorderGradAV)");
    bg.setAttribute("stroke-width", "2.5");
    svg.appendChild(bg);

    const signGridCoords = {
        11: [0, 0], 0: [1, 0], 1: [2, 0], 2: [3, 0],
        3: [3, 1], 4: [3, 2], 5: [3, 3],
        6: [2, 3], 7: [1, 3], 8: [0, 3],
        9: [0, 2], 10: [0, 1]
    };

    const cellSize = 165;
    const offset = 10;
    const savList = av.sarvashtakavarga || [];
    const bav = av.bhinnashtakavarga || {};

    let maxScore = -1, minScore = 999;
    let maxRasi = "", minRasi = "";
    let beneficCount = 0, maleficCount = 0;

    savList.forEach(s => {
        if (s.points > maxScore) { maxScore = s.points; maxRasi = s.rasi_name; }
        if (s.points < minScore) { minScore = s.points; minRasi = s.rasi_name; }
        if (s.points >= 28) beneficCount++; else maleficCount++;
    });

    // Draw 12 Outer Cells
    for (let r_id = 0; r_id < 12; r_id++) {
        const gridPos = signGridCoords[r_id];
        const gx = offset + gridPos[0] * cellSize;
        const gy = offset + gridPos[1] * cellSize;
        const sInfo = savList.find(s => s.rasi_id === r_id) || { points: 0 };
        const rInfo = RASHI_DATA[r_id];
        const isHigh = (sInfo.points >= 28);

        // Clip-Path
        const clipId = `clip-av-${r_id}`;
        const clipPath = document.createElementNS("http://www.w3.org/2000/svg", "clipPath");
        clipPath.setAttribute("id", clipId);
        const clipRect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        clipRect.setAttribute("x", gx + 2);
        clipRect.setAttribute("y", gy + 2);
        clipRect.setAttribute("width", cellSize - 4);
        clipRect.setAttribute("height", cellSize - 4);
        clipRect.setAttribute("rx", "10");
        clipPath.appendChild(clipRect);
        defs.appendChild(clipPath);

        const cellGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        cellGroup.setAttribute("clip-path", `url(#${clipId})`);

        // Cell rect
        const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        rect.setAttribute("x", gx + 2);
        rect.setAttribute("y", gy + 2);
        rect.setAttribute("width", cellSize - 4);
        rect.setAttribute("height", cellSize - 4);
        rect.setAttribute("rx", "10");
        rect.setAttribute("stroke", isHigh ? (isLight ? '#059669' : '#10b981') : cPalette.cellBorder);
        rect.setAttribute("stroke-width", isHigh ? "2" : "1.2");
        rect.setAttribute("fill", isHigh ? (isLight ? 'rgba(5, 150, 105, 0.08)' : 'rgba(16, 185, 129, 0.08)') : cPalette.cellBg);
        cellGroup.appendChild(rect);

        // Header Line 1: English + Symbol (Left)
        const txtEn = document.createElementNS("http://www.w3.org/2000/svg", "text");
        txtEn.setAttribute("x", gx + 8);
        txtEn.setAttribute("y", gy + 16);
        txtEn.setAttribute("font-size", "13.5px");
        txtEn.setAttribute("font-weight", "800");
        txtEn.setAttribute("fill", cPalette.rasiEnColor);
        txtEn.textContent = `${rInfo.en} ${rInfo.symbol}`;
        cellGroup.appendChild(txtEn);

        // House badge (Right)
        let lagnaId = 0;
        if (window.currentHoroscopeData?.divisional_charts?.['D-1']?.ascendant_rasi !== undefined) {
            lagnaId = window.currentHoroscopeData.divisional_charts['D-1'].ascendant_rasi;
        }
        let hNum = ((r_id - lagnaId + 12) % 12) + 1;
        const hBadge = document.createElementNS("http://www.w3.org/2000/svg", "text");
        hBadge.setAttribute("x", gx + cellSize - 10);
        hBadge.setAttribute("y", gy + 16);
        hBadge.setAttribute("text-anchor", "end");
        hBadge.setAttribute("font-size", "11.5px");
        hBadge.setAttribute("font-weight", "800");
        hBadge.setAttribute("fill", isLight ? "#57534e" : textSecondary);
        hBadge.textContent = `H${hNum}`;
        cellGroup.appendChild(hBadge);

        // Header Line 2: Tamil Name (Left)
        const txtTa = document.createElementNS("http://www.w3.org/2000/svg", "text");
        txtTa.setAttribute("x", gx + 8);
        txtTa.setAttribute("y", gy + 32);
        txtTa.setAttribute("font-size", "13px");
        txtTa.setAttribute("font-weight", "800");
        txtTa.setAttribute("fill", cPalette.rasiTaColor);
        txtTa.textContent = rInfo.ta;
        cellGroup.appendChild(txtTa);

        // Prominent SAV Score Badge in center of cell
        const scoreBadge = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        scoreBadge.setAttribute("x", gx + 8);
        scoreBadge.setAttribute("y", gy + 42);
        scoreBadge.setAttribute("width", cellSize - 16);
        scoreBadge.setAttribute("height", "34");
        scoreBadge.setAttribute("rx", "6");
        scoreBadge.setAttribute("fill", isHigh ? cPalette.highScoreBg : cPalette.lowScoreBg);
        scoreBadge.setAttribute("stroke", isHigh ? cPalette.highScoreBorder : cPalette.lowScoreBorder);
        scoreBadge.setAttribute("stroke-width", "1.4");
        cellGroup.appendChild(scoreBadge);

        const scoreTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
        scoreTxt.setAttribute("x", gx + (cellSize / 2));
        scoreTxt.setAttribute("y", gy + 64);
        scoreTxt.setAttribute("text-anchor", "middle");
        scoreTxt.setAttribute("font-size", "18px");
        scoreTxt.setAttribute("font-weight", "900");
        scoreTxt.setAttribute("fill", isHigh ? cPalette.highScoreText : cPalette.lowScoreText);
        scoreTxt.textContent = `SAV: ${sInfo.points} Rekhas`;
        cellGroup.appendChild(scoreTxt);

        // Divider
        const divL = document.createElementNS("http://www.w3.org/2000/svg", "line");
        divL.setAttribute("x1", gx + 8);
        divL.setAttribute("y1", gy + 84);
        divL.setAttribute("x2", gx + cellSize - 8);
        divL.setAttribute("y2", gy + 84);
        divL.setAttribute("stroke", isLight ? "rgba(180, 83, 9, 0.25)" : borderGold);
        divL.setAttribute("stroke-width", "0.8");
        cellGroup.appendChild(divL);

        // Planetary Rekha scores breakdown
        const su = bav['Sun'] ? bav['Sun'][r_id] : 0;
        const mo = bav['Moon'] ? bav['Moon'][r_id] : 0;
        const ma = bav['Mars'] ? bav['Mars'][r_id] : 0;
        const me = bav['Mercury'] ? bav['Mercury'][r_id] : 0;
        const ju = bav['Jupiter'] ? bav['Jupiter'][r_id] : 0;
        const ve = bav['Venus'] ? bav['Venus'][r_id] : 0;
        const sa = bav['Saturn'] ? bav['Saturn'][r_id] : 0;

        // Line 1: Sun, Moon, Mars, Mercury
        const pLine1 = document.createElementNS("http://www.w3.org/2000/svg", "text");
        pLine1.setAttribute("x", gx + 10);
        pLine1.setAttribute("y", gy + 104);
        pLine1.setAttribute("font-size", "12px");
        pLine1.setAttribute("font-weight", "800");
        pLine1.setAttribute("fill", cPalette.rekhaColor);
        pLine1.textContent = `☉${su}   ☾${mo}   ♂${ma}   ☿${me}`;
        cellGroup.appendChild(pLine1);

        // Line 2: Jupiter, Venus, Saturn
        const pLine2 = document.createElementNS("http://www.w3.org/2000/svg", "text");
        pLine2.setAttribute("x", gx + 10);
        pLine2.setAttribute("y", gy + 126);
        pLine2.setAttribute("font-size", "12px");
        pLine2.setAttribute("font-weight", "800");
        pLine2.setAttribute("fill", cPalette.rekhaColor);
        pLine2.textContent = `♃${ju}   ♀${ve}   ♄${sa}`;
        cellGroup.appendChild(pLine2);

        // Status Label (Benefic / Malefic)
        const statusTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
        statusTxt.setAttribute("x", gx + (cellSize / 2));
        statusTxt.setAttribute("y", gy + 150);
        statusTxt.setAttribute("text-anchor", "middle");
        statusTxt.setAttribute("font-size", "11px");
        statusTxt.setAttribute("font-weight", "800");
        statusTxt.setAttribute("fill", isHigh ? (isLight ? '#065f46' : '#34d399') : (isLight ? '#991b1b' : '#f87171'));
        statusTxt.textContent = isHigh ? "Benefic / சுப பலம்" : "Malefic / குறைந்த பலம்";
        cellGroup.appendChild(statusTxt);

        svg.appendChild(cellGroup);
    }

    // Center Square (330x330)
    const centerGx = offset + cellSize;
    const centerGy = offset + cellSize;
    const centerW = cellSize * 2;
    const centerH = cellSize * 2;

    const centerRect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    centerRect.setAttribute("x", centerGx + 3);
    centerRect.setAttribute("y", centerGy + 3);
    centerRect.setAttribute("width", centerW - 6);
    centerRect.setAttribute("height", centerH - 6);
    centerRect.setAttribute("rx", "14");
    centerRect.setAttribute("fill", cPalette.centerBg);
    centerRect.setAttribute("stroke", isLight ? cPalette.centerBorder : "url(#goldBorderGradAV)");
    centerRect.setAttribute("stroke-width", "2");
    svg.appendChild(centerRect);

    // Sacred Pranavam
    const omTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
    omTxt.setAttribute("x", 340);
    omTxt.setAttribute("y", 295);
    omTxt.setAttribute("text-anchor", "middle");
    omTxt.setAttribute("font-size", "68px");
    omTxt.setAttribute("fill", cPalette.omColor);
    omTxt.setAttribute("font-family", "var(--font-serif)");
    omTxt.textContent = "ௐ";
    svg.appendChild(omTxt);

    // Title
    const titleTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
    titleTxt.setAttribute("x", 340);
    titleTxt.setAttribute("y", 308);
    titleTxt.setAttribute("text-anchor", "middle");
    titleTxt.setAttribute("font-family", "var(--font-serif)");
    titleTxt.setAttribute("font-size", "20px");
    titleTxt.setAttribute("font-weight", "800");
    titleTxt.setAttribute("fill", cPalette.titleColor);
    titleTxt.textContent = "Sarvashtakavarga Chart";
    svg.appendChild(titleTxt);

    // Subtitle
    const subTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
    subTxt.setAttribute("x", 340);
    subTxt.setAttribute("y", 332);
    subTxt.setAttribute("text-anchor", "middle");
    subTxt.setAttribute("font-size", "13.5px");
    subTxt.setAttribute("font-weight", "700");
    subTxt.setAttribute("fill", cPalette.subtitleColor);
    subTxt.textContent = "சர்வ அஷ்டகவர்க்க சக்கரம் (SAV)";
    svg.appendChild(subTxt);

    // Total Banner
    const totalBadge = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    totalBadge.setAttribute("x", "205");
    totalBadge.setAttribute("y", "348");
    totalBadge.setAttribute("width", "270");
    totalBadge.setAttribute("height", "32");
    totalBadge.setAttribute("rx", "6");
    totalBadge.setAttribute("fill", cPalette.badgeBg);
    totalBadge.setAttribute("stroke", cPalette.badgeBorder);
    totalBadge.setAttribute("stroke-width", "1.2");
    svg.appendChild(totalBadge);

    const totalTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
    totalTxt.setAttribute("x", 340);
    totalTxt.setAttribute("y", 369);
    totalTxt.setAttribute("text-anchor", "middle");
    totalTxt.setAttribute("font-size", "14px");
    totalTxt.setAttribute("font-weight", "800");
    totalTxt.setAttribute("fill", cPalette.badgeText);
    totalTxt.textContent = "Total: 337 Rekhas • Avg: 28 / Sign";
    svg.appendChild(totalTxt);

    // High / Low summary
    const summaryTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
    summaryTxt.setAttribute("x", 340);
    summaryTxt.setAttribute("y", 400);
    summaryTxt.setAttribute("text-anchor", "middle");
    summaryTxt.setAttribute("font-size", "12px");
    summaryTxt.setAttribute("font-weight", "700");
    summaryTxt.setAttribute("fill", isLight ? "#065f46" : "#34d399");
    summaryTxt.textContent = `★ Strongest: ${maxRasi} (${maxScore}) • Lowest: ${minRasi} (${minScore})`;
    svg.appendChild(summaryTxt);

    // Counts line
    const countsTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
    countsTxt.setAttribute("x", 340);
    countsTxt.setAttribute("y", 420);
    countsTxt.setAttribute("text-anchor", "middle");
    countsTxt.setAttribute("font-size", "11px");
    countsTxt.setAttribute("font-weight", "600");
    countsTxt.setAttribute("fill", cPalette.epheColor);
    countsTxt.textContent = `Benefic (≥28): ${beneficCount} Signs • Malefic (<28): ${maleficCount} Signs`;
    svg.appendChild(countsTxt);

    container.appendChild(svg);
}

async function fetchLiveTransits(planets) {
    const tbody = document.getElementById("transitsTableBody");
    const sadeBadge = document.getElementById("sadeSatiBadge");
    if (!tbody) return;

    // Find natal Moon & Lagna
    const moon = planets.find(p => p.key === "Moon") || { rasi_id: 0 };
    const lagna = planets.find(p => p.key === "Lagna") || { rasi_id: 0 };

    try {
        const res = await fetch(`/api/transits?moon_rasi=${moon.rasi_id}&lagna_rasi=${lagna.rasi_id}`);
        const json = await res.json();
        if (!json.success) return;

        const data = json.data;
        tbody.innerHTML = "";

        const themeName = document.body.getAttribute("data-theme") || "human-crafted";
        const isLight = (themeName === "palm-leaf" || themeName === "pleasant-vedic" || !themeName || themeName === "default");

        // Sade Sati badge with Dual Language English & Tamil
        if (sadeBadge) {
            if (data.sade_sati.is_active) {
                sadeBadge.className = "badge badge-combust";
                sadeBadge.innerHTML = `⚠️ <strong>Sade Sati Active / ஏழரை சனி:</strong> ${data.sade_sati.phase}`;
            } else {
                sadeBadge.className = "badge badge-exalted";
                sadeBadge.innerHTML = `✓ <strong>No Active Sade Sati / ஏழரை சனி இல்லை</strong> (Saturn in H${data.sade_sati.saturn_house_from_moon} from Moon)`;
            }
        }

        const PLANET_TAMIL = {
            'Sun': 'சூரியன்',
            'Moon': 'சந்திரன்',
            'Mars': 'செவ்வாய்',
            'Mercury': 'புதன்',
            'Jupiter': 'குரு',
            'Venus': 'சுக்கிரன்',
            'Saturn': 'சனி',
            'Rahu': 'ராகு',
            'Ketu': 'கேது'
        };

        const getOrdinal = (n) => {
            const s = ["th", "st", "nd", "rd"];
            const v = n % 100;
            return n + (s[(v - 20) % 10] || s[v] || s[0]);
        };

        data.transits.forEach(t => {
            const tr = document.createElement("tr");
            const iconSvg = PLANET_SVG[t.planet] || "";
            const taName = PLANET_TAMIL[t.planet] || t.tamil || "";

            // Status Pill
            let statusBadge = "";
            if (t.planet === "Ketu") {
                statusBadge = `
                    <span class="transit-status-badge badge-transit-spiritual">
                        ☸ Spiritual / ஆன்மீகம்
                    </span>`;
            } else if (t.is_benefic_transit) {
                statusBadge = `
                    <span class="transit-status-badge badge-transit-benefic">
                        ✓ Favorable / சுப பலன்
                    </span>`;
            } else {
                statusBadge = `
                    <span class="transit-status-badge badge-transit-caution">
                        ⚠️ Caution / கவன பலன்
                    </span>`;
            }

            // Retrograde indicator
            const retroPill = (t.is_retrograde && t.planet !== 'Rahu' && t.planet !== 'Ketu')
                ? `<span class="badge badge-retro-tag">R</span>`
                : '';

            // Nakshatra text
            const nakText = t.nakshatra ? `${t.nakshatra.name}-${t.nakshatra.pada} (${t.nakshatra.tamil})` : '';

            tr.innerHTML = `
                <td>
                    <div class="transit-planet-cell">
                        <span class="transit-planet-icon">${iconSvg}</span>
                        <div class="transit-planet-info">
                            <strong class="planet-en-name">${t.planet}</strong>
                            <span class="planet-ta-name">/ ${taName}</span>
                        </div>
                    </div>
                </td>
                <td>
                    <div class="transit-sign-cell">
                        <span class="transit-sign-symbol">${t.rasi_symbol}</span>
                        <strong class="transit-sign-en">${t.rasi_name}</strong>
                        <span class="transit-sign-ta">/ ${t.rasi_tamil || ''}</span>
                        ${retroPill}
                    </div>
                </td>
                <td>
                    <div class="transit-deg-primary">${t.longitude_dms}</div>
                    <div class="transit-deg-sub">${t.deg_in_sign_dms} • ${nakText}</div>
                </td>
                <td>
                    <div class="transit-house-cell">
                        <span class="badge transit-house-badge">
                            H${t.house_from_moon} (${getOrdinal(t.house_from_moon)})
                        </span>
                        <span class="transit-house-ta">${t.house_from_moon}ம் பாவம்</span>
                    </div>
                </td>
                <td>
                    <div class="transit-house-cell">
                        <span class="badge transit-house-badge">
                            H${t.house_from_lagna} (${getOrdinal(t.house_from_lagna)})
                        </span>
                        <span class="transit-house-ta">${t.house_from_lagna}ம் பாவம்</span>
                    </div>
                </td>
                <td>
                    ${statusBadge}
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error("Transits error:", e);
    }
}

function renderShadbala(shadbala) {
    const tbody = document.getElementById("shadbalaTableBody");
    if (!tbody || !shadbala) return;
    tbody.innerHTML = "";

    shadbala.forEach(s => {
        const tr = document.createElement("tr");
        const iconSvg = PLANET_SVG[s.planet] || "";

        tr.innerHTML = `
            <td style="font-weight:700; color:var(--gold-bright); text-align:center;">#${s.rank}</td>
            <td>
                <div class="planet-cell">
                    <span style="display:inline-block; width:22px; height:22px;">${iconSvg}</span>
                    <span>${s.planet}</span>
                </div>
            </td>
            <td>${s.sthana_bala}</td>
            <td>${s.dig_bala}</td>
            <td>${s.kaala_bala}</td>
            <td>${s.cheshta_bala}</td>
            <td>${s.naisargika_bala}</td>
            <td>${s.drik_bala}</td>
            <td style="font-weight:700; color:var(--gold-light);">${s.total_rupas}</td>
            <td>${s.min_required_rupas}</td>
            <td><strong>${s.strength_ratio}</strong> (${s.power_percentage}%)</td>
            <td>
                <span class="badge ${s.is_strong ? 'badge-exalted' : 'badge-debilitated'}">
                    ${s.is_strong ? 'Powerful (பலம் / உன்னதம்)' : 'Deficit (குறைவு / சுமாரானது)'}
                </span>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderYogasAndDoshas(yd) {
    const yogasGrid = document.getElementById("yogasGrid");
    const doshasGrid = document.getElementById("doshasGrid");
    if (!yd) return;

    if (yogasGrid) {
        yogasGrid.innerHTML = "";
        if (!yd.yogas || yd.yogas.length === 0) {
            yogasGrid.innerHTML = `<div style="color:var(--text-secondary);">No prominent Pancha Mahapurusha or classical Raja Yogas triggered.</div>`;
        } else {
            yd.yogas.forEach(y => {
                const card = document.createElement("div");
                card.className = "yoga-card";
                card.innerHTML = `
                    <div class="yoga-title">
                        <span>✨</span> ${y.name}
                    </div>
                    <div style="font-size:0.75rem; color:#34d399; font-weight:600; margin-bottom:6px;">
                        ${y.type}
                    </div>
                    <div class="yoga-desc">
                        ${y.description}
                    </div>
                `;
                yogasGrid.appendChild(card);
            });
        }
    }

    if (doshasGrid) {
        doshasGrid.innerHTML = "";
        if (!yd.doshas || yd.doshas.length === 0) {
            doshasGrid.innerHTML = `<div style="color:var(--text-secondary);">No doshas detected.</div>`;
        } else {
            yd.doshas.forEach(d => {
                const card = document.createElement("div");
                card.className = "yoga-card";
                card.style.borderColor = d.is_present ? "rgba(239, 68, 68, 0.5)" : "rgba(16, 185, 129, 0.4)";
                card.innerHTML = `
                    <div class="yoga-title" style="color:${d.is_present ? '#f87171' : '#34d399'};">
                        <span>${d.is_present ? '⚠️' : '✓'}</span> ${d.name}
                    </div>
                    <div style="font-size:0.8rem; font-weight:700; color:${d.is_present ? '#f87171' : '#34d399'}; margin-bottom:8px;">
                        ${d.status}
                    </div>
                    <div class="yoga-desc" style="white-space: pre-line;">
                        ${d.description}
                    </div>
                `;
                doshasGrid.appendChild(card);
            });
        }
    }
}

function openHouseModal(hNum, hData) {
    const modal = document.getElementById("houseModal");
    const content = document.getElementById("modalHouseContent");
    if (!modal || !content) return;

    // Get house significations from BHAVAS
    const bhava = (typeof BHAVAS !== 'undefined') ? BHAVAS.find(b => b.house === hNum) : null;
    const rasi = (typeof RASHIS !== 'undefined') ? RASHIS[hData.rasi_id] : null;

    let occupantsHtml = `<div style="color:var(--text-secondary); margin-top:6px;">No planets occupying this house.</div>`;
    if (hData.planets && hData.planets.length > 0) {
        occupantsHtml = `<div style="display:flex; flex-direction:column; gap:8px; margin-top:8px;">`;
        hData.planets.forEach(p => {
            occupantsHtml += `
                <div style="background:rgba(255,255,255,0.06); padding:8px 12px; border-radius:6px; display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:600; color:var(--gold-bright);">${p.label}</span>
                    <span style="font-size:0.85rem; color:var(--text-secondary);">${p.deg_dms}</span>
                </div>
            `;
        });
        occupantsHtml += `</div>`;
    }

    content.innerHTML = `
        <h2 style="font-family:var(--font-serif); color:var(--gold-bright); margin-bottom:6px;">
            House ${hNum} • ${bhava ? bhava.sanskrit : ''}
        </h2>
        <div style="font-size:0.95rem; font-weight:600; color:var(--gold-light); margin-bottom:12px;">
            Sign: ${rasi ? rasi.name : ''} ${rasi ? rasi.symbol : ''} (${rasi ? rasi.sanskrit : ''}) • Lord: ${rasi ? rasi.lord : ''}
        </div>
        <div style="font-size:0.88rem; color:var(--text-secondary); margin-bottom:12px; line-height:1.6;">
            <strong>Classification:</strong> ${bhava ? bhava.type : ''}<br>
            <strong>Primary Karaka:</strong> ${bhava ? bhava.karaka : ''}<br>
            <strong>Significations:</strong> ${bhava ? bhava.significations : ''}
        </div>
        <hr style="border:none; border-top:1px solid rgba(212,175,55,0.2); margin:12px 0;">
        <div style="font-weight:700; color:var(--gold-light); font-size:0.9rem;">
            Planetary Occupants in House ${hNum}:
        </div>
        ${occupantsHtml}
    `;

    modal.classList.add("open");
}

function closeHouseModal() {
    const modal = document.getElementById("houseModal");
    if (modal) modal.classList.remove("open");
}

function populateMilanSelects() {
    const boySelect = document.getElementById("milanBoyNak");
    const girlSelect = document.getElementById("milanGirlNak");
    if (!boySelect || !girlSelect || typeof NAKSHATRAS === 'undefined') return;

    boySelect.innerHTML = "";
    girlSelect.innerHTML = "";

    NAKSHATRAS.forEach(nak => {
        const tamilName = nak.tamil ? ` / ${nak.tamil}` : '';
        const lordName = nak.lord_tamil ? `${nak.lord} / ${nak.lord_tamil}` : nak.lord;
        const optB = document.createElement("option");
        optB.value = nak.id;
        optB.textContent = `${nak.id}. ${nak.name}${tamilName} (${lordName})`;
        if (nak.id === 4) optB.selected = true; // Rohini default
        boySelect.appendChild(optB);

        const optG = document.createElement("option");
        optG.value = nak.id;
        optG.textContent = `${nak.id}. ${nak.name}${tamilName} (${lordName})`;
        if (nak.id === 8) optG.selected = true; // Pushya default
        girlSelect.appendChild(optG);
    });
}

async function calculateMatching() {
    const boyNak = document.getElementById("milanBoyNak").value;
    const boyPada = document.getElementById("milanBoyPada").value;
    const girlNak = document.getElementById("milanGirlNak").value;
    const girlPada = document.getElementById("milanGirlPada").value;

    try {
        const res = await fetch("/api/match", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                boy_nakshatra: parseInt(boyNak),
                boy_pada: parseInt(boyPada),
                girl_nakshatra: parseInt(girlNak),
                girl_pada: parseInt(girlPada)
            })
        });

        const json = await res.json();
        if (!json.success) {
            alert("Match error: " + json.error);
            return;
        }

        const data = json.data;
        document.getElementById("milanScoreHero").style.display = "block";
        document.getElementById("milanTablesWrapper").style.display = "block";

        document.getElementById("milanTotalScore").textContent = `${data.ashtakoota_north.total_score} / 36`;
        document.getElementById("milanVerdict").textContent = `${data.ashtakoota_north.verdict} (${data.ashtakoota_north.percentage}%)`;

        // North Indian Table
        const nBody = document.getElementById("milanNorthTableBody");
        nBody.innerHTML = "";
        data.ashtakoota_north.kootas.forEach(k => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${k.name}</strong></td>
                <td style="font-weight:700; color:var(--gold-bright); text-align:center;">${k.score}</td>
                <td style="text-align:center;">${k.max}</td>
                <td style="color:var(--text-secondary); font-size:0.85rem;">${k.desc}</td>
            `;
            nBody.appendChild(tr);
        });

        // South Indian Table
        const sBody = document.getElementById("milanSouthTableBody");
        sBody.innerHTML = "";
        data.dasa_porutham_south.poruthams.forEach(p => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>${p.name}</strong></td>
                <td>
                    <span class="badge ${p.status ? 'badge-exalted' : 'badge-debilitated'}">
                        ${p.status ? '✓ Favorable (பொருத்தம் உண்டு)' : '✗ Incompatible (பொருத்தமில்லை)'}
                    </span>
                </td>
            `;
            sBody.appendChild(tr);
        });

    } catch (e) {
        console.error("Match error:", e);
    }
}

function loadPreset(key) {
    const presets = {
        now: () => {
            const now = new Date();
            const yyyy = now.getFullYear();
            const mm = String(now.getMonth() + 1).padStart(2, '0');
            const dd = String(now.getDate()).padStart(2, '0');
            const hh = String(now.getHours()).padStart(2, '0');
            const min = String(now.getMinutes()).padStart(2, '0');
            const ss = String(now.getSeconds()).padStart(2, '0');
            const tz = -now.getTimezoneOffset() / 60;
            return {
                name: "Sky Right Now / கோச்சார நிலை",
                date: `${yyyy}-${mm}-${dd}`,
                time: `${hh}:${min}:${ss}`,
                place: "Chennai, Tamil Nadu, India",
                lat: 13.0827,
                lon: 80.2707,
                tz: tz || 5.5
            };
        },
        vivekananda: () => ({
            name: "Swami Vivekananda",
            date: "1863-01-12",
            time: "06:33:00",
            place: "Kolkata, India",
            lat: 22.5726, lon: 88.3639, tz: 5.5
        }),
        einstein: () => ({
            name: "Albert Einstein",
            date: "1879-03-14",
            time: "11:30:00",
            place: "Ulm, Germany",
            lat: 48.4011, lon: 9.9876, tz: 1.0
        }),
        gandhi: () => ({
            name: "Mahatma Gandhi",
            date: "1869-10-02",
            time: "07:12:00",
            place: "Porbandar, India",
            lat: 21.6417, lon: 69.6293, tz: 5.5
        }),
        jobs: () => ({
            name: "Steve Jobs",
            date: "1955-02-24",
            time: "19:15:00",
            place: "San Francisco, USA",
            lat: 37.7749, lon: -122.4194, tz: -8.0
        }),
        kalam: () => ({
            name: "Dr. A.P.J. Abdul Kalam",
            date: "1931-10-15",
            time: "01:15:00",
            place: "Rameswaram, India",
            lat: 9.2876, lon: 79.3129, tz: 5.5
        })
    };

    const p = presets[key]?.();
    if (p) {
        document.getElementById("inputName").value = p.name;
        document.getElementById("inputDate").value = p.date;
        document.getElementById("inputTime").value = p.time;
        document.getElementById("inputPlace").value = p.place;
        document.getElementById("inputLat").value = p.lat;
        document.getElementById("inputLon").value = p.lon;
        document.getElementById("inputTz").value = p.tz;

        document.querySelectorAll(".preset-btn").forEach(btn => {
            const isThis = btn.getAttribute("onclick")?.includes(`'${key}'`);
            btn.classList.toggle("active", Boolean(isThis));
        });

        calculateHoroscope();
    }
}

// ==========================================================================
// Theme Switching (7 Sacred Vedic Color Themes / 7 வண்ண வடிவங்கள்)
// ==========================================================================
function switchTheme(themeName) {
    if (!themeName) return;
    document.body.setAttribute("data-theme", themeName);
    try {
        localStorage.setItem("vedic_horizon_theme", themeName);
    } catch (e) {}

    const select = document.getElementById("selectTheme");
    if (select && select.value !== themeName) {
        select.value = themeName;
    }

    document.querySelectorAll(".theme-chip").forEach(chip => {
        chip.classList.toggle("active", chip.getAttribute("data-theme-val") === themeName);
    });

    if (window.chartRenderer) {
        window.chartRenderer.render();
    }
    if (window.d9ChartRenderer) {
        window.d9ChartRenderer.render();
    }
    if (window.progChartRenderer) {
        window.progChartRenderer.render();
    }
    if (window.transitChartRenderer) {
        window.transitChartRenderer.render();
    }
    if (currentHoroscopeData && currentHoroscopeData.ashtakavarga) {
        renderAshtakavarga(currentHoroscopeData.ashtakavarga);
    }
    if (currentHoroscopeData && currentHoroscopeData.planets) {
        fetchLiveTransits(currentHoroscopeData.planets);
    }
}

function initTheme() {
    let saved = null;
    try {
        saved = localStorage.getItem("vedic_horizon_theme");
    } catch (e) {}
    const theme = saved || "pleasant-vedic";
    switchTheme(theme);
}

// ==========================================================================
// DASA PROGRESSION & TRANSITS (P.V.R. NARASIMHA RAO METHOD)
// ==========================================================================

async function fetchPvrPresets() {
    const container = document.getElementById("pvrPresetsContainer");
    if (!container) return;
    try {
        const res = await fetch("/api/progression/presets");
        const json = await res.json();
        if (json.success && json.presets) {
            pvrPresetsList = json.presets;
            renderPvrPresets();
        }
    } catch (e) {
        console.error("Failed to load PVR presets:", e);
    }
}

function renderPvrPresets() {
    const container = document.getElementById("pvrPresetsContainer");
    if (!container) return;
    container.innerHTML = "";

    const categoryIcons = {
        "Education": "🎓",
        "Travel": "✈️",
        "Children": "👶",
        "Marriage": "💍",
        "Accident": "🏇",
        "Career": "💼"
    };

    pvrPresetsList.forEach((preset, idx) => {
        const card = document.createElement("div");
        card.className = "pvr-preset-card";
        if (idx === 0) card.classList.add("active");

        let icon = "⭐";
        for (const [k, ic] of Object.entries(categoryIcons)) {
            if (preset.category.includes(k)) {
                icon = ic;
                break;
            }
        }

        card.innerHTML = `
            <div class="pvr-preset-header">
                <span class="pvr-preset-title">${icon} ${preset.title}</span>
                <span class="pvr-preset-badge">${preset.div_chart}</span>
            </div>
            <div class="pvr-preset-sub">${preset.tamil_title}</div>
            <div class="pvr-preset-highlight">
                ⚡ ${preset.highlight}
            </div>
        `;

        card.addEventListener("click", () => {
            document.querySelectorAll(".pvr-preset-card").forEach(c => c.classList.remove("active"));
            card.classList.add("active");
            loadPvrPreset(idx);
        });

        container.appendChild(card);
    });
}

function loadPvrPreset(idx) {
    const p = pvrPresetsList[idx];
    if (!p) return;

    // Fill form inputs
    const nameEl = document.getElementById("inputName");
    if (nameEl) nameEl.value = p.title.split(":")[1]?.trim() || p.title;

    const dateEl = document.getElementById("inputDate");
    if (dateEl) dateEl.value = p.birth_date;

    const timeEl = document.getElementById("inputTime");
    if (timeEl) timeEl.value = p.birth_time;

    const placeEl = document.getElementById("inputPlace");
    if (placeEl) placeEl.value = p.place;

    const latEl = document.getElementById("inputLat");
    if (latEl) latEl.value = p.lat;

    const lonEl = document.getElementById("inputLon");
    if (lonEl) lonEl.value = p.lon;

    const tzEl = document.getElementById("inputTz");
    if (tzEl) tzEl.value = p.tz;

    const tgtDateEl = document.getElementById("progTargetDate");
    if (tgtDateEl) tgtDateEl.value = p.target_date;

    const tgtTimeEl = document.getElementById("progTargetTime");
    if (tgtTimeEl) tgtTimeEl.value = p.target_time;

    const divChartEl = document.getElementById("progDivChart");
    if (divChartEl) divChartEl.value = p.div_chart;

    const methodEl = document.getElementById("progMethod");
    if (methodEl) methodEl.value = p.progression_type;

    const ayanamsaEl = document.getElementById("progAyanamsa");
    if (ayanamsaEl) ayanamsaEl.value = p.ayanamsa;

    // Execute progression computation
    calculateProgression();
}

function setProgChartStyle(style) {
    progCurrentStyle = style;
    document.getElementById("btnProgNorth")?.classList.toggle("active", style === "north");
    document.getElementById("btnProgSouth")?.classList.toggle("active", style === "south");
    if (progChartRenderer) progChartRenderer.setStyle(style);
    if (transitChartRenderer) transitChartRenderer.setStyle(style);
}

async function calculateProgression() {
    const btn = document.getElementById("btnRunProgression");
    const origText = btn ? btn.innerHTML : "";
    if (btn) {
        btn.innerHTML = `<span>⏳</span> Computing Progression & Transits...`;
        btn.disabled = true;
    }

    const payload = {
        birth_date: document.getElementById("inputDate").value,
        birth_time: document.getElementById("inputTime").value,
        latitude: parseFloat(document.getElementById("inputLat").value),
        longitude: parseFloat(document.getElementById("inputLon").value),
        timezone: parseFloat(document.getElementById("inputTz").value),
        target_date: document.getElementById("progTargetDate").value,
        target_time: document.getElementById("progTargetTime").value,
        progression_type: document.getElementById("progMethod").value,
        div_chart: document.getElementById("progDivChart").value,
        ayanamsa: document.getElementById("progAyanamsa").value
    };

    try {
        const res = await fetch("/api/progression", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            currentProgressionData = data;
            renderProgressionResults(data);
        } else {
            alert("Progression Calculation Error: " + data.error);
        }
    } catch (e) {
        console.error("Progression error:", e);
        alert("Failed to compute Dasa progression. See console for details.");
    } finally {
        if (btn) {
            btn.innerHTML = origText;
            btn.disabled = false;
        }
    }
}

function renderProgressionResults(data) {
    // 1. Reveal hidden sections
    const banner = document.getElementById("progSummaryBanner");
    const chartsSec = document.getElementById("progChartsSection");
    const actsSec = document.getElementById("progActivationsSection");
    const tblSec = document.getElementById("progTableSection");

    if (banner) banner.style.display = "block";
    if (chartsSec) chartsSec.style.display = "block";
    if (actsSec) actsSec.style.display = "block";
    if (tblSec) tblSec.style.display = "block";

    // 2. Progression Metrics Banner
    const pSum = data.progression_summary || {};
    const dInfo = pSum.active_dasha_info || {};
    const runningStr = dInfo.running_dasha || `${dInfo.maha_lord || ''} - ${dInfo.antar_lord || ''} - ${dInfo.prat_lord || ''}`;

    const rDashaEl = document.getElementById("metricRunningDasha");
    if (rDashaEl) rDashaEl.textContent = runningStr || "Active Dasa";

    const dSubEl = document.getElementById("metricDashaSub");
    if (dSubEl) dSubEl.textContent = dInfo.elapsed_years ? `Elapsed: ${dInfo.elapsed_years} solar years` : "Maha - Antar - Pratyantar";

    const pAngleEl = document.getElementById("metricProgAngle");
    if (pAngleEl) pAngleEl.textContent = pSum.progression_angle_dms || "--";

    const pAngleSubEl = document.getElementById("metricProgAngleSub");
    if (pAngleSubEl) pAngleSubEl.textContent = `${pSum.progression_angle_deg || 0}° non-linear chart rotation`;

    const moonEl = document.getElementById("metricMoonProg");
    if (moonEl && pSum.natal_moon_dms && pSum.progressed_moon_dms) {
        const nParts = pSum.natal_moon_dms.split(" ");
        const pParts = pSum.progressed_moon_dms.split(" ");
        moonEl.textContent = `${nParts[0]} ${nParts[1]} ➔ ${pParts[0]} ${pParts[1]}`;
    }

    const moonSubEl = document.getElementById("metricMoonProgSub");
    if (moonSubEl) moonSubEl.textContent = pSum.progressed_moon_dms || "";

    const divNameEl = document.getElementById("metricDivName");
    if (divNameEl) divNameEl.textContent = data.meta.divisional_chart_name || data.meta.divisional_chart;

    const divSignifEl = document.getElementById("metricDivSignif");
    if (divSignifEl) divSignifEl.textContent = data.meta.divisional_signification || "";

    // 3. Render Dual Charts
    const progHdrTitle = document.getElementById("progChartHeaderTitle");
    if (progHdrTitle) progHdrTitle.textContent = `Progressed ${data.meta.divisional_chart} Chart (சுழற்சி சக்கரம்)`;

    const progHdrSub = document.getElementById("progChartHeaderSub");
    if (progHdrSub) progHdrSub.textContent = `Rotated by Δλ = ${pSum.progression_angle_dms} (${data.meta.divisional_chart_name})`;

    const progBadge = document.getElementById("progChartBadge");
    if (progBadge) progBadge.textContent = `Progressed ${data.meta.divisional_chart}`;

    const transHdrSub = document.getElementById("transitChartHeaderSub");
    if (transHdrSub) transHdrSub.textContent = `Event Transits at ${data.meta.target_date} ${data.meta.target_time} (${data.meta.ayanamsa})`;

    if (progChartRenderer && data.progressed_chart_render) {
        progChartRenderer.setStyle(progCurrentStyle);
        progChartRenderer.setChartData(data.progressed_chart_render);
    }
    if (transitChartRenderer && data.transit_chart_render) {
        transitChartRenderer.setStyle(progCurrentStyle);
        transitChartRenderer.setChartData(data.transit_chart_render);
    }

    // 4. Render Activations List
    const actList = document.getElementById("activationsList");
    const countBadge = document.getElementById("activationsCountBadge");
    if (countBadge) {
        countBadge.textContent = `${data.activations_count} Activations Found / ${data.activations_count} தூண்டுதல்கள்`;
        countBadge.style.background = data.activations_count > 0 ? "rgba(16, 185, 129, 0.2)" : "rgba(100, 116, 139, 0.2)";
        countBadge.style.color = data.activations_count > 0 ? "#6ee7b7" : "var(--text-muted)";
        countBadge.style.borderColor = data.activations_count > 0 ? "#10b981" : "rgba(100, 116, 139, 0.4)";
    }

    if (actList) {
        actList.innerHTML = "";
        if (!data.activations || data.activations.length === 0) {
            actList.innerHTML = `
                <div style="grid-column: 1 / -1; padding: 24px; text-align: center; color: var(--text-muted); background: var(--bg-input); border-radius: var(--radius-md);">
                    No close transit aspects (< 5.5°) detected on this target date. Try adjusting the target date or divisional chart.
                </div>
            `;
        } else {
            data.activations.forEach((act) => {
                const card = document.createElement("div");
                card.className = `activation-card ${act.is_tight ? 'tight-orb' : 'medium-orb'}`;

                const orbBadgeClass = act.is_tight ? "orb-tight" : "orb-normal";
                const orbBadgeText = act.is_tight ? `🔥 Tight Orb: ${act.orb_dms}` : `⚡ Orb: ${act.orb_dms}`;

                const tIcon = PLANET_SVG[act.transit_planet] || "🪐";
                const pIcon = PLANET_SVG[act.target_planet] || "⭐";

                card.innerHTML = `
                    <div class="activation-card-top">
                        <div class="activation-planets">
                            <span style="display:inline-flex; align-items:center; gap:4px; color:#6ee7b7;">
                                ${tIcon} Transit ${act.transit_planet}
                            </span>
                            <span class="activation-arrow">➔</span>
                            <span style="display:inline-flex; align-items:center; gap:4px; color:var(--gold-bright);">
                                ${pIcon} ${act.target_planet}
                            </span>
                        </div>
                        <span class="activation-orb-badge ${orbBadgeClass}">
                            ${orbBadgeText}
                        </span>
                    </div>

                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap;">
                        <span class="activation-aspect">
                            ${act.aspect_type}
                        </span>
                        <span style="font-size: 0.74rem; color: var(--text-muted);">
                            ${act.target_context}
                        </span>
                    </div>

                    <div class="activation-event">
                        <span>🎯</span> ${act.event_indicator}
                    </div>

                    <div class="activation-explanation">
                        ${act.explanation}
                    </div>

                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); border-top: 1px solid rgba(255,255,255,0.06); padding-top: 8px; margin-top: 2px;">
                        <span>Transit: <strong style="color:var(--text-primary);">${act.transit_lon_dms}</strong></span>
                        <span>Progressed: <strong style="color:var(--gold-light);">${act.progressed_lon_dms}</strong></span>
                    </div>
                `;
                actList.appendChild(card);
            });
        }
    }

    // 5. Render Comparison Table
    const tableBody = document.getElementById("progComparisonTableBody");
    if (tableBody) {
        tableBody.innerHTML = "";
        const natalMap = {};
        (data.natal_planets || []).forEach(p => { natalMap[p.name] = p; });
        const transitMap = {};
        (data.transit_planets || []).forEach(p => { transitMap[p.name] = p; });

        (data.progressed_planets || []).forEach(progP => {
            const pName = progP.name;
            const natalP = natalMap[pName] || {};
            const trP = transitMap[pName] || {};

            const tr = document.createElement("tr");
            const iconSvg = PLANET_SVG[pName] || "";

            tr.innerHTML = `
                <td>
                    <div class="planet-cell">
                        ${iconSvg ? `<span class="planet-glyph">${iconSvg}</span>` : ""}
                        <div>
                            <div class="planet-name">${progP.name_dual || pName}</div>
                            <div class="planet-tamil">${progP.tamil || ""}</div>
                        </div>
                    </div>
                </td>
                <td>
                    <div style="font-weight: 600; color: var(--text-primary);">${natalP.sign_dms || natalP.longitude_dms || '--'}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">${natalP.longitude ? natalP.longitude.toFixed(2) + '°' : ''}</div>
                </td>
                <td>
                    <div style="font-weight: 700; color: var(--gold-bright);">${progP.sign_dms || progP.longitude_dms || '--'}</div>
                    <div style="font-size: 0.75rem; color: var(--gold-light);">${progP.longitude ? progP.longitude.toFixed(2) + '°' : ''}</div>
                </td>
                <td>
                    <div style="font-weight: 600; color: #6ee7b7;">${trP.sign_dms || trP.longitude_dms || '--'}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">${trP.longitude ? trP.longitude.toFixed(2) + '°' : ''}</div>
                </td>
                <td>
                    <span class="badge" style="background: rgba(212, 175, 55, 0.15); color: var(--gold-light); border: 1px solid rgba(212, 175, 55, 0.3);">
                        +${pSum.progression_angle_dms || ''}
                    </span>
                </td>
                <td>
                    <div style="font-weight: 600;">${progP.rasi_name} (${progP.rasi_symbol})</div>
                    <div style="font-size: 0.76rem; color: var(--text-secondary);">${progP.rasi_tamil}</div>
                </td>
            `;
            tableBody.appendChild(tr);
        });
    }
}


/**
 * Renders Mani Kanda Kerala Jothidam Yogas, 12 Bhavas, and Longevity / Dosha Shield
 */
function renderKeralaJothidam(kd) {
    if (!kd) return;

    // 1. Render Kerala Yogas
    const yogasGrid = document.getElementById("keralaYogasGrid");
    if (yogasGrid) {
        yogasGrid.innerHTML = "";
        const yogas = kd.kerala_yogas || [];
        if (yogas.length === 0) {
            yogasGrid.innerHTML = `<div style="color:var(--text-secondary); padding: 16px; font-size: 1rem;">No primary Agastya Kerala royal yogas triggered for this planetary alignment.</div>`;
        } else {
            yogas.forEach(y => {
                const card = document.createElement("div");
                card.className = "yoga-card";
                card.style.border = "1.5px solid var(--border-gold)";
                card.style.borderLeft = "6px solid var(--gold-primary)";
                card.style.background = "var(--bg-card)";
                card.style.padding = "20px";
                card.style.boxShadow = "var(--shadow-card)";
                card.innerHTML = `
                    <div class="yoga-title" style="color:var(--gold-bright); font-size:1.2rem; font-weight:800; font-family:var(--font-serif); margin-bottom:6px;">
                        <span>✨</span> ${y.name}
                    </div>
                    <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:10px;">
                        <span style="font-size:0.82rem; background:#ecfdf5; color:#047857; border:1px solid #a7f3d0; padding:2px 10px; border-radius:12px; font-weight:700;">
                            ${y.category}
                        </span>
                        <span style="font-size:0.88rem; color:#0284c7; font-weight:700;">
                            ${y.tamil_name}
                        </span>
                    </div>
                    <div class="yoga-desc" style="color:var(--text-primary); font-size:0.96rem; line-height:1.65; font-weight:500;">
                        ${y.description}
                    </div>
                `;
                yogasGrid.appendChild(card);
            });
        }
    }

    // 2. Render Longevity & Dosha Shield
    const longevBox = document.getElementById("keralaLongevityBox");
    if (longevBox && kd.longevity_and_dosha) {
        const ld = kd.longevity_and_dosha;
        let protectiveHtml = "";
        if (ld.dosha_nivarthi && ld.dosha_nivarthi.length > 0) {
            protectiveHtml = ld.dosha_nivarthi.map(p => `
                <li style="margin-bottom:8px; font-size:0.94rem; color:var(--text-primary); line-height:1.6; font-weight:500;">
                    ${p}
                </li>
            `).join("");
        }

        longevBox.style.background = "var(--bg-card)";
        longevBox.style.border = "1.5px solid var(--border-gold)";
        longevBox.style.borderRadius = "var(--radius-md)";
        longevBox.style.padding = "24px";
        longevBox.style.boxShadow = "var(--shadow-card)";

        longevBox.innerHTML = `
            <div style="display: flex; flex-wrap: wrap; gap: 20px; align-items: center; justify-content: space-between; border-bottom: 1.5px solid var(--border-gold); padding-bottom: 18px; margin-bottom: 20px;">
                <div>
                    <div style="font-size: 0.85rem; text-transform: uppercase; font-weight: 800; letter-spacing: 0.06em; color: var(--gold-bright);">
                        Classical Longevity Assessment / ஆயுள் பலம் (மணிகண்ட கேரளம் அத்தியாயம் 44)
                    </div>
                    <div style="font-size: 1.35rem; font-weight: 800; color: #047857; margin-top: 6px;">
                        ${ld.longevity_classification}
                    </div>
                    <div style="font-size: 0.95rem; font-weight: 700; color: #7c2d12; margin-top: 6px; line-height: 1.5;">
                        ${ld.longevity_tamil}
                    </div>
                </div>
                <div style="background: rgba(2, 132, 199, 0.08); border: 1.5px solid rgba(2, 132, 199, 0.3); border-radius: 8px; padding: 12px 20px; text-align: right;">
                    <div style="font-size: 0.8rem; color: #0284c7; font-weight: 800; text-transform: uppercase;">Lagna Nature</div>
                    <div style="font-size: 1.05rem; font-weight: 800; color: var(--text-primary);">${ld.lagna_mobility}</div>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; margin-bottom: 20px;">
                <div style="background: rgba(220, 38, 38, 0.06); border: 1.5px solid rgba(220, 38, 38, 0.25); border-radius: 8px; padding: 16px 18px;">
                    <div style="font-size: 0.92rem; color: #b91c1c; font-weight: 800; margin-bottom: 6px;">
                        ⚠️ Badhaka Sthanam (பாதக ஸ்தானம் & அதிபதி)
                    </div>
                    <div style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 6px; font-weight: 600;">
                        ${ld.badhaka_rule}
                    </div>
                    <div style="font-size: 1rem; font-weight: 800; color: #7f1d1d;">
                        ${ld.badhaka_sign} (${ld.badhaka_sign_tamil}) • ${ld.badhaka_lord}
                    </div>
                </div>

                <div style="background: rgba(217, 119, 6, 0.06); border: 1.5px solid rgba(217, 119, 6, 0.25); border-radius: 8px; padding: 16px 18px;">
                    <div style="font-size: 0.92rem; color: #b45309; font-weight: 800; margin-bottom: 6px;">
                        ⚔️ Maraka Lords (மாரகாதிபதிகள் - 2 & 7 வீடுகள்)
                    </div>
                    <div style="font-size: 0.98rem; font-weight: 800; color: #78350f; margin-top: 8px;">
                        ${ld.maraka_lords.join(" • ")}
                    </div>
                </div>
            </div>

            <div style="background: rgba(5, 150, 105, 0.08); border-left: 5px solid #059669; border-radius: 8px; padding: 16px 20px;">
                <div style="font-size: 0.98rem; font-weight: 800; color: #065f46; margin-bottom: 10px;">
                    🛡️ Protective Shield & Dosha Nivarthi (தோஷ நிவர்த்தி & இறை பாதுகாப்பு):
                </div>
                <ul style="margin: 0; padding-left: 22px;">
                    ${protectiveHtml}
                </ul>
            </div>
        `;
    }

    // 3. Render 12 Bhavas
    const bhavasGrid = document.getElementById("keralaBhavasGrid");
    if (bhavasGrid) {
        bhavasGrid.innerHTML = "";
        const bhavas = kd.bhava_predictions || [];
        bhavas.forEach(b => {
            const card = document.createElement("div");
            card.style.cssText = `
                background: var(--bg-card);
                border: 1.5px solid var(--border-gold);
                border-radius: var(--radius-md);
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 14px;
                box-shadow: var(--shadow-card);
                transition: var(--transition);
            `;
            
            const occupantsText = (b.occupants && b.occupants.length > 0)
                ? b.occupants.join(", ")
                : "None (கிரகங்கள் இல்லை)";

            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1.5px solid var(--border-gold); padding-bottom: 12px;">
                    <div>
                        <div style="font-weight: 800; font-size: 1.12rem; color: var(--gold-bright); font-family: var(--font-serif);">
                            ${b.house_number}. ${b.bhava_name}
                        </div>
                        <div style="font-size: 0.94rem; color: #0284c7; font-weight: 700; margin-top: 2px;">
                            ${b.bhava_tamil}
                        </div>
                    </div>
                    <span style="font-size: 0.78rem; background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; padding: 3px 10px; border-radius: 12px; font-weight: 800; white-space: nowrap;">
                        ${b.chapter}
                    </span>
                </div>

                <div style="font-size: 0.88rem; display: flex; flex-wrap: wrap; gap: 10px; background: var(--card-sub-bg, #fdfbf7); border: 1px solid var(--border-gold); padding: 10px 14px; border-radius: 6px; color: var(--text-primary); font-weight: 500;">
                    <div><span style="color: var(--text-secondary); font-weight: 600;">Sign:</span> <strong>${b.sign_name} (${b.sign_tamil})</strong></div>
                    <div style="color: var(--border-gold);">|</div>
                    <div><span style="color: var(--text-secondary); font-weight: 600;">Lord:</span> <strong>${b.lord_name} (${b.lord_tamil})</strong> in <strong>H-${b.lord_placed_house}</strong> (${b.lord_dignity})</div>
                    <div style="color: var(--border-gold);">|</div>
                    <div><span style="color: var(--text-secondary); font-weight: 600;">Occupants:</span> <strong>${occupantsText}</strong></div>
                </div>

                <div style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.55; font-style: italic;">
                    ${b.significations}
                </div>

                <div style="background: rgba(217, 119, 6, 0.08); border-left: 4.5px solid #b45309; border-radius: 6px; padding: 14px 16px; margin-top: auto;">
                    <div style="font-size: 0.98rem; font-weight: 700; color: #7c2d12; line-height: 1.65; margin-bottom: 6px;">
                        📜 ${b.prediction.tamil}
                    </div>
                    <div style="font-size: 0.88rem; color: var(--text-secondary); line-height: 1.5; font-weight: 500;">
                        ${b.prediction.english}
                    </div>
                </div>
            `;
            bhavasGrid.appendChild(card);
        });
    }
}

/* ==========================================================================
   JAMAKKOL ARUDAM (ஜாமக்கோள் ஆருடம்) CONTROLLER & RENDERER
   ========================================================================== */

let currentJamakkolData = null;

function initJamakkolControls() {
    const now = new Date();
    const dateInput = document.getElementById("jamakkolDate");
    const timeInput = document.getElementById("jamakkolTime");
    const placeInput = document.getElementById("jamakkolPlace");

    if (dateInput && !dateInput.value) {
        const yyyy = now.getFullYear();
        const mm = String(now.getMonth() + 1).padStart(2, "0");
        const dd = String(now.getDate()).padStart(2, "0");
        dateInput.value = `${yyyy}-${mm}-${dd}`;
    }
    if (timeInput && !timeInput.value) {
        const hh = String(now.getHours()).padStart(2, "0");
        const min = String(now.getMinutes()).padStart(2, "0");
        const ss = String(now.getSeconds()).padStart(2, "0");
        timeInput.value = `${hh}:${min}:${ss}`;
    }
    if (placeInput && (!placeInput.value || placeInput.value === "Chennai, India") && currentHoroscopeData?.meta?.name) {
        placeInput.value = currentHoroscopeData.meta.name;
    }
}

function loadJamakkolNow() {
    const now = new Date();
    const dateInput = document.getElementById("jamakkolDate");
    const timeInput = document.getElementById("jamakkolTime");
    const selectArudam = document.getElementById("jamakkolArudamSelect");

    if (dateInput) {
        const yyyy = now.getFullYear();
        const mm = String(now.getMonth() + 1).padStart(2, "0");
        const dd = String(now.getDate()).padStart(2, "0");
        dateInput.value = `${yyyy}-${mm}-${dd}`;
    }
    if (timeInput) {
        const hh = String(now.getHours()).padStart(2, "0");
        const min = String(now.getMinutes()).padStart(2, "0");
        const ss = String(now.getSeconds()).padStart(2, "0");
        timeInput.value = `${hh}:${min}:${ss}`;
    }
    if (selectArudam) {
        selectArudam.value = "auto";
    }

    recalculateJamakkol();
}

function onJamakkolArudamChange(val) {
    recalculateJamakkol();
}

function setJamakkolArudam(signIdx) {
    const select = document.getElementById("jamakkolArudamSelect");
    if (select) {
        select.value = String(signIdx);
        recalculateJamakkol();
    }
}

async function recalculateJamakkol() {
    initJamakkolControls();
    const dateVal = document.getElementById("jamakkolDate")?.value;
    const timeVal = document.getElementById("jamakkolTime")?.value;
    const placeVal = document.getElementById("jamakkolPlace")?.value || "Chennai, India";
    const arudamVal = document.getElementById("jamakkolArudamSelect")?.value;

    let lat = 13.0827;
    let lon = 80.2707;
    let tz = 5.5;

    if (currentHoroscopeData?.meta) {
        lat = currentHoroscopeData.meta.latitude || lat;
        lon = currentHoroscopeData.meta.longitude || lon;
        tz = currentHoroscopeData.meta.timezone || tz;
    }

    const payload = {
        date: dateVal,
        time: timeVal,
        place: placeVal,
        lat: lat,
        lon: lon,
        tz: tz,
        arudam_sign: arudamVal === "auto" ? null : parseInt(arudamVal, 10)
    };

    try {
        const res = await fetch("/api/jamakkol", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (json.status === "success") {
            currentJamakkolData = json;
            renderJamakkol(json);
        } else {
            console.error("Jamakkol calculation error:", json.message);
        }
    } catch (err) {
        console.error("Failed to fetch /api/jamakkol:", err);
    }
}

function renderJamakkol(data) {
    if (!data || !data.pillars) return;

    // Sync input controls if present
    if (data.query_metadata) {
        const dInput = document.getElementById("jamakkolDate");
        const tInput = document.getElementById("jamakkolTime");
        const pInput = document.getElementById("jamakkolPlace");
        if (dInput && data.query_metadata.date) dInput.value = data.query_metadata.date;
        if (tInput && data.query_metadata.time) tInput.value = data.query_metadata.time;
        if (pInput && data.query_metadata.place) pInput.value = data.query_metadata.place;
    }

    const p = data.pillars;
    const j = data.jaamam_info;
    const pred = data.predictions;

    // 1. RENDER THE 4 PILLARS CARDS
    const pillarsGrid = document.getElementById("jamakkolPillarsGrid");
    if (pillarsGrid) {
        pillarsGrid.innerHTML = `
            <!-- Pillar 1: Udhayam -->
            <div class="jamakkol-pillar-card" style="border-left: 5px solid #f59e0b;">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <span style="font-size:0.8rem; background:#fef3c7; color:#92400e; font-weight:800; padding:2px 8px; border-radius:12px;">1. UDHAYAM / உதயம்</span>
                        <span style="font-size:0.8rem; color:#f59e0b; font-weight:700;">★ Querent / ஜாதகர்</span>
                    </div>
                    <div style="font-size:1.35rem; font-weight:800; color:var(--text-primary); font-family:var(--font-serif);">
                        ${p.udhayam.sign_name_ta} <span style="font-size:1.05rem; font-weight:600; color:var(--text-secondary);">(${p.udhayam.sign_name_en})</span>
                    </div>
                    <div style="font-size:0.88rem; color:#b45309; font-weight:700; margin-top:2px;">
                        ${p.udhayam.deg_dms} • ${p.udhayam.nakshatra} (Pada ${p.udhayam.pada})
                    </div>
                </div>
                <div style="margin-top:12px; font-size:0.82rem; background:rgba(0,0,0,0.03); padding:8px 10px; border-radius:6px; line-height:1.5;">
                    <div><strong>Lord / அதிபதி:</strong> ${p.udhayam.lord_ta} (${p.udhayam.lord_en})</div>
                    <div><strong>Nature / குணம்:</strong> ${p.udhayam.quality.ta} • ${p.udhayam.dmj.ta}</div>
                    <div><strong>Direction / திசை:</strong> ${p.udhayam.direction.ta} (${p.udhayam.direction.en})</div>
                </div>
                <div style="margin-top:8px; font-size:0.82rem; color:var(--text-secondary); line-height:1.45; font-style:italic;">
                    ${p.udhayam.description_ta}
                </div>
            </div>

            <!-- Pillar 2: Arudam -->
            <div class="jamakkol-pillar-card" style="border-left: 5px solid #10b981;">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <span style="font-size:0.8rem; background:#ecfdf5; color:#047857; font-weight:800; padding:2px 8px; border-radius:12px;">2. ARUDAM / ஆருடம்</span>
                        <span style="font-size:0.8rem; color:#10b981; font-weight:700;">★ Question / காரியம்</span>
                    </div>
                    <div style="font-size:1.35rem; font-weight:800; color:var(--text-primary); font-family:var(--font-serif);">
                        ${p.arudam.sign_name_ta} <span style="font-size:1.05rem; font-weight:600; color:var(--text-secondary);">(${p.arudam.sign_name_en})</span>
                    </div>
                    <div style="font-size:0.88rem; color:#047857; font-weight:700; margin-top:2px;">
                        House ${p.arudam.bhava_from_udhayam} from Udhayam (உதயத்திற்கு ${p.arudam.bhava_from_udhayam}ம் பாவம்)
                    </div>
                </div>
                <div style="margin-top:12px; font-size:0.82rem; background:rgba(0,0,0,0.03); padding:8px 10px; border-radius:6px; line-height:1.5;">
                    <div><strong>Lord / அதிபதி:</strong> ${p.arudam.lord_ta} (${p.arudam.lord_en})</div>
                    <div><strong>Nature / குணம்:</strong> ${p.arudam.quality.ta} • ${p.arudam.dmj.ta}</div>
                    <div><strong>Direction / திசை:</strong> ${p.arudam.direction.ta} (${p.arudam.direction.en})</div>
                </div>
                <div style="margin-top:8px; font-size:0.82rem; color:var(--text-secondary); line-height:1.45; font-style:italic;">
                    ${p.arudam.description_ta}
                </div>
            </div>

            <!-- Pillar 3: Surya Veedhi -->
            <div class="jamakkol-pillar-card" style="border-left: 5px solid #6366f1;">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <span style="font-size:0.8rem; background:#eef2ff; color:#3730a3; font-weight:800; padding:2px 8px; border-radius:12px;">3. SURYA VEEDHI / சூரிய வீதி</span>
                        <span style="font-size:0.8rem; color:#6366f1; font-weight:700;">★ Solar Axis / சூரிய மார்க்கம்</span>
                    </div>
                    <div style="font-size:1.35rem; font-weight:800; color:var(--text-primary); font-family:var(--font-serif);">
                        ${p.surya_veedhi.veedhi_sign_name_ta} வீதி <span style="font-size:1.05rem; font-weight:600; color:var(--text-secondary);">(${p.surya_veedhi.veedhi_sign_name_en})</span>
                    </div>
                    <div style="font-size:0.88rem; color:#4338ca; font-weight:700; margin-top:2px;">
                        Sun in ${p.surya_veedhi.sun_sign_name_ta} (${p.surya_veedhi.sun_sign_name_en})
                    </div>
                </div>
                <div style="margin-top:12px; font-size:0.82rem; background:rgba(0,0,0,0.03); padding:8px 10px; border-radius:6px; line-height:1.5;">
                    <div><strong>Axis / மார்க்கம்:</strong> ${p.surya_veedhi.name_ta}</div>
                    <div><strong>Rule / விதி:</strong> 4 மாதங்களுக்கு ஒரு வீதி வீதம் ஆண்டுக்கு 3 வீதிகள்</div>
                    <div><strong>Sunrise / உதயம்:</strong> ${data.query_metadata?.sunrise || "--"} • <strong>Sunset / அஸ்தமனம்:</strong> ${data.query_metadata?.sunset || "--"}</div>
                </div>
                <div style="margin-top:8px; font-size:0.82rem; color:var(--text-secondary); line-height:1.45; font-style:italic;">
                    சூரிய சஞ்சாரப் பாதையின்படி கவிப்பு கணக்கீட்டிற்கான மூல அச்சாகும்.
                </div>
            </div>

            <!-- Pillar 4: Kavippu -->
            <div class="jamakkol-pillar-card" style="border-left: 5px solid #ef4444;">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                        <span style="font-size:0.8rem; background:#fef2f2; color:#991b1b; font-weight:800; padding:2px 8px; border-radius:12px;">4. KAVIPPU / கவிப்பு</span>
                        <span style="font-size:0.8rem; color:#ef4444; font-weight:700;">★ Obstruction / மறைவுத் தடை</span>
                    </div>
                    <div style="font-size:1.35rem; font-weight:800; color:var(--text-primary); font-family:var(--font-serif);">
                        ${p.kavippu.sign_name_ta} <span style="font-size:1.05rem; font-weight:600; color:var(--text-secondary);">(${p.kavippu.sign_name_en})</span>
                    </div>
                    <div style="font-size:0.88rem; color:#b91c1c; font-weight:700; margin-top:2px;">
                        H-${p.kavippu.bhava_from_udhayam} from Udhayam • H-${p.kavippu.bhava_from_arudam} from Arudam
                    </div>
                </div>
                <div style="margin-top:12px; font-size:0.82rem; background:rgba(0,0,0,0.03); padding:8px 10px; border-radius:6px; line-height:1.5;">
                    <div><strong>Formula / சூத்திரம்:</strong> (உதயம் + சூரிய வீதி - ஆருடம்) mod 12</div>
                    <div><strong>Lord / அதிபதி:</strong> ${p.kavippu.lord_ta} (${p.kavippu.lord_en})</div>
                    <div><strong>Nature / குணம்:</strong> ${p.kavippu.quality.ta} • ${p.kavippu.dmj.ta}</div>
                </div>
                <div style="margin-top:8px; font-size:0.82rem; color:var(--text-secondary); line-height:1.45; font-style:italic;">
                    ${p.kavippu.description_ta}
                </div>
            </div>
        `;
    }

    // 2. RENDER 8 JAAMAMS TIMELINE BAR
    const timelineBar = document.getElementById("jaamamTimelineBar");
    const activeBadge = document.getElementById("jaamamActiveBadge");
    const timeRangeText = document.getElementById("jaamamTimeRangeText");

    if (activeBadge) {
        const periodText = j.is_night ? "Night / இரவுப் பொழுது" : "Day / பகல் பொழுது";
        activeBadge.innerHTML = `
            <span class="live-blink-dot" style="margin-right:6px;"></span>
            ${periodText} • Active Jaamam ${j.active_jaamam_number} (${j.active_jaamam_lord?.lord_name_ta})
        `;
    }
    if (timeRangeText) {
        timeRangeText.innerHTML = `
            ${j.active_weekday_name_ta} (${j.active_weekday_name_en}) • Jaamam Duration: <strong>${j.jaamam_duration_minutes} mins</strong> (3.75 Nazhigai)
        `;
    }

    if (timelineBar && j.all_jaamams) {
        timelineBar.innerHTML = "";
        j.all_jaamams.forEach(item => {
            const card = document.createElement("div");
            card.className = `jaamam-step-card ${item.is_active ? "active-jaamam" : ""}`;
            card.innerHTML = `
                <div class="jaamam-number" style="font-size:0.78rem; font-weight:700; color:var(--text-secondary);">
                    Jaamam ${item.jaamam_number} ${item.is_active ? "★ ACTIVE" : ""}
                </div>
                <div style="font-size:0.96rem; font-weight:800; color:var(--gold-bright); margin:4px 0;">
                    ${item.lord_short_ta}
                </div>
                <div style="font-size:0.75rem; color:var(--text-secondary); white-space:nowrap;">
                    ${item.start_time} - ${item.end_time}
                </div>
            `;
            timelineBar.appendChild(card);
        });
    }

    // 3. RENDER SOUTH INDIAN DUAL-RING MANDALA
    const chakraGrid = document.getElementById("jamakkolChakraGrid");
    if (chakraGrid && data.signs_grid) {
        chakraGrid.innerHTML = "";

        // South Indian 4x4 coordinate placement map:
        // Row 1: Meena (11), Mesha (0), Rishaba (1), Mithuna (2)
        // Row 2: Kumbha (10), Center, Kataka (3)
        // Row 3: Makara (9), Center, Simha (4)
        // Row 4: Dhanus (8), Vrischika (7), Thula (6), Kanni (5)
        const cellOrder = [
            11, 0, 1, 2,
            10, -1, -1, 3,
            9, -1, -1, 4,
            8, 7, 6, 5
        ];

        let centerAppended = false;

        cellOrder.forEach(signIdx => {
            if (signIdx === -1) {
                if (!centerAppended) {
                    centerAppended = true;
                    const centerBox = document.createElement("div");
                    centerBox.className = "jamakkol-center-box";
                    centerBox.innerHTML = `
                        <div style="font-weight:900; color:var(--gold-bright); font-size:1.15rem; font-family:var(--font-serif);">
                            சாமுக்கோள் ஆருடம்
                        </div>
                        <div style="font-size:0.85rem; color:#b45309; font-weight:700; margin-top:2px;">
                            ${j.active_weekday_name_ta} • சாமம் ${j.active_jaamam_number}
                        </div>
                        <div style="font-size:0.8rem; color:var(--text-secondary); margin-top:4px;">
                            Lord: <strong>${j.active_jaamam_lord?.lord_name_ta}</strong>
                        </div>
                        <div style="font-size:0.78rem; color:var(--text-secondary); margin-top:2px;">
                            ${data.query_metadata?.time || ""} • ${data.query_metadata?.place || ""}
                        </div>
                        <div style="margin-top:8px;">
                            <span class="badge" style="background:#047857; color:#fff; font-size:0.78rem; padding:4px 8px; border-radius:12px;">
                                ${pred.kariya_siddhi_score}% • ${pred.kariya_siddhi_verdict_ta.split(' ')[0]}
                            </span>
                        </div>
                    `;
                    chakraGrid.appendChild(centerBox);
                }
                return;
            }

            const signData = data.signs_grid[signIdx];
            if (!signData) return;

            const isUdhayam = (signIdx === p.udhayam.sign_idx);
            const isArudam = (signIdx === p.arudam.sign_idx);
            const isKavippu = (signIdx === p.kavippu.sign_idx);
            const isSuryaVeedhi = (signIdx === p.surya_veedhi.veedhi_sign);

            let extraClasses = "";
            if (isUdhayam) extraClasses += " cell-udhayam";
            if (isArudam) extraClasses += " cell-arudam";
            if (isKavippu) extraClasses += " cell-kavippu";
            if (isSuryaVeedhi) extraClasses += " cell-surya-veedhi";

            const cell = document.createElement("div");
            cell.className = `jamakkol-cell ${extraClasses}`;
            cell.title = `Click to set Arudam to ${signData.sign_name_ta} (${signData.sign_name_en})`;
            cell.onclick = () => setJamakkolArudam(signIdx);

            // Outer zone (Jama Grahas)
            let outerHtml = "";
            if (signData.is_fixed_sign) {
                outerHtml = `<span style="font-size:0.68rem; color:var(--text-secondary); opacity:0.6;">✕ ஸ்திரம்</span>`;
            } else if (signData.jama_planets && signData.jama_planets.length > 0) {
                outerHtml = signData.jama_planets.map(jg => `
                    <span class="jama-graha-badge" title="Jama Graha: ${jg.name_en}">
                        ☸ ${jg.short_ta}
                    </span>
                `).join(" ");
            }

            // Inner zone (Transit Grahas)
            let innerHtml = "";
            if (signData.inner_planets && signData.inner_planets.length > 0) {
                innerHtml = signData.inner_planets.map(ip => `
                    <span class="transit-graha-pill" title="${ip.name_en} ${ip.deg_in_sign_dms}">
                        ${ip.name_ta} ${ip.deg_in_sign_dms.split(':')[0]}°
                    </span>
                `).join(" ");
            }

            // Key badges
            let badgesHtml = "";
            if (isUdhayam) badgesHtml += `<strong style="color:#f59e0b; font-size:0.75rem;">[உத]</strong> `;
            if (isArudam) badgesHtml += `<strong style="color:#10b981; font-size:0.75rem;">[ஆரு]</strong> `;
            if (isKavippu) badgesHtml += `<strong style="color:#ef4444; font-size:0.75rem;">[கவி]</strong> `;
            if (isSuryaVeedhi) badgesHtml += `<strong style="color:#6366f1; font-size:0.75rem;">[சூ.வீ]</strong> `;

            cell.innerHTML = `
                <!-- Outer Ring Zone: Jama Graha -->
                <div style="display:flex; justify-content:space-between; align-items:center; min-height:18px;">
                    <div>${outerHtml}</div>
                    <div style="font-size:0.72rem; color:var(--text-secondary); font-weight:700;">${signIdx + 1}</div>
                </div>

                <!-- Sign Label -->
                <div style="text-align:center; margin:4px 0;">
                    <div style="font-weight:800; font-size:0.86rem; color:var(--text-primary);">
                        ${signData.sign_name_ta}
                    </div>
                    <div style="font-size:0.72rem; color:var(--text-secondary);">
                        ${signData.sign_name_en}
                    </div>
                </div>

                <!-- Inner Ring Zone: Transit Grahas & Markers -->
                <div style="min-height:22px; display:flex; flex-direction:column; gap:2px;">
                    <div style="display:flex; flex-wrap:wrap; gap:3px;">
                        ${innerHtml}
                    </div>
                    <div style="text-align:right;">
                        ${badgesHtml}
                    </div>
                </div>
            `;

            chakraGrid.appendChild(cell);
        });
    }

    // 4. RENDER KARIYA SIDDHI VERDICT BOX
    const verdictBox = document.getElementById("jamakkolVerdictBox");
    if (verdictBox) {
        let badgeColor = "#047857";
        let badgeBg = "#ecfdf5";
        if (pred.kariya_siddhi_score < 40) {
            badgeColor = "#b91c1c";
            badgeBg = "#fef2f2";
        } else if (pred.kariya_siddhi_score < 55) {
            badgeColor = "#b45309";
            badgeBg = "#fef3c7";
        }

        const reasonsList = (pred.reasons_ta || []).map((r, i) => `
            <li style="margin-bottom:6px; font-size:0.9rem; line-height:1.55; color:var(--text-primary); font-weight:500;">
                ${r} <span style="font-size:0.82rem; color:var(--text-secondary); display:block;">${pred.reasons_en[i] || ""}</span>
            </li>
        `).join("");

        verdictBox.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:14px;">
                <div style="font-weight:800; color:var(--gold-bright); font-size:1.15rem; font-family:var(--font-serif);">
                    🎯 Kariya Siddhi Verdict / காரிய சித்தி பலன் தீர்ப்பு
                </div>
                <div style="background:${badgeBg}; color:${badgeColor}; font-weight:800; font-size:0.95rem; padding:4px 14px; border-radius:14px; border:1px solid ${badgeColor};">
                    ${pred.kariya_siddhi_score}% Success Likelihood
                </div>
            </div>

            <!-- Progress Meter -->
            <div style="background:var(--border-color); height:12px; border-radius:6px; overflow:hidden; margin-bottom:16px;">
                <div style="width:${pred.kariya_siddhi_score}%; height:100%; background:linear-gradient(90deg, #f59e0b, #10b981); transition:width 0.8s ease;"></div>
            </div>

            <div style="background:rgba(217, 119, 6, 0.08); border-left:4.5px solid #d97706; padding:12px 16px; border-radius:6px; margin-bottom:16px;">
                <div style="font-weight:800; font-size:1.05rem; color:#92400e; margin-bottom:4px;">
                    ${pred.kariya_siddhi_verdict_ta}
                </div>
                <div style="font-size:0.88rem; color:var(--text-secondary); font-weight:600;">
                    ${pred.kariya_siddhi_verdict_en}
                </div>
            </div>

            <div style="font-size:0.88rem; font-weight:700; color:var(--text-primary); margin-bottom:8px;">
                Astrological Factors (ஜோதிட காரணங்கள்):
            </div>
            <ul style="padding-left:18px; margin:0;">
                ${reasonsList}
            </ul>
        `;
    }

    // 5. RENDER KAVIPPU OBSTRUCTION ANALYSIS
    const kavippuBox = document.getElementById("jamakkolKavippuAnalysisBox");
    if (kavippuBox) {
        const affInner = pred.afflicted_by_kavippu?.inner_planets?.length > 0
            ? pred.afflicted_by_kavippu.inner_planets.join(", ")
            : "None (நேரடி கிரக பாதிப்பு இல்லை)";
        const affJama = pred.afflicted_by_kavippu?.jama_planets?.length > 0
            ? pred.afflicted_by_kavippu.jama_planets.join(", ")
            : "None";

        kavippuBox.innerHTML = `
            <div style="font-weight:800; color:#ef4444; font-size:1.08rem; font-family:var(--font-serif); margin-bottom:12px; display:flex; align-items:center; gap:8px;">
                <span>🛡️</span> Kavippu Obstruction Analysis / கவிப்பு தோஷ & மறைவு ஆய்வு
            </div>
            <div style="font-size:0.9rem; color:var(--text-primary); line-height:1.6; font-weight:500;">
                கவிப்பு புள்ளி <strong>${p.kavippu.sign_name_ta} (${p.kavippu.sign_name_en})</strong> ராசியில் அமைந்துள்ளது.
                இது உதயத்திற்கு <strong>${pred.bhava_kavippu_from_udhayam}ம் பாவகம்</strong> மற்றும் ஆருடத்திற்கு <strong>${pred.bhava_kavippu_from_arudam}ம் பாவகம்</strong> ஆகும்.
            </div>
            <div style="margin-top:12px; background:rgba(239, 68, 68, 0.08); border-left:4px solid #ef4444; padding:10px 14px; border-radius:6px; font-size:0.86rem;">
                <div><strong>Afflicted Transit Planets / கவிப்பில் உள்ள கோள்கள்:</strong> ${affInner}</div>
                <div style="margin-top:4px;"><strong>Afflicted Jama Planets / கவிப்பில் உள்ள சாமக்கோள்கள்:</strong> ${affJama}</div>
            </div>
            <div style="margin-top:10px; font-size:0.84rem; color:var(--text-secondary); line-height:1.5; font-style:italic;">
                விளக்கம்: கவிப்பு நிற்கும் பாவகத்திற்குரிய விஷயங்கள் மறைக்கப்படலாம் அல்லது ஆரம்ப தடைகளை சந்திக்கலாம்.
            </div>
        `;
    }

    // 6. RENDER DHATU MOOLA JEEVA BOX
    const dmjBox = document.getElementById("jamakkolDmjBox");
    if (dmjBox) {
        dmjBox.innerHTML = `
            <div style="font-weight:800; color:var(--gold-bright); font-size:1.02rem; font-family:var(--font-serif); margin-bottom:10px; display:flex; align-items:center; gap:6px;">
                <span>🌿</span> Question Nature / தாது - மூல - ஜீவ நிர்ணயம்
            </div>
            <div style="font-size:0.88rem; color:var(--text-primary); line-height:1.55; margin-bottom:10px;">
                பாடம் 13-14 விதிப்படி கேள்வி கேட்கப்பட்ட பொருள் அல்லது நபரின் தன்மையை அறியும் முறை:
            </div>
            <div style="font-size:0.84rem; background:rgba(0,0,0,0.03); padding:10px 12px; border-radius:6px; line-height:1.6;">
                <div>• <strong>Udhayam (உதயம்):</strong> ${pred.udhayam_dmj.ta} (${pred.udhayam_dmj.en})</div>
                <div>• <strong>Arudam (ஆருடம்):</strong> ${pred.arudam_dmj.ta} (${pred.arudam_dmj.en})</div>
                <div>• <strong>Kavippu (கவிப்பு):</strong> ${pred.kavippu_dmj.ta} (${pred.kavippu_dmj.en})</div>
            </div>
            <div style="margin-top:10px; font-size:0.84rem; color:var(--text-secondary); line-height:1.5;">
                <strong>சுருக்கம்:</strong> ${pred.dmj_summary_ta}
            </div>
        `;
    }

    // 7. RENDER TIMING BOX (KALA NIRNAYAM)
    const timingBox = document.getElementById("jamakkolTimingBox");
    if (timingBox && pred.timing_analysis) {
        const t = pred.timing_analysis;
        timingBox.innerHTML = `
            <div style="font-weight:800; color:#0284c7; font-size:1.02rem; font-family:var(--font-serif); margin-bottom:10px; display:flex; align-items:center; gap:6px;">
                <span>⏳</span> Fruition Timing / கால நிர்ணய கணிதம்
            </div>
            <div style="font-size:0.88rem; color:var(--text-primary); line-height:1.55; margin-bottom:10px;">
                பாடம் 10-ல் குறிப்பிடப்பட்டுள்ள பாரம்பரிய சந்திரன்-உதய காலக் கணித முறை:
            </div>
            <div style="font-size:0.84rem; background:rgba(2, 132, 199, 0.08); border-left:4px solid #0284c7; padding:10px 12px; border-radius:6px; line-height:1.6;">
                <div>• <strong>Moon to Udhayam Distance:</strong> ${t.moon_distance_houses} Houses (${t.estimated_days} Days)</div>
                <div>• <strong>Arudam Lord Period:</strong> ${t.arudam_lord_time_unit_ta} (${t.arudam_lord_time_unit_en})</div>
            </div>
            <div style="margin-top:10px; font-size:0.86rem; color:#0369a1; font-weight:700; line-height:1.5;">
                ${t.summary_ta}
            </div>
        `;
    }

    // 8. RENDER REMEDIES BOX
    const remediesBox = document.getElementById("jamakkolRemediesBox");
    if (remediesBox) {
        remediesBox.innerHTML = `
            <div style="font-weight:800; color:#059669; font-size:1.02rem; font-family:var(--font-serif); margin-bottom:10px; display:flex; align-items:center; gap:6px;">
                <span>🪔</span> Auspicious Direction & Remedies / வெற்றி திசை & பரிகாரம்
            </div>
            <div style="font-size:0.88rem; color:var(--text-primary); line-height:1.55; margin-bottom:10px;">
                ஆருடத்தின் வழி காரிய வெற்றி பெறுவதற்கான திசை மற்றும் தெய்வ வழிபாடு:
            </div>
            <div style="font-size:0.84rem; background:rgba(16, 185, 129, 0.08); border-left:4px solid #059669; padding:10px 12px; border-radius:6px; line-height:1.6;">
                <div>• <strong>வெற்றி திசை (Auspicious Direction):</strong> <strong>${pred.auspicious_direction_ta} (${pred.auspicious_direction_en})</strong></div>
                <div>• <strong>காரிய அனுகூல திசை:</strong> பேச்சுவார்த்தை அல்லது முயற்சிக்கு இத்திசை நோக்கி அமர்வது நலம்.</div>
                <div>• <strong>சாமுக்கோள் பரிகாரம்:</strong> சாம அதிபதியான <strong>${j.active_jaamam_lord?.lord_name_ta}</strong>க்குரிய தீபம் ஏற்றி வழிபட தடைகள் நீங்கி காரிய சித்தி உண்டாகும்.</div>
            </div>
        `;
    }
}
