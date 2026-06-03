// ── Price formatting ──────────────────────────────────────────────────────────
export function priceInGold(copper) {
  if (!copper) return "0 мм";
  for (const [rate, abbr] of [[100, "зм"], [10, "см"], [1, "мм"]]) {
    if (copper >= rate && copper % rate === 0) return `${copper / rate} ${abbr}`;
  }
  return `${(copper / 100).toPrecision(2)} зм`;
}

// ── Rarity badge ──────────────────────────────────────────────────────────────
const RARITY_COLORS = {
  "обычный": "#9d9d9d",   "обычное": "#9d9d9d",   "обычная": "#9d9d9d",
  "необычный": "#1eff00", "необычное": "#1eff00",  "необычная": "#1eff00",
  "редкий": "#0070dd",    "редкое": "#0070dd",     "редкая": "#0070dd",
  "очень редкий": "#a335ee", "очень редкое": "#a335ee", "очень редкая": "#a335ee",
  "легендарный": "#ff8000", "легендарное": "#ff8000",
  "артефакт": "#e6cc80",
  "редкость варьируется": "#c0c0c0",
};

export function RarityBadge({ rarity }) {
  if (!rarity) return null;
  const color = RARITY_COLORS[rarity.toLowerCase()] || "#9d9d9d";
  return <span className="rarity-badge" style={{ color }}>{rarity}</span>;
}

