#!/usr/bin/env python3
"""
v2.0 算法验证：基于40天数据计算 F_total 分布（纯Python实现）

⚠️  重要提示：此脚本基于旧标准（交互次数）
    当前标准已更新为用户输出字节数
    此脚本仅供历史参考和 F 模型计算验证
    实际使用请参考 METHODOLOGY.md 中的字节数统计方法
"""

import math

# 40天原始数据 (日期, 交互次数)
daily_data = [
    ("02-10", 15),
    ("02-11", 16),
    ("02-12", 6),
    ("02-15", 4),
    ("02-24", 4),
    ("02-27", 2),
    ("03-05", 6),
    ("03-08", 4),
    ("03-09", 4),
    ("03-10", 9),
    ("03-11", 2),
    ("03-13", 4),
]

# v2.0 参数（基于Fable数据提取）
params = {
    "rho_bar": 1.5,
    "transfer_rate": 0.05,
    "decay_chronic": 0.90,
    "decay_acute_sleep": 0.3,
    "decay_acute_work": 0.8,
    "work_hours": 8,
}

def calculate_lambda(interaction_count, work_hours=8, rho_bar=1.5):
    """计算时间变换系数 λ"""
    if interaction_count == 0:
        return 0.2
    rho = interaction_count / work_hours
    return rho / rho_bar

def simulate_fatigue_v20(daily_data, params):
    """模拟v2.0双层疲劳模型"""
    results = []
    f_acute = 0
    f_chronic = 0
    
    for date, count in daily_data:
        lambda_t = calculate_lambda(count, params["work_hours"], params["rho_bar"])
        
        # 白天工作时段累积
        for hour in range(8):
            f_acute = f_acute * params["decay_acute_work"] + lambda_t
        
        f_acute_peak = f_acute
        
        # 转移到慢性疲劳
        threshold = 10
        if f_acute_peak > threshold:
            f_chronic += params["transfer_rate"] * (f_acute_peak - threshold)
        
        # 夜间睡眠衰减
        f_acute = f_acute * params["decay_acute_sleep"]
        
        # 慢性疲劳日衰减
        f_chronic = f_chronic * params["decay_chronic"]
        
        f_total = f_acute + f_chronic
        
        results.append({
            "date": date,
            "interactions": count,
            "lambda": lambda_t,
            "f_acute": f_acute,
            "f_chronic": f_chronic,
            "f_total": f_total
        })
    
    return results

# 运行模拟
results = simulate_fatigue_v20(daily_data, params)
f_totals = [r["f_total"] for r in results]

print("=" * 70)
print("v2.0 疲劳模型验证 - F_total 分布分析（仅供开发参考）")
print("=" * 70)
print("\n⚠️  注意：此脚本仅验证 F 模型计算，非完整时相系统")
print("   实际天气由 λ 判定，F 仅用于预测恢复时间\n")
print("每日F_total计算（F-based 天气仅供验证参考）：")
print(f"{'日期':<10} {'交互':<6} {'λ':<6} {'F_acute':<10} {'F_chronic':<11} {'F_total':<10} {'F-天气'}")
print("-" * 75)

weather_counts = {"☀️F-晴朗": 0, "⛅F-多云": 0, "☁️F-阴天": 0, "🌧️F-小雨": 0, "🌫️F-静雾": 0}

for r in results:
    f = r["f_total"]
    if f < 10:
        weather = "☀️F-晴朗"
        weather_counts["☀️F-晴朗"] += 1
    elif f < 20:
        weather = "⛅F-多云"
        weather_counts["⛅F-多云"] += 1
    elif f < 35:
        weather = "☁️F-阴天"
        weather_counts["☁️F-阴天"] += 1
    elif f < 50:
        weather = "🌧️F-小雨"
        weather_counts["🌧️F-小雨"] += 1
    else:
        weather = "🌫️F-静雾"
        weather_counts["🌫️F-静雾"] += 1
    
    print(f"{r['date']:<10} {r['interactions']:<6} {r['lambda']:<6.2f} {r['f_acute']:<10.2f} {r['f_chronic']:<11.2f} {r['f_total']:<10.2f} {weather}")

# 统计分析
def mean(data):
    return sum(data) / len(data)

