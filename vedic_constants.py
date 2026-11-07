"""
Vedic Astrology Constants, Metadata, and Descriptions
Reference: PyJHora, Brihat Parashara Hora Shastra, Jaimini Sutras
Dual Language: English and Tamil (strictly avoiding Hindi / Devanagari)
"""

RASHIS = [
    {
        "id": 0, "name": "Aries", "tamil": "மேஷம்", "dual": "Aries / மேஷம்",
        "sanskrit": "Mesha (மேஷம்)", "symbol": "♈",
        "lord": "Mars", "lord_tamil": "செவ்வாய்", "lord_sanskrit": "Mangala / செவ்வாய்",
        "element": "Fire / நெருப்பு (Agni)", "modality": "Movable / சரம் (Chara)",
        "gender": "Male / ஆண்", "color": "#ef4444",
        "body_part": "Head, Brain / தலை, மூளை",
        "attributes": "Courageous, Pioneering, Energetic, Direct / தைரியம், தலைமை, வேகம்"
    },
    {
        "id": 1, "name": "Taurus", "tamil": "ரிஷபம்", "dual": "Taurus / ரிஷபம்",
        "sanskrit": "Rishabha (ரிஷபம்)", "symbol": "♉",
        "lord": "Venus", "lord_tamil": "சுக்கிரன்", "lord_sanskrit": "Shukra / சுக்கிரன்",
        "element": "Earth / நிலம் (Prithvi)", "modality": "Fixed / ஸ்திரம் (Sthira)",
        "gender": "Female / பெண்", "color": "#10b981",
        "body_part": "Face, Throat, Neck / முகம், தொண்டை, கழுத்து",
        "attributes": "Stable, Sensual, Enduring, Resourceful / உறுதி, அழகு, பொறுமை, செல்வம்"
    },
    {
        "id": 2, "name": "Gemini", "tamil": "மிதுனம்", "dual": "Gemini / மிதுனம்",
        "sanskrit": "Mithuna (மிதுனம்)", "symbol": "♊",
        "lord": "Mercury", "lord_tamil": "புதன்", "lord_sanskrit": "Budha / புதன்",
        "element": "Air / காற்று (Vayu)", "modality": "Dual / உபயம் (Dvisvabhava)",
        "gender": "Male / ஆண்", "color": "#f59e0b",
        "body_part": "Shoulders, Arms, Hands / தோள்கள், கைகள்",
        "attributes": "Intellectual, Communicative, Adaptable, Curious / புத்தி கூர்மை, பேச்சு, கற்பனை"
    },
    {
        "id": 3, "name": "Cancer", "tamil": "கடகம்", "dual": "Cancer / கடகம்",
        "sanskrit": "Kataka (கடகம்)", "symbol": "♋",
        "lord": "Moon", "lord_tamil": "சந்திரன்", "lord_sanskrit": "Chandra / சந்திரன்",
        "element": "Water / நீர் (Jala)", "modality": "Movable / சரம் (Chara)",
        "gender": "Female / பெண்", "color": "#06b6d4",
        "body_part": "Chest, Heart, Lungs / மார்பு, இதயம், நுரையீரல்",
        "attributes": "Nurturing, Intuitive, Emotional, Protective / பாசம், உள்ளுணர்வு, தயை"
    },
    {
        "id": 4, "name": "Leo", "tamil": "சிம்மம்", "dual": "Leo / சிம்மம்",
        "sanskrit": "Simha (சிம்மம்)", "symbol": "♌",
        "lord": "Sun", "lord_tamil": "சூரியன்", "lord_sanskrit": "Surya / சூரியன்",
        "element": "Fire / நெருப்பு (Agni)", "modality": "Fixed / ஸ்திரம் (Sthira)",
        "gender": "Male / ஆண்", "color": "#f97316",
        "body_part": "Upper Spine, Heart / முதுகுத்தண்டு, இதயம்",
        "attributes": "Regal, Magnanimous, Creative, Authoritative / கம்பீரம், பெருந்தன்மை, அதிகாரம்"
    },
    {
        "id": 5, "name": "Virgo", "tamil": "கன்னி", "dual": "Virgo / கன்னி",
        "sanskrit": "Kanya (கன்னி)", "symbol": "♍",
        "lord": "Mercury", "lord_tamil": "புதன்", "lord_sanskrit": "Budha / புதன்",
        "element": "Earth / நிலம் (Prithvi)", "modality": "Dual / உபயம் (Dvisvabhava)",
        "gender": "Female / பெண்", "color": "#84cc16",
        "body_part": "Digestive System, Intestines / செரிமான பகுதி, குடல்",
        "attributes": "Analytical, Service-oriented, Meticulous, Practical / நுட்பமான பகுப்பாய்வு, சேவை, நிர்வாகம்"
    },
    {
        "id": 6, "name": "Libra", "tamil": "துலாம்", "dual": "Libra / துலாம்",
        "sanskrit": "Thula (துலாம்)", "symbol": "♎",
        "lord": "Venus", "lord_tamil": "சுக்கிரன்", "lord_sanskrit": "Shukra / சுக்கிரன்",
        "element": "Air / காற்று (Vayu)", "modality": "Movable / சரம் (Chara)",
        "gender": "Male / ஆண்", "color": "#ec4899",
        "body_part": "Lower Back, Kidneys / இடுப்பு, சிறுநீரகம்",
        "attributes": "Harmonious, Diplomatic, Aesthetic, Just / சமநிலை, நீதி, அமைதி, கலை நேர்த்தி"
    },
    {
        "id": 7, "name": "Scorpio", "tamil": "விருச்சிகம்", "dual": "Scorpio / விருச்சிகம்",
        "sanskrit": "Vrischika (விருச்சிகம்)", "symbol": "♏",
        "lord": "Mars / Ketu", "lord_tamil": "செவ்வாய் / கேது", "lord_sanskrit": "Mangala / Ketu",
        "element": "Water / நீர் (Jala)", "modality": "Fixed / ஸ்திரம் (Sthira)",
        "gender": "Female / பெண்", "color": "#b91c1c",
        "body_part": "Generative Organs, Pelvis / பிறப்புறுப்புகள், இடுப்பு எலும்பு",
        "attributes": "Intense, Transformative, Mystical, Penetrating / ஆழ்ந்த ஞானம், மாற்றம், ரகசியம்"
    },
    {
        "id": 8, "name": "Sagittarius", "tamil": "தனுசு", "dual": "Sagittarius / தனுசு",
        "sanskrit": "Dhanus (தனுசு)", "symbol": "♐",
        "lord": "Jupiter", "lord_tamil": "குரு", "lord_sanskrit": "Guru / குரு",
        "element": "Fire / நெருப்பு (Agni)", "modality": "Dual / உபயம் (Dvisvabhava)",
        "gender": "Male / ஆண்", "color": "#8b5cf6",
        "body_part": "Thighs, Hips / தொடைகள், இடுப்பு",
        "attributes": "Philosophical, Optimistic, Truth-seeking, Expansive / தர்மம், ஆன்மீகம், நம்பிக்கை, அறிவு"
    },
    {
        "id": 9, "name": "Capricorn", "tamil": "மகரம்", "dual": "Capricorn / மகரம்",
        "sanskrit": "Makara (மகரம்)", "symbol": "♑",
        "lord": "Saturn", "lord_tamil": "சனி", "lord_sanskrit": "Shani / சனி",
        "element": "Earth / நிலம் (Prithvi)", "modality": "Movable / சரம் (Chara)",
        "gender": "Female / பெண்", "color": "#64748b",
        "body_part": "Knees, Bones, Joints / முழங்கால், எலும்புகள்",
        "attributes": "Disciplined, Ambitious, Patient, Structured / உழைப்பு, ஒழுக்கம், பொறுமை, இலக்கு"
    },
    {
        "id": 10, "name": "Aquarius", "tamil": "கும்பம்", "dual": "Aquarius / கும்பம்",
        "sanskrit": "Kumbha (கும்பம்)", "symbol": "♒",
        "lord": "Saturn / Rahu", "lord_tamil": "சனி / ராகு", "lord_sanskrit": "Shani / Rahu",
        "element": "Air / காற்று (Vayu)", "modality": "Fixed / ஸ்திரம் (Sthira)",
        "gender": "Male / ஆண்", "color": "#0ea5e9",
        "body_part": "Calves, Ankles, Circulation / கணுக்கால், ரத்த ஓட்டம்",
        "attributes": "Humanitarian, Visionary, Scientific, Unconventional / மக்கள் நலம், அறிவியல் நோக்கு, புதுமை"
    },
    {
        "id": 11, "name": "Pisces", "tamil": "மீனம்", "dual": "Pisces / மீனம்",
        "sanskrit": "Meena (மீனம்)", "symbol": "♓",
        "lord": "Jupiter", "lord_tamil": "குரு", "lord_sanskrit": "Guru / குரு",
        "element": "Water / நீர் (Jala)", "modality": "Dual / உபயம் (Dvisvabhava)",
        "gender": "Female / பெண்", "color": "#a855f7",
        "body_part": "Feet, Lymphatic System / பாதங்கள், நிணநீர் மண்டலம்",
        "attributes": "Compassionate, Transcendent, Imaginative, Spiritual / கருணை, பக்தி, மோட்ச நாட்டம்"
    }
]

