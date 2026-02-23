import fastf1
import pandas as pd

print(f"FastF1 version: {fastf1.__version__}")

fastf1.Cache.enable_cache('./cache')
print("✅ Cache aktif di folder './cache'\n")

# get_session(year, gp, identifier)
# identifier: 'FP1', 'FP2', 'FP3', 'Q', 'SQ', 'S', 'R'

print("=" * 50)
print("BAGIAN 2: Load Session")
print("=" * 50)

session = fastf1.get_session(2021, 7, 'Q')
print(f"Nama Sesi  : {session.name}")
print(f"Tanggal    : {session.date}")
print(f"Event      : {session.event['EventName']}")
print(f"Negara     : {session.event['Country']}")
print(f"Lokasi     : {session.event['Location']}")

print("\n" + "=" * 50)
print("BAGIAN 3: Load Session by Name")
print("=" * 50)

session_by_name = fastf1.get_session(2021, 'French Grand Prix', 'Q')
print(f"✅ Nama GP  : {session_by_name.event['EventName']}")

session_by_country = fastf1.get_session(2021, 'Silverstone', 'Q')
print(f"✅ Silverstone -> {session_by_country.event['EventName']}")

print("\n" + "=" * 50)
print("BAGIAN 4: Event Schedule 2023")
print("=" * 50)

schedule = fastf1.get_event_schedule(2023)

print("Kolom:", schedule.columns.tolist())
print()

cols = ['RoundNumber', 'Country', 'EventName', 'EventDate']
print(schedule[cols].to_string(index=False))

gp_monaco = schedule.get_event_by_name('Monaco')
print(f"\nMonaco GP tanggal: {gp_monaco['EventDate'].date()}")

gp_round_1 = schedule.get_event_by_round(1)
print(f"Round 1 adalah    : {gp_round_1['EventName']}")

print("\n" + "=" * 50)
print("BAGIAN 5: Load Data & Session Results")
print("=" * 50)
print("⏳ Mengunduh data (pertama kali agak lama)...\n")

session = fastf1.get_session(2021, 'French Grand Prix', 'Q')
session.load()

print("✅ Data berhasil dimuat!")
print(f"\nKolom session results:")
print(session.results.columns.tolist())

print("\n🏁 Top 10 Qualifying - French GP 2021")
print("-" * 45)
top10 = session.results.iloc[0:10][['Abbreviation', 'TeamName', 'Q3']]
for i, (_, row) in enumerate(top10.iterrows(), 1):
    q3 = str(row['Q3']).split(' ')[-1] if pd.notna(row['Q3']) else 'N/A'
    print(f"P{i:2d}  {row['Abbreviation']}  {row['TeamName'][:20]:<20}  {q3}")

print("\n" + "=" * 50)
print("BAGIAN 6: Data Lap")
print("=" * 50)

laps = session.laps
print(f"Total baris lap : {len(laps)}")
print(f"Kolom tersedia  : {laps.columns.tolist()}")

fastest = session.laps.pick_fastest()
print(f"\n⚡ Lap Tercepat:")
print(f"   Driver   : {fastest['Driver']}")
print(f"   Lap Time : {fastest['LapTime']}")
print(f"   Compound : {fastest['Compound']}")
print(f"   Lap No.  : {fastest['LapNumber']}")

ver_laps = session.laps.pick_drivers('VER')
print(f"\nTotal lap VER: {len(ver_laps)}")
print(ver_laps[['LapNumber', 'LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time', 'Compound']].dropna(subset=['LapTime']).to_string(index=False))

print("\n✅ Selesai! Jalankan 02_telemetri_dan_visualisasi.py untuk lanjut.")