// ── Placeholder SVGs ──────────────────────────────────────────────────────────
export const PLACEHOLDER_SVGS = (() => {
  const p = { fill: "none", stroke: "#c9a84c", strokeWidth: "1.5", strokeLinecap: "round", strokeLinejoin: "round", opacity: "0.45" };
  return {
    weapon: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <line x1="30" y1="7" x2="30" y2="44"/>
        <line x1="20" y1="27" x2="40" y2="27"/>
        <path d="M28 44 L30 53 L32 44"/>
        <circle cx="30" cy="7" r="2" fill="rgba(201,168,76,0.2)"/>
      </svg>
    ),
    armor: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <path d="M30 8 L42 14 L42 30 Q42 46 30 52 Q18 46 18 30 L18 14 Z"/>
        <path d="M30 8 Q30 20 30 52" strokeOpacity="0.4"/>
        <path d="M20 22 Q30 26 40 22" strokeOpacity="0.4"/>
      </svg>
    ),
    shield: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <path d="M30 7 L52 17 L52 35 Q52 50 30 56 Q8 50 8 35 L8 17 Z"/>
        <path d="M30 16 L43 22 L43 34 Q43 44 30 49 Q17 44 17 34 L17 22 Z" strokeOpacity="0.35"/>
      </svg>
    ),
    potion: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <path d="M24 22 L24 10 L36 10 L36 22 L46 40 Q50 55 30 55 Q10 55 14 40 Z"/>
        <line x1="22" y1="12" x2="38" y2="12"/>
        <ellipse cx="30" cy="42" rx="9" ry="5" fill="rgba(201,168,76,0.15)"/>
        <path d="M20 30 Q25 27 30 30" strokeOpacity="0.5"/>
      </svg>
    ),
    scroll: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <path d="M16 14 Q16 7 23 7 L50 7 Q57 7 57 14 L57 46 Q57 53 50 53 L23 53 Q16 53 16 46 L16 14 Z"/>
        <path d="M16 14 Q9 14 9 21 L9 46 Q9 53 16 53"/>
        <line x1="24" y1="20" x2="49" y2="20"/>
        <line x1="24" y1="28" x2="49" y2="28"/>
        <line x1="24" y1="36" x2="39" y2="36"/>
      </svg>
    ),
    ring: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <ellipse cx="30" cy="36" rx="15" ry="9"/>
        <ellipse cx="30" cy="27" rx="15" ry="9"/>
        <line x1="15" y1="27" x2="15" y2="36"/>
        <line x1="45" y1="27" x2="45" y2="36"/>
        <polygon points="30,10 36,22 24,22" fill="rgba(201,168,76,0.2)"/>
        <line x1="28" y1="22" x2="26" y2="27" strokeOpacity="0.4"/>
        <line x1="32" y1="22" x2="34" y2="27" strokeOpacity="0.4"/>
      </svg>
    ),
    wand: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <line x1="10" y1="50" x2="44" y2="16"/>
        <circle cx="47" cy="13" r="5" fill="rgba(201,168,76,0.15)"/>
        <line x1="47" y1="6" x2="47" y2="3"/>
        <line x1="52" y1="9" x2="55" y2="7"/>
        <line x1="54" y1="14" x2="57" y2="14"/>
        <line x1="52" y1="18" x2="54" y2="21"/>
        <line x1="42" y1="8" x2="40" y2="5"/>
      </svg>
    ),
    staff: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <line x1="30" y1="55" x2="30" y2="18"/>
        <circle cx="30" cy="13" r="7" fill="rgba(201,168,76,0.1)"/>
        <circle cx="30" cy="13" r="4" fill="rgba(201,168,76,0.2)"/>
        <path d="M23 32 Q30 27 37 32" strokeOpacity="0.5"/>
        <path d="M24 40 Q30 36 36 40" strokeOpacity="0.3"/>
      </svg>
    ),
    artifact: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <polygon points="30,4 35,22 53,22 39,33 44,51 30,40 16,51 21,33 7,22 25,22" fill="rgba(201,168,76,0.08)"/>
        <polygon points="30,13 33,23 43,23 35,29 38,39 30,33 22,39 25,29 17,23 27,23" fill="rgba(201,168,76,0.12)" strokeOpacity="0.5"/>
      </svg>
    ),
    wondrous: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <circle cx="30" cy="30" r="20"/>
        <circle cx="30" cy="30" r="13" strokeOpacity="0.4"/>
        <path d="M30 10 L30 16 M30 44 L30 50 M10 30 L16 30 M44 30 L50 30" strokeOpacity="0.6"/>
        <path d="M16 16 L20 20 M40 40 L44 44 M44 16 L40 20 M20 40 L16 44" strokeOpacity="0.4" strokeWidth="1"/>
        <circle cx="30" cy="30" r="4" fill="rgba(201,168,76,0.2)"/>
      </svg>
    ),
    magic: (
      <svg viewBox="0 0 80 80" width="60" height="60" fill="none">
        <polygon points="40,10 45,32 68,32 50,46 57,68 40,54 23,68 30,46 12,32 35,32"
          stroke="#c9a84c" strokeWidth="2" fill="rgba(201,168,76,0.1)"/>
      </svg>
    ),
    default: (
      <svg viewBox="0 0 60 60" width="52" height="52" {...p}>
        <polygon points="30,6 54,20 54,40 30,54 6,40 6,20" fill="rgba(201,168,76,0.06)"/>
        <polygon points="30,14 46,23 46,37 30,46 14,37 14,23" strokeOpacity="0.4"/>
        <circle cx="30" cy="30" r="5" fill="rgba(201,168,76,0.2)"/>
      </svg>
    ),
  };
})();

// ── Placeholder kind detection ────────────────────────────────────────────────
export function getPlaceholderKind(item, section) {
  const sec = section || (item.item_type === "magic_item" ? "magic" : "equipment");
  const t = (sec === "magic"
    ? (item.type || "") + " " + (item.rarity || "")
    : (item.category || "") + " " + (item.type || "")
  ).toLowerCase();

  if (/оружие|меч|кинжал|топор|копь|лук|арбалет|дубин|булав|молот|серп|коса|праща|рапир|шпаг|сабл|фехт/.test(t)) return "weapon";
  if (/доспех|броня|кольчуг|латы|нагрудник|кираса/.test(t)) return "armor";
  if (/щит/.test(t)) return "shield";
  if (/зелье/.test(t)) return "potion";
  if (/свиток/.test(t)) return "scroll";
  if (/кольцо/.test(t)) return "ring";
  if (/волшебная палочка|жезл/.test(t)) return "wand";
  if (/посох/.test(t)) return "staff";
  if (/артефакт/.test(t)) return "artifact";
  if (/чудесный/.test(t)) return "wondrous";
  return "default";
}
