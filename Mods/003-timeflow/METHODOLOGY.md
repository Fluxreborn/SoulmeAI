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

定义：单位时间内的有效认知交互次数
```
ρ = N_effective / Δt

N_effective = 有效交互次数（需认知资源的深度互动）
Δt = 时间窗口（小时）
```

**关键定义**：
- **有效交互**：需要认知资源的互动（提问、决策、深度回复、复杂任务执行）
- **排除**：简单确认、表情回复、自动消息、被动接收
- **采样粒度**：建议以"小时"为单位统计，也可按"会话"聚合
- **Δt 窗口**：通常为1小时，也可根据场景调整（30分钟/2小时）

**时间变换系数 λ**
```
λ = ρ / ρ̄

ρ̄ = 用户历史平均信息密度（个人基线）
```

**关键定义**：
- **ρ̄ 计算窗口**：建议7天滑动平均（冷启动时可用默认值1.5）
- **ρ̄ 更新频率**：每天更新一次，或每新增50条记录更新
- **冷启动默认值**：ρ̄ = 1.5（基于典型知识工作者数据）

**业务时间累积 τ**
```
τ = Σ(λ_i × Δt_i)
```

**关键定义**：
- **累积方式**：按小时累加，或按会话累加
- **重置时机**：建议每日重置（τ_daily），也可保留周累计（τ_weekly）
- **用途**：统计当日/当周"活过"的有效时间

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

**关键定义**：

| 参数 | 定义 | 默认值 | 个性化 |
|:---|:---|:---:|:---:|
| `λ(t)` | 时间变换系数（来自2.1） | - | 是 |
| `F_acute` | 急性疲劳：短期累积，睡眠后快速恢复 | 0 | 是 |
| `F_chronic` | 慢性疲劳：长期累积，恢复缓慢 | 0 | 是 |
| `decay_acute` | 急性疲劳衰减率 | 见下表 | 否（生理规律）|
| `decay_chronic` | 慢性疲劳日衰减率 | 0.85 | 是 |
| `transfer_rate` | 转慢性率 | 0.10 | 是 |
| `threshold` | 转慢性阈值 | 10 | 否 |
| `F_acute_peak` | 当日峰值急性疲劳 | - | 是 |

**上下文感知恢复速率**（decay_acute）：

| 时段 | 上下文 | decay_acute | 说明 |
|:---|:---|:---:|:---|
| 00-06点 | 睡眠 | 0.30 | 深度恢复 |
| 06-09点 | 晨间准备 | 0.50 | 中等恢复 |
| 09-17点(工作日) | 物理工作 | 0.80 | 轻度恢复 |
| 12-13点 | 午休 | 0.60 | 中等恢复 |
| 18-23点 | 晚间放松 | 0.50 | 中等恢复 |
| 周末全天 | 休闲 | 0.40 | 较好恢复 |

**关键定义**：
- **decay_acute**：每小时保留的疲劳比例（1-decay=恢复比例）
- **decay_chronic**：每天保留的慢性疲劳比例
- **transfer_rate**：当日峰值疲劳超过阈值后，转为慢性疲劳的比例
- **threshold**：开始转为慢性疲劳的阈值（默认10，约等于1小时高强度工作）

**个性化参数提取逻辑**：
- **提取时机**：14天后首次提取，之后每7天更新
- **提取依据**：用户历史恢复模式（连续高强度后的恢复速度）
- **参数范围**：
  - transfer_rate：0.05（恢复快）~ 0.15（恢复慢）
  - decay_chronic：0.80（恢复慢）~ 0.95（恢复快）

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

**参数范围**（个性化 vs 通用）：

| 参数 | 冷启动（通用） | 个性化提取后 | 说明 |
|:---|:---:|:---:|:---|
| `transfer_rate` | 0.10 | 0.05-0.15 | 从用户恢复模式学习 |
| `decay_chronic` | 0.85 | 0.80-0.95 | 从用户恢复模式学习 |
| `decay_acute_sleep` | 0.30（通用） | 0.30（通用） | 生理规律，不变 |
| `decay_acute_work` | 0.80（通用） | 0.80（通用） | 上下文决定，不变 |

**提取逻辑**：
- 0-14天：使用通用默认值
- 14天后：分析用户历史数据，提取个性化参数
- 之后每7天更新一次

---

## 三、执行流程

### 3.1 查询当前状态

**触发**：用户问"我现在状态如何"

**步骤**：
1. 读取 `profile.json` 获取个性化参数（如有）
2. **计算当前 λ**（基于最近交互密度）
3. **检查数据充足性**：
   - 当前小时交互数 ≥ 3：正常计算 λ
   - 当前小时交互数 < 3：进入稀疏数据模式
4. **基于 λ 判定当前天气**（核心）
5. 计算当前 F_acute 和 F_chronic（辅助参考）
6. 返回：天气状态 + λ值 + 疲劳参考 + 恢复预测

**数据稀疏处理模式**（交互 < 3条/小时）：

当当前小时有效交互不足3条时，使用 F_total 推断 λ 估计值：

