import sys
import os
import math

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from src.strategy_simulator import (
    find_optimal_strategy, 
    find_best_strategy_combo, 
    find_best_strategy_by_stop_count,
    compute_lap_time, 
    extract_degradation_pattern, 
    TIRE_COMPOUNDS
    )


st.title("WEC Race Strategy Simulator")

st.caption(
    "Endurance race strategy optimization with tire degradation and pit-stop modeling."
)

# CSV 불러오기
data_path = os.path.join(os.path.dirname(__file__), '../data/lap_times.csv')
df = pd.read_csv(data_path)

st.header("Data Analysis (Raw Data)")

with st.expander("Telemetry Logs"):
    st.write(df)

degradation_pattern, base_time = extract_degradation_pattern(df)

# 그래프 (랩타임 변화)
st.subheader("Lap Time Degradation") 

fig, ax = plt.subplots(figsize=(10,4))
ax.plot(df["lap"], df["lap_time"])
ax.set_xlabel("Lap")
ax.set_ylabel("Lap Time")
ax.set_title("Lap Time vs Lap")

st.pyplot(fig)

# stint별 평균 계산
stint_avg = df.groupby("stint")["lap_time"].mean()

st.write("Average Lap Time per Stint", stint_avg) # 로그 생성

# 타이어 열화 시각화 (기울기 증가 -> 타이어 성능 저하)
st.subheader("Degradation per stint")

fig2, ax2 = plt.subplots(figsize=(10,4))

for stint in df["stint"].unique():
    stint_data = df[df["stint"] == stint]
    ax2.plot(stint_data["lap"], stint_data["lap_time"], label=f"Stint {stint}")

ax2.set_xlabel("Lap")
ax2.set_ylabel("Lap Time")
ax2.set_title("Degradation by Stint")
ax2.legend()

st.pyplot(fig2)

st.subheader("Degradation Rate") # 타이어 열화율을 통해 몇랩마다 피트 들어가야 하는지 계산 가능!

df["lap_diff"] = df["lap_time"].diff() # lap_diff : 한 랩마다 얼마나 느려졌는지, 0.2~0.4면 정상, 0.8 이상이면 급격한 degradation

with st.expander("Degradation Logs"):
    st.write(df[["lap", "lap_time", "lap_diff"]])

st.divider()


st.header("Strategy Simulation") # 여기부터 섹션 크게 분리!!!

with st.sidebar: 

    st.header("Simulation Parameters")

    deg_factor = st.slider(
        "Degradation Factor",
        1.0,
        3.0,
        1.5
    )

    deg_exp = st.slider(
        "Degradation Exponent",
        1.0,
        2.0,
        1.3
    )

    fuel_factor = st.slider(
        "Fuel Load Effect",
        0.0,
        10.0,
        8.0
    )

    baseline_compound = st.selectbox(
        "Baseline Tire Model",
        list(TIRE_COMPOUNDS.keys())
    )
    st.caption(
        "Used only for equal-stint baseline simulation."
    )

    safety_car_prob = st.slider(
        "Safety Car Probability",
        0.0,
        0.5,
        0.1
    )

best_stint, best_time = find_optimal_strategy(
    df, 
    pit_loss=25, 
    deg_factor=deg_factor,
    deg_exp=deg_exp,
    fuel_factor=fuel_factor,
    compound=baseline_compound,
    safety_car_prob=safety_car_prob
    )

# 최적화 전략 출력
st.subheader("Optimal strategy") # 로그 이름
st.write("Note: Baseline simulation using equal stint lengths and a single tire compound.")

num_stops = math.ceil(len(df) / best_stint) - 1

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric(
        "Optimal Stint",
        f"{best_stint} laps"
    )

with kpi2:
    st.metric(
        "Race Time",
        f"{round(best_time,1)} sec"
    )

with kpi3:
    st.metric(
        "Pit Stops",
        num_stops
    )


# pit stop 2번 or 3번중 어떤게 최적일지에 대한 그래프
st.subheader("Best Full Strategy (2-stop vs 3-stop)")

best_combo, combo_time = find_best_strategy_combo(
    df, 
    pit_loss=25, 
    deg_factor=deg_factor, 
    deg_exp=deg_exp,
    fuel_factor=fuel_factor,
    safety_car_prob=safety_car_prob
)

# 최적값 결과에 대한 한줄 해석
stop_count = len(best_combo) - 1

