# 时相系统方法论（Shixiang Methodology）

版本：v2.0
最后更新：2026-03-20

---

## 一、系统概述

时相（Shixiang）是检测用户认知能量节律的时间天气预报系统。基于**时间膨胀理论**，分析用户交互模式，预测最佳工作窗口与决策时机。

### 核心概念：时间膨胀

**物理时间 ≠ 业务时间**

传统认知：1小时 = 1小时  
时相认知：1小时深度工作 ≠ 1小时发呆

**核心公式**（始终不变）：
```
λ = ρ / ρ̄                    # 时间变换系数
τ = Σ(λ_i × Δt_i)            # 业务时间累积
```

- λ = 12 时：1物理小时 = 12业务小时（心流状态）
- λ = 0.2 时：5物理小时 = 1业务小时（静雾状态）

> v2.0 更新：新增**双层疲劳模型**作为辅助预测系统，用于预测未来的 λ 变化，不改变核心天气判定逻辑。

---

## 二、核心算法

### 2.1 时间膨胀理论（核心）

**信息密度 ρ**
```
ρ = N_effective / Δt

N_effective = 单位时间内的有效交互次数
Δt = 时间窗口（小时）
```

**时间变换系数 λ**
```
λ = ρ / ρ̄

ρ̄ = 用户历史平均信息密度（个人基线）
```

**业务时间累积 τ**
```
τ = Σ(λ_i × Δt_i)
```

### 2.2 天气状态判定（基于 λ）

**判定依据**：当前 λ 值（时间变换系数）

| 天气 | 图标 | λ 值 | 时间膨胀 | 能量 | 建议 |
|:---|:---:|:---:|:---:|:---:|:---|
| 晴朗 | ☀️ | > 10 | 1h → 10h+ | 95% | 深度工作、复杂决策 |
| 多云 | ⛅ | 5-10 | 1h → 5-10h | 65% | 创意产出、写作 |
| 阴天 | ☁️ | 2-5 | 1h → 2-5h | 40% | 事务处理、邮件 |
| 小雨 | 🌧️ | 1-2 | 1h → 1-2h | 25% | 轻量任务、准备 |
| 静雾 | 🌫️ | < 1 | 1h → <1h | 15% | 休息、恢复 |

### 2.3 双层疲劳模型（辅助预测）

**作用**：预测未来的 λ 变化（何时能回到高 λ 状态）

**核心洞察**：今天的疲劳会影响明天的 λ

**公式定义**：
```
F_total(t) = F_acute(t) + F_chronic(t)

F_acute(t) = F_acute(t-1) × decay_acute + λ(t)
F_chronic(t) = F_chronic(t-1) × decay_chronic + transfer_rate × max(0, F_acute_peak - threshold)
```

**参数说明**：
- `λ(t)` = 时间变换系数（来自 2.1）
- `decay_acute` = 急性疲劳衰减率（睡眠0.3，工作0.8）
- `decay_chronic` = 慢性疲劳衰减率（每天0.80-0.95，**个性化参数**）
- `transfer_rate` = 转慢性率（0.05-0.15，**个性化参数**）

### 2.2 上下文感知恢复速率

**核心洞察**：相同静默时段，恢复效果因上下文而异

| 时段 | 上下文 | decay_acute | 说明 |
|:---|:---|:---:|:---|
| 00-06点 | 睡眠 | 0.30 | 深度恢复 |
| 06-09点 | 晨间准备 | 0.50 | 中等恢复 |
| 09-17点(工作日) | 物理工作 | 0.80 | 轻度恢复 |
| 12-13点 | 午休 | 0.60 | 中等恢复 |
| 18-23点 | 晚间放松 | 0.50 | 中等恢复 |
| 周末全天 | 休闲 | 0.40 | 较好恢复 |

### 2.3 个性化参数提取

**提取时机**：
- 冷启动：使用默认值（transfer_rate=0.10, decay_chronic=0.85）
- 14天后：首次提取
- 之后：每7天更新

