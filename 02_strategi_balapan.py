import os
import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

os.makedirs('./cache', exist_ok=True)
fastf1.Cache.enable_cache('./cache')
fastf1.plotting.setup_mpl(
    mpl_timedelta_support=True,
    color_scheme='fastf1',
    misc_mpl_mods=True
)
print("✅ Setup selesai")

print("\n" + "=" * 50)
print("BAGIAN 1: Load Race Monaco GP 2023")
print("=" * 50)
print("⏳ Loading...\n")

race = fastf1.get_session(2023, 'Monaco Grand Prix', 'R')
race.load()

print(f"✅ {race.event['EventName']} - {race.name}")
print(f"Total baris lap: {len(race.laps)}")

# Top 10 finisher
top10_drivers = race.results.iloc[0:10]['Abbreviation'].tolist()
print(f"Top 10: {top10_drivers}")

print("\n" + "=" * 50)
print("BAGIAN 2: Tire Strategy")
print("=" * 50)

laps = race.laps

# Kelompokkan per driver + stint untuk tahu compound & lap range
stints = laps[['Driver', 'Stint', 'Compound', 'LapNumber']].copy()
stints = stints.groupby(['Driver', 'Stint', 'Compound'], as_index=False).agg(
    StartLap=('LapNumber', 'min'),
    EndLap=('LapNumber', 'max')
)
stints_top10 = stints[stints['Driver'].isin(top10_drivers)]

print("Data stint top 10:")
print(stints_top10.to_string(index=False))

# Warna standar compound ban F1
compound_colors = {
    'SOFT':         '#FF1E1E',
    'MEDIUM':       '#FFF200',
    'HARD':         '#EBEBEB',
    'INTERMEDIATE': '#43B02A',
    'WET':          '#0067FF',
    'UNKNOWN':      '#888888',
}

fig, ax = plt.subplots(figsize=(14, 7))
fig.suptitle(
    f'Tire Strategy — {race.event["EventName"]} {race.event["EventDate"].year}',
    fontsize=14, fontweight='bold'
)

for i, driver in enumerate(top10_drivers):
    driver_stints = stints_top10[stints_top10['Driver'] == driver]
    for _, stint in driver_stints.iterrows():
        compound = stint['Compound'] if isinstance(stint['Compound'], str) else 'UNKNOWN'
        color = compound_colors.get(compound.upper(), '#888888')
        ax.barh(
            y=i,
            width=stint['EndLap'] - stint['StartLap'] + 1,
            left=stint['StartLap'],
            color=color,
            edgecolor='black',
            linewidth=0.7,
            height=0.6
        )

ax.set_yticks(range(len(top10_drivers)))
ax.set_yticklabels(top10_drivers, fontsize=11)
ax.set_xlabel('Lap Number', fontsize=12)
ax.set_xlim(1, race.laps['LapNumber'].max() + 1)
ax.invert_yaxis()
ax.grid(True, axis='x', alpha=0.3)

legend_patches = [
    mpatches.Patch(color=c, label=name.title(), edgecolor='black')
    for name, c in compound_colors.items() if name != 'UNKNOWN'
]
ax.legend(handles=legend_patches, loc='lower right', fontsize=9)

plt.tight_layout()
plt.savefig('tire_strategy.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Disimpan: tire_strategy.png")

print("\n" + "=" * 50)
print("BAGIAN 3: Tire Degradation")
print("=" * 50)

drivers_analyze = ['VER', 'ALO', 'HAM']

fig, ax = plt.subplots(figsize=(13, 6))
fig.suptitle('Tire Degradation — Lap Time vs Tyre Life', fontsize=13, fontweight='bold')

for driver in drivers_analyze:
    driver_laps = race.laps.pick_drivers(driver).pick_quicklaps().copy()
    driver_laps['LapTimeSeconds'] = driver_laps['LapTime'].dt.total_seconds()
    color = fastf1.plotting.get_driver_color(driver, session=race)

    for compound in driver_laps['Compound'].dropna().unique():
        compound_laps = driver_laps[driver_laps['Compound'] == compound]
        ax.scatter(
            compound_laps['TyreLife'],
            compound_laps['LapTimeSeconds'],
            color=color,
            label=f'{driver} ({compound[:1]})',
            s=30,
            alpha=0.8
        )

ax.set_xlabel('Tyre Life (Laps)', fontsize=12)
ax.set_ylabel('Lap Time (seconds)', fontsize=12)
ax.legend(loc='upper left', fontsize=9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('tire_degradation.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Disimpan: tire_degradation.png")

print("\n" + "=" * 50)
print("BAGIAN 4: Race Position per Lap")
print("=" * 50)

fig, ax = plt.subplots(figsize=(14, 8))
fig.suptitle(
    f'Race Position per Lap — {race.event["EventName"]} {race.event["EventDate"].year}',
    fontsize=13, fontweight='bold'
)

for driver in top10_drivers:
    driver_laps = race.laps.pick_drivers(driver)
    color = fastf1.plotting.get_driver_color(driver, session=race)
    ax.plot(
        driver_laps['LapNumber'],
        driver_laps['Position'],
        label=driver,
        color=color,
        linewidth=2,
        alpha=0.9
    )

ax.set_xlabel('Lap Number', fontsize=12)
ax.set_ylabel('Position', fontsize=12)
ax.set_yticks(range(1, 21))
ax.invert_yaxis()
ax.legend(loc='right', fontsize=9, bbox_to_anchor=(1.12, 0.5))
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('race_positions.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Disimpan: race_positions.png")

print("\n" + "=" * 50)
print("BAGIAN 5: Analisis Pit Stop")
print("=" * 50)

pit_laps = race.laps[race.laps['PitInTime'].notna()][
    ['Driver', 'LapNumber', 'PitInTime', 'PitOutTime', 'Compound']
].copy()
pit_laps['PitDuration'] = (pit_laps['PitOutTime'] - pit_laps['PitInTime']).dt.total_seconds()

pit_laps_top10 = pit_laps[pit_laps['Driver'].isin(top10_drivers)].dropna(subset=['PitDuration'])
pit_laps_top10 = pit_laps_top10[pit_laps_top10['PitDuration'] > 10]

print("Pit stop top 10 driver:")
print(pit_laps_top10[['Driver', 'LapNumber', 'PitDuration', 'Compound']].to_string(index=False))

if not pit_laps_top10.empty:
    fig, ax = plt.subplots(figsize=(12, 5))
    colors_bars = [fastf1.plotting.get_driver_color(d, session=race) for d in pit_laps_top10['Driver']]
    bars = ax.bar(
        range(len(pit_laps_top10)),
        pit_laps_top10['PitDuration'],
        color=colors_bars,
        edgecolor='black',
        linewidth=0.5
    )

    for bar, (_, row) in zip(bars, pit_laps_top10.iterrows()):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.2,
            f"{row['PitDuration']:.1f}s\n(Lap {int(row['LapNumber'])})",
            ha='center', va='bottom', fontsize=8
        )

    ax.set_xticks(range(len(pit_laps_top10)))
    ax.set_xticklabels([row['Driver'] for _, row in pit_laps_top10.iterrows()])
    ax.set_ylabel('Pit Stop Duration (seconds)')
    ax.set_title(f"Pit Stop Durations — {race.event['EventName']} {race.event['EventDate'].year}")
    ax.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('pit_stop_durations.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("✅ Disimpan: pit_stop_durations.png")

print("\n🏁🏁🏁🏁🏁🏁🏁🏁")
