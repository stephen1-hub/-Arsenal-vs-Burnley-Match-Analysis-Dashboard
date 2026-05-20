# ---------------------------------------------------
# IMPORT LIBRARIES
# ---------------------------------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
from mplsoccer import Pitch
import matplotlib.pyplot as plt

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Arsenal vs Burnley Shot Analysis",
    layout="wide"
)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.title("⚽ Arsenal vs Burnley Shot Analysis Dashboard")

st.markdown("""
### Tactical & xG Analysis

This dashboard explores:
- Shot Locations
- Expected Goals (xG)
- Player Threat
- Shot Outcomes
- Tactical Efficiency
""")

# ---------------------------------------------------
# DATASET
# ---------------------------------------------------
data = {
    "team": [
        "Arsenal","Arsenal","Arsenal","Arsenal","Arsenal","Arsenal",
        "Arsenal","Arsenal","Arsenal","Arsenal","Arsenal","Arsenal",
        "Arsenal","Burnley","Burnley","Burnley","Burnley","Burnley"
    ],

    "player": [
        "Bukayo Saka","Bukayo Saka","Bukayo Saka",
        "Eberechi Eze","Eberechi Eze","Eberechi Eze",
        "Gabriel","Kai Havertz","Kai Havertz","Kai Havertz",
        "Leandro Trossard","Leandro Trossard","Martin Odegaard",
        "Florentino Luís","Hannibal Mejbri","Hannibal Mejbri",
        "Jaidon Anthony","Loum Tchaouna"
    ],

    "X": [
        0.813,0.869,0.973,
        0.815,0.896,0.918,
        0.781,
        0.902,0.931,0.958,
        0.788,0.854,
        0.864,
        0.812,0.747,0.909,
        0.753,0.872
    ],

    "Y": [
        0.338,0.331,0.303,
        0.542,0.474,0.507,
        0.667,
        0.380,0.305,0.482,
        0.568,0.614,
        0.550,
        0.505,0.544,0.648,
        0.652,0.307
    ],

    "xG": [
        0.040854,0.050398,0.071398,
        0.059477,0.113144,0.068261,
        0.018437,
        0.056986,0.060654,0.499152,
        0.036300,0.054298,
        0.097594,
        0.036573,0.021653,0.070853,
        0.016024,0.049781
    ],

    "result": [
        "MissedShots","BlockedShot","MissedShots",
        "SavedShot","ShotOnPost","SavedShot",
        "MissedShots",
        "MissedShots","BlockedShot","Goal",
        "ShotOnPost","MissedShots",
        "BlockedShot",
        "MissedShots","MissedShots","MissedShots",
        "MissedShots","BlockedShot"
    ],

    "shots": [1] * 18
}

df = pd.DataFrame(data)

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------
st.sidebar.header("Dashboard Filters")

# Team selector
team_filter = st.sidebar.selectbox(
    "Select Team",
    ["All Teams"] + sorted(df["team"].unique())
)

# Dynamic player selector
if team_filter == "All Teams":
    player_options = sorted(df["player"].unique())
else:
    player_options = sorted(
        df[df["team"] == team_filter]["player"].unique()
    )

player_filter = st.sidebar.selectbox(
    "Select Player",
    ["All Players"] + player_options
)

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------
filtered_df = df.copy()

# Team filter
if team_filter != "All Teams":
    filtered_df = filtered_df[
        filtered_df["team"] == team_filter
    ]

# Player filter
if player_filter != "All Players":
    filtered_df = filtered_df[
        filtered_df["player"] == player_filter
    ]

# ---------------------------------------------------
# KPIs
# ---------------------------------------------------
st.subheader("📊 Match KPIs")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Shots",
        len(filtered_df)
    )

with col2:
    st.metric(
        "Total xG",
        round(filtered_df["xG"].sum(), 3)
    )

with col3:
    goals = (
        filtered_df["result"] == "Goal"
    ).sum()

    st.metric(
        "Goals",
        goals
    )

with col4:
    st.metric(
        "Avg xG per Shot",
        round(filtered_df["xG"].mean(), 3)
    )

# ---------------------------------------------------
# SHOT MAP
# ---------------------------------------------------
st.subheader("🎯 Shot Map (xG Intensity)")

# Coordinate conversion
filtered_df["plotX"] = filtered_df["X"] * 100
filtered_df["plotY"] = filtered_df["Y"] * 100

# Create pitch
pitch = Pitch(
    pitch_type="opta",
    pitch_color="#1e1e1e",
    line_color="white"
)

fig, ax = pitch.draw(figsize=(9, 6))

# Scatter shots
scatter = pitch.scatter(
    filtered_df["plotX"],
    filtered_df["plotY"],
    s=filtered_df["xG"] * 2500,
    c=filtered_df["xG"],
    cmap="coolwarm",
    edgecolors="black",
    linewidth=1,
    alpha=0.85,
    ax=ax
)

# Colorbar
cbar = plt.colorbar(
    scatter,
    ax=ax,
    fraction=0.03,
    pad=0.02
)

cbar.set_label("xG")

# Title
ax.set_title(
    f"Shot Map — {player_filter}",
    fontsize=15,
    color="white",
    pad=12
)

st.pyplot(fig)

# ---------------------------------------------------
# PLAYER PERFORMANCE
# ---------------------------------------------------
st.subheader("🔥 Player Performance")

player_summary = (
    filtered_df.groupby(["team", "player"])
    .agg(
        shots=("shots", "count"),
        total_xG=("xG", "sum"),
        goals=("result", lambda x: (x == "Goal").sum()),
        on_target=("result", lambda x: x.isin(
            ["Goal", "SavedShot", "ShotOnPost"]
        ).sum())
    )
    .reset_index()
    .sort_values("total_xG", ascending=False)
)

st.dataframe(
    player_summary,
    use_container_width=True
)

# ---------------------------------------------------
# xG LEADERBOARD
# ---------------------------------------------------
st.subheader("📈 xG Leaderboard")

fig_xg = px.bar(
    player_summary,
    x="player",
    y="total_xG",
    color="team",
    text_auto=".3f"
)

fig_xg.update_layout(
    template="plotly_dark",
    xaxis_title="Player",
    yaxis_title="Total xG",
    xaxis_tickangle=45
)

st.plotly_chart(
    fig_xg,
    use_container_width=True
)

# ---------------------------------------------------
# SHOT OUTCOME DISTRIBUTION
# ---------------------------------------------------
st.subheader("⚽ Shot Outcome Distribution")

result_counts = (
    filtered_df["result"]
    .value_counts()
    .reset_index()
)

result_counts.columns = [
    "result",
    "count"
]

fig_result = px.bar(
    result_counts,
    x="result",
    y="count",
    color="result",
    text_auto=True
)

fig_result.update_layout(
    template="plotly_dark",
    xaxis_title="Shot Result",
    yaxis_title="Count"
)

st.plotly_chart(
    fig_result,
    use_container_width=True
)

# ---------------------------------------------------
# TACTICAL INSIGHTS
# ---------------------------------------------------
st.subheader("📌 Tactical Insights")

st.markdown("""
### Arsenal
- Generated higher-quality chances
- Kai Havertz recorded the highest xG contribution
- Multiple attackers occupied central danger zones

### Burnley
- Relied on lower-quality shooting opportunities
- Limited penalty-box penetration
- Struggled to create high xG chances

### Tactical Conclusion
Arsenal produced more dangerous shooting situations and showed superior chance quality throughout the match.
""")