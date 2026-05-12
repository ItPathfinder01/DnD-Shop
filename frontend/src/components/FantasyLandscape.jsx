export default function FantasyLandscape() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 1440 900"
      preserveAspectRatio="xMidYMid slice"
      style={{ position: "fixed", inset: 0, width: "100%", height: "100%", zIndex: 0 }}
    >
      <defs>
        {/* Небо */}
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stopColor="#04051a"/>
          <stop offset="40%"  stopColor="#0a0e35"/>
          <stop offset="75%"  stopColor="#1a1040"/>
          <stop offset="100%" stopColor="#2d1b5e"/>
        </linearGradient>
        {/* Луна */}
        <radialGradient id="moon" cx="50%" cy="50%" r="50%">
          <stop offset="0%"   stopColor="#fffbe6"/>
          <stop offset="60%"  stopColor="#f5d97a"/>
          <stop offset="100%" stopColor="#c9943a" stopOpacity="0"/>
        </radialGradient>
        {/* Ореол луны */}
        <radialGradient id="moonGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%"  stopColor="#f5d97a" stopOpacity="0.25"/>
          <stop offset="100%" stopColor="#f5d97a" stopOpacity="0"/>
        </radialGradient>
        {/* Туман */}
        <linearGradient id="mist" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"  stopColor="#7b6fff" stopOpacity="0"/>
          <stop offset="60%" stopColor="#9b8fdd" stopOpacity="0.18"/>
          <stop offset="100%" stopColor="#c8beff" stopOpacity="0.32"/>
        </linearGradient>
        {/* Дальние горы */}
        <linearGradient id="mtn1" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#1e1250"/>
          <stop offset="100%" stopColor="#2d1b5e"/>
        </linearGradient>
        {/* Средние горы */}
        <linearGradient id="mtn2" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#120d38"/>
          <stop offset="100%" stopColor="#1a1040"/>
        </linearGradient>
        {/* Лес */}
        <linearGradient id="forest" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0a1a0e"/>
          <stop offset="100%" stopColor="#050d06"/>
        </linearGradient>
        {/* Луг */}
        <linearGradient id="meadow" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0d1f10"/>
          <stop offset="100%" stopColor="#060f08"/>
        </linearGradient>
        {/* Свечение от луны на земле */}
        <radialGradient id="groundGlow" cx="50%" cy="0%" r="60%">
          <stop offset="0%"   stopColor="#9b8fdd" stopOpacity="0.15"/>
          <stop offset="100%" stopColor="#9b8fdd" stopOpacity="0"/>
        </radialGradient>
        <filter id="blur2">
          <feGaussianBlur stdDeviation="2"/>
        </filter>
        <filter id="blur8">
          <feGaussianBlur stdDeviation="8"/>
        </filter>
      </defs>

      {/* Небо */}
      <rect width="1440" height="900" fill="url(#sky)"/>

      {/* Звёзды */}
      {[
        [80,40],[150,90],[230,30],[320,70],[400,20],[500,55],[590,35],[680,15],[760,60],[840,25],
        [920,50],[1010,80],[1100,40],[1180,65],[1270,30],[1360,55],[1420,20],[60,120],[180,110],
        [300,140],[440,100],[580,130],[720,90],[860,120],[1000,110],[1140,95],[1300,115],[1400,90],
        [110,160],[260,180],[410,155],[560,170],[710,150],[870,165],[1030,145],[1200,175],[50,200],
        [200,210],[370,195],[520,220],[670,205],[820,215],[980,200],[1150,210],[1320,190],[1430,215],
        [130,240],[290,260],[450,245],[600,255],[760,240],[900,265],[1060,250],[1220,260],[340,280],
        [490,290],[650,275],[810,285],[960,270],[1110,280],[1280,275],
      ].map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r={Math.random() > 0.8 ? 1.4 : 0.8}
          fill="white" opacity={0.5 + (i % 5) * 0.1}/>
      ))}

      {/* Ореол луны */}
      <circle cx="900" cy="140" r="120" fill="url(#moonGlow)" filter="url(#blur8)"/>
      {/* Луна */}
      <circle cx="900" cy="140" r="54" fill="url(#moon)"/>
      {/* Кратеры луны */}
      <circle cx="880" cy="125" r="7" fill="#e8c85a" opacity="0.3"/>
      <circle cx="915" cy="155" r="5" fill="#e8c85a" opacity="0.2"/>
      <circle cx="895" cy="148" r="3" fill="#d4b050" opacity="0.25"/>

      {/* Замок на горе вдали */}
      <g opacity="0.55" fill="#12093a">
        {/* Основание */}
        <rect x="670" y="320" width="80" height="60"/>
        {/* Башни */}
        <rect x="660" y="295" width="20" height="85"/>
        <rect x="730" y="300" width="18" height="80"/>
        <rect x="695" y="285" width="22" height="95"/>
        {/* Зубцы */}
        <rect x="660" y="290" width="6" height="8"/>
        <rect x="668" y="290" width="6" height="8"/>
        <rect x="695" y="280" width="6" height="8"/>
        <rect x="703" y="280" width="6" height="8"/>
        <rect x="711" y="280" width="6" height="8"/>
        <rect x="730" y="295" width="5" height="7"/>
        <rect x="737" y="295" width="5" height="7"/>
        {/* Окошко с огнём */}
        <rect x="698" y="320" width="8" height="12" fill="#c9a84c" opacity="0.7"/>
      </g>

      {/* Дальние горы */}
      <path d="M0,480 L120,310 L200,390 L310,270 L420,360 L540,250 L630,340 L720,280 L820,370 L930,240 L1020,330 L1130,260 L1240,350 L1340,280 L1440,360 L1440,900 L0,900Z"
        fill="url(#mtn1)"/>

      {/* Снег на дальних вершинах */}
      <path d="M120,310 L140,335 L100,335Z M310,270 L335,300 L285,300Z M540,250 L562,278 L518,278Z M720,280 L742,305 L698,305Z M930,240 L955,268 L905,268Z M1130,260 L1152,285 L1108,285Z"
        fill="white" opacity="0.25"/>

      {/* Средние горы */}
      <path d="M0,560 L80,420 L180,500 L280,390 L380,470 L500,380 L600,450 L710,400 L810,480 L920,370 L1020,450 L1130,395 L1230,465 L1340,410 L1440,480 L1440,900 L0,900Z"
        fill="url(#mtn2)"/>

      {/* Лес — деревья */}
      <path d="
        M0,680 L20,640 L40,680 L45,635 L65,680 L70,630 L90,680 L95,628 L115,680
        L120,632 L140,680 L145,625 L165,680 L170,630 L190,680 L195,622 L215,680
        L220,628 L240,680 L245,620 L265,680 L270,626 L290,680 L295,624 L315,680
        L320,618 L340,680 L345,622 L365,680 L370,630 L390,680 L395,625 L415,680
        L420,620 L440,680 L445,616 L465,680 L470,624 L490,680 L495,618 L515,680
        L520,622 L540,680 L545,628 L565,680 L570,620 L590,680 L595,614 L615,680
        L620,622 L640,680 L645,618 L665,680 L670,624 L690,680 L695,616 L715,680
        L720,620 L740,680 L745,628 L765,680 L770,622 L790,680 L795,618 L815,680
        L820,614 L840,680 L845,620 L865,680 L870,626 L890,680 L895,618 L915,680
        L920,624 L940,680 L945,616 L965,680 L970,622 L990,680 L995,630 L1015,680
        L1020,620 L1040,680 L1045,614 L1065,680 L1070,618 L1090,680 L1095,622 L1115,680
        L1120,628 L1140,680 L1145,616 L1165,680 L1170,624 L1190,680 L1195,618 L1215,680
        L1220,622 L1240,680 L1245,628 L1265,680 L1270,620 L1290,680 L1295,614 L1315,680
        L1320,622 L1340,680 L1345,630 L1365,680 L1370,624 L1390,680 L1395,618 L1415,680
        L1420,626 L1440,680 L1440,900 L0,900Z"
        fill="url(#forest)"/>

      {/* Луг */}
      <path d="M0,760 Q180,730 360,755 Q540,780 720,745 Q900,720 1080,750 Q1260,775 1440,748 L1440,900 L0,900Z"
        fill="url(#meadow)"/>

      {/* Отражение луны на лугу */}
      <ellipse cx="900" cy="830" rx="200" ry="30" fill="#f5d97a" opacity="0.04"/>

      {/* Светлячки */}
      {[
        [200,700],[350,680],[500,720],[650,690],[800,710],[950,695],[1100,715],[1250,700],
        [150,740],[300,750],[450,735],[600,745],[750,730],[880,748],[1020,738],[1180,742],
      ].map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="2" fill="#c9ff8a" opacity={0.3 + (i % 4) * 0.15}>
          <animate attributeName="opacity"
            values={`${0.2 + (i % 3) * 0.2};0.8;${0.2 + (i % 3) * 0.2}`}
            dur={`${2 + (i % 5)}s`} repeatCount="indefinite"/>
        </circle>
      ))}

      {/* Туман */}
      <rect x="0" y="640" width="1440" height="260" fill="url(#mist)"/>

      {/* Свечение на горизонте */}
      <ellipse cx="720" cy="650" rx="500" ry="80" fill="#4a2f8a" opacity="0.2" filter="url(#blur8)"/>
    </svg>
  );
}
