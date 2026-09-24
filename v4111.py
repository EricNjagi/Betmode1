def v411_predict(home, away, home_tier, away_tier, home_form_pts, away_form_pts, 
                is_b_team=False, home_games_week=0, away_games_week=0,
                attendance_spike=False, ref_avg_cards=2.0, weather="normal"):
    base = {
        1: (1.45, 1.05),  # Championship
        2: (1.30, 0.95),  # League One
        3: (1.20, 1.00),  # League Two
        4: (1.05, 1.25),  # Lowland/Highland
        5: (1.15, 1.10)   # B team base
    }
    att_h, def_h = base[home_tier]
    att_a, def_a = base[away_tier]

    # v4.11 NEW: B-team fatigue
    if is_b_team:
        if away_tier == 5:
            att_a += 0.25
            def_a -= 0.15
            if away_games_week >= 2:
                att_a -= 0.20  # Youth fatigue -0.20
        if home_tier == 5:
            att_h += 0.25
            def_h -= 0.15
            if home_games_week >= 2:
                att_h -= 0.20

    # Highland boost + crowd
    if home_tier == 4 and away_tier <= 2:
        att_h += 0.25
    if attendance_spike:
        att_h += 0.10

    # Form cap (v4.10) + inverse cap
    form_diff = (home_form_pts - away_form_pts) / 9.0
    if home_form_pts == 9 and away_form_pts <= 3:
        form_diff = min(form_diff, 0.15)
    if away_form_pts == 9 and home_form_pts <= 3:
        form_diff = max(form_diff, -0.15)

    # v4.11 NEW: Ref leniency = set piece boost for seniors
    if ref_avg_cards < 1.8:
        if home_tier <= 2:
            att_h += 0.05
        if away_tier <= 2:
            att_a += 0.05

    # v4.11 NEW: Heavy weather nerfs skill teams
    if weather == "heavy":
        if att_h > 1.3 or att_a > 1.3:
            att_h = max(0.8, att_h - 0.2)
            att_a = max(0.8, att_a - 0.2)

    total_boost = 0.35
    xg_h = att_h + (1.2 - def_a)*0.5 + form_diff*0.6 + 0.25 + total_boost/2
    xg_a = att_a + (1.2 - def_h)*0.5 - form_diff*0.6 + total_boost/2
    xg_h = max(0.5, round(xg_h,2))
    xg_a = max(0.4, round(xg_a,2))

    diff = xg_h - xg_a
    p1 = max(0.18, min(0.68, 0.5 + diff*0.20))
    p2 = max(0.15, min(0.42, 0.35 - diff*0.13))
    pd = 1 - p1 - p2

    total = xg_h + xg_a
    o25 = max(0.45, min(0.78, 0.20 + total*0.19))
    btts = max(0.42, min(0.72, 0.30 + (xg_h*xg_a)*0.20))

    exp = f"{int(round(xg_h))}-{int(round(xg_a))}"
    pick = "1" if p1>0.52 else "2" if p2>0.38 else "1X" if p1>p2 else "X2"
    return {"xG": f"{xg_h}-{xg_a}", "EXP": exp, "HDA": f"{p1*100:.1f}/{pd*100:.1f}/{p2*100:.1f}", "O2.5": f"{o25*100:.0f}%", "BTTS": f"{btts*100:.0f}%", "PICK": pick}