GRAHAS = [
    {
        "id": 0, "key": "Sun", "name": "Sun", "tamil": "சூரியன்", "dual": "Sun / சூரியன்",
        "sanskrit": "Surya (சூரியன்)", "symbol": "☉",
        "nature": "Malefic / கொடிய கிரகம் (Krura)", "gender": "Male / ஆண்", "caste": "Kshatriya",
        "exaltation": "Aries 10° / மேஷம் 10° (உச்சம்)", "debilitation": "Libra 10° / துலாம் 10° (நீசம்)",
        "own_sign": "Leo / சிம்மம் (ஆட்சி)",
        "gemstone": "Ruby / மாணிக்கம் (Manikkam)", "color": "#f59e0b",
        "day": "Sunday / ஞாயிறு", "day_tamil": "ஞாயிறு",
        "significations": "Soul, Father, Royalty, Vitality, Authority, Government / ஆத்மா, தந்தை, அதிகாரம், அரசாங்கம், உடல் பலம்"
    },
    {
        "id": 1, "key": "Moon", "name": "Moon", "tamil": "சந்திரன்", "dual": "Moon / சந்திரன்",
        "sanskrit": "Chandra (சந்திரன்)", "symbol": "☾",
        "nature": "Benefic / சுப கிரகம் (Saumya)", "gender": "Female / பெண்", "caste": "Vaishya",
        "exaltation": "Taurus 3° / ரிஷபம் 3° (உச்சம்)", "debilitation": "Scorpio 3° / விருச்சிகம் 3° (நீசம்)",
        "own_sign": "Cancer / கடகம் (ஆட்சி)",
        "gemstone": "Pearl / முத்து (Muthu)", "color": "#e2e8f0",
        "day": "Monday / திங்கள்", "day_tamil": "திங்கள்",
        "significations": "Mind, Mother, Emotions, Memory, Peace / மனம், தாய், எண்ணங்கள், அமைதி, நீர்ச்சத்து"
    },
    {
        "id": 2, "key": "Mars", "name": "Mars", "tamil": "செவ்வாய்", "dual": "Mars / செவ்வாய்",
        "sanskrit": "Mangala / Sevvai (செவ்வாய்)", "symbol": "♂",
        "nature": "Malefic / கொடிய கிரகம் (Krura)", "gender": "Male / ஆண்", "caste": "Kshatriya",
        "exaltation": "Capricorn 28° / மகரம் 28° (உச்சம்)", "debilitation": "Cancer 28° / கடகம் 28° (நீசம்)",
        "own_sign": "Aries, Scorpio / மேஷம், விருச்சிகம் (ஆட்சி)",
        "gemstone": "Red Coral / பவளம் (Pavalam)", "color": "#ef4444",
        "day": "Tuesday / செவ்வாய்", "day_tamil": "செவ்வாய்",
        "significations": "Energy, Siblings, Courage, Land, Passion, Combat / வீரம், சகோதரன், நிலம், ரத்தம், ஆற்றல்"
    },
    {
        "id": 3, "key": "Mercury", "name": "Mercury", "tamil": "புதன்", "dual": "Mercury / புதன்",
        "sanskrit": "Budha (புதன்)", "symbol": "☿",
        "nature": "Benefic / சுப கிரகம் (Saumya)", "gender": "Neuter / அலி", "caste": "Vaishya",
        "exaltation": "Virgo 15° / கன்னி 15° (உச்சம்)", "debilitation": "Pisces 15° / மீனம் 15° (நீசம்)",
        "own_sign": "Gemini, Virgo / மிதுனம், கன்னி (ஆட்சி)",
        "gemstone": "Emerald / மரகதம் (Maragatham)", "color": "#10b981",
        "day": "Wednesday / புதன்", "day_tamil": "புதன்",
        "significations": "Intellect, Speech, Commerce, Logic, Communication / புத்தி, வாக்கு, கல்வி, வியாபாரம், தொடர்பு"
    },
    {
        "id": 4, "key": "Jupiter", "name": "Jupiter", "tamil": "குரு", "dual": "Jupiter / குரு",
        "sanskrit": "Guru / Brihaspati (குரு)", "symbol": "♃",
        "nature": "Supreme Benefic / முழு சுப கிரகம் (Parama Saumya)", "gender": "Male / ஆண்", "caste": "Brahmin",
        "exaltation": "Cancer 5° / கடகம் 5° (உச்சம்)", "debilitation": "Capricorn 5° / மகரம் 5° (நீசம்)",
        "own_sign": "Sagittarius, Pisces / தனுசு, மீனம் (ஆட்சி)",
        "gemstone": "Yellow Sapphire / புஷ்பராகம் (Pushparagam)", "color": "#eab308",
        "day": "Thursday / வியாழன்", "day_tamil": "வியாழன்",
        "significations": "Wisdom, Dharma, Children, Wealth, Spirituality / ஞானம், புத்திர பாக்கியம், தர்மம், செல்வம், அருள்"
    },
    {
        "id": 5, "key": "Venus", "name": "Venus", "tamil": "சுக்கிரன்", "dual": "Venus / சுக்கிரன்",
        "sanskrit": "Shukra (சுக்கிரன்)", "symbol": "♀",
        "nature": "Great Benefic / பெரும் சுப கிரகம் (Saumya)", "gender": "Female / பெண்", "caste": "Brahmin",
        "exaltation": "Pisces 27° / மீனம் 27° (உச்சம்)", "debilitation": "Virgo 27° / கன்னி 27° (நீசம்)",
        "own_sign": "Taurus, Libra / ரிஷபம், துலாம் (ஆட்சி)",
        "gemstone": "Diamond / வைரம் (Vairam)", "color": "#f472b6",
        "day": "Friday / வெள்ளி", "day_tamil": "வெள்ளி",
        "significations": "Love, Marriage, Arts, Luxury, Vehicles, Beauty / காதல், திருமணம், கலை, வாகனம், ஆடம்பரம், சுகம்"
    },
    {
        "id": 6, "key": "Saturn", "name": "Saturn", "tamil": "சனி", "dual": "Saturn / சனி",
        "sanskrit": "Shani (சனி)", "symbol": "♄",
        "nature": "Great Malefic / கர்ம கிரகம் (Krura/Papi)", "gender": "Neuter / அலி", "caste": "Shudra",
        "exaltation": "Libra 20° / துலாம் 20° (உச்சம்)", "debilitation": "Aries 20° / மேஷம் 20° (நீசம்)",
        "own_sign": "Capricorn, Aquarius / மகரம், கும்பம் (ஆட்சி)",
        "gemstone": "Blue Sapphire / நீலக்கல் (Neelakkal)", "color": "#3b82f6",
        "day": "Saturday / சனி", "day_tamil": "சனி",
        "significations": "Karma, Longevity, Discipline, Labor, Patience, Justice / கர்மா, ஆயுள், உழைப்பு, நீதி, பொறுமை"
    },
    {
        "id": 7, "key": "Rahu", "name": "Rahu", "tamil": "ராகு", "dual": "Rahu (North Node) / ராகு",
        "sanskrit": "Rahu (ராகு)", "symbol": "☊",
        "nature": "Shadow Malefic / நிழல் கிரகம் (Chhaya Graha)", "gender": "Female / பெண்", "caste": "Outcaste",
        "exaltation": "Taurus / Gemini (ரிஷபம் / மிதுனம்)", "debilitation": "Scorpio / Sagittarius (விருச்சிகம் / தனுசு)",
        "own_sign": "Aquarius / கும்பம் (இணை அதிபதி)",
        "gemstone": "Hessonite Garnet / கோமேதகம் (Gomedhakam)", "color": "#6366f1",
        "day": "Saturday/Tuesday / சனி/செவ்வாய்", "day_tamil": "சனி/செவ்வாய்",
        "significations": "Ambition, Material Desire, Foreign Travel, Innovation / பேராசை, மாயை, வெளிநாட்டு யோகம், நவீன அறிவியல்"
    },
    {
        "id": 8, "key": "Ketu", "name": "Ketu", "tamil": "கேது", "dual": "Ketu (South Node) / கேது",
        "sanskrit": "Ketu (கேது)", "symbol": "☋",
        "nature": "Moksha Karaka / ஞான மோட்ச கிரகம் (Spiritual)", "gender": "Neuter / அலி", "caste": "Outcaste",
        "exaltation": "Scorpio / Sagittarius (விருச்சிகம் / தனுசு)", "debilitation": "Taurus / Gemini (ரிஷபம் / மிதுனம்)",
        "own_sign": "Scorpio / விருச்சிகம் (இணை அதிபதி)",
        "gemstone": "Cat's Eye / வைடூரியம் (Vaidhooriyam)", "color": "#8b5cf6",
        "day": "Tuesday / செவ்வாய்", "day_tamil": "செவ்வாய்",
        "significations": "Moksha, Spiritual Wisdom, Renunciation, Occult / மோட்சம், ஆன்மீகம், பற்றற்ற நிலை, ஞானம்"
    }
]

