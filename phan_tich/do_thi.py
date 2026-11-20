from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# 1. CAU HINH

HERE = Path(__file__).resolve().parent
ROOT = HERE if (HERE / "ket_qua").exists() else HERE.parent

RESULTS = ROOT / "ket_qua"
CHARTS = RESULTS / "do_thi"

N_BOOT = 10000
ALPHA = 0.05
RNG = np.random.default_rng(2026)

TEN_DANG = {
    "random": "ngẫu nhiên",
    "sorted": "đã sắp xếp",
    "nearly": "gần sắp xếp",
    "reversed": "ngược thứ tự",
}

CHARTS.mkdir(parents=True, exist_ok=True)


# 2. DOC DU LIEU TU CAC JVM

# Doc tat ca file raw_run1.csv, raw_run2.csv,...
# Dong thoi ho tro file raw.csv neu co.

raw_files = sorted(RESULTS.glob("raw*.csv"))

if not raw_files:
    raise FileNotFoundError(
        f"Khong tim thay file raw*.csv trong {RESULTS}"
    )

data = []

for file in raw_files:
    temp = pd.read_csv(file)

    # Lay ma lan chay tu ten file
    temp["run_id"] = file.stem.replace("raw_", "")

    data.append(temp)

df = pd.concat(data, ignore_index=True)

required_columns = {
    "type", "n", "cutoff", "rep", "time_ms", "run_id"
}

missing = required_columns - set(df.columns)

if missing:
    raise ValueError(f"CSV thieu cac cot: {sorted(missing)}")

# Chuyen cac cot ve dung kieu du lieu
df["n"] = df["n"].astype(int)
df["cutoff"] = df["cutoff"].astype(int)
df["rep"] = df["rep"].astype(int)
df["time_ms"] = df["time_ms"].astype(float)

if df["time_ms"].isna().any() or (df["time_ms"] <= 0).any():
    raise ValueError("Du lieu time_ms khong hop le.")

print("Da doc cac file:")
for file in raw_files:
    print("-", file.name)

print(f"Tong so lan do: {len(df)}")


# 3. HAM TINH KHOANG TIN CAY BOOTSTRAP

def boot_ci(values, alpha=ALPHA):
    """
    Tinh khoang tin cay bootstrap cho trung vi.
    """

    values = np.asarray(values, dtype=float)

    if len(values) == 0:
        return np.nan, np.nan

    # Lay mau bootstrap
    indices = RNG.integers(
        0, len(values),
        size=(N_BOOT, len(values))
    )

    bootstrap_medians = np.median(values[indices], axis=1)

    lower, upper = np.percentile(
        bootstrap_medians,
        [
            100 * alpha / 2,
            100 * (1 - alpha / 2)
        ]
    )

    return lower, upper


# 4. THONG KE MO TA

rows = []

for (data_type, n, cutoff), group in df.groupby(
    ["type", "n", "cutoff"]
):
    times = group["time_ms"].to_numpy()

    lower, upper = boot_ci(times)

    rows.append({
        "type": data_type,
        "n": n,
        "cutoff": cutoff,
        "count": len(times),
        "mean_ms": times.mean(),
        "median_ms": np.median(times),
        "median_lo_ms": lower,
        "median_hi_ms": upper,
        "std_ms": times.std(ddof=1),
        "min_ms": times.min(),
        "max_ms": times.max(),
    })

summary = pd.DataFrame(rows).sort_values(
    ["type", "n", "cutoff"]
)

summary.to_csv(
    RESULTS / "summary.csv",
    index=False,
    float_format="%.6f"
)


# Kiem tra so lan do giua cac CUTOFF

for (data_type, n), group in summary.groupby(["type", "n"]):
    if group["count"].nunique() != 1:
        print(
            f"CANH BAO: So lan do khong dong deu: "
            f"{data_type}, N={n}"
        )


# 5. SO SANH CAC CUTOFF

# Moi mang duoc do voi tat ca CUTOFF.
# Ghep cap theo run_id va rep.

wide = df.pivot_table(
    index=["type", "n", "run_id", "rep"],
    columns="cutoff",
    values="time_ms"
)

wide = wide.dropna()

# So nhom du lieu can so sanh

groups = wide.reset_index()[["type", "n"]].drop_duplicates()
n_groups = len(groups)

if n_groups == 0:
    raise ValueError("Khong co nhom du lieu hop le.")

# Hieu chinh so sanh CUTOFF 7 va 10

alpha_7_10 = ALPHA / n_groups


def ket_luan_7_10(lower, upper):
    if lower > 0:
        return "CUTOFF 7 nhanh hon"

    if upper < 0:
        return "CUTOFF 10 nhanh hon"

    return "Khong phan biet duoc"


best_rows = []
compare_rows = []

