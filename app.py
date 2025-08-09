
import streamlit as st
import pandas as pd
import sqlite3, json, datetime as dt, numpy as np
from pathlib import Path
from templates import generate_routine, SPLITS

DB_PATH = Path(__file__).parent / "pt.db"
EQUIP_PATH = Path(__file__).parent / "equipment.json"

st.set_page_config(page_title="PT Log — 병승 전용", page_icon="💪", layout="wide")

@st.cache_data
def load_equipment():
    return json.loads(EQUIP_PATH.read_text(encoding="utf-8"))

def get_conn():
    return sqlite3.connect(DB_PATH)

def get_last_best(exercise:str, lookback_days:int=120):
    conn = get_conn()
    df = pd.read_sql_query(
        """SELECT date, exercise, MAX(weight) AS max_w, MAX(reps) AS max_r
               FROM sets s JOIN workouts w ON s.workout_id=w.id
               WHERE exercise=? AND date >= ?
               GROUP BY date, exercise
               ORDER BY date DESC""",
        conn, params=(exercise, (dt.date.today()-dt.timedelta(days=lookback_days)).isoformat())
    )
    conn.close()
    if df.empty:
        return None
    # take the overall best by weight first, then reps
    row = df.sort_values(["max_w","max_r"], ascending=[False, False]).iloc[0]
    return {"date":row["date"], "weight":row["max_w"], "reps":row["max_r"]}

def save_workout(split:str, injury_flags:str, notes:str, rows:list):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO workouts(date, split, injury_flags, notes) VALUES (?,?,?,?)",
                (dt.date.today().isoformat(), split, injury_flags, notes))
    wid = cur.lastrowid
    for r in rows:
        cur.execute("INSERT INTO sets(workout_id, exercise, bodypart, weight, reps, rpe) VALUES (?,?,?,?,?,?)",
                    (wid, r["exercise"], r["bodypart"], r["weight"], r["reps"], r.get("rpe", None)))
    conn.commit(); conn.close()
    return wid

def fetch_history(n_days:int=60):
    conn = get_conn()
    df = pd.read_sql_query(
        """SELECT w.date, w.split, s.exercise, s.bodypart, s.weight, s.reps, s.rpe
               FROM workouts w JOIN sets s ON w.id=s.workout_id
               WHERE date >= ?
               ORDER BY w.date DESC, s.exercise""", conn,
        params=((dt.date.today()-dt.timedelta(days=n_days)).isoformat(),))
    conn.close()
    return df

st.title("💪 병승 전용 — 루틴 · 기록 · 피드백")

equip = load_equipment()
knee_safe = st.sidebar.toggle("🦵 Knee-safe mode (meniscus)", value=True)
split = st.sidebar.selectbox("오늘의 스플릿", SPLITS, index=0)
date_use = st.sidebar.date_input("운동 날짜", dt.date.today())
st.sidebar.write("헬스장 기구:", ", ".join(equip["has"]["back"][:3]), "…")

st.header("1) 오늘 루틴 생성")
plan, sugg = generate_routine(split, equip, knee_safe=knee_safe, day=date_use)
df_plan = pd.DataFrame([{"Exercise":ex, "Bodypart":bp, "Sets/Reps":f'{sugg[ex]["sets"]} × {sugg[ex]["reps"]}', "Last best": ""} for ex, bp in plan])

# Fill last best
for i, row in df_plan.iterrows():
    lb = get_last_best(row["Exercise"])
    if lb:
        df_plan.at[i,"Last best"] = f'{lb["weight"]} kg × {int(lb["reps"])} (@{lb["date"]})'
    else:
        df_plan.at[i,"Last best"] = "—"

st.dataframe(df_plan, use_container_width=True)

st.header("2) 수행 기록 입력")
st.caption("아래 표에 오늘 수행한 세트를 입력하세요. (무게, 반복수). 필요 없는 운동은 비워두세요.")
rows = []
for ex, bp in plan:
    with st.expander(f"{ex} — {bp}"):
        num_sets = st.number_input(f"{ex} 세트 수", min_value=0, max_value=10, value=3, key=f"sets_{ex}")
        for s in range(1, num_sets+1):
            cols = st.columns(3)
            w = cols[0].number_input(f"무게(kg) 세트{s}", min_value=0.0, max_value=1000.0, value=0.0, key=f"w_{ex}_{s}")
            r = cols[1].number_input(f"반복수 세트{s}", min_value=0, max_value=100, value=0, key=f"r_{ex}_{s}")
            rpe = cols[2].number_input(f"RPE 세트{s}", min_value=0.0, max_value=10.0, value=0.0, key=f"rpe_{ex}_{s}")
            if w>0 and r>0:
                rows.append({"exercise":ex, "bodypart":bp, "weight":w, "reps":r, "rpe":rpe})

injury = "knee_safe" if knee_safe else ""
notes = st.text_area("메모 (옵션)", placeholder="컨디션, 통증, 대체 운동 등")

if st.button("💾 오늘 기록 저장"):
    if rows:
        wid = save_workout(split, injury, notes, rows)
        st.success(f"기록 저장 완료! workout_id={wid}")
    else:
        st.warning("입력된 세트가 없습니다. 한 세트 이상 입력해주세요.")

st.header("3) 자동 피드백")
if rows:
    # Compare per exercise vs last best
    fb_lines = []
    for ex in set([r["exercise"] for r in rows]):
        best_today_w = max([r["weight"] for r in rows if r["exercise"]==ex])
        best_today_r = max([r["reps"] for r in rows if r["exercise"]==ex and r["weight"]==best_today_w], default=0)
        lb = get_last_best(ex)
        if lb is None:
            fb_lines.append(f"• {ex}: 첫 기록! 오늘 {best_today_w} kg × {best_today_r}. 폼 유지하며 2주간 2.5~5kg 증량 시도.")
        else:
            win_w = best_today_w > lb["weight"] + 0.5
            tie_w = abs(best_today_w - lb["weight"]) <= 0.5
            improve = ""
            if win_w:
                improve = f"PR 갱신! (기존 {lb['weight']}kg → 오늘 {best_today_w}kg)"
            elif tie_w and best_today_r > lb["reps"]:
                improve = f"반복수 향상! (기존 {int(lb['reps'])}회 → 오늘 {int(best_today_r)}회)"
            else:
                improve = "유지. 다음엔 템포·그립 변화로 자극 다양화."
            fb_lines.append(f"• {ex}: {improve}")
    st.write("\n".join(fb_lines))
else:
    st.info("기록을 입력하면 자동 피드백이 생성됩니다.")

st.header("4) 기록/분석")
col1, col2 = st.columns(2)
with col1:
    days = st.slider("최근 N일", 14, 180, 60)
with col2:
    bodypart_filter = st.multiselect("부위 필터", ["Back","Chest","Legs","Shoulders","Biceps","Triceps"], default=[])

df_hist = fetch_history(days)
if not df_hist.empty:
    if bodypart_filter:
        df_hist = df_hist[df_hist["bodypart"].isin(bodypart_filter)]
    st.dataframe(df_hist, use_container_width=True)
    # Simple pivot: total volume by bodypart
    df_hist["volume"] = df_hist["weight"] * df_hist["reps"]
    vol = df_hist.groupby(["date","bodypart"], as_index=False)["volume"].sum()
    st.line_chart(vol.pivot(index="date", columns="bodypart", values="volume").fillna(0))
else:
    st.caption("표시할 기록이 아직 없습니다.")

st.divider()
st.caption("Tip: knee-safe 모드가 켜져 있으면 하체 루틴은 스쿼트/프레스류가 자동 제외됩니다.")