NAKSHATRAS = [
    {"id": 1, "name": "Ashwini", "tamil": "அஸ்வினி", "lord": "Ketu", "lord_tamil": "கேது", "symbol": "Horse's Head / குதிரை முகம்", "deity": "Ashwini Kumaras (மருத்துவ தேவர்கள்)", "shakti": "Healing & Swiftness / நிவாரணம் & வேகம்"},
    {"id": 2, "name": "Bharani", "tamil": "பரணி", "lord": "Venus", "lord_tamil": "சுக்கிரன்", "symbol": "Yoni / முக்கோண அடுப்பு", "deity": "Yama (எமதர்மன்)", "shakti": "Restraint & Transformation / தாங்கும் ஆற்றல்"},
    {"id": 3, "name": "Krittika", "tamil": "கார்த்திகை", "lord": "Sun", "lord_tamil": "சூரியன்", "symbol": "Flame / தீப்பிழம்பு / கத்தி", "deity": "Agni (அக்னி பகவான்)", "shakti": "Purification & Radiance / தூய்மை & பிரகாசம்"},
    {"id": 4, "name": "Rohini", "tamil": "ரோகிணி", "lord": "Moon", "lord_tamil": "சந்திரன்", "symbol": "Chariot / தேர் / வண்டி", "deity": "Brahma / Prajapati (பிரம்மா)", "shakti": "Growth & Creation / வளர்ச்சி & வசீகரம்"},
    {"id": 5, "name": "Mrigashira", "tamil": "மிருகசீரிஷம்", "lord": "Mars", "lord_tamil": "செவ்வாய்", "symbol": "Deer's Head / மான் தலை", "deity": "Soma (சந்திர தேவன்)", "shakti": "Searching & Exploration / தேடல் & ஆராய்ச்சி"},
    {"id": 6, "name": "Ardra", "tamil": "திருவாதிரை", "lord": "Rahu", "lord_tamil": "ராகு", "symbol": "Teardrop / நீர்த்துளி / வைரம்", "deity": "Rudra / Lord Shiva (ருத்ரன் / சிவன்)", "shakti": "Transformation & Renewal / மாற்றம் & ஞானம்"},
    {"id": 7, "name": "Punarvasu", "tamil": "புனர்பூசம்", "lord": "Jupiter", "lord_tamil": "குரு", "symbol": "Bow and Quiver / வில்லும் அம்பறாத்தூணியும்", "deity": "Aditi (அதிதி தேவி)", "shakti": "Renewal & Return of Light / புத்துணர்வு"},
    {"id": 8, "name": "Pushya", "tamil": "பூசம்", "lord": "Saturn", "lord_tamil": "சனி", "symbol": "Cow's Udder / தாமரை / மடி", "deity": "Brihaspati (தேவகுரு)", "shakti": "Spiritual Nourishment / ஆன்மீக போஷணை"},
    {"id": 9, "name": "Ashlesha", "tamil": "ஆயில்யம்", "lord": "Mercury", "lord_tamil": "புதன்", "symbol": "Coiled Serpent / சுருண்ட பாம்பு", "deity": "Sarpas (நாக தேவதைகள்)", "shakti": "Wisdom & Kundalini / உள்ளுணர்வு & ஞானம்"},
    {"id": 10, "name": "Magha", "tamil": "மகம்", "lord": "Ketu", "lord_tamil": "கேது", "symbol": "Royal Throne / சிம்மாசனம்", "deity": "Pitris (பித்ருக்கள் / முன்னோர்கள்)", "shakti": "Regal Honor & Lineage / அதிகாரம் & முன்னோர்கள் அருள்"},
    {"id": 11, "name": "Purva Phalguni", "tamil": "பூரம்", "lord": "Venus", "lord_tamil": "சுக்கிரன்", "symbol": "Couch / ஊஞ்சல் / கட்டில்", "deity": "Bhaga (பாக தேவன்)", "shakti": "Affection & Prosperity / அன்பு & மகிழ்ச்சி"},
    {"id": 12, "name": "Uttara Phalguni", "tamil": "உத்திரம்", "lord": "Sun", "lord_tamil": "சூரியன்", "symbol": "Bed / மஞ்சம் / கட்டில் கால்", "deity": "Aryaman (அர்யமான்)", "shakti": "Generosity & Patronage / கொடை & மேன்மை"},
    {"id": 13, "name": "Hasta", "tamil": "அஸ்தம்", "lord": "Moon", "lord_tamil": "சந்திரன்", "symbol": "Open Palm / கை விரல்கள்", "deity": "Savitr (சாவித்ரு - சூரியன்)", "shakti": "Dexterity & Manifestation / கைவினைக் கலை & சித்தி"},
    {"id": 14, "name": "Chitra", "tamil": "சித்திரை", "lord": "Mars", "lord_tamil": "செவ்வாய்", "symbol": "Bright Jewel / மாணிக்க மணி", "deity": "Vishwakarma (விஸ்வகர்மா)", "shakti": "Design, Splendor & Form / கலை நேர்த்தி & அழகு"},
    {"id": 15, "name": "Swati", "tamil": "சுவாதி", "lord": "Rahu", "lord_tamil": "ராகு", "symbol": "Coral / இளம்பயிர் / பவளம்", "deity": "Vayu (வாயு பகவான்)", "shakti": "Independence & Agility / சுதந்திரம் & சுறுசுறுப்பு"},
    {"id": 16, "name": "Vishakha", "tamil": "விசாகம்", "lord": "Jupiter", "lord_tamil": "குரு", "symbol": "Triumphal Arch / வெற்றி வளைவு", "deity": "Indra-Agni (இந்திரன் & அக்னி)", "shakti": "Purposeful Ambition / வெற்றிக்கான வேட்கை"},
    {"id": 17, "name": "Anuradha", "tamil": "அனுஷம்", "lord": "Saturn", "lord_tamil": "சனி", "symbol": "Lotus Flower / தாமரை மலர்", "deity": "Mitra (மித்ர தேவன்)", "shakti": "Friendship & Devotion / நட்பு & பக்தி"},
    {"id": 18, "name": "Jyeshtha", "tamil": "கேட்டை", "lord": "Mercury", "lord_tamil": "புதன்", "symbol": "Umbrella / குடை / காப்பு", "deity": "Indra (இந்திரன்)", "shakti": "Seniority & Protection / தலைமை & பாதுகாப்பு"},
    {"id": 19, "name": "Mula", "tamil": "மூலம்", "lord": "Ketu", "lord_tamil": "கேது", "symbol": "Tied Roots / வேர்க்கொத்து", "deity": "Nirriti (நிருருதி தேவி)", "shakti": "Deep Exploration & Roots / மூலத்தை அறிதல்"},
    {"id": 20, "name": "Purva Ashadha", "tamil": "பூராடம்", "lord": "Venus", "lord_tamil": "சுக்கிரன்", "symbol": "Fan / முறம் / விசிறி", "deity": "Apas (வருண தேவதை)", "shakti": "Invincibility & Purity / தோல்வியற்ற வெற்றி"},
    {"id": 21, "name": "Uttara Ashadha", "tamil": "உத்திராடம்", "lord": "Sun", "lord_tamil": "சூரியன்", "symbol": "Elephant's Tusk / யானைத் தந்தம்", "deity": "Vishvadevas (விஸ்வேதேவர்கள்)", "shakti": "Final Victory & Endurance / நிலையான வெற்றி"},
    {"id": 22, "name": "Shravana", "tamil": "திருவோணம்", "lord": "Moon", "lord_tamil": "சந்திரன்", "symbol": "Ear / மூன்று பாதங்கள் / காது", "deity": "Lord Vishnu (மகாவிஷ்ணு)", "shakti": "Listening & Connection / கேட்டறிதல் & ஞானம்"},
    {"id": 23, "name": "Dhanishta", "tamil": "அவிட்டம்", "lord": "Mars", "lord_tamil": "செவ்வாய்", "symbol": "Mridangam / மிருதங்கம் / புல்லாங்குழல்", "deity": "Ashta Vasus (அஷ்ட வசுக்கள்)", "shakti": "Wealth & Harmony / செல்வம் & இசை"},
    {"id": 24, "name": "Shatabhisha", "tamil": "சதயம்", "lord": "Rahu", "lord_tamil": "ராகு", "symbol": "Empty Circle / வட்டம் / 100 மருத்துவர்கள்", "deity": "Varuna (வருண பகவான்)", "shakti": "Healing & Mystic Vision / நிவாரணம் & ரகசிய ஞானம்"},
    {"id": 25, "name": "Purva Bhadrapada", "tamil": "பூரட்டாதி", "lord": "Jupiter", "lord_tamil": "குரு", "symbol": "Front Legs of Cot / வாள் / கட்டிலின் முன்பகுதி", "deity": "Aja Ekapada (ஏகபாத மூர்த்தி)", "shakti": "Spiritual Fire & Tapas / தவ வலிமை"},
    {"id": 26, "name": "Uttara Bhadrapada", "tamil": "உத்திரட்டாதி", "lord": "Saturn", "lord_tamil": "சனி", "symbol": "Back Legs of Cot / கட்டிலின் பின்பகுதி", "deity": "Ahirbudhnya (அஹிர்புத்னியன்)", "shakti": "Kundalini & Peace / சாந்தம் & தியானம்"},
    {"id": 27, "name": "Revati", "tamil": "ரேவதி", "lord": "Mercury", "lord_tamil": "புதன்", "symbol": "Fish / ஜோடி மீன்கள் / படகு", "deity": "Pushan (பூஷா - வழிகாட்டும் தேவன்)", "shakti": "Nourishment & Safe Journey / பாதுகாப்பு & நிறைவு"}
]