**提取算法**：
```python
def extract_fatigue_params(user_history):
    """
    从用户历史数据中提取个性化疲劳参数
    """
    # 1. 找出连续高强度时段（>10次/天，连续≥2天）
    high_streaks = find_consecutive_high_intensity(user_history, threshold=10, min_days=2)
    
    if not high_streaks:
        return default_params  # 无数据使用默认
    
    # 2. 分析恢复模式
    recovery_ratios = []
    for streak in high_streaks:
        day1 = user_history[streak.end + 1].intensity  # 第1天恢复
        day2 = user_history[streak.end + 2].intensity  # 第2天恢复
        
        # 恢复比例 = 恢复后强度 / 高强度均值
        ratio = (day1 + day2) / 2 / streak.avg_intensity
        recovery_ratios.append(ratio)
    
    avg_ratio = mean(recovery_ratios)
    
    # 3. 根据恢复速度反推参数
    if avg_ratio > 0.5:  # 恢复快（如你）
        return {"transfer_rate": 0.05, "decay_chronic": 0.90}
    elif avg_ratio > 0.3:
        return {"transfer_rate": 0.10, "decay_chronic": 0.85}
    else:  # 恢复慢
        return {"transfer_rate": 0.15, "decay_chronic": 0.80}
```

**参数范围**：
- `transfer_rate`: 0.05（恢复快）~ 0.15（恢复慢）
- `decay_chronic`: 0.80（恢复慢）~ 0.95（恢复快）

### 2.4 天气状态判定（v2.0）

**判定依据**：总疲劳度 F_total

| 天气 | 图标 | F_total 范围 | 能量水平 | 建议 |
|:---|:---:|:---:|:---:|:---|
| 晴朗 | ☀️ | < 10 | 95% | 深度工作、复杂决策 |
| 多云 | ⛅ | 10-20 | 65% | 创意产出、写作 |
| 阴天 | ☁️ | 20-35 | 40% | 事务处理、邮件 |
| 小雨 | 🌧️ | 35-50 | 25% | 轻量任务、准备 |
| 静雾 | 🌫️ | > 50 | 15% | 休息、恢复 |

---

## 三、执行流程

### 3.1 查询当前状态

**触发**：用户问"我现在状态如何"

**步骤**：
1. 读取 `profile.json` 获取个性化参数
2. 计算当前 F_acute（基于最近交互密度）
3. 计算当前 F_chronic（基于历史累积）
4. F_total = F_acute + F_chronic
5. 查表判定天气状态
6. 返回状态 + 建议 + 恢复时间预测

**输出示例**：
```
🌧️ 小雨（λ=1.3，时间膨胀 1h→1.3h）
├─ 急性疲劳：F_acute=18（当天工作累积）
├─ 慢性疲劳：F_chronic=24（连续3天高强度累积）
├─ 预计恢复：16小时后 λ 回升至 2+（阴天状态）
└─ 建议：轻量任务，避免重大决策，明日8点可恢复正常
```

### 3.2 生成今日预报

**步骤**：
1. 获取当前 λ（时间变换系数）和 F（疲劳度）
2. **基于 λ 判定当前天气**（核心）
3. **基于 F 预测未来 λ 变化**（辅助）：
   - 模拟疲劳恢复路径
   - 预测何时 λ 回升至 2+/5+/10+
4. 输出预报：各时段的天气 + 预计 λ 值

**预报示例**：
```
📅 今日预报 | 周五

当前：🌧️ 小雨（λ=1.3）疲劳累积中

08:00-09:30 ☀️ 晴朗（预计 λ→12）深度工作
  └─ 基于：F_acute 夜间恢复至 <10

09:30-11:00 ⛅ 多云（预计 λ→6）创意产出
  └─ 基于：上午工作开始累积疲劳

11:00-12:30 ☁️ 阴天（预计 λ→3）事务处理
  └─ 基于：F_acute 持续增长
```

### 3.3 波峰预测（基于疲劳恢复）

**核心逻辑**：用 F 预测未来的 λ

