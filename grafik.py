import re  
import pandas as pd  
from bokeh.plotting import figure, show, output_file 
from bokeh.models import DatetimeTickFormatter, FixedTicker 
from datetime import datetime  

# Nama file input
file_path = "soal_chart_bokeh.txt"
data = [] 
current_time = None  

with open(file_path, "r") as f:
    for line in f:
        line = line.strip()

        # Jika baris dimulai dengan "Timestamp:", ambil waktu
        if line.startswith("Timestamp:"):
            try:
                ts_str = line.replace("Timestamp:", "").strip()
                current_time = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
            except:
                current_time = None

        # Jika baris mengandung "sender" dan "Mbits/sec", ambil nilai speed
        if "sender" in line and "Mbits/sec" in line:
            match = re.search(r"([\d\.]+)\s+Mbits/sec", line)
            if current_time and match:
                speed = float(match.group(1))
                data.append((current_time, speed))
                current_time = None  # reset agar timestamp hanya dipakai sekali

# Masukkan hasil parsing ke DataFrame
df = pd.DataFrame(data, columns=["time", "speed_mbps"])
print("Jumlah data terbaca:", len(df))
print(df.head())

# Ambil hanya 1 data per jam dengan pakai waktu asli
df["hour_bucket"] = df["time"].dt.floor("h")
df_one = (
    df.sort_values("time")
      .groupby("hour_bucket", as_index=False)
      .first()[["time", "speed_mbps"]]
)

# Siapkan file output HTML untuk grafik
output_file("grafik_speed.html")

# Buat objek grafik
p = figure(
    title="Testing Jaringan",
    x_axis_label="DATE TIME",
    y_axis_label="Speed (Mbps)",
    x_axis_type="datetime",
    width=800,
    height=400
)

# plot pakai waktu asli
p.line(df_one["time"], df_one["speed_mbps"], line_width=2, legend_label="Speed")
p.scatter(df_one["time"], df_one["speed_mbps"], size=6)

ticks_ms = [int(pd.to_datetime(t).value // 10**6) for t in df_one["time"]]
p.xaxis.ticker = FixedTicker(ticks=sorted(ticks_ms))

# Format label tanggal & jam lengkap
p.xaxis.formatter = DatetimeTickFormatter(
    milliseconds="%m/%d/%Y %H:%M:%S",
    seconds="%m/%d/%Y %H:%M:%S",
    minsec="%m/%d/%Y %H:%M:%S",
    hours="%m/%d/%Y %H:%M:%S",
    days="%m/%d/%Y %H:%M:%S",
    months="%m/%d/%Y %H:%M:%S",
    years="%m/%d/%Y %H:%M:%S",
)

p.xaxis.major_label_orientation = 0.7  # miring agar tidak bertumpuk
p.legend.location = "top_left"

p.yaxis.ticker = FixedTicker(ticks=[0.00, 25.00, 50.00, 75.00, 100.00, 125.00])

show(p)