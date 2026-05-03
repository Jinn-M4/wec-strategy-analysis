SIMULATION_RUNS = 10

import pandas as pd
import random

TIRE_COMPOUNDS = {
    "Soft": {
        "deg_factor_mult": 1.6,
        "base_time_offset": -1.2
    },
    "Medium": {
        "deg_factor_mult": 1.0,
        "base_time_offset": 0.0
    },
    "Hard": {
        "deg_factor_mult": 0.55,
        "base_time_offset": 0.3
    }
}

COMPOUND_SEQUENCES = {
        2: [ # 2-stop 일때
            ["Soft", "Medium", "Hard"],
            ["Medium", "Hard", "Hard"],
            ["Soft", "Hard", "Hard"],
            ["Medium", "Medium", "Hard"]
        ],

        3: [ # 3-stop 일때
            ["Soft", "Soft", "Medium", "Hard"],
            ["Soft", "Medium", "Medium", "Hard"],
            ["Medium", "Medium", "Hard", "Hard"]
        ]
    }

def extract_degradation_pattern(df):
    # 첫 stint만 추출
    first_stint = df[df["stint"] == 1].copy()
    first_stint = first_stint.reset_index(drop=True)

    # lap 기준 증가량 계산
    base_time = first_stint.loc[0, "lap_time"]
    first_stint["degradation"] = first_stint["lap_time"] - base_time

    return first_stint["degradation"].tolist(), base_time

def compute_lap_time(
    i, 
    stint_length, 
    base_time, 
    degradation_pattern, 
    deg_factor, 
    deg_exp, 
    fuel_factor,
    compound="Medium"
    ):

    if i < len(degradation_pattern):
        deg = degradation_pattern[i]

    else:
        # Telemetry 범위를 초과한 경우
        extra_laps = i - len(degradation_pattern) + 1

        # nonlinear tire degradation 증가
        deg = (
            degradation_pattern[-1]
            + 0.18 * (extra_laps ** 1.35)
        )
    
    compound_data = TIRE_COMPOUNDS[compound]

    compound_deg = (
        deg_factor * compound_data["deg_factor_mult"]
    )

    base_offset = compound_data["base_time_offset"]
    
    tire_effect = (deg * compound_deg) ** deg_exp

    fuel_load = (stint_length - i) / stint_length
    fuel_penalty = fuel_load * fuel_factor
    
    random_variation = random.uniform(-0.15, 0.15)

    return (
        base_time 
        + base_offset 
        + tire_effect 
        + fuel_penalty
        + random_variation
    )

def simulate_strategy(
    df,
    stint_length, 
    pit_loss=25,  # 피트 소요 시간: 25 
    deg_factor=1.5, 
    deg_exp=1.3, 
    fuel_factor=8,
    compound="Medium",
    safety_car_prob=0.0
    ): 

    degradation_pattern, base_time = extract_degradation_pattern(df)

    total_time = 0
    total_laps = len(df)

    current_lap = 0
    while current_lap < total_laps:
        for i in range(stint_length):
            if current_lap >= total_laps:
                break

            lap_time = compute_lap_time(
                i, 
                stint_length, 
                base_time, 
                degradation_pattern,
                deg_factor, 
                deg_exp,
                fuel_factor,
                compound
            )

            total_time += lap_time
            current_lap += 1

        # 피트
        if current_lap < total_laps:

            adjusted_pit_loss = pit_loss

            # Safety Car 발생
            if random.random() < safety_car_prob:
                adjusted_pit_loss *= 0.5 # Safety Car 발생 시 피트 손해 12.5초로 변동됨

            total_time += adjusted_pit_loss

    return total_time

