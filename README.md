# WEC Race Strategy Simulator

Endurance racing strategy simulator based on tire degradation, fuel load dynamics, and pit-stop optimization.

This project models race strategy decisions by simulating lap times under different conditions and evaluating optimal pit strategies, tire compound choices, and race scenarios.

---

🔗 Live Demo: [https://your-app-url.streamlit.app](https://wec-strategy-analysis-pvnt5bxqsnrpkpt4bwcgtb.streamlit.app/)

---

# Overview

In endurance racing, strategy is a trade-off between:

* Tire degradation (performance loss over time)
* Fuel load (weight vs speed)
* Pit stop cost (time loss vs fresh tires)

This simulator explores that trade-off using a data-driven approach based on telemetry logs.

---

# Core Modeling Logic

## 1. Tire Degradation Model

* Based on telemetry-derived lap time differences
* Modeled as a progressive performance loss over each stint

Key idea:

* Early laps → stable performance
* Later laps → increasing degradation impact

```python
tire_effect = deg_rate * i * deg_factor * compound_multiplier
```

---

## 2. Fuel Load Model

Fuel affects lap time across the entire race:

* Heavy fuel → slower lap times
* Light fuel → faster lap times

```python
fuel_load = (total_laps - current_lap) / total_laps
fuel_penalty = fuel_load * fuel_factor
```

Resulting behavior:

> Stint start → slow (heavy fuel)
> Mid stint → fastest
> Stint end → slow again (tire degradation dominates)

---

## 3. Tire Compound Strategy

Each compound has different characteristics:

| Compound | Grip     | Degradation | Base Pace |
| -------- | -------- | ----------- | --------- |
| Soft     | High     | Fast wear   | Fastest   |
| Medium   | Balanced | Moderate    | Neutral   |
| Hard     | Low      | Slow wear   | Slowest   |

Supports:

* Single compound strategies
* Mixed compound strategies (e.g., Soft → Medium → Hard)

---

## 4. Pit Stop Modeling

* Fixed pit loss (default: 25 sec)
* Optional Safety Car effect

```python
if random.random() < safety_car_prob:
    pit_loss *= 0.5
```

---

## Key Features

* Optimal stint length search
* Multi-stop strategy comparison (2-stop vs 3-stop)
* Mixed tire compound strategies
* Safety Car probability modeling
* Monte Carlo simulation (random lap variation)
* Interactive dashboard (Streamlit)

---

# Dashboard

The dashboard provides:

* Raw telemetry visualization
* Tire degradation analysis
* Strategy optimization results
* Tire strategy timeline (visual)
* Simulated lap time vs lap graph
* Pit loss sensitivity analysis

---

# Development Timeline

## 2026-04-23

* Implemented non-linear tire degradation behavior
* Introduced fuel load model

Key insight:

* Stint performance curve:

  * Early → slow (fuel)
  * Mid → fastest
  * Late → slow (degradation)

---

## 2026-05-02

* Added tire compound system
* Introduced Safety Car probability
* Refactored code (removed duplication)
* Improved dashboard UI and visualization clarity

---

## 2026-05-03

* Improved degradation model beyond telemetry range
* Reduced simulation runs (50 → 10) for performance
* Added mixed compound strategies
* Enhanced dashboard layout and usability

---

# Limitations

* Tire degradation modeled as simplified function (not fully physics-based)
* Fuel model assumes linear weight effect
* Safety Car is probabilistic, not event-driven
* Strategy search space is partially constrained (predefined compound sets)

---

# Tech Stack

* Python
* Pandas
* Matplotlib
* Streamlit

---

# Conclusion

This project demonstrates how race strategy can be modeled as a balance between:

* Performance degradation
* Resource management (fuel, tires)
* Operational cost (pit stops)

Rather than relying on fixed rules, the simulator evaluates strategies through simulation and data-driven modeling.

---
