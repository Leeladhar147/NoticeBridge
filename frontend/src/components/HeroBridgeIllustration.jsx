import React from 'react';

/**
 * HeroBridgeIllustration
 * A bold, substantial, clearly visible architectural bridge illustration for NoticeBridge.
 * Features a heavy, prominent visual representing:
 * Current Company (Left Corporate Skyline) -> Heavy Suspension Bridge -> New Opportunity (Right Modern Skyline)
 * Includes bold suspension pylons, vibrant green catenary cables, multi-level deck with transit indicator,
 * architectural cross-trusses, and rhythmic water reflections.
 */
export default function HeroBridgeIllustration({ className = '' }) {
  return (
    <div
      className={`hero-bridge-illustration ${className}`}
      style={{
        position: 'relative',
        width: '100%',
        maxWidth: '820px',
        margin: '0 auto',
        pointerEvents: 'none',
        userSelect: 'none'
      }}
      aria-label="NoticeBridge Transition Illustration"
    >
      <svg
        viewBox="0 0 920 460"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{
          width: '100%',
          height: 'auto',
          display: 'block',
          overflow: 'visible'
        }}
      >
        <defs>
          {/* Subtle soft gradient for corporate towers */}
          <linearGradient id="corpTowerGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="100%" stopColor="#F1F5F9" />
          </linearGradient>

          {/* Vibrant brand green gradient for bridge deck & suspension cables */}
          <linearGradient id="bridgeMainCableGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#475569" />
            <stop offset="35%" stopColor="#16A34A" />
            <stop offset="70%" stopColor="#15803D" />
            <stop offset="100%" stopColor="#16A34A" />
          </linearGradient>

          {/* New Opportunity Tower Gradient */}
          <linearGradient id="techTowerGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#F0FDF4" />
            <stop offset="100%" stopColor="#DCFCE7" />
          </linearGradient>

          {/* Water reflection gradient */}
          <linearGradient id="waterSurfaceGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#E2E8F0" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0" />
          </linearGradient>

          {/* Drop shadow for bridge pylons and deck */}
          <filter id="bridgeShadow" x="-10%" y="-10%" width="120%" height="120%">
            <feDropShadow dx="0" dy="4" stdDeviation="6" floodColor="#0F172A" floodOpacity="0.08" />
          </filter>
        </defs>

        {/* ============================================================== */}
        {/* 1. DISTANT CITY HORIZON & FAINT BACKDROP SKYLINE */}
        {/* ============================================================== */}
        {/* Faint distant hills/city horizon */}
        <path
          d="M 20 320 Q 240 280 480 300 T 900 290"
          stroke="#CBD5E1"
          strokeWidth="1.5"
          fill="none"
          opacity="0.6"
        />

        {/* Distant background high-rises */}
        <rect x="80" y="210" width="34" height="110" fill="#F8FAFC" stroke="#CBD5E1" strokeWidth="1" />
        <rect x="122" y="235" width="28" height="85" fill="#F8FAFC" stroke="#CBD5E1" strokeWidth="1" />
        <rect x="760" y="230" width="32" height="90" fill="#F0FDF4" stroke="#BBF7D0" strokeWidth="1" />
        <rect x="800" y="215" width="38" height="105" fill="#F0FDF4" stroke="#BBF7D0" strokeWidth="1" />

        {/* ============================================================== */}
        {/* 2. LEFT SHORE: CURRENT COMPANY ARCHITECTURAL COMPLEX */}
        {/* ============================================================== */}
        {/* Main Headquarters Building */}
        <rect
          x="140"
          y="150"
          width="74"
          height="170"
          rx="3"
          fill="url(#corpTowerGrad)"
          stroke="#475569"
          strokeWidth="2"
          filter="url(#bridgeShadow)"
        />
        {/* Office Window Grid */}
        <g stroke="#94A3B8" strokeWidth="1.2">
          <line x1="154" y1="172" x2="200" y2="172" />
          <line x1="154" y1="190" x2="200" y2="190" />
          <line x1="154" y1="208" x2="200" y2="208" />
          <line x1="154" y1="226" x2="200" y2="226" />
          <line x1="154" y1="244" x2="200" y2="244" />
          <line x1="154" y1="262" x2="200" y2="262" />
          <line x1="154" y1="280" x2="200" y2="280" />
          <line x1="154" y1="298" x2="200" y2="298" />
        </g>

        {/* Secondary Corporate Wing */}
        <rect
          x="222"
          y="190"
          width="62"
          height="130"
          rx="3"
          fill="url(#corpTowerGrad)"
          stroke="#64748B"
          strokeWidth="1.8"
        />
        <g stroke="#CBD5E1" strokeWidth="1.2">
          <line x1="234" y1="210" x2="272" y2="210" />
          <line x1="234" y1="228" x2="272" y2="228" />
          <line x1="234" y1="246" x2="272" y2="246" />
          <line x1="234" y1="264" x2="272" y2="264" />
          <line x1="234" y1="282" x2="272" y2="282" />
          <line x1="234" y1="300" x2="272" y2="300" />
        </g>

        {/* Left Shore Pier Abutment */}
        <path
          d="M 120 320 L 305 320 L 315 342 L 105 342 Z"
          fill="#334155"
          stroke="#1E293B"
          strokeWidth="2"
        />

        {/* Current Company Label Badge */}
        <g>
          <rect x="142" y="118" width="138" height="24" rx="12" fill="#FFFFFF" stroke="#CBD5E1" strokeWidth="1.5" />
          <circle cx="154" cy="130" r="4" fill="#64748B" />
          <text
            x="215"
            y="134"
            textAnchor="middle"
            fill="#334155"
            fontFamily="var(--font-heading), sans-serif"
            fontSize="10.5"
            fontWeight="800"
            letterSpacing="0.06em"
          >
            CURRENT COMPANY
          </text>
        </g>

        {/* ============================================================== */}
        {/* 3. THE HEAVY NOTICEBRIDGE SUSPENSION STRUCTURE */}
        {/* ============================================================== */}

        {/* --- Left Pylon Tower (x = 360) --- */}
        {/* Tower Legs */}
        <path
          d="M 348 335 L 356 95 L 366 95 L 374 335 Z"
          fill="#F8FAFC"
          stroke="#1E293B"
          strokeWidth="2.5"
          filter="url(#bridgeShadow)"
        />
        {/* Architectural Cross Braces & Portals */}
        <rect x="353" y="145" width="16" height="5" fill="#334155" />
        <rect x="351" y="205" width="20" height="5" fill="#334155" />
        <rect x="349" y="265" width="24" height="6" fill="#334155" />
        <line x1="353" y1="105" x2="368" y2="145" stroke="#64748B" strokeWidth="1.5" />
        <line x1="368" y1="105" x2="353" y2="145" stroke="#64748B" strokeWidth="1.5" />
        {/* Pylon Crown Cap */}
        <rect x="352" y="85" width="18" height="12" rx="2" fill="#1E293B" stroke="#0F172A" strokeWidth="1.5" />
        {/* Pier Foundation Block */}
        <rect x="342" y="325" width="38" height="26" rx="3" fill="#E2E8F0" stroke="#475569" strokeWidth="2" />

        {/* --- Right Pylon Tower (x = 640) --- */}
        <path
          d="M 628 335 L 636 85 L 646 85 L 654 335 Z"
          fill="#F0FDF4"
          stroke="#15803D"
          strokeWidth="2.5"
          filter="url(#bridgeShadow)"
        />
        {/* Cross Braces with Green Accents */}
        <rect x="633" y="140" width="16" height="5" fill="#16A34A" />
        <rect x="631" y="200" width="20" height="5" fill="#16A34A" />
        <rect x="629" y="260" width="24" height="6" fill="#16A34A" />
        <line x1="633" y1="95" x2="648" y2="140" stroke="#16A34A" strokeWidth="1.5" />
        <line x1="648" y1="95" x2="633" y2="140" stroke="#16A34A" strokeWidth="1.5" />
        {/* Pylon Crown Cap with Emerald Beacon */}
        <rect x="632" y="75" width="18" height="12" rx="2" fill="#16A34A" stroke="#15803D" strokeWidth="1.5" />
        <circle cx="641" cy="71" r="3.5" fill="#16A34A" />
        {/* Pier Foundation Block */}
        <rect x="622" y="325" width="38" height="26" rx="3" fill="#DCFCE7" stroke="#16A34A" strokeWidth="2" />

        {/* --- MAIN CATENARY SUSPENSION CABLES (BOLD & HEAVY) --- */}
        {/* Left Backstay Anchor Cable */}
        <path
          d="M 235 320 Q 295 220 361 95"
          stroke="#475569"
          strokeWidth="3.5"
          strokeLinecap="round"
          fill="none"
        />

        {/* Central Sweeping Span Cable (Vibrant Brand Green) */}
        <path
          d="M 361 95 Q 500 245 641 85"
          stroke="url(#bridgeMainCableGrad)"
          strokeWidth="4"
          strokeLinecap="round"
          fill="none"
        />
        {/* Parallel Secondary Cable for Depth & Truss Structure */}
        <path
          d="M 361 104 Q 500 252 641 94"
          stroke="#16A34A"
          strokeWidth="1.8"
          strokeDasharray="5 4"
          opacity="0.8"
          fill="none"
        />

        {/* Right Forward Anchor Cable */}
        <path
          d="M 641 85 Q 710 210 775 320"
          stroke="#16A34A"
          strokeWidth="3.5"
          strokeLinecap="round"
          fill="none"
        />

        {/* --- VERTICAL SUSPENSION HANGER CABLES (SOLID & RHYTHMIC) --- */}
        <g stroke="#64748B" strokeWidth="1.6" opacity="0.85">
          {/* Left backstay hangers */}
          <line x1="275" y1="270" x2="275" y2="320" />
          <line x1="305" y1="215" x2="305" y2="320" />
          <line x1="335" y1="150" x2="335" y2="320" />
        </g>

        {/* Center span hangers (Emerald Green Gradient & Crisp Charcoal) */}
        <g strokeWidth="1.8">
          <line x1="395" y1="135" x2="395" y2="320" stroke="#64748B" />
          <line x1="425" y1="168" x2="425" y2="320" stroke="#16A34A" />
          <line x1="455" y1="198" x2="455" y2="320" stroke="#16A34A" />
          <line x1="485" y1="220" x2="485" y2="320" stroke="#15803D" strokeWidth="2.2" />
          <line x1="515" y1="230" x2="515" y2="320" stroke="#15803D" strokeWidth="2.5" />
          <line x1="545" y1="225" x2="545" y2="320" stroke="#15803D" strokeWidth="2.2" />
          <line x1="575" y1="205" x2="575" y2="320" stroke="#16A34A" />
          <line x1="605" y1="172" x2="605" y2="320" stroke="#16A34A" />
        </g>

        {/* Right forward hangers */}
        <g stroke="#16A34A" strokeWidth="1.6" opacity="0.85">
          <line x1="675" y1="150" x2="675" y2="320" />
          <line x1="705" y1="215" x2="705" y2="320" />
          <line x1="735" y1="270" x2="735" y2="320" />
        </g>

        {/* --- HEAVY MULTI-LAYER BRIDGE ROADWAY DECK --- */}
        {/* Bottom Truss Structure */}
        <path
          d="M 220 328 L 790 328"
          stroke="#475569"
          strokeWidth="3"
        />
        {/* Truss cross-diagonals */}
        <g stroke="#94A3B8" strokeWidth="1.2" opacity="0.75">
          <line x1="240" y1="320" x2="260" y2="328" />
          <line x1="280" y1="320" x2="300" y2="328" />
          <line x1="320" y1="320" x2="340" y2="328" />
          <line x1="380" y1="320" x2="400" y2="328" />
          <line x1="420" y1="320" x2="440" y2="328" />
          <line x1="460" y1="320" x2="480" y2="328" />
          <line x1="500" y1="320" x2="520" y2="328" />
          <line x1="540" y1="320" x2="560" y2="328" />
          <line x1="580" y1="320" x2="600" y2="328" />
          <line x1="620" y1="320" x2="640" y2="328" />
          <line x1="660" y1="320" x2="680" y2="328" />
          <line x1="700" y1="320" x2="720" y2="328" />
          <line x1="740" y1="320" x2="760" y2="328" />
        </g>

        {/* Solid Main Road Deck */}
        <rect
          x="210"
          y="316"
          width="590"
          height="8"
          rx="2"
          fill="#0F172A"
          stroke="#1E293B"
          strokeWidth="1.5"
          filter="url(#bridgeShadow)"
        />

        {/* Active Green Transit Highway Line */}
        <line
          x1="220"
          y1="320"
          x2="790"
          y2="320"
          stroke="#16A34A"
          strokeWidth="2.5"
          strokeDasharray="8 5"
        />

        {/* Prominent Transit Crossing Indicator (Employee Crossing) */}
        <g>
          <circle cx="515" cy="320" r="7" fill="#16A34A" stroke="#FFFFFF" strokeWidth="2" />
          <circle cx="515" cy="320" r="13" stroke="#16A34A" strokeWidth="1.8" opacity="0.5" />
          {/* Subtle Directional Arrow on the Bridge */}
          <path d="M 528 317 L 535 320 L 528 323" stroke="#16A34A" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
        </g>

        {/* Center Keystone NoticeBridge Badge */}
        <g>
          <rect x="440" y="278" width="150" height="24" rx="12" fill="#FFFFFF" stroke="#16A34A" strokeWidth="1.8" filter="url(#bridgeShadow)" />
          <circle cx="454" cy="290" r="4.5" fill="#16A34A" />
          <text
            x="519"
            y="294"
            textAnchor="middle"
            fill="#15803D"
            fontFamily="var(--font-heading), sans-serif"
            fontSize="10.5"
            fontWeight="900"
            letterSpacing="0.08em"
          >
            NOTICEBRIDGE SPAN
          </text>
        </g>

        {/* ============================================================== */}
        {/* 4. RIGHT SHORE: NEW OPPORTUNITY TECH SKYLINE */}
        {/* ============================================================== */}
        {/* Soaring Tech Tower 1 (Angled Peak) */}
        <path
          d="M 710 320 L 710 135 L 755 95 L 780 95 L 780 320 Z"
          fill="url(#techTowerGrad)"
          stroke="#15803D"
          strokeWidth="2"
          filter="url(#bridgeShadow)"
        />
        {/* Pinnacle Spire & Beacon */}
        <line x1="755" y1="95" x2="755" y2="55" stroke="#16A34A" strokeWidth="2.5" strokeLinecap="round" />
        <circle cx="755" cy="55" r="4.5" fill="#16A34A" stroke="#FFFFFF" strokeWidth="1.5" />

        {/* Modern Stepped Glass Tower 2 */}
        <rect
          x="790"
          y="155"
          width="75"
          height="165"
          rx="3"
          fill="url(#techTowerGrad)"
          stroke="#16A34A"
          strokeWidth="1.8"
        />
        {/* Modern Window Lines */}
        <g stroke="#86EFAC" strokeWidth="1.4">
          <line x1="802" y1="178" x2="852" y2="178" />
          <line x1="802" y1="198" x2="852" y2="198" />
          <line x1="802" y1="218" x2="852" y2="218" />
          <line x1="802" y1="238" x2="852" y2="238" />
          <line x1="802" y1="258" x2="852" y2="258" />
          <line x1="802" y1="278" x2="852" y2="278" />
          <line x1="802" y1="298" x2="852" y2="298" />
        </g>

        {/* Right Shore Pier Embankment */}
        <path
          d="M 695 320 L 890 320 L 890 342 L 685 342 Z"
          fill="#14532D"
          stroke="#052E16"
          strokeWidth="2"
        />

        {/* New Opportunity Label Badge */}
        <g>
          <rect x="718" y="70" width="154" height="24" rx="12" fill="#DCFCE7" stroke="#16A34A" strokeWidth="1.8" />
          <circle cx="732" cy="82" r="4" fill="#16A34A" />
          <text
            x="799"
            y="86"
            textAnchor="middle"
            fill="#15803D"
            fontFamily="var(--font-heading), sans-serif"
            fontSize="10.5"
            fontWeight="900"
            letterSpacing="0.06em"
          >
            NEW OPPORTUNITY
          </text>
        </g>

        {/* ============================================================== */}
        {/* 5. WATER SURFACE & RHYTHMIC WATER REFLECTIONS */}
        {/* ============================================================== */}
        {/* Water Surface Base Layer */}
        <rect x="60" y="342" width="840" height="95" fill="url(#waterSurfaceGrad)" />

        {/* Left bank water reflections */}
        <line x1="140" y1="352" x2="270" y2="352" stroke="#94A3B8" strokeWidth="2" strokeDasharray="18 10" opacity="0.6" />
        <line x1="180" y1="365" x2="260" y2="365" stroke="#CBD5E1" strokeWidth="1.8" strokeDasharray="14 8" opacity="0.5" />
        <line x1="210" y1="378" x2="280" y2="378" stroke="#E2E8F0" strokeWidth="1.5" strokeDasharray="12 6" opacity="0.4" />

        {/* Tower 1 vertical reflection */}
        <line x1="356" y1="348" x2="366" y2="348" stroke="#475569" strokeWidth="2.5" opacity="0.7" />
        <line x1="352" y1="360" x2="370" y2="360" stroke="#94A3B8" strokeWidth="2" opacity="0.5" />
        <line x1="354" y1="374" x2="368" y2="374" stroke="#CBD5E1" strokeWidth="1.5" opacity="0.4" />

        {/* Central Span Water Reflections (Bright Green & Soft Slate) */}
        <line x1="430" y1="350" x2="570" y2="350" stroke="#16A34A" strokeWidth="2.2" strokeDasharray="20 12" opacity="0.65" />
        <line x1="480" y1="362" x2="610" y2="362" stroke="#86EFAC" strokeWidth="2" strokeDasharray="22 14" opacity="0.6" />
        <line x1="450" y1="375" x2="580" y2="375" stroke="#16A34A" strokeWidth="1.8" strokeDasharray="16 10" opacity="0.45" />
        <line x1="400" y1="388" x2="620" y2="388" stroke="#CBD5E1" strokeWidth="1.5" strokeDasharray="18 10" opacity="0.35" />

        {/* Tower 2 vertical reflection */}
        <line x1="636" y1="348" x2="646" y2="348" stroke="#16A34A" strokeWidth="2.5" opacity="0.7" />
        <line x1="632" y1="360" x2="650" y2="360" stroke="#4ADE80" strokeWidth="2" opacity="0.55" />
        <line x1="634" y1="374" x2="648" y2="374" stroke="#86EFAC" strokeWidth="1.5" opacity="0.4" />

        {/* Right bank water reflections */}
        <line x1="720" y1="352" x2="860" y2="352" stroke="#16A34A" strokeWidth="2" strokeDasharray="18 10" opacity="0.6" />
        <line x1="750" y1="365" x2="840" y2="365" stroke="#86EFAC" strokeWidth="1.8" strokeDasharray="14 8" opacity="0.5" />
        <line x1="780" y1="378" x2="860" y2="378" stroke="#DCFCE7" strokeWidth="1.5" strokeDasharray="12 6" opacity="0.4" />
      </svg>
    </div>
  );
}