def simulate_strategy_sequence(
    df, 
    stint_lengths, 
    pit_loss=25, 
    deg_factor=1.5, 
    deg_exp=1.3, 
    fuel_factor=8,
    safety_car_prob=0.0
    ):

    degradation_pattern, base_time = extract_degradation_pattern(df)

    total_time = 0 
    total_laps = len(df)
    current_lap = 0

    for stint_length, compound in stint_lengths:
        for i in range(stint_length):
            if current_lap >= total_laps:
                break

            lap_time = compute_lap_time(
                i,stint_length, base_time, 
                degradation_pattern, deg_factor, deg_exp,
                fuel_factor, compound
            )

            total_time += lap_time
            current_lap += 1
        
        # 마지막 stint 아니면 pit stop
        if current_lap < total_laps:

            adjusted_pit_loss = pit_loss

            if random.random() < safety_car_prob:
                adjusted_pit_loss *= 0.5

            total_time += adjusted_pit_loss

    return total_time        

def simulate_multiple_runs(
    df,
    strategy,
    runs,
    pit_loss,
    deg_factor,
    deg_exp,
    fuel_factor,
    safety_car_prob
):
    
    total = 0

    for _ in range(runs):

        total += simulate_strategy_sequence(
            df,
            strategy,
            pit_loss,
            deg_factor,
            deg_exp,
            fuel_factor,
            safety_car_prob
        )

    return total / runs

def find_optimal_strategy(
    df, 
    pit_loss=25, 
    deg_factor=1.5, 
    deg_exp=1.3, 
    fuel_factor=8,
    compound="Medium",
    safety_car_prob=0.0
    ):

    best_time = float("inf")
    best_stint = None

    for stint_length in range(5, 25):  # 탐색 범위
        total_time = simulate_strategy(
            df, 
            stint_length, 
            pit_loss, 
            deg_factor, 
            deg_exp, 
            fuel_factor,
            compound,
            safety_car_prob
            )

        if total_time < best_time:
            best_time = total_time
            best_stint = stint_length
        

    return best_stint, best_time

def find_best_strategy_combo(
    df, 
    pit_loss=25, 
    deg_factor=1.5, 
    deg_exp=1.3, 
    fuel_factor=8,
    safety_car_prob=0.0
    ):

    best_time = float("inf")
    best_strategy = None
    
    for stop_count in [2, 3]:

        strategy, time = find_best_strategy_by_stop_count(
            df,
            stop_count,
            pit_loss,
            deg_factor,
            deg_exp,
            fuel_factor,
            safety_car_prob
        )

        if time < best_time:
            best_time = time
            best_strategy = strategy
    

    return best_strategy, best_time

def generate_strategy_combinations(total_laps, num_stints, min_stint=5):

    strategies = []

    def backtrack(remaining_laps, current_strategy):

        # 마지막 stint
        if len(current_strategy) == num_stints - 1:

            final_stint = remaining_laps

            if final_stint >= min_stint:
                strategies.append(current_strategy + [final_stint])

            return

        # 현재 stint 탐색
        max_stint = remaining_laps - min_stint * (
            num_stints - len(current_strategy) - 1
        )

        for stint in range(min_stint, min(max_stint, 12) + 1):

            backtrack(
                remaining_laps - stint, 
                current_strategy + [stint]
            )

    backtrack(total_laps, [])

    return strategies

def find_best_strategy_by_stop_count(
    df,
    stop_count,
    pit_loss=25,
    deg_factor=1.5,
    deg_exp=1.3,
    fuel_factor=8,
    safety_car_prob=0.0
):
    
    total_laps = len(df)

    num_stints = stop_count + 1

    strategies = generate_strategy_combinations(
        total_laps,
        num_stints
    )

    best_time = float("inf")
    best_strategy = None

    compound_sequences = COMPOUND_SEQUENCES[stop_count]

    for strategy in strategies:

        for compound_sequence in compound_sequences:

            compound_strategy = list(
                zip(strategy, compound_sequence)
            )

            time = simulate_multiple_runs(
                df,
                compound_strategy,
                SIMULATION_RUNS,
                pit_loss,
                deg_factor,
                deg_exp,
                fuel_factor,
                safety_car_prob
            )
            
            if time < best_time:
                best_time = time
                best_strategy = compound_strategy

    return best_strategy, best_time