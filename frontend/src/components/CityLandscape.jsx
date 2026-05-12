export default function CityLandscape() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 1440 900"
      preserveAspectRatio="xMidYMid slice"
      style={{ position: "fixed", inset: 0, width: "100%", height: "100%", zIndex: 0 }}
    >
      <defs>
        <linearGradient id="csky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stopColor="#020412"/>
          <stop offset="35%"  stopColor="#080c2a"/>
          <stop offset="70%"  stopColor="#130a2e"/>
          <stop offset="100%" stopColor="#1e0f3a"/>
        </linearGradient>
        <radialGradient id="cmoon" cx="50%" cy="50%" r="50%">
          <stop offset="0%"   stopColor="#fff8e0"/>
          <stop offset="55%"  stopColor="#f0d070"/>
          <stop offset="100%" stopColor="#c08030" stopOpacity="0"/>
        </radialGradient>
        <radialGradient id="cmoonGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%"  stopColor="#f0d070" stopOpacity="0.3"/>
          <stop offset="100%" stopColor="#f0d070" stopOpacity="0"/>
        </radialGradient>
        <radialGradient id="cityGlow" cx="50%" cy="100%" r="60%">
          <stop offset="0%"  stopColor="#c9780a" stopOpacity="0.22"/>
          <stop offset="100%" stopColor="#c9780a" stopOpacity="0"/>
        </radialGradient>
        <radialGradient id="cityGlow2" cx="50%" cy="100%" r="50%">
          <stop offset="0%"  stopColor="#f0c040" stopOpacity="0.12"/>
          <stop offset="100%" stopColor="#f0c040" stopOpacity="0"/>
        </radialGradient>
        <linearGradient id="cmtn1" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#15103a"/>
          <stop offset="100%" stopColor="#1e1445"/>
        </linearGradient>
        <linearGradient id="cmtn2" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0d0920"/>
          <stop offset="100%" stopColor="#140e30"/>
        </linearGradient>
        <linearGradient id="cforest" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#071408"/>
          <stop offset="100%" stopColor="#030a04"/>
        </linearGradient>
        <linearGradient id="cmeadow" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0a180c"/>
          <stop offset="100%" stopColor="#040808"/>
        </linearGradient>
        <linearGradient id="cityBase" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0e0c28"/>
          <stop offset="100%" stopColor="#080618"/>
        </linearGradient>
        <linearGradient id="cityMid" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0a0820"/>
          <stop offset="100%" stopColor="#060512"/>
        </linearGradient>
        <linearGradient id="cmist" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%"   stopColor="#6055aa" stopOpacity="0"/>
          <stop offset="50%"  stopColor="#8070cc" stopOpacity="0.12"/>
          <stop offset="100%" stopColor="#b0a0ee" stopOpacity="0.22"/>
        </linearGradient>
        <filter id="cblur4"><feGaussianBlur stdDeviation="4"/></filter>
        <filter id="cblur10"><feGaussianBlur stdDeviation="10"/></filter>
        <filter id="cblur2"><feGaussianBlur stdDeviation="2"/></filter>
      </defs>

      {/* Небо */}
      <rect width="1440" height="900" fill="url(#csky)"/>

      {/* Звёзды */}
      {[
        [55,25],[130,60],[210,20],[305,50],[385,18],[470,42],[560,28],[645,12],[730,48],[810,22],
        [890,40],[975,68],[1060,30],[1140,55],[1225,22],[1315,48],[1400,18],[1435,60],
        [75,95],[165,82],[260,108],[390,75],[530,100],[675,78],[815,95],[955,82],[1090,72],[1240,90],[1385,78],
        [95,135],[240,155],[390,128],[545,142],[700,125],[855,138],[1000,122],[1155,140],[1310,128],[1420,145],
        [50,175],[180,188],[325,165],[480,180],[635,168],[790,182],[940,172],[1095,185],[1250,170],[1400,180],
        [110,218],[270,232],[430,215],[585,228],[740,210],[895,225],[1050,215],[1205,230],[1360,218],
        [160,260],[320,275],[480,258],[640,270],[800,255],[960,268],[1120,258],[1280,272],
      ].map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r={i % 7 === 0 ? 1.5 : 0.9}
          fill="white" opacity={0.45 + (i % 6) * 0.09}/>
      ))}

      {/* Ореол луны */}
      <circle cx="260" cy="130" r="140" fill="url(#cmoonGlow)" filter="url(#cblur10)"/>
      {/* Луна */}
      <circle cx="260" cy="130" r="58" fill="url(#cmoon)"/>
      <circle cx="240" cy="115" r="8"  fill="#ddb840" opacity="0.25"/>
      <circle cx="275" cy="148" r="5"  fill="#ddb840" opacity="0.18"/>
      <circle cx="255" cy="140" r="3"  fill="#c8a030" opacity="0.22"/>

      {/* ======= ДАЛЬНИЕ ГОРЫ ======= */}
      <path d="M0,460 L90,290 L175,380 L270,250 L365,340 L460,220 L555,320 L640,260 L730,355 L820,200 L910,300 L1000,240 L1090,330 L1180,270 L1275,360 L1365,290 L1440,340 L1440,900 L0,900Z"
        fill="url(#cmtn1)"/>
      {/* Снег */}
      <path d="M90,290 L112,318 L68,318Z M270,250 L294,280 L246,280Z M460,220 L486,252 L434,252Z M640,260 L662,286 L618,286Z M820,200 L846,232 L794,232Z M1000,240 L1022,264 L978,264Z M1180,270 L1200,292 L1160,292Z"
        fill="white" opacity="0.22"/>

      {/* Средние горы */}
      <path d="M0,530 L70,390 L155,468 L245,360 L335,440 L430,355 L520,430 L615,375 L705,455 L800,345 L890,430 L985,370 L1075,448 L1170,385 L1265,455 L1360,395 L1440,450 L1440,900 L0,900Z"
        fill="url(#cmtn2)"/>

      {/* ======= ФЭНТЕЗИЙНЫЙ ГОРОД ======= */}
      {/* Свечение города */}
      <ellipse cx="720" cy="600" rx="420" ry="90" fill="url(#cityGlow)" filter="url(#cblur10)"/>
      <ellipse cx="720" cy="610" rx="280" ry="60" fill="url(#cityGlow2)" filter="url(#cblur4)"/>

      {/* Дальние здания (фон) */}
      <g fill="url(#cityBase)" opacity="0.9">
        {/* Левый квартал */}
        <rect x="310" y="500" width="28" height="120"/>
        <rect x="322" y="488" width="14" height="132"/>
        <rect x="345" y="512" width="22" height="108"/>
        <rect x="370" y="495" width="18" height="125"/>
        <rect x="392" y="505" width="25" height="115"/>
        <rect x="420" y="488" width="20" height="132"/>
        <rect x="443" y="498" width="16" height="122"/>
        <rect x="462" y="510" width="22" height="110"/>
        <rect x="487" y="500" width="18" height="120"/>
        <rect x="508" y="490" width="24" height="130"/>

        {/* Правый квартал */}
        <rect x="912" y="498" width="24" height="122"/>
        <rect x="938" y="510" width="18" height="110"/>
        <rect x="958" y="492" width="28" height="128"/>
        <rect x="988" y="505" width="20" height="115"/>
        <rect x="1010" y="495" width="22" height="125"/>
        <rect x="1035" y="508" width="16" height="112"/>
        <rect x="1053" y="490" width="26" height="130"/>
        <rect x="1082" y="500" width="20" height="120"/>
        <rect x="1105" y="514" width="18" height="106"/>
        <rect x="1125" y="498" width="24" height="122"/>
      </g>

      {/* ===== ГЛАВНЫЙ ЗАМОК (центр) ===== */}
      <g fill="url(#cityMid)">
        {/* Основной донжон */}
        <rect x="670" y="380" width="100" height="240"/>
        {/* Боковые башни донжона */}
        <rect x="650" y="400" width="30" height="220"/>
        <rect x="760" y="410" width="28" height="210"/>
        {/* Главная башня */}
        <rect x="700" y="330" width="40" height="290"/>
        {/* Шпиль */}
        <polygon points="720,268 706,342 734,342" fill="#0d0c28"/>
        {/* Флаг */}
        <rect x="720" y="268" width="1.5" height="30" fill="#c9a84c" opacity="0.9"/>
        <polygon points="721.5,270 735,277 721.5,284" fill="#c9a84c" opacity="0.9"/>

        {/* Левая башня замка */}
        <rect x="570" y="430" width="50" height="190"/>
        <rect x="560" y="420" width="26" height="200"/>
        <polygon points="573,378 560,432 586,432" fill="#0a0920"/>
        {/* Правая башня замка */}
        <rect x="820" y="435" width="50" height="185"/>
        <rect x="858" y="422" width="26" height="198"/>
        <polygon points="871,380 858,434 884,434" fill="#0a0920"/>

        {/* Стены замка */}
        <rect x="586" y="530" width="268" height="90"/>

        {/* Ворота */}
        <rect x="695" y="555" width="50" height="65" fill="#04020e"/>
        <path d="M695,555 Q720,535 745,555" fill="#04020e"/>

        {/* Зубцы */}
        {[650,660,672,684,696,756,768,780,792].map((x,i) => (
          <rect key={i} x={x} y="395" width="8" height="12" fill="#0a0920"/>
        ))}
        {[560,568,576].map((x,i)=>(
          <rect key={i} x={x} y="413" width="6" height="10" fill="#0a0920"/>
        ))}
        {[858,866,874].map((x,i)=>(
          <rect key={i} x={x} y="415" width="6" height="10" fill="#0a0920"/>
        ))}
        {[586,600,614,628,782,796,810,824,838,852].map((x,i)=>(
          <rect key={i} x={x} y="523" width="9" height="13" fill="#0a0920"/>
        ))}
      </g>

      {/* Окна замка со светом */}
      {[
        [706,360,10,14],[724,360,10,14],
        [706,395,8,10],[724,395,8,10],
        [655,435,7,9],[660,455,7,9],[765,440,7,9],[769,460,7,9],
        [578,455,6,8],[582,472,6,8],[863,458,6,8],[867,476,6,8],
        [680,545,7,9],[750,545,7,9],[680,565,7,9],[750,565,7,9],
      ].map(([x,y,w,h],i)=>(
        <rect key={i} x={x} y={y} width={w} height={h}
          fill="#f0c060" opacity={0.55 + (i%3)*0.1}
          rx="1"/>
      ))}

      {/* ===== СРЕДНИЙ ПЛАН: ГОРОД ===== */}
      <g fill="#080618" opacity="0.95">
        {/* Левый городской квартал */}
        <rect x="130" y="548" width="35" height="132"/>
        <rect x="168" y="535" width="28" height="145"/>
        <rect x="152" y="540" width="18" height="140"/>
        {/* Колокольня */}
        <rect x="200" y="510" width="22" height="170"/>
        <polygon points="211,488 200,522 222,522" fill="#06040f"/>
        <rect x="209" y="480" width="3" height="12" fill="#c9a84c" opacity="0.8"/>
        <rect x="198" y="540" width="26" height="4" fill="#06040f"/>

        <rect x="228" y="545" width="30" height="135"/>
        <rect x="261" y="532" width="24" height="148"/>
        <rect x="288" y="540" width="32" height="140"/>

        {/* Правый городской квартал */}
        <rect x="1120" y="542" width="35" height="138"/>
        <rect x="1158" y="528" width="28" height="152"/>
        <rect x="1178" y="536" width="22" height="144"/>
        <rect x="1203" y="512" width="22" height="168"/>
        <polygon points="1214,490 1203,524 1225,524" fill="#06040f"/>
        <rect x="1212" y="482" width="3" height="12" fill="#c9a84c" opacity="0.8"/>
        <rect x="1228" y="540" width="30" height="140"/>
        <rect x="1261" y="530" width="26" height="150"/>
        <rect x="1290" y="545" width="34" height="135"/>
        <rect x="1328" y="536" width="28" height="144"/>
      </g>

      {/* Окна в городских зданиях */}
      {[
        [135,558],[135,574],[135,590],[172,545],[172,561],[172,577],[204,520],[204,536],[204,554],
        [232,555],[232,571],[265,542],[265,560],[292,550],[292,568],
        [1124,552],[1124,568],[1162,540],[1162,556],[1162,572],[1182,546],[1182,562],[1207,522],[1207,540],[1207,558],
        [1232,550],[1232,566],[1265,540],[1265,558],[1294,555],[1294,571],[1332,546],[1332,562],
      ].map(([x,y],i)=>(
        <rect key={i} x={x} y={y} width={6} height={8}
          fill="#f0c060" opacity={0.4+(i%4)*0.12} rx="1"/>
      ))}

      {/* ===== ЛЕС по бокам ===== */}
      {/* Левый лес */}
      <path d="M0,700 L22,655 L44,700 L48,648 L70,700 L74,642 L96,700 L100,638 L122,700 L126,646 L148,700 L152,640 L174,700 L178,652 L200,700 L204,644 L226,700 L230,636 L252,700 L256,644 L278,700 L282,650 L304,700 L308,638 L330,700 L0,900Z"
        fill="url(#cforest)"/>
      {/* Правый лес */}
      <path d="M1440,700 L1418,652 L1396,700 L1392,644 L1370,700 L1366,638 L1344,700 L1340,646 L1318,700 L1314,640 L1292,700 L1288,652 L1266,700 L1262,644 L1240,700 L1236,638 L1214,700 L1210,646 L1188,700 L1184,652 L1162,700 L1158,640 L1136,700 L1440,900Z"
        fill="url(#cforest)"/>

      {/* ===== ЛУГОВИНА (передний план) ===== */}
      <path d="M0,778 Q200,752 400,768 Q600,784 720,760 Q840,742 1040,765 Q1240,784 1440,762 L1440,900 L0,900Z"
        fill="url(#cmeadow)"/>

      {/* Дорога к воротам */}
      <path d="M720,900 L680,780 Q718,762 756,780 L720,900Z" fill="#0a0810" opacity="0.7"/>

      {/* Туман */}
      <rect x="0" y="650" width="1440" height="250" fill="url(#cmist)"/>

      {/* Отражение луны */}
      <ellipse cx="260" cy="860" rx="120" ry="18" fill="#f0d060" opacity="0.04"/>

      {/* Светлячки */}
      {[
        [80,730],[180,715],[320,740],[480,720],[600,735],[820,718],[1000,730],[1150,715],[1300,738],[1420,720],
        [140,768],[280,752],[420,770],[560,755],[680,748],[790,762],[920,750],[1060,765],[1200,752],[1370,762],
      ].map(([x,y],i)=>(
        <circle key={i} cx={x} cy={y} r="1.8" fill="#b8ff80" opacity={0.25+(i%4)*0.15}>
          <animate attributeName="opacity"
            values={`${0.15+(i%3)*0.2};0.75;${0.15+(i%3)*0.2}`}
            dur={`${2.5+(i%6)*0.5}s`} repeatCount="indefinite"/>
        </circle>
      ))}

      {/* Искры/огни над городом */}
      {[700,715,730,710,740,720,705,725,735].map((x,i)=>(
        <circle key={i} cx={x} cy={340+(i%3)*8} r="1.2" fill="#ffaa30" opacity={0.5+(i%3)*0.15}>
          <animate attributeName="cy" values={`${340+(i%3)*8};${330+(i%3)*8};${340+(i%3)*8}`}
            dur={`${1.5+i*0.3}s`} repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.6;0.1;0.6"
            dur={`${1.5+i*0.3}s`} repeatCount="indefinite"/>
        </circle>
      ))}
    </svg>
  );
}