if stop_count >= 3:
    st.info(
        "Aggressive multi-stop strategy selected due to high tire degradation."
    )
else:
    st.info(
        "Long-run consistency favors fewer pit stops."
    )

compound_icons = {
    "Soft": "🔴",
    "Medium": "🟡",
    "Hard": "⚫"
}

strategy_text = " → ".join(
    [
        f"{compound_icons[compound]} {compound}({stint})"
        for stint, compound in best_combo
    ]
)

st.subheader("Best Mixed Strategy")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Strategy Type",
        f"{len(best_combo)-1}-stop mixed"
    )

with col2:
    
    st.metric(
        "Race Time",
        f"{round(combo_time,1)} sec"
    )

with col3:
    st.metric(
        "Pit Stops",
        len(best_combo)-1
    )

st.divider()


st.markdown("### Tire Strategy Timeline")

timeline_cols = st.columns(len(best_combo))

for idx, (stint, compound) in enumerate(best_combo):
    with timeline_cols[idx]:

        icon = compound_icons[compound]

        st.markdown(
            f"""
            ### {icon} {compound}
            **Stint {idx+1}**
            {stint} laps
            """
        )

# 2-stop vs 3-stop 상세 비교
st.subheader("Strategy Decision Insight")

best_2stop, time_2stop = find_best_strategy_by_stop_count(
    df, 
    2,
    25,
    deg_factor, 
    deg_exp, 
    fuel_factor,
    safety_car_prob
)

best_3stop, time_3stop = find_best_strategy_by_stop_count(
    df,
    3, 
    25, 
    deg_factor, 
    deg_exp, 
    fuel_factor,
    safety_car_prob
)

col1, col2 = st.columns(2)

col1.metric(
    "2-Stop Strategy",
    f"{round(time_2stop,2)} sec"
)

col2.metric(
    "3-Stop Strategy",
    f"{round(time_3stop,2)} sec"
)

time_diff = abs(time_2stop - time_3stop)

recommended = (
    "2-stop"
    if time_2stop < time_3stop
    else "3-stop"
)

st.metric(
    "Recommended Strategy",
    recommended
)

st.write(f"Time Difference: {round(time_diff,2)} sec")

st.divider()


# 모델 기반 전체 레이스 시뮬레이션 그래프
st.subheader("Simulated Lap Time vs Lap")

sim_laps = []
sim_times = []
current_lap = 0

for stint_length, compound in best_combo:
    for i in range(stint_length):
        lap_time = compute_lap_time(
            i,
            stint_length,
            base_time,
            degradation_pattern,
            deg_factor,
            deg_exp,
            fuel_factor,
            compound=compound
        )
        sim_times.append(lap_time)
        sim_laps.append(current_lap)
        current_lap += 1

fig_sim, ax_sim = plt.subplots(figsize=(12,5))
ax_sim.plot(
    sim_laps, 
    sim_times,
    linewidth=2)

pit_lap = 0

first_pit = best_combo[0][0]

for stint_length, compound in best_combo[:-1]:

    pit_lap += stint_length
    
    ax_sim.axvline(
        x=pit_lap,
        linestyle="--",
        alpha=0.7,
        label="Pit Window" if pit_lap == first_pit else ""
    )

ax_sim.legend()
ax_sim.set_title("Simulated Race Lap Time")
ax_sim.set_xlabel("Lap")
ax_sim.set_ylabel("Lap Time")

st.pyplot(fig_sim)

pit_losses = [20, 25, 30, 35, 40]
results = []

for pit in pit_losses:
    temp_stint, temp_time = find_optimal_strategy(
        df, 
        pit_loss=pit, 
        deg_factor=deg_factor, 
        deg_exp=deg_exp, 
        fuel_factor=fuel_factor,
        compound=baseline_compound,
        safety_car_prob=safety_car_prob
        )

    results.append((pit, temp_stint, temp_time))

st.subheader("Pit Loss Sensitivity")

pit_values = [r[0] for r in results]
best_stints = [r[1] for r in results]

fig_pit, ax_pit = plt.subplots(figsize=(10,4))

ax_pit.plot(
    pit_values,
    best_stints,
    marker="o"
)

ax_pit.set_xlabel("Pit Loss (sec)")
ax_pit.set_ylabel("Optimal Stint Length")
ax_pit.set_title("Strategy Sensitivity to Pit Loss")

st.pyplot(fig_pit)