BHAVAS = [
    {
        "house": 1, "tamil": "லக்னம் / உடல் - தன் பாவம்", "sanskrit": "Tanu Bhava (லக்னம் / உடல் பாவம்)",
        "name": "Ascendant / Lagna", "type": "Kendra & Trikona (Dharma / தர்ம கேந்திரம்)",
        "karaka": "Sun / சூரியன்",
        "significations": "Self, Physical body, Appearance, Vitality, Temperament / உயிர், உடல் அமைப்பு, ஆரோக்கியம், தோற்றம், தொடக்கம்"
    },
    {
        "house": 2, "tamil": "தன பாவம் / தனம் & குடும்பம்", "sanskrit": "Dhana Bhava (தன பாவம் / குடும்பம்)",
        "name": "Wealth & Family", "type": "Panaphara / Maraka (Artha / அர்த்த பாவம்)",
        "karaka": "Jupiter / குரு",
        "significations": "Accumulated wealth, Speech, Family lineage, Food intake, Right eye / குடும்பம், வாக்கு, சேமிப்பு செல்வம், உணவு, கண் பார்வை"
    },
    {
        "house": 3, "tamil": "சகஜ பாவம் / தைரியம் & இளைய சகோதரன்", "sanskrit": "Sahaja Bhava (சகஜ பாவம் / தைரியம்)",
        "name": "Siblings & Courage", "type": "Apoklima / Upachaya (Kama / உபசய பாவம்)",
        "karaka": "Mars / செவ்வாய்",
        "significations": "Younger siblings, Valour, Initiative, Short journeys, Communication, Hands / இளைய சகோதரன், வீரம், முயற்சி, குறுகிய பயணம், எழுத்து"
    },
    {
        "house": 4, "tamil": "சுக பாவம் / தாய் & சுகம் & வாகனம்", "sanskrit": "Sukha Bhava (சுக பாவம் / தாய்)",
        "name": "Mother & Happiness", "type": "Kendra (Moksha / மோட்ச கேந்திரம்)",
        "karaka": "Moon / சந்திரன்",
        "significations": "Mother, Heart, Happiness, Home, Lands, Vehicles, Education, Peace / தாய், வீடு, நிலம், வாகனம், ஆரம்பக் கல்வி, மன அமைதி"
    },
    {
        "house": 5, "tamil": "புத்திர பாவம் / பூர்வ புண்ணியம் & பிள்ளைகள்", "sanskrit": "Putra Bhava (புத்திர பாவம் / பூர்வ புண்ணியம்)",
        "name": "Children & Intellect", "type": "Trikona (Dharma / தர்ம திரிகோணம்)",
        "karaka": "Jupiter / குரு",
        "significations": "Past life merit (Purva Punya), Progeny, Intellect, Mantras, Speculation / பிள்ளைகள், பூர்வ புண்ணியம், கூர்மையான அறிவு, மந்திர சித்தி"
    },
    {
        "house": 6, "tamil": "ரிபு பாவம் / கடன், நோய், எதிரி", "sanskrit": "Ari / Runa Bhava (ரிபு பாவம் / கடன், நோய்)",
        "name": "Enemies & Disease", "type": "Dusthana / Upachaya (துஸ்தானம் / உபசயம்)",
        "karaka": "Mars / Saturn (செவ்வாய் / சனி)",
        "significations": "Debts, Diseases, Enemies, Litigation, Service, Competitive strength / கடன், நோய், எதிரிகள், வழக்கு, போட்டி, உழைப்பு"
    },
    {
        "house": 7, "tamil": "களத்திர பாவம் / வாழ்க்கைத்துணை & கூட்டணி", "sanskrit": "Kalathra Bhava (களத்திர பாவம் / வாழ்க்கைத்துணை)",
        "name": "Spouse & Partnerships", "type": "Kendra / Maraka (காம கேந்திரம்)",
        "karaka": "Venus / சுக்கிரன்",
        "significations": "Marriage partner, Business alliances, Public relations, Foreign residence / கணவன் / மனைவி, கூட்டுத் தொழில், வெளிநாட்டு பயணம்"
    },
    {
        "house": 8, "tamil": "ஆயுள் பாவம் / ஆயுள் & மரணம்", "sanskrit": "Ayur / Randhra Bhava (ஆயுள் பாவம்)",
        "name": "Longevity & Transformation", "type": "Dusthana (Moksha / துஸ்தானம்)",
        "karaka": "Saturn / சனி",
        "significations": "Longevity, Sudden events, Occult knowledge, Chronic ailments, Inheritance / ஆயுள், எதிர்பாராத நிகழ்வுகள், மறைபொருள் அறிவு, உயில்"
    },
    {
        "house": 9, "tamil": "பாக்கிய பாவம் / தந்தை, தர்மம் & குரு", "sanskrit": "Bhagya / Dharma Bhava (பாக்கிய பாவம் / தர்மம்)",
        "name": "Fortune & Wisdom", "type": "Trikona (Dharma / தர்ம திரிகோணம்)",
        "karaka": "Jupiter / Sun (குரு / சூரியன்)",
        "significations": "Guru, Father, Dharma, Higher philosophy, Good fortune, Pilgrimages / தந்தை, குரு, அதிர்ஷ்டம், ஆன்மீக யாத்திரை, தெய்வ பக்தி"
    },
    {
        "house": 10, "tamil": "கர்ம பாவம் / தொழில் & கீர்த்தி", "sanskrit": "Karma Bhava (கர்ம பாவம் / தொழில்)",
        "name": "Career & Reputation", "type": "Kendra / Upachaya (கர்ம கேந்திரம்)",
        "karaka": "Mercury / Sun / Jupiter / Saturn",
        "significations": "Profession, Fame, Social status, Authority, Public deeds, Government / தொழில், உத்தியோகம், சமூக அந்தஸ்து, புகழ், அதிகாரம்"
    },
    {
        "house": 11, "tamil": "லாப பாவம் / லாபம் & மூத்த சகோதரன்", "sanskrit": "Labha Bhava (லாப பாவம் / வருமானம்)",
        "name": "Gains & Aspirations", "type": "Panaphara / Upachaya (லாப பாவம்)",
        "karaka": "Jupiter / குரு",
        "significations": "Income, Realization of hopes, Elder siblings, Large circles, Success / வருமானம், லாபம், மூத்த சகோதரன், விருப்பங்கள் நிறைவேறுதல்"
    },
    {
        "house": 12, "tamil": "விரய பாவம் / விரயம் & மோட்சம்", "sanskrit": "Vyaya Bhava (விரய பாவம் / மோட்சம்)",
        "name": "Losses & Liberation", "type": "Dusthana (Moksha / விரய துஸ்தானம்)",
        "karaka": "Saturn / Ketu (சனி / கேது)",
        "significations": "Moksha (Liberation), Foreign lands, Expenses, Solitude, Meditation / சுப விரயம், வெளிநாடு, தூக்கம், தனிமை, மோட்சம்"
    }
]