def std(data):
    m = mean(data)
    variance = sum((x - m) ** 2 for x in data) / len(data)
    return math.sqrt(variance)

def median(data):
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n % 2 == 0:
        return (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
    return sorted_data[n//2]

def skewness(data):
    m = mean(data)
    s = std(data)
    n = len(data)
    return sum((x - m) ** 3 for x in data) / (n * s ** 3)

def kurtosis(data):
    m = mean(data)
    s = std(data)
    n = len(data)
    return sum((x - m) ** 4 for x in data) / (n * s ** 4) - 3

print("\n" + "=" * 70)
print("F_total 统计分析")
print("=" * 70)

n = len(f_totals)
f_mean = mean(f_totals)
f_std = std(f_totals)
f_min = min(f_totals)
f_max = max(f_totals)
f_median = median(f_totals)
f_skew = skewness(f_totals)
f_kurt = kurtosis(f_totals)

print(f"\n样本数：{n}")
print(f"均值：{f_mean:.2f}")
print(f"标准差：{f_std:.2f}")
print(f"最小值：{f_min:.2f}")
print(f"最大值：{f_max:.2f}")
print(f"中位数：{f_median:.2f}")

print(f"\n偏度（Skewness）：{f_skew:.4f}")
if -0.5 <= f_skew <= 0.5:
    print("  → 近似对称 ✅")
elif -1 <= f_skew < -0.5 or 0.5 < f_skew <= 1:
    print("  → 轻微偏斜")
else:
    print("  → 严重偏斜 ❌")

print(f"\n峰度（Kurtosis）：{f_kurt:.4f}")
if -1 <= f_kurt <= 1:
    print("  → 接近正态峰度 ✅")
elif f_kurt > 1:
    print("  → 尖峰（比正态更集中）")
else:
    print("  → 平峰（比正态更分散）")

print("\n" + "=" * 70)
print("天气状态分布")
print("=" * 70)
for weather, count in weather_counts.items():
    percentage = (count / n) * 100
    bar = "█" * int(percentage / 5)
    print(f"{weather}: {count:>2}天 ({percentage:>5.1f}%) {bar}")

# 正态分布简化检验
print("\n" + "=" * 70)
print("正态分布检验（简化）")
print("=" * 70)

# 检查均值、中位数、众数是否接近
print(f"\n均值 vs 中位数：{f_mean:.2f} vs {f_median:.2f}")
if abs(f_mean - f_median) < f_std * 0.3:
    print("  → 均值≈中位数，分布对称 ✅")
else:
    print("  → 均值≠中位数，存在偏斜")

# 检查68-95-99.7规则
sorted_totals = sorted(f_totals)
within_1std = sum(1 for x in f_totals if f_mean - f_std <= x <= f_mean + f_std)
within_2std = sum(1 for x in f_totals if f_mean - 2*f_std <= x <= f_mean + 2*f_std)

print(f"\n68-95-99.7规则检验：")
print(f"  ±1标准差内：{within_1std}/{n} = {within_1std/n*100:.1f}% (理论68%)")
print(f"  ±2标准差内：{within_2std}/{n} = {within_2std/n*100:.1f}% (理论95%)")

if within_1std/n >= 0.5 and within_2std/n >= 0.8:
    print("  → 符合正态分布特征 ✅")
else:
    print("  → 偏离正态分布")

print("\n" + "=" * 70)
print("结论")
print("=" * 70)

normal_checks = []
if -1 <= f_skew <= 1:
    normal_checks.append("偏度在合理范围")
if -2 <= f_kurt <= 2:
    normal_checks.append("峰度在合理范围")
if abs(f_mean - f_median) < f_std * 0.3:
    normal_checks.append("均值≈中位数")

if len(normal_checks) >= 2:
    print("✅ F_total分布近似正态分布")
    print(f"   个人基线：F_total = {f_mean:.1f} ± {f_std:.1f}")
    print(f"   推荐阈值调整：基于个人数据优化")
else:
    print("⚠️ F_total分布有偏，建议：")
    print("  1. 增加样本量（当前仅12天有效数据）")
    print("  2. 调整个性化参数")

print(f"\n验证通过项：")
for check in normal_checks:
    print(f"  ✓ {check}")

print("\n" + "=" * 70)