for (data_type, n), sub in wide.groupby(level=["type", "n"]):

    sub = sub.droplevel(["type", "n"])

    medians = sub.median()
    best = int(medians.idxmin())

    # Tim cac CUTOFF khong khac biet ro rang
    # so voi CUTOFF co trung vi tot nhat.

    others = [c for c in sub.columns if c != best]

    alpha_c = ALPHA / len(others) if others else ALPHA
    not_different = [best]

    for cutoff in others:
        diff = (sub[cutoff] - sub[best]).to_numpy()

        lower, upper = boot_ci(diff, alpha=alpha_c)

        if lower <= 0 <= upper:
            not_different.append(int(cutoff))

    best_rows.append({
        "type": data_type,
        "n": n,
        "cutoff_tot_nhat": best,
        "median_ms": medians[best],

        "nhanh_hon_cutoff_1_pct": (
            100 * (1 - medians[best] / medians[1])
            if 1 in medians.index else np.nan
        ),

        "cutoff_khong_phan_biet_duoc": " ".join(
            str(c) for c in sorted(not_different)
        ),

        "tot_nhat_nam_o_bien_luoi": (
            best == int(sub.columns.min())
            or best == int(sub.columns.max())
        )
    })

    # So sanh CUTOFF 7 va 10

    if 7 in sub.columns and 10 in sub.columns:

        # Hieu = thoi gian CUTOFF 10 - thoi gian CUTOFF 7

        diff = (sub[10] - sub[7]).to_numpy()

        lower, upper = boot_ci(diff)

        lower_corrected, upper_corrected = boot_ci(
            diff,
            alpha=alpha_7_10
        )

        compare_rows.append({
            "type": data_type,
            "n": n,
            "median_7_ms": medians[7],
            "median_10_ms": medians[10],
            "trung_vi_hieu_10_tru_7_ms": np.median(diff),

            "khoang_tin_cay_95_thap": lower,
            "khoang_tin_cay_95_cao": upper,

            "khoang_tin_cay_hieu_chinh_thap": lower_corrected,
            "khoang_tin_cay_hieu_chinh_cao": upper_corrected,

            "ket_luan_chua_hieu_chinh": ket_luan_7_10(
                lower, upper
            ),

            "ket_luan": ket_luan_7_10(
                lower_corrected, upper_corrected
            )
        })


best_df = pd.DataFrame(best_rows).sort_values(["type", "n"])

compare_df = pd.DataFrame(compare_rows).sort_values(["type", "n"])

best_df.to_csv(
    RESULTS / "best_cutoff.csv",
    index=False,
    float_format="%.6f"
)

compare_df.to_csv(
    RESULTS / "so_sanh_7_10.csv",
    index=False,
    float_format="%.6f"
)


# 6. VE 4 BIEU DO THEO CUTOFF

for data_type in TEN_DANG:

    subset = summary[summary["type"] == data_type].copy()

    cutoffs = sorted(subset["cutoff"].unique())

    # Dung vi tri cach deu de bieu do de nhin

    positions = {c: i for i, c in enumerate(cutoffs)}

    # Thoi gian

    plt.figure(figsize=(9, 5))

    for n in sorted(subset["n"].unique()):

        line = subset[subset["n"] == n].sort_values("cutoff")

        median = line["median_ms"].to_numpy()

        error = [
            median - line["median_lo_ms"].to_numpy(),
            line["median_hi_ms"].to_numpy() - median
        ]

        plt.errorbar(
            line["cutoff"].map(positions),
            median,
            yerr=error,
            marker="o",
            capsize=3,
            label=f"N = {n:,}"
        )

    plt.xlabel("CUTOFF")
    plt.ylabel("Thời gian trung vị (ms)")
    plt.title(
        f"Thời gian theo CUTOFF - "
        f"{TEN_DANG.get(data_type, data_type)}"
    )

    plt.xticks(range(len(cutoffs)), cutoffs)
    plt.yscale("log")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        CHARTS / f"{data_type}_median_time.png",
        dpi=160
    )

    plt.close()


# 7. IN KET QUA

print("\nDA PHAN TICH XONG!")

print(f"\nSo file JVM: {len(raw_files)}")
print(f"So lan do: {len(df)}")

print(f"\nBang thong ke: {RESULTS / 'summary.csv'}")
print(f"Cutoff tot nhat: {RESULTS / 'best_cutoff.csv'}")
print(f"So sanh 7 va 10: {RESULTS / 'so_sanh_7_10.csv'}")
print(f"Bieu do: {CHARTS}")

print("\nCUTOFF TOT NHAT THEO TUNG NHOM:")

print(
    best_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.3f}"
    )
)

print("\nSO SANH CUTOFF 7 VA 10:")

if not compare_df.empty:
    print(
        compare_df[
            [
                "type",
                "n",
                "trung_vi_hieu_10_tru_7_ms",
                "ket_luan_chua_hieu_chinh",
                "ket_luan"
            ]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}"
        )
    )
else:
    print("Khong co du lieu de so sanh CUTOFF 7 va 10.")
