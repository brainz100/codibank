"""
[2026-04-08] Phase 2: 퍼스널컬러 프롬프트 빌더 (공통 헬퍼)
코디쌤/코디하기/Ai옷장에서 공용으로 사용
"""

def _build_pc_prompt_block(personal_color, mode="styling"):
    if not personal_color:
        return ""
    season = personal_color.get("season", "")
    if not season:
        return ""
    
    undertone = personal_color.get("undertone", "")
    skin_tone = personal_color.get("skin_tone", "")
    best_colors = ", ".join((personal_color.get("best_colors") or [])[:5])
    best_names = ", ".join((personal_color.get("best_color_names") or [])[:5])
    avoid_colors = ", ".join((personal_color.get("avoid_colors") or [])[:3])
    avoid_names = ", ".join((personal_color.get("avoid_color_names") or [])[:3])
    season_group = personal_color.get("season_group", "")
    season_en = personal_color.get("season_en", "")
    chroma = personal_color.get("chroma", "")
    clarity = personal_color.get("clarity", "")
    style_tip = personal_color.get("style_tip", "")

    if mode == "styling":
        # ─── [2026-04-26 v21 TJ] 컬러 자유도 증가 ───
        # 이전: "Outfit MUST use colors from best palette" → 매번 같은 best 5색만 사용
        # 변경: avoid 컬러만 강력 제외 + best는 우선 가이드 (스타일리스트가 코디 목적/날씨에 맞춰 자유 조합)
        # ─── [2026-05-12 v61 TJ] 추가 자유화 — 상/하의 컬러 랜덤 매칭 강제 ───
        # 사용자 보고: 여전히 퍼스널컬러 best 컬러가 바지에 자주 매칭됨.
        # 원인: "Recommended palette (for inspiration)" 표현이 여전히 AI에게
        #       "이 색을 따르라"는 약한 명령으로 인식됨.
        # 변경:
        #   1. best palette 표현을 더 느슨하게 ("Reference only - loose hint, AI free to ignore")
        #   2. 상/하의 컬러 매칭을 명시적으로 랜덤화 강제
        #   3. avoid 컬러만 strict 유지
        lines = [
            "",
            "PERSONAL COLOR PROFILE (12-Subtype):",
            "  Season: " + season + " (" + (season_en or season_group or undertone) + ")",
            "  Undertone: " + undertone + " | Skin: " + skin_tone,
            "  Reference colors (LOOSE HINT — AI may freely ignore and use any non-avoid color): " + best_names + " (" + best_colors + ")",
            "  ⛔ Colors to AVOID (STRICT — NEVER use): " + avoid_names + " (" + avoid_colors + ")",
        ]
        if chroma:
            lines.append("  Chroma: " + str(chroma) + " - " + str(clarity))
        lines += [
            "",
            "  COLOR RULES (priority order):",
            "  1. ⛔ STRICT: NEVER use any avoid color as a main garment color (top, bottom, dress, outer).",
            "  2. ⛔ STRICT: Avoid colors NEVER in skin-adjacent areas (collar, neckline, face frame).",
            "  3. 🎲 RANDOMIZE TOP/BOTTOM COLORS: For each generation, randomly pair top and bottom",
            "     from the vast universe of " + (undertone or season) + "-compatible colors (white, ivory, cream,",
            "     beige, camel, khaki, olive, navy, charcoal, denim blue, soft gray, brown, terracotta,",
            "     muted earth tones, and any season-harmonious colors). Do NOT default to the reference palette.",
            "  4. ⚠️ ANTI-REPETITION: Different generations MUST use noticeably different color combinations.",
            "     Even with the same user/purpose/weather, vary top and bottom colors each time.",
            "     Avoid the pattern of always pairing top with bottom from the reference palette.",
            "  5. HARMONY: All chosen colors must blend with " + (undertone or season) + " undertone",
            "     (e.g., warm undertone → avoid pure icy blues; cool undertone → avoid warm yellows).",
            "  6. PRIORITY: The outfit must look natural, season-appropriate, and purpose-fit.",
            "     The reference palette is INSPIRATION ONLY — never a strict requirement.",
        ]
        if style_tip:
            lines.append("  Style tip: " + style_tip)
        return "\n".join(lines)
    
    elif mode == "codistyle":
        lines = [
            "",
            "PERSONAL COLOR: " + season + " (" + undertone + ")",
            "  Best: " + best_names + " (" + best_colors + ")",
            "  Avoid: " + avoid_names + " (" + avoid_colors + ")",
        ]
        if chroma:
            lines.append("  Chroma: " + str(chroma) + " (" + str(clarity) + ")")
        lines += [
            "",
            "  SCORING (total 100):",
            "  color_harmony/30, garment_match/30, personal_color_fit/20, overall_style/20",
            "  If garment uses avoid colors: deduct 10-15 from color_harmony.",
            "  If garment uses best colors: add 5-10 bonus to personal_color_fit.",
        ]
        return "\n".join(lines)
    
    elif mode == "recommend":
        lines = [
            "퍼스널컬러: " + season + " (" + undertone + ")",
            "추천 컬러: " + best_names,
            "피해야 할 컬러: " + avoid_names,
        ]
        if skin_tone:
            lines.append("피부 밝기: " + skin_tone)
        if style_tip:
            lines.append("스타일 팁: " + style_tip)
        return "\n".join(lines)
    
    return ""