```python
def predict_next_peak(current_lambda, current_F, schedule, params):
    """
    基于疲劳恢复预测下一次 λ > 10（晴朗）的时间
    """
    # 当前状态
    lambda_current = current_lambda
    F_current = current_F
    
    if lambda_current >= 10:
        return now(), lambda_current  # 现在就是高峰
    
    hours = 0
    lambda_predicted = lambda_current
    
    while lambda_predicted < 10 and hours < 72:
        # 1. 模拟疲劳恢复
        if is_sleep_hour(hours):
            F_new = F_current * params.decay_acute_sleep
        elif is_working_hour(hours):
            F_new = F_current * params.decay_acute_work + 0.5  # 轻度工作
        else:
            F_new = F_current * 0.6  # 休息恢复
        
        # 2. 基于 F 预测 λ（简化模型：F 越低，λ 越高）
        if F_new < 10:
            lambda_predicted = 12  # 晴朗
        elif F_new < 20:
            lambda_predicted = 7   # 多云
        elif F_new < 35:
            lambda_predicted = 3   # 阴天
        else:
            lambda_predicted = 1.5 # 小雨/静雾
        
        F_current = F_new
        hours += 1
    
    return now() + hours, lambda_predicted
```

**场景示例**：
- 连续3天高强度后：λ=0.5（静雾），F_total ≈ 60
- **基于 F 预测**：
  - 第4天休息：F → 42，预测 λ → 1.5（小雨）
  - 第5天：F → 30，预测 λ → 3（阴天）
  - 第6天：F → 20，预测 λ → 7（多云）
  - 第7天：F → 12，预测 λ → 12（晴朗）✅
- **预报结果**："预计7天后恢复晴朗状态，λ≈12"

---

## 四、数据维护

### 4.1 存储规范

```
storage/{user_id}/
├── history.jsonl       # 交互日志
├── profile.json        # 包含个性化疲劳参数
└── fatigue.log         # 疲劳度历史（可选）
```

### 4.2 profile.json Schema（v2.0）

```json
{
  "meta": {
    "user_id": "string",
    "version": "2.0",
    "fatigue_model_version": "2.0"
  },
  "fatigue_model": {
    "personal_params": {
      "transfer_rate": 0.05,
      "decay_chronic": 0.90,
      "extracted_at": "2026-03-20T08:00:00Z",
      "confidence": 0.8,
      "based_on_days": 40
    },
    "recovery_history": [
      {
        "streak_start": "2026-02-10",
        "streak_end": "2026-02-11",
        "streak_length": 2,
        "recovery_day1_ratio": 0.4,
        "recovery_day2_ratio": 0.25
      }
    ]
  },
  "current_fatigue": {
    "F_acute": 18,
    "F_chronic": 24,
    "F_total": 42,
    "last_updated": "2026-03-20T12:00:00Z"
  }
}
```

---

## 五、集成场景

### 5.1 剧场模式前置检查（v2.0）

```python
if F_total > 50:  # 静雾
    advice = "当前深度疲劳，建议休息1-3天后再决策"
elif F_total > 35:  # 小雨
    advice = "疲劳累积中，简单决策可继续，复杂决策建议延后"
elif F_total > 20:  # 阴天
    advice = "轻度疲劳，30分钟内可完成决策"
else:  # 多云/晴朗
    start_theater_mode()
```

### 5.2 模式漂移检测

**检测条件**：
- 连续5天 F_total > 35（小雨+状态）
- 夜间活动频率 > 20%

**触发**：重新提取个性化参数，可能模式切换

---

## 六、验证与校准

### 6.1 准确率验证

**方法**：
1. 预测次日天气
2. 记录实际天气（用户反馈）
3. 统计准确率

**目标**：
- v2.0 目标准确率：> 85%（v1.0 为 80%）
- 连续高强度后恢复预测：> 70%

### 6.2 参数校准

**校准触发**：
- 准确率 < 80%
- 用户连续3次反馈"不准确"
- 数据量新增50条

---

*文档版本：v2.0 | 双层疲劳模型 | 个性化参数提取*
