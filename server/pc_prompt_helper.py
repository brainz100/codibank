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
        lines = [
            "",
            "PERSONAL COLOR PROFILE (12-Subtype):",
            "  Season: " + season + " (" + (season_en or season_group or undertone) + ")",
            "  Undertone: " + undertone + " | Skin: " + skin_tone,
            "  Best colors: " + best_names + " (" + best_colors + ")",
            "  Avoid colors: " + avoid_names + " (" + avoid_colors + ")",
        ]
        if chroma:
            lines.append("  Chroma: " + str(chroma) + " - " + str(clarity))
        lines += [
            "",
            "  CRITICAL: Outfit MUST use colors from best palette.",
            "  NEVER use avoid colors as main garment colors.",
            "  Color harmony must match " + season + " type.",
        ]
        if style_tip:
            lines.append("  Style: " + style_tip)
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