| F_total 范围 | 推断 λ | 推断天气 | 置信度 |
|:---:|:---:|:---:|:---:|
| < 10 | ≈ 12 | ☀️ 晴朗 | 中（基于恢复状态）|
| 10-20 | ≈ 7 | ⛅ 多云 | 中（基于恢复状态）|
| 20-35 | ≈ 3 | ☁️ 阴天 | 中（基于疲劳累积）|
| ≥ 35 | ≈ 1.5 | 🌧️ 小雨 | 中（基于深度疲劳）|

**输出示例（数据充足）**：
```
🌧️ 小雨（λ=1.3，时间膨胀 1h→1.3h）
├─ 急性疲劳：F_acute=18（参考值）
├─ 慢性疲劳：F_chronic=24（参考值）
├─ 预计恢复：16小时后 λ 回升至 2+（阴天状态）
└─ 建议：轻量任务，避免重大决策
```

**输出示例（数据稀疏）**：
```
☀️ 晴朗（基于恢复状态预估，F=8）
├─ 实时校准中（已收集 1/3 条交互）...
├─ 置信度：中等（基于疲劳度推断）
├─ 预计 2-3 条交互后确认实际状态
└─ 建议：可开始轻度工作，稍后确认深度工作时机
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

**关键定义**：
- **预测目标**：下一次 λ ≥ 10（晴朗状态）的时间点
- **预测方法**：模拟疲劳恢复路径，推算 F 降至阈值以下所需时间
- **F-to-λ 映射**（简化模型）：
  - F < 10 → λ ≈ 12（晴朗）
  - 10 ≤ F < 20 → λ ≈ 7（多云）
  - 20 ≤ F < 35 → λ ≈ 3（阴天）
  - 35 ≤ F < 50 → λ ≈ 1.5（小雨）
  - F ≥ 50 → λ ≈ 0.5（静雾）

**关键定义**：
- **模拟步长**：1小时为单位
- **最大预测时长**：72小时（3天）
- **预测精度**：±2小时（受上下文变化影响）

**输出格式**：
```
预计 [X] 小时后 λ 回升至 [Y]+（[天气状态]）
基于：当前 F=[F_acute]+[F_chronic]，恢复速率 [decay_context]
```

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

### 4.1 存储规范（写入位置固定）

**统一写入位置**（必须指定，防止乱存）：
```
~/Projects/soulmeai/Mods/003-timeflow/storage/{user_id}/
```

**文件结构**：
```
storage/{user_id}/
├── history.jsonl       # 交互日志（append-only）
├── profile.json        # 个人参数（原子更新）
└── fatigue.log         # 疲劳历史（可选）
```

**写入规则**：
- **history.jsonl**：每次交互后立即追加，格式为 JSON Lines
- **profile.json**：参数更新时原子写入（先写 .tmp 再重命名）
- **并发安全**：多 Agent 可同时追加，不会冲突

### 4.2 数据读取（模糊指令）

**指令**：`抓取近30天交互记录`

**Agent 执行策略**（多源抓取）：

```python
def fetch_interaction_records(user_id, days=30):
    """
    从多个可能的数据源抓取交互记录
    返回合并后的记录列表
    """
    records = []
    
    # 1. 优先读取官方存储位置（SoulmeAI 项目目录）
    official_path = f"~/Projects/soulmeai/Mods/003-timeflow/storage/{user_id}/history.jsonl"
    if exists(official_path):
        records.extend(read_jsonl(official_path))
    
    # 2. 如不足30天，搜索其他来源
    if len(records) < threshold:
        # 搜索 OpenClaw memory/ 目录
        memory_files = glob(f"~/.openclaw/workspace/memory/*")
        for f in memory_files:
            records.extend(extract_interactions_from_memory(f))
        
        # 搜索 session 历史（如可访问）
        session_records = fetch_from_session_history(user_id, days)
        records.extend(session_records)
        
        # 搜索其他 agent 工作区
        agent_workspaces = glob(f"~/.openclaw/agents/*/workspace/memory/*")
        for ws in agent_workspaces:
            records.extend(extract_from_workspace(ws))
    
    # 3. 去重、排序、过滤
    records = deduplicate_by_timestamp(records)
    records = filter_by_date_range(records, days=30)
    records = sort_by_timestamp(records)
    
    return records
```

**去重策略**：
- 同一秒内的相同事件类型视为重复
- 保留最完整的 metadata
- 标记数据来源（`source: history.jsonl | memory | session`）

### 4.3 数据更新机制

**profile.json 更新**：
- **更新触发**：
  1. 每7天自动更新
  2. history.jsonl 新增100条记录
  3. 用户手动触发："/时相 更新"
- **更新流程**：
  1. 调用 `fetch_interaction_records()` 抓取最新数据
  2. 重新计算 ρ̄（7天滑动平均）
  3. 重新提取个性化疲劳参数（14天后）
  4. 原子写入 profile.json

**智能合并策略**：
- **触发条件**：数据量阈值（100条）或时间阈值（7天）
- **合并流程**：
  1. 抓取全量历史（多源）
  2. 重新计算所有模型参数
  3. 原子写入新 profile.json

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
