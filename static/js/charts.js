/**
 * Interactive Vedic Chart Renderer: North & South Indian Styles
 */

class VedicChartRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentChartStyle = 'south'; // South Indian style by default
        this.currentChartData = null;
        this.onHouseClickCallback = null;
    }

    setChartData(chartData) {
        this.currentChartData = chartData;
        this.render();
    }

    setStyle(style) {
        if (style === 'north' || style === 'south') {
            this.currentChartStyle = style;
            this.render();
        }
    }

    onHouseClick(cb) {
        this.onHouseClickCallback = cb;
    }

    render() {
        if (!this.container || !this.currentChartData) return;
        this.container.innerHTML = '';

        if (this.currentChartStyle === 'north') {
            this.renderNorthIndian();
        } else {
            this.renderSouthIndian();
        }
    }

    renderNorthIndian() {
        const data = this.currentChartData.north_indian;
        if (!data || data.length < 12) return;

        // SVG Parashari diamond layout
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("viewBox", "0 0 500 500");
        svg.setAttribute("class", "vedic-chart-svg north-chart");

        // Read dynamic theme colors from document.body
        const compStyle = getComputedStyle(document.body);
        const goldBright = compStyle.getPropertyValue('--gold-bright').trim() || '#ffd700';
        const goldPrimary = compStyle.getPropertyValue('--gold-primary').trim() || '#d4af37';
        const bgInput = compStyle.getPropertyValue('--bg-input').trim() || '#0f172a';
        const bgDark = compStyle.getPropertyValue('--bg-dark').trim() || '#070a13';
        const borderGold = compStyle.getPropertyValue('--border-gold').trim() || 'rgba(212, 175, 55, 0.45)';

        // Definitions: Gradients, Filters
        const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
        defs.innerHTML = `
            <linearGradient id="chartBg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="${bgInput}" stop-opacity="0.95"/>
                <stop offset="100%" stop-color="${bgDark}" stop-opacity="0.98"/>
            </linearGradient>
            <linearGradient id="goldBorder" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="${goldBright}"/>
                <stop offset="50%" stop-color="${goldPrimary}"/>
                <stop offset="100%" stop-color="${goldPrimary}"/>
            </linearGradient>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over"/>
            </filter>
        `;
        svg.appendChild(defs);

        // Chart Background
        const bg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        bg.setAttribute("x", "10");
        bg.setAttribute("y", "10");
        bg.setAttribute("width", "480");
        bg.setAttribute("height", "480");
        bg.setAttribute("rx", "12");
        bg.setAttribute("fill", "url(#chartBg)");
        bg.setAttribute("stroke", "url(#goldBorder)");
        bg.setAttribute("stroke-width", "3");
        svg.appendChild(bg);

        // Watermark in Center (Tamil Sacred Om)
        const wm = document.createElementNS("http://www.w3.org/2000/svg", "text");
        wm.setAttribute("x", "250");
        wm.setAttribute("y", "260");
        wm.setAttribute("text-anchor", "middle");
        wm.setAttribute("class", "chart-watermark");
        wm.textContent = "ௐ";
        svg.appendChild(wm);

        // House Polygons Definition (x, y coordinates for 500x500 box with 10px margin)
        // Midpoints: (250, 10), (490, 250), (250, 490), (10, 250)
        const housesCoords = [
            // House 1 (Top Center Diamond)
            { house: 1, points: "250,10 370,130 250,250 130,130", center: [250, 140], rasiPos: [250, 50] },
            // House 2 (Top Left Triangle)
            { house: 2, points: "10,10 250,10 130,130", center: [130, 60], rasiPos: [70, 40] },
            // House 3 (Left Top Triangle)
            { house: 3, points: "10,10 130,130 10,250", center: [50, 140], rasiPos: [40, 70] },
            // House 4 (Left Center Diamond)
            { house: 4, points: "10,250 130,130 250,250 130,370", center: [130, 250], rasiPos: [50, 250] },
            // House 5 (Left Bottom Triangle)
            { house: 5, points: "10,250 130,370 10,490", center: [50, 360], rasiPos: [40, 430] },
            // House 6 (Bottom Left Triangle)
            { house: 6, points: "10,490 130,370 250,490", center: [130, 440], rasiPos: [70, 460] },
            // House 7 (Bottom Center Diamond)
            { house: 7, points: "250,250 370,370 250,490 130,370", center: [250, 360], rasiPos: [250, 450] },
            // House 8 (Bottom Right Triangle)
            { house: 8, points: "250,490 370,370 490,490", center: [370, 440], rasiPos: [430, 460] },
            // House 9 (Right Bottom Triangle)
            { house: 9, points: "490,250 490,490 370,370", center: [450, 360], rasiPos: [460, 430] },
            // House 10 (Right Center Diamond)
            { house: 10, points: "250,250 370,130 490,250 370,370", center: [370, 250], rasiPos: [450, 250] },
            // House 11 (Right Top Triangle)
            { house: 11, points: "490,10 490,250 370,130", center: [450, 140], rasiPos: [460, 70] },
            // House 12 (Top Right Triangle)
            { house: 12, points: "250,10 490,10 370,130", center: [370, 60], rasiPos: [430, 40] }
        ];

        // Draw house polygons
        housesCoords.forEach((hCoord) => {
            const hNum = hCoord.house;
            const hData = data.find(d => d.house === hNum) || { planets: [], rasi_id: 0, rasi_name: '' };

            const poly = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
            poly.setAttribute("points", hCoord.points);
            poly.setAttribute("class", `house-poly house-${hNum}`);
            poly.setAttribute("stroke", borderGold);
            poly.setAttribute("stroke-width", "1.5");
            poly.setAttribute("fill", hNum === 1 ? borderGold.replace(/[\d\.]+\)$/, "0.12)") : "transparent");

            poly.addEventListener("click", () => {
                if (this.onHouseClickCallback) {
                    this.onHouseClickCallback(hNum, hData);
                }
            });

            svg.appendChild(poly);

            // Rasi Index Number (1 to 12)
            const rasiTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
            rasiTxt.setAttribute("x", hCoord.rasiPos[0]);
            rasiTxt.setAttribute("y", hCoord.rasiPos[1]);
            rasiTxt.setAttribute("class", "rasi-num-text");
            rasiTxt.setAttribute("text-anchor", "middle");
            rasiTxt.setAttribute("dominant-baseline", "central");
            rasiTxt.textContent = (hData.rasi_id + 1); // 1=Aries, 2=Taurus...
            svg.appendChild(rasiTxt);

            // Render planets in house
            if (hData.planets && hData.planets.length > 0) {
                const group = document.createElementNS("http://www.w3.org/2000/svg", "g");
                group.setAttribute("class", "planets-group");

                const cx = hCoord.center[0];
                const cy = hCoord.center[1];
                const count = hData.planets.length;
                const startY = cy - ((count - 1) * 9);

                hData.planets.forEach((p, idx) => {
                    const pTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
                    const py = startY + (idx * 18);
                    pTxt.setAttribute("x", cx);
                    pTxt.setAttribute("y", py);
                    pTxt.setAttribute("text-anchor", "middle");
                    pTxt.setAttribute("dominant-baseline", "central");
                    pTxt.setAttribute("class", `chart-planet-text ${p.label.includes('Lagna') ? 'is-asc' : ''}`);

                    // Planet text format: e.g. "Ju ♃ 14°"
                    let shortLabel = p.label.split(' ')[0];
                    if (p.label.includes('Lagna')) shortLabel = "ASC";
                    pTxt.textContent = `${shortLabel} ${Math.round(p.deg)}°`;

                    group.appendChild(pTxt);
                });

                svg.appendChild(group);
            }
        });

        // Diagonals and Diamond overlay lines for aesthetic sharpness
        const linesGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        linesGroup.setAttribute("stroke", "url(#goldBorder)");
        linesGroup.setAttribute("stroke-width", "2");
        linesGroup.setAttribute("pointer-events", "none");
        linesGroup.innerHTML = `
            <line x1="10" y1="10" x2="490" y2="490" opacity="0.6"/>
            <line x1="490" y1="10" x2="10" y2="490" opacity="0.6"/>
            <polygon points="250,10 490,250 250,490 10,250" fill="none" opacity="0.8"/>
        `;
        svg.appendChild(linesGroup);

        this.container.appendChild(svg);
    }

    // Creates an animated, pulsing SVG blinking dot
    createBlinkDot(cx, cy, r = 3.5, color = "#10b981") {
        const dotGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
        dotGroup.setAttribute("class", "chart-blink-dot-group");

        // Outer pulsing aura
        const glowCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        glowCircle.setAttribute("cx", cx);
        glowCircle.setAttribute("cy", cy);
        glowCircle.setAttribute("r", r + 1.5);
        glowCircle.setAttribute("fill", color);
        glowCircle.setAttribute("opacity", "0.4");

        const glowAnimR = document.createElementNS("http://www.w3.org/2000/svg", "animate");
        glowAnimR.setAttribute("attributeName", "r");
        glowAnimR.setAttribute("values", `${r + 0.5};${r + 3.8};${r + 0.5}`);
        glowAnimR.setAttribute("dur", "1.3s");
        glowAnimR.setAttribute("repeatCount", "indefinite");
        glowCircle.appendChild(glowAnimR);

        const glowAnimOp = document.createElementNS("http://www.w3.org/2000/svg", "animate");
        glowAnimOp.setAttribute("attributeName", "opacity");
        glowAnimOp.setAttribute("values", "0.45;0.08;0.45");
        glowAnimOp.setAttribute("dur", "1.3s");
        glowAnimOp.setAttribute("repeatCount", "indefinite");
        glowCircle.appendChild(glowAnimOp);

        // Core bright dot
        const coreCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        coreCircle.setAttribute("cx", cx);
        coreCircle.setAttribute("cy", cy);
        coreCircle.setAttribute("r", r);
        coreCircle.setAttribute("fill", color);

        const coreAnim = document.createElementNS("http://www.w3.org/2000/svg", "animate");
        coreAnim.setAttribute("attributeName", "opacity");
        coreAnim.setAttribute("values", "1;0.22;1");
        coreAnim.setAttribute("dur", "1.3s");
        coreAnim.setAttribute("repeatCount", "indefinite");
        coreCircle.appendChild(coreAnim);

        dotGroup.appendChild(glowCircle);
        dotGroup.appendChild(coreCircle);
        return dotGroup;
    }

    renderSouthIndian() {
        const signsData = this.currentChartData.south_indian;
        if (!signsData || signsData.length < 12) return;

        const chartCode = this.currentChartData.code || 'D-1';
        const isD1 = (chartCode === 'D-1' || !chartCode || (this.currentChartData.name && this.currentChartData.name.includes('Rasi')));
        const isD9 = (chartCode === 'D-9' || (this.currentChartData.name && this.currentChartData.name.includes('Navamsa')));

        // Modern South Indian 4x4 Grid (viewBox 0 0 680 680, cellSize = 165, offset = 10)
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
        svg.setAttribute("viewBox", "0 0 680 680");
        svg.setAttribute("class", "vedic-chart-svg south-chart modern-south-chart");

        // Dynamic theme colors from CSS variables
        const compStyle = getComputedStyle(document.body);
        const goldBright = compStyle.getPropertyValue('--gold-bright').trim() || '#ffd700';
        const goldPrimary = compStyle.getPropertyValue('--gold-primary').trim() || '#d4af37';
        const bgInput = compStyle.getPropertyValue('--bg-input').trim() || '#0f172a';
        const bgDark = compStyle.getPropertyValue('--bg-dark').trim() || '#070a13';
        const borderGold = compStyle.getPropertyValue('--border-gold').trim() || 'rgba(212, 175, 55, 0.4)';
        const textPrimary = compStyle.getPropertyValue('--text-primary').trim() || '#f8fafc';
        const textSecondary = compStyle.getPropertyValue('--text-secondary').trim() || '#94a3b8';

        const themeName = document.body.getAttribute("data-theme") || "human-crafted";
        const isLight = (themeName === "palm-leaf" || themeName === "pleasant-vedic" || !themeName || themeName === "default");

        // High-Contrast Theme Adaptive Palette
        const cPalette = isLight ? {
            chartBg: "#fbf8ef",
            chartBorder: "#b45309",
            cellBg: "#f5eedf",
            cellBorder: "rgba(180, 83, 9, 0.45)",
            cellAscBg: "rgba(5, 150, 105, 0.12)",
            cellAscBorder: "#059669",
            centerBg: "#f7f1e4",
            centerBorder: "#b45309",
            omColor: "rgba(180, 83, 9, 0.13)",
            titleColor: "#78350f",
            subtitleColor: "#1c1917",
            lagnaBadgeBg: "rgba(5, 150, 105, 0.14)",
            lagnaBadgeBorder: "#059669",
            lagnaBadgeText: "#065f46",
            epheTextColor: "#57534e",
            rasiEnColor: "#78350f",
            rasiTaColor: "#92400e",
            houseBadgeBg: "rgba(0, 0, 0, 0.05)",
            houseBadgeBorder: "rgba(180, 83, 9, 0.45)",
            houseBadgeText: "#44403c",
            nakTextColor: "#44403c",
            dividerColor: "rgba(180, 83, 9, 0.25)",
            rowBg: "rgba(0, 0, 0, 0.04)",
            rowBorder: "rgba(0, 0, 0, 0.09)",
            nakBadgeColor: "#78350f",
            planets: {
                'Sun': '#b45309', 'Su': '#b45309', '0': '#b45309',
                'Moon': '#0369a1', 'Mo': '#0369a1', '1': '#0369a1',
                'Mars': '#b91c1c', 'Ma': '#b91c1c', '2': '#b91c1c',
                'Mercury': '#047857', 'Me': '#047857', '3': '#047857',
                'Jupiter': '#92400e', 'Ju': '#92400e', '4': '#92400e',
                'Venus': '#be185d', 'Ve': '#be185d', '5': '#be185d',
                'Saturn': '#581c87', 'Sa': '#581c87', '6': '#581c87',
                'Rahu': '#6b21a8', 'Ra': '#6b21a8', '7': '#6b21a8',
                'Ketu': '#701a75', 'Ke': '#701a75', '8': '#701a75',
                'ASC': '#065f46', 'Lagna': '#065f46', 'L': '#065f46'
            }
        } : {
            chartBg: bgDark,
            chartBorder: goldPrimary,
            cellBg: "rgba(255, 255, 255, 0.04)",
            cellBorder: borderGold,
            cellAscBg: "rgba(16, 185, 129, 0.15)",
            cellAscBorder: "#10b981",
            centerBg: "rgba(10, 15, 26, 0.95)",
            centerBorder: goldBright,
            omColor: "rgba(212, 175, 55, 0.16)",
            titleColor: goldBright,
            subtitleColor: "#f8fafc",
            lagnaBadgeBg: "rgba(16, 185, 129, 0.18)",
            lagnaBadgeBorder: "#10b981",
            lagnaBadgeText: "#6ee7b7",
            epheTextColor: textSecondary,
            rasiEnColor: goldBright,
            rasiTaColor: "#facc15",
            houseBadgeBg: "rgba(148, 163, 184, 0.12)",
            houseBadgeBorder: "rgba(148, 163, 184, 0.3)",
            houseBadgeText: textSecondary,
            nakTextColor: "rgba(203, 213, 225, 0.9)",
            dividerColor: borderGold,
            rowBg: "rgba(255, 255, 255, 0.045)",
            rowBorder: "rgba(255, 255, 255, 0.08)",
            nakBadgeColor: "#fef08a",
            planets: {
                'Sun': '#fbbf24', 'Su': '#fbbf24', '0': '#fbbf24',
                'Moon': '#38bdf8', 'Mo': '#38bdf8', '1': '#38bdf8',
                'Mars': '#f87171', 'Ma': '#f87171', '2': '#f87171',
                'Mercury': '#34d399', 'Me': '#34d399', '3': '#34d399',
                'Jupiter': '#facc15', 'Ju': '#facc15', '4': '#facc15',
                'Venus': '#f472b6', 'Ve': '#f472b6', '5': '#f472b6',
                'Saturn': '#a78bfa', 'Sa': '#a78bfa', '6': '#a78bfa',
                'Rahu': '#c084fc', 'Ra': '#c084fc', '7': '#c084fc',
                'Ketu': '#e879f9', 'Ke': '#e879f9', '8': '#e879f9',
                'ASC': '#10b981', 'Lagna': '#10b981', 'L': '#10b981'
            }
        };

        // Complete 12 Zodiac Rashis Dual Lookup (Aries to Pisces)
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

        // Resident Nakshatras per Rasi - Compact 2-Line Format Fitting 100% Inside Cell
        const SIGN_RESIDENT_NAKSHATRAS = {
            11: { l1: "பூரட்டாதி 4 • உத்திரட்டாதி", l2: "ரேவதி (Revati)" },
            0:  { l1: "அஸ்வினி • பரணி", l2: "கார்த்திகை 1 (Krit-1)" },
            1:  { l1: "கார்த்திகை 2-4 • ரோகிணி", l2: "மிருகசீரிஷம் 1-2 (Mrig)" },
            2:  { l1: "மிருகசீரிஷம் 3-4 • திருவாதிரை", l2: "புனர்பூசம் 1-3 (Punar)" },
            3:  { l1: "புனர்பூசம் 4 • பூசம்", l2: "ஆயில்யம் (Ashlesha)" },
            4:  { l1: "மகம் • பூரம்", l2: "உத்திரம் 1 (UPha-1)" },
            5:  { l1: "உத்திரம் 2-4 • அஸ்தம்", l2: "சித்திரை 1-2 (Chitra)" },
            6:  { l1: "சித்திரை 3-4 • சுவாதி", l2: "விசாகம் 1-3 (Vishakha)" },
            7:  { l1: "விசாகம் 4 • அனுஷம்", l2: "கேட்டை (Jyeshtha)" },
            8:  { l1: "மூலம் • பூராடம்", l2: "உத்திராடம் 1 (UAsh-1)" },
            9:  { l1: "உத்திராடம் 2-4 • திருவோணம்", l2: "அவிட்டம் 1-2 (Dhan)" },
            10: { l1: "அவிட்டம் 3-4 • சதயம்", l2: "பூரட்டாதி 1-3 (PBh)" }
        };

        const NAKSHATRA_TAMIL = [
            "அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிஷம்", "திருவாதிரை",
            "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்", "உத்திரம்",
            "அஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்", "கேட்டை",
            "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்", "அவிட்டம்", "சதயம்",
            "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"
        ];

        const NAKSHATRA_EN = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
            "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
            "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
        ];


        const containerId = this.container.id || "chart";
        const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
        defs.innerHTML = `
            <linearGradient id="goldBorderGrad" x1="0%" y1="0%" x2="100%" y2="100%">
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
        bg.setAttribute("stroke", isLight ? cPalette.chartBorder : "url(#goldBorderGrad)");
        bg.setAttribute("stroke-width", "2.5");
        svg.appendChild(bg);

        // Fixed South Indian Sign Positions in 4x4 grid (cellSize = 165, offset = 10)
        const signGridCoords = {
            11: [0, 0], 0: [1, 0], 1: [2, 0], 2: [3, 0],
            3: [3, 1], 4: [3, 2], 5: [3, 3],
            6: [2, 3], 7: [1, 3], 8: [0, 3],
            9: [0, 2], 10: [0, 1]
        };

        const cellSize = 165;
        const offset = 10;

        // Draw 12 Outer Cells
        for (let r_id = 0; r_id < 12; r_id++) {
            const gridPos = signGridCoords[r_id];
            const gx = offset + gridPos[0] * cellSize;
            const gy = offset + gridPos[1] * cellSize;
            const sData = signsData.find(s => s.rasi_id === r_id) || { planets: [], is_ascendant: false };
            const rInfo = RASHI_DATA[r_id] || { en: sData.rasi_name || "", ta: "", symbol: "" };
            const rasiEn = sData.rasi_name || rInfo.en;
            const rasiTa = sData.rasi_tamil || rInfo.ta;
            const rasiSymbol = sData.rasi_symbol || rInfo.symbol;

            // Clip-Path definition for this cell so NO text or elements can ever overflow
            const clipId = `clip-${containerId}-${r_id}`;
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

            // Cell Container Group with Clip Path
            const cellGroup = document.createElementNS("http://www.w3.org/2000/svg", "g");
            cellGroup.setAttribute("class", "modern-south-cell-group");
            cellGroup.setAttribute("clip-path", `url(#${clipId})`);
            cellGroup.style.cursor = "pointer";

            // Click Handler to view house details
            cellGroup.addEventListener("click", () => {
                if (this.onHouseClickCallback) {
                    this.onHouseClickCallback(sData.house_num, sData);
                }
            });

            // Detect Janma Rasi (Moon Sign in D1) & Lagna (in D9 or D1)
            const moonPlanet = sData.planets ? sData.planets.find(p => p.short === 'Mo' || p.name === 'Moon' || (p.label && p.label.includes('Moon'))) : null;
            const isJanmaRasiCell = isD1 && Boolean(moonPlanet);
            const isD9LagnaCell = isD9 && sData.is_ascendant;

            // Inner Cell Card
            const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            rect.setAttribute("x", gx + 2);
            rect.setAttribute("y", gy + 2);
            rect.setAttribute("width", cellSize - 4);
            rect.setAttribute("height", cellSize - 4);
            rect.setAttribute("rx", "10");

            let cellStroke = sData.is_ascendant ? cPalette.cellAscBorder : cPalette.cellBorder;
            let cellStrokeW = sData.is_ascendant ? "2.5" : "1.2";
            let cellFill = sData.is_ascendant ? cPalette.cellAscBg : cPalette.cellBg;

            if (isJanmaRasiCell && !sData.is_ascendant) {
                cellStroke = isLight ? "#0284c7" : "#38bdf8";
                cellStrokeW = "2.2";
                cellFill = isLight ? "rgba(14, 165, 233, 0.12)" : "rgba(56, 189, 248, 0.14)";
            }

            rect.setAttribute("stroke", cellStroke);
            rect.setAttribute("stroke-width", cellStrokeW);
            rect.setAttribute("fill", cellFill);
            rect.setAttribute("class", `south-cell ${sData.is_ascendant ? 'is-asc-cell' : ''} ${isJanmaRasiCell ? 'is-janma-rasi-cell' : ''}`);
            cellGroup.appendChild(rect);

            // 1. Header Line 1: English Sign Name + Symbol (Left)
            const signLabelEn = document.createElementNS("http://www.w3.org/2000/svg", "text");
            signLabelEn.setAttribute("x", gx + 8);
            signLabelEn.setAttribute("y", gy + 16);
            signLabelEn.setAttribute("font-size", "12.5px");
            signLabelEn.setAttribute("font-weight", "800");
            signLabelEn.setAttribute("fill", sData.is_ascendant ? (isLight ? '#065f46' : goldBright) : (isJanmaRasiCell ? (isLight ? '#0369a1' : '#38bdf8') : cPalette.rasiEnColor));
            signLabelEn.textContent = `${rasiEn} ${rasiSymbol}`;
            cellGroup.appendChild(signLabelEn);

            // 2. House Number Badge (Top-Right Pill) with Blinking Dot for Janma Rasi (D1) or Lagna (D9)
            if (sData.house_num) {
                let badgeW = sData.is_ascendant ? 44 : 28;
                if (isJanmaRasiCell) {
                    badgeW = sData.is_ascendant ? 66 : 56;
                } else if (isD9LagnaCell) {
                    badgeW = 46;
                }

                const hNumBg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                hNumBg.setAttribute("x", gx + cellSize - badgeW - 8);
                hNumBg.setAttribute("y", gy + 5);
                hNumBg.setAttribute("width", badgeW);
                hNumBg.setAttribute("height", "17");
                hNumBg.setAttribute("rx", "4");

                let badgeBgColor = sData.is_ascendant ? (isLight ? "rgba(5, 150, 105, 0.22)" : "rgba(16, 185, 129, 0.28)") : cPalette.houseBadgeBg;
                let badgeBorderColor = sData.is_ascendant ? cPalette.cellAscBorder : cPalette.houseBadgeBorder;
                let badgeTextColor = sData.is_ascendant ? (isLight ? "#065f46" : "#6ee7b7") : cPalette.houseBadgeText;

                if (isJanmaRasiCell) {
                    badgeBgColor = isLight ? "rgba(14, 165, 233, 0.20)" : "rgba(56, 189, 248, 0.25)";
                    badgeBorderColor = isLight ? "#0284c7" : "#38bdf8";
                    badgeTextColor = isLight ? "#0369a1" : "#38bdf8";
                }

                hNumBg.setAttribute("fill", badgeBgColor);
                hNumBg.setAttribute("stroke", badgeBorderColor);
                hNumBg.setAttribute("stroke-width", "1");
                cellGroup.appendChild(hNumBg);

                // Add blinking dot inside badge if Janma Rasi (D1) or Lagna (D9)
                if (isJanmaRasiCell) {
                    const dotX = gx + cellSize - badgeW - 8 + 7;
                    const dotY = gy + 13.5;
                    cellGroup.appendChild(this.createBlinkDot(dotX, dotY, 3, "#0284c7"));
                } else if (isD9LagnaCell) {
                    const dotX = gx + cellSize - badgeW - 8 + 7;
                    const dotY = gy + 13.5;
                    cellGroup.appendChild(this.createBlinkDot(dotX, dotY, 3, "#10b981"));
                }

                const hNumTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
                const textX = (isJanmaRasiCell || isD9LagnaCell) 
                    ? (gx + cellSize - (badgeW / 2) - 8 + 4)
                    : (gx + cellSize - (badgeW / 2) - 8);
                hNumTxt.setAttribute("x", textX);
                hNumTxt.setAttribute("y", gy + 17);
                hNumTxt.setAttribute("text-anchor", "middle");
                hNumTxt.setAttribute("font-size", isJanmaRasiCell ? "10px" : "11.5px");
                hNumTxt.setAttribute("font-weight", "800");
                hNumTxt.setAttribute("fill", badgeTextColor);

                if (isJanmaRasiCell) {
                    hNumTxt.textContent = sData.is_ascendant ? `★ H1·☾` : `H${sData.house_num} ☾ Rasi`;
                } else {
                    hNumTxt.textContent = sData.is_ascendant ? `★ H1` : `H${sData.house_num}`;
                }
                cellGroup.appendChild(hNumTxt);
            }

            // 3. Header Line 2: Tamil Sign Name (Distinct, Large & Bold)
            const signLabelTa = document.createElementNS("http://www.w3.org/2000/svg", "text");
            signLabelTa.setAttribute("x", gx + 8);
            signLabelTa.setAttribute("y", gy + 31);
            signLabelTa.setAttribute("font-size", "13px");
            signLabelTa.setAttribute("font-weight", "800");
            signLabelTa.setAttribute("fill", sData.is_ascendant ? (isLight ? '#065f46' : goldBright) : cPalette.rasiTaColor);
            signLabelTa.textContent = rasiTa;
            cellGroup.appendChild(signLabelTa);

            // 4. Resident Nakshatras (Clear 2-Line Sub-Header: 8.5px Clean Fit Without Clipping)
            const resNak = SIGN_RESIDENT_NAKSHATRAS[r_id] || { l1: "", l2: "" };
            const nakLine1 = document.createElementNS("http://www.w3.org/2000/svg", "text");
            nakLine1.setAttribute("x", gx + 8);
            nakLine1.setAttribute("y", gy + 44);
            nakLine1.setAttribute("font-size", "8.5px");
            nakLine1.setAttribute("font-weight", "600");
            nakLine1.setAttribute("fill", cPalette.nakTextColor);
            nakLine1.textContent = `• ${resNak.l1}`;
            cellGroup.appendChild(nakLine1);

            const nakLine2 = document.createElementNS("http://www.w3.org/2000/svg", "text");
            nakLine2.setAttribute("x", gx + 8);
            nakLine2.setAttribute("y", gy + 55);
            nakLine2.setAttribute("font-size", "8.5px");
            nakLine2.setAttribute("font-weight", "600");
            nakLine2.setAttribute("fill", cPalette.nakTextColor);
            nakLine2.textContent = `  ${resNak.l2}`;
            cellGroup.appendChild(nakLine2);

            // Subtle divider line
            const divLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
            divLine.setAttribute("x1", gx + 6);
            divLine.setAttribute("y1", gy + 62);
            divLine.setAttribute("x2", gx + cellSize - 6);
            divLine.setAttribute("y2", gy + 62);
            divLine.setAttribute("stroke", cPalette.dividerColor);
            divLine.setAttribute("stroke-width", "0.8");
            cellGroup.appendChild(divLine);

            // 5. Occupying Planets with Large, Bold, High-Contrast Typography
            const planets = sData.planets || [];
            if (planets.length > 0) {
                const pCount = planets.length;
                const isDense = pCount >= 4;
                const startY = gy + (isDense ? 74 : (pCount === 1 ? 88 : 78));
                const stepY = isDense ? (pCount >= 5 ? 19 : 21) : 24;
                const rowH = isDense ? 18 : 20;

                planets.slice(0, 5).forEach((p, pIdx) => {
                    const py = startY + (pIdx * stepY);

                    // Extract Short Name & Degree
                    let pKey = p.short || (p.label ? p.label.split(' ')[0] : (p.name || 'P'));
                    let pGlyph = '';
                    if (pKey === 'ASC' || (p.label && p.label.includes('Lagna'))) { pKey = 'ASC'; pGlyph = '★'; }
                    else if (pKey === 'Su' || pKey === 'Sun') pGlyph = '☉';
                    else if (pKey === 'Mo' || pKey === 'Moon') pGlyph = '☾';
                    else if (pKey === 'Ma' || pKey === 'Mars') pGlyph = '♂';
                    else if (pKey === 'Me' || pKey === 'Mercury') pGlyph = '☿';
                    else if (pKey === 'Ju' || pKey === 'Jupiter') pGlyph = '♃';
                    else if (pKey === 'Ve' || pKey === 'Venus') pGlyph = '♀';
                    else if (pKey === 'Sa' || pKey === 'Saturn') pGlyph = '♄';
                    else if (pKey === 'Ra' || pKey === 'Rahu') pGlyph = '☊';
                    else if (pKey === 'Ke' || pKey === 'Ketu') pGlyph = '☋';

                    const degVal = p.deg_dms ? p.deg_dms.split(' ')[0] : (p.deg !== undefined ? `${Math.round(p.deg)}°` : '');
                    const color = cPalette.planets[pKey] || cPalette.planets[p.name] || cPalette.rasiEnColor;

                    // Planet's Exact Nakshatra & Pada
                    let nakPadaLabel = p.nak_pada_tamil || p.nak_pada || '';
                    if (!nakPadaLabel && p.deg !== undefined) {
                        const absL = (r_id * 30.0 + p.deg) % 360.0;
                        const nIdx = Math.floor(absL / (360.0 / 27.0));
                        const pada = Math.floor(((absL / (360.0 / 27.0)) - nIdx) * 4) + 1;
                        nakPadaLabel = `${NAKSHATRA_TAMIL[nIdx % 27]}-${pada}`;
                    }

                    // Planet Micro-Row Background Card
                    const rowBg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                    rowBg.setAttribute("x", gx + 5);
                    rowBg.setAttribute("y", py - (rowH / 2) - 1);
                    rowBg.setAttribute("width", cellSize - 10);
                    rowBg.setAttribute("height", rowH);
                    rowBg.setAttribute("rx", "4");
                    rowBg.setAttribute("fill", pKey === 'ASC' ? (isLight ? "rgba(5, 150, 105, 0.14)" : "rgba(16, 185, 129, 0.16)") : cPalette.rowBg);
                    rowBg.setAttribute("stroke", pKey === 'ASC' ? (isLight ? "rgba(5, 150, 105, 0.35)" : "rgba(16, 185, 129, 0.35)") : cPalette.rowBorder);
                    rowBg.setAttribute("stroke-width", "0.7");
                    cellGroup.appendChild(rowBg);

                    // Compact Tamil Nakshatra Map for Zero Font Overlap
                    const NAK_PADA_SHORT_TAMIL = {
                        "மிருகசீரிஷம்": "மிருகசீ",
                        "உத்திரட்டாதி": "உத்திரட்டா",
                        "பூரட்டாதி": "பூரட்டா",
                        "புனர்பூசம்": "புனர்பூ",
                        "உத்திராடம்": "உத்திரா",
                        "திருவாதிரை": "திருவா",
                        "கார்த்திகை": "கார்த்தி",
                        "திருவோணம்": "திருவோ"
                    };

                    let shortNakPada = nakPadaLabel;
                    if (nakPadaLabel) {
                        if (nakPadaLabel.includes('-')) {
                            const parts = nakPadaLabel.split('-');
                            const baseName = parts[0].trim();
                            const pada = parts.slice(1).join('-');
                            const shortBase = NAK_PADA_SHORT_TAMIL[baseName] || baseName;
                            shortNakPada = `${shortBase}-${pada}`;
                        } else if (nakPadaLabel.includes(' ')) {
                            const parts = nakPadaLabel.split(' ');
                            const baseName = parts[0].trim();
                            const pada = parts.slice(1).join(' ');
                            const shortBase = NAK_PADA_SHORT_TAMIL[baseName] || baseName;
                            shortNakPada = `${shortBase} ${pada}`;
                        } else {
                            shortNakPada = NAK_PADA_SHORT_TAMIL[nakPadaLabel.trim()] || nakPadaLabel;
                        }
                    }

                    // Check if this row is Moon in D1 (Janma Rasi & Janma Nakshatra) or ASC in D9 (Lagna)
                    const isMoonInD1 = isD1 && (pKey === 'Mo' || p.name === 'Moon' || (p.label && p.label.includes('Moon')));
                    const isAscInD9 = isD9 && pKey === 'ASC';

                    // Add blinking indicator dot for Janma Rasi (Moon) or D9 Lagna
                    const hasLeftDot = isMoonInD1 || isAscInD9;
                    if (hasLeftDot) {
                        const dotColor = isMoonInD1 ? "#0284c7" : "#10b981";
                        cellGroup.appendChild(this.createBlinkDot(gx + 12, py + 3, 3, dotColor));
                    }

                    // Planet Name & Degree Text (Crisp, High-Contrast Typography: 11.5px / 10.5px)
                    const pTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
                    pTxt.setAttribute("x", hasLeftDot ? gx + 18 : gx + 8);
                    pTxt.setAttribute("y", py + 3.5);
                    pTxt.setAttribute("font-size", isDense ? "10.5px" : "11.5px");
                    pTxt.setAttribute("font-weight", "800");
                    pTxt.setAttribute("fill", color);
                    pTxt.textContent = `${pGlyph} ${pKey} ${degVal}`;
                    cellGroup.appendChild(pTxt);

                    // Planet's Exact Nakshatra Badge (Right Aligned: 10px / 9.5px - Guaranteed Zero Collision)
                    if (shortNakPada) {
                        if (isMoonInD1) {
                            // Blinking dot right next to Janma Nakshatra (Birth Star)
                            const nakDotX = gx + cellSize - 8 - 48;
                            cellGroup.appendChild(this.createBlinkDot(nakDotX, py + 3, 3, "#0284c7"));
                        }

                        const nakTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
                        nakTxt.setAttribute("x", gx + cellSize - 8);
                        nakTxt.setAttribute("y", py + 3.5);
                        nakTxt.setAttribute("text-anchor", "end");
                        nakTxt.setAttribute("font-size", isDense ? "9.5px" : "10px");
                        nakTxt.setAttribute("font-weight", isMoonInD1 ? "800" : "700");
                        nakTxt.setAttribute("fill", isMoonInD1 ? (isLight ? "#0284c7" : "#38bdf8") : (pKey === 'ASC' ? (isLight ? "#065f46" : "#6ee7b7") : cPalette.nakBadgeColor));
                        nakTxt.textContent = shortNakPada;
                        cellGroup.appendChild(nakTxt);
                    }
                });

                if (planets.length > 5) {
                    const moreTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
                    moreTxt.setAttribute("x", gx + (cellSize / 2));
                    moreTxt.setAttribute("y", gy + cellSize - 6);
                    moreTxt.setAttribute("text-anchor", "middle");
                    moreTxt.setAttribute("font-size", "9.5px");
                    moreTxt.setAttribute("font-weight", "700");
                    moreTxt.setAttribute("fill", cPalette.houseBadgeText);
                    moreTxt.textContent = `+${planets.length - 5} more (view)...`;
                    cellGroup.appendChild(moreTxt);
                }
            } else {
                // Empty house serene placeholder
                const emptyDot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
                emptyDot.setAttribute("cx", gx + (cellSize / 2));
                emptyDot.setAttribute("cy", gy + 105);
                emptyDot.setAttribute("r", "3");
                emptyDot.setAttribute("fill", cPalette.dividerColor);
                emptyDot.setAttribute("opacity", "0.45");
                cellGroup.appendChild(emptyDot);
            }

            svg.appendChild(cellGroup);
        }

        // Center Square (2x2 cells = 330x330)
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
        centerRect.setAttribute("stroke", isLight ? cPalette.centerBorder : "url(#goldBorderGrad)");
        centerRect.setAttribute("stroke-width", "2");
        svg.appendChild(centerRect);

        // Center Sacred Pranavam Watermark (ௐ)
        const omTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
        omTxt.setAttribute("x", 340);
        omTxt.setAttribute("y", 295);
        omTxt.setAttribute("text-anchor", "middle");
        omTxt.setAttribute("font-size", "68px");
        omTxt.setAttribute("fill", cPalette.omColor);
        omTxt.setAttribute("font-family", "var(--font-serif)");
        omTxt.textContent = "ௐ";
        svg.appendChild(omTxt);

        // Center Title (Chart Name: 21px Bold)
        const titleTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
        titleTxt.setAttribute("x", 340);
        titleTxt.setAttribute("y", 312);
        titleTxt.setAttribute("text-anchor", "middle");
        titleTxt.setAttribute("font-family", "var(--font-serif)");
        titleTxt.setAttribute("font-size", "21px");
        titleTxt.setAttribute("font-weight", "800");
        titleTxt.setAttribute("fill", cPalette.titleColor);
        titleTxt.textContent = this.currentChartData.name || "Rasi Chart / ராசி சக்கரம்";
        svg.appendChild(titleTxt);

        // Center Subtitle (Divisional Code: 13.5px)
        const codeTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
        codeTxt.setAttribute("x", 340);
        codeTxt.setAttribute("y", 338);
        codeTxt.setAttribute("text-anchor", "middle");
        codeTxt.setAttribute("font-size", "13.5px");
        codeTxt.setAttribute("font-weight", "700");
        codeTxt.setAttribute("fill", cPalette.subtitleColor);
        codeTxt.textContent = `${this.currentChartData.code || 'D-1'}`;
        svg.appendChild(codeTxt);

        // Center Banner: Janma Rasi in D-1, Lagna in D-9 & other divisional charts
        let centerBannerLabel = "";
        let centerBannerColor = "";
        let centerBannerBg = "";
        let centerBannerBorder = "";

        if (isD1) {
            // Mention Janma Rasi (Moon Sign) in D-1 middle banner
            const moonSign = signsData.find(s => s.planets && s.planets.some(p => p.short === 'Mo' || p.name === 'Moon' || (p.label && p.label.includes('Moon'))));
            let rasiDisplay = "Calculated";
            if (moonSign) {
                const rInfo = RASHI_DATA[moonSign.rasi_id] || {};
                const rEn = moonSign.rasi_name || rInfo.en || "";
                const rTa = moonSign.rasi_tamil || rInfo.ta || "";
                rasiDisplay = (rEn && rTa) ? `${rEn} / ${rTa}` : (rEn || rTa || 'Rasi');
            }
            centerBannerLabel = `☾ Rasi: ${rasiDisplay}`;
            centerBannerBg = isLight ? "rgba(3, 105, 161, 0.12)" : "rgba(56, 189, 248, 0.16)";
            centerBannerBorder = isLight ? "#0284c7" : "#38bdf8";
            centerBannerColor = isLight ? "#075985" : "#7dd3fc";
        } else {
            // Lagna for D-9 and other divisional charts
            const ascSign = signsData.find(s => s.is_ascendant);
            let ascDisplay = "Calculated";
            if (ascSign) {
                const rInfo = RASHI_DATA[ascSign.rasi_id] || {};
                const aEn = ascSign.rasi_name || rInfo.en || "";
                const aTa = ascSign.rasi_tamil || rInfo.ta || "";
                ascDisplay = (aEn && aTa) ? `${aEn} / ${aTa}` : (aEn || aTa || 'Lagna');
            }
            centerBannerLabel = `★ Lagna: ${ascDisplay}`;
            centerBannerBg = cPalette.lagnaBadgeBg;
            centerBannerBorder = cPalette.lagnaBadgeBorder;
            centerBannerColor = cPalette.lagnaBadgeText;
        }

        const badgeBg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        badgeBg.setAttribute("x", "205");
        badgeBg.setAttribute("y", "358");
        badgeBg.setAttribute("width", "270");
        badgeBg.setAttribute("height", "34");
        badgeBg.setAttribute("rx", "7");
        badgeBg.setAttribute("fill", centerBannerBg);
        badgeBg.setAttribute("stroke", centerBannerBorder);
        badgeBg.setAttribute("stroke-width", "1.2");
        svg.appendChild(badgeBg);

        if (isD1) {
            // Blinking cyan dot inside D1 center Rasi banner
            svg.appendChild(this.createBlinkDot(222, 375, 4.5, isLight ? "#0284c7" : "#38bdf8"));
        } else if (isD9) {
            // Blinking green dot inside D9 center Lagna banner
            svg.appendChild(this.createBlinkDot(222, 375, 4.5, "#10b981"));
        }

        const badgeTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
        badgeTxt.setAttribute("x", (isD1 || isD9) ? 346 : 340);
        badgeTxt.setAttribute("y", 380);
        badgeTxt.setAttribute("text-anchor", "middle");
        badgeTxt.setAttribute("font-size", "14px");
        badgeTxt.setAttribute("font-weight", "800");
        badgeTxt.setAttribute("fill", centerBannerColor);
        badgeTxt.textContent = centerBannerLabel;
        svg.appendChild(badgeTxt);

        if (isD1) {
            // Secondary Center Banner in D-1: Moon's Nakshatra & Pada in English and Tamil
            const moonSign = signsData.find(s => s.planets && s.planets.some(p => p.short === 'Mo' || p.name === 'Moon' || (p.label && p.label.includes('Moon'))));
            const moonPlanet = moonSign ? moonSign.planets.find(p => p.short === 'Mo' || p.name === 'Moon' || (p.label && p.label.includes('Moon'))) : null;

            let nakEn = moonPlanet ? (moonPlanet.nakshatra || "") : "";
            let nakTa = moonPlanet ? (moonPlanet.nakshatra_tamil || "") : "";
            let pada = (moonPlanet && moonPlanet.pada !== undefined && moonPlanet.pada !== null) ? moonPlanet.pada : "";

            // Fallback: calculate from Moon longitude / degree if properties missing
            if ((!nakEn || !nakTa || !pada) && moonPlanet && moonPlanet.deg !== undefined && moonSign) {
                const absL = (moonSign.rasi_id * 30.0) + moonPlanet.deg;
                const nIdx = Math.floor(absL / (360.0 / 27.0));
                const pNum = Math.floor(((absL / (360.0 / 27.0)) - nIdx) * 4) + 1;
                if (!pada) pada = pNum;
                if (!nakTa && NAKSHATRA_TAMIL[nIdx % 27]) nakTa = NAKSHATRA_TAMIL[nIdx % 27];
                if (!nakEn && NAKSHATRA_EN[nIdx % 27]) nakEn = NAKSHATRA_EN[nIdx % 27];
            }

            // Clean any trailing pada from nakshatra names if present
            if (nakEn) nakEn = nakEn.replace(/[-\s]\d+$/, '').trim();
            if (nakTa) nakTa = nakTa.replace(/[-\s]\d+$/, '').trim();

            let starDisplay = "";
            if (nakEn && nakTa) {
                starDisplay = pada ? `${nakEn}-${pada} / ${nakTa}-${pada}` : `${nakEn} / ${nakTa}`;
            } else if (nakEn) {
                starDisplay = pada ? `${nakEn}-${pada}` : nakEn;
            } else if (nakTa) {
                starDisplay = pada ? `${nakTa}-${pada}` : nakTa;
            }

            if (starDisplay) {
                const starBannerLabel = `✨ Star: ${starDisplay}`;
                const starBannerBg = isLight ? "rgba(217, 119, 6, 0.10)" : "rgba(251, 191, 36, 0.14)";
                const starBannerBorder = isLight ? "#d97706" : "#fbbf24";
                const starBannerColor = isLight ? "#92400e" : "#fef08a";
                const starDotColor = isLight ? "#d97706" : "#fbbf24";

                const starBadgeBg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                starBadgeBg.setAttribute("x", "205");
                starBadgeBg.setAttribute("y", "400");
                starBadgeBg.setAttribute("width", "270");
                starBadgeBg.setAttribute("height", "32");
                starBadgeBg.setAttribute("rx", "7");
                starBadgeBg.setAttribute("fill", starBannerBg);
                starBadgeBg.setAttribute("stroke", starBannerBorder);
                starBadgeBg.setAttribute("stroke-width", "1.2");
                svg.appendChild(starBadgeBg);

                // Blinking amber star dot inside Star banner
                svg.appendChild(this.createBlinkDot(222, 416, 4.5, starDotColor));

                // Dynamic font size scaling to prevent clipping on longer nakshatras
                let starFontSize = "12.5px";
                if (starBannerLabel.length > 38) {
                    starFontSize = "10.5px";
                } else if (starBannerLabel.length > 32) {
                    starFontSize = "11.5px";
                }

                const starBadgeTxt = document.createElementNS("http://www.w3.org/2000/svg", "text");
                starBadgeTxt.setAttribute("x", "346");
                starBadgeTxt.setAttribute("y", "421");
                starBadgeTxt.setAttribute("text-anchor", "middle");
                starBadgeTxt.setAttribute("font-size", starFontSize);
                starBadgeTxt.setAttribute("font-weight", "700");
                starBadgeTxt.setAttribute("fill", starBannerColor);
                starBadgeTxt.textContent = starBannerLabel;
                svg.appendChild(starBadgeTxt);
            }
        }



        this.container.appendChild(svg);
    }
}