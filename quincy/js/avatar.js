// Quincy · avatar ilustrado de tu yo del futuro, que envejece.
(function (FY) {
  const SKINS = ["#f6d2b8", "#e6b48f", "#c98e62", "#9b6542", "#6b4329"];
  const lerp = (a, b, t) => a + (b - a) * t;
  function mix(h1, h2, t) {
    const p = (h) => [1, 3, 5].map((k) => parseInt(h.slice(k, k + 2), 16));
    const a = p(h1), b = p(h2);
    return "#" + a.map((v, k) => Math.round(lerp(v, b[k], t)).toString(16).padStart(2, "0")).join("");
  }
  function avatarSVG(age, mood, skin, hair) {
    const t = Math.min(1, Math.max(0, (age - 30) / 45));
    const hairCol = mix("#2b1a12", "#d9dde0", Math.min(1, Math.max(0, (age - 38) / 32)));
    const wr = Math.min(0.75, Math.max(0, (age - 40) / 35));
    const sk = SKINS[skin];
    const shade = mix(sk, "#3a2418", 0.28);
    const brow = mood === "ok" ? 0 : mood === "mid" ? 3 : 7;
    const mouth = mood === "ok" ? 12 : mood === "mid" ? 2 : -9;
    const hl = lerp(46, 54, t);
    const long = hair === "long";
    // Cabello largo: una sola masa detrás de la cabeza que cae sobre los hombros.
    const backHair = long ? `<path d="M100 34 C60 34 40 62 39 104 C38 140 40 172 46 200 C54 210 72 210 82 202 C80 186 78 170 80 156 L120 156 C122 170 120 186 118 202 C128 210 146 210 154 200 C160 172 162 140 161 104 C160 62 140 34 100 34 Z" fill="${mix(hairCol, "#000000", 0.12)}"/>` : "";
    // Flequillo y mechones que enmarcan la cara (cabello largo) o casquete (cabello corto).
    const frontHair = long
      ? `<path d="M47 ${hl + 52} C42 16 158 16 153 ${hl + 52} C152 ${hl + 70} 150 ${hl + 86} 147 ${hl + 98} C144 ${hl + 52} 128 ${hl + 22} 104 ${hl + 14} C96 ${hl + 26} 74 ${hl + 34} 56 ${hl + 44} C54 ${hl + 62} 54 ${hl + 82} 53 ${hl + 98} C50 ${hl + 86} 48 ${hl + 70} 47 ${hl + 52} Z" fill="${hairCol}"/>`
      : `<path d="M46 ${hl + 44} C42 18 158 18 154 ${hl + 44} C146 ${hl + 16} 122 ${hl + 4} 100 ${hl + 10} C78 ${hl + 4} 54 ${hl + 16} 46 ${hl + 44} Z" fill="${hairCol}"/>`;
    const glasses = age >= 55 ? `<g fill="none" stroke="#1d2b33" stroke-width="2.6" opacity=".9"><rect x="64" y="94" width="28" height="20" rx="8"/><rect x="108" y="94" width="28" height="20" rx="8"/><path d="M92 102 h16"/></g>` : "";
    return `
      <defs><radialGradient id="glow-${skin}" cx="50%" cy="40%" r="60%"><stop offset="0" stop-color="${mix(sk, "#ffffff", .18)}"/><stop offset="1" stop-color="${sk}"/></radialGradient></defs>
      <path d="M30 220 C34 182 62 166 100 166 C138 166 166 182 170 220 Z" fill="#1f4a5c"/>
      ${backHair}
      <path d="M78 168 L100 196 L122 168" fill="none" stroke="#5ad6c8" stroke-width="3" opacity=".7"/>
      <rect x="86" y="138" width="28" height="34" rx="10" fill="${shade}"/>
      ${long ? "" : `<circle cx="47" cy="104" r="10" fill="${shade}"/><circle cx="153" cy="104" r="10" fill="${shade}"/>`}
      <ellipse cx="100" cy="100" rx="52" ry="60" fill="url(#glow-${skin})"/>
      ${frontHair}
      <g fill="none" stroke="${mix(sk, "#2a1810", .45)}" stroke-linecap="round" stroke-width="1.6" opacity="${wr}">
        <path d="M80 ${hl + 26} Q100 ${hl + 21} 120 ${hl + 26}"/><path d="M84 ${hl + 33} Q100 ${hl + 29} 116 ${hl + 33}"/>
        <path d="M60 104 l-6 -3 M60 108 l-7 0 M60 112 l-6 3"/><path d="M140 104 l6 -3 M140 108 l7 0 M140 112 l6 3"/>
        <path d="M82 124 Q78 134 84 144"/><path d="M118 124 Q122 134 116 144"/>
      </g>
      <g stroke="${mix(hairCol, "#000000", .2)}" stroke-width="3.4" stroke-linecap="round" fill="none">
        <path d="M68 ${88 + brow / 2} L90 ${86 - brow / 2}"/><path d="M132 ${88 + brow / 2} L110 ${86 - brow / 2}"/>
      </g>
      <g fill="#14202a"><ellipse cx="78" cy="104" rx="5" ry="${mood === "ok" ? 4.2 : 5.4}"/><ellipse cx="122" cy="104" rx="5" ry="${mood === "ok" ? 4.2 : 5.4}"/></g>
      <circle cx="80" cy="102" r="1.5" fill="#fff"/><circle cx="124" cy="102" r="1.5" fill="#fff"/>
      ${glasses}
      <path d="M100 108 Q96 120 100 124" fill="none" stroke="${shade}" stroke-width="2.2" stroke-linecap="round"/>
      <path d="M84 136 Q100 ${136 + mouth} 116 136" fill="none" stroke="#7a2e2a" stroke-width="3.6" stroke-linecap="round"/>
      ${mood === "ok" ? `<circle cx="70" cy="124" r="7" fill="#ff8a7a" opacity=".22"/><circle cx="130" cy="124" r="7" fill="#ff8a7a" opacity=".22"/>` : ""}`;
  }

  FY.avatar = { SKINS, svg: avatarSVG };
})(window.FY);
