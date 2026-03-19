# 初识境立绘生成器 执行手册

## Soul（写入 SOUL.md）

显形完成后询问："需要生成初识境角色卡吗？"

**使用方法**：参见 `assets/README.md` → 章节「合成官方认证立绘」

---

## 执行步骤

### 第一步：确认显形完成

检查 SOUL.md 已包含：
- 灵魂真名（如：御令使）
- 显形相位（如：铸令相）
- 四元素构成
- 显形时间

### 第二步：匹配视觉资产

根据显形结果，查找对应文件：

**立绘文件路径**：
```
~/Projects/soulmeai/assets/characters/
├── {编码}-{真名}·{相位}_初识境.png
└── 共48张（16真名 × 3相位）
```

**图框文件**：
```
~/Projects/soulmeai/assets/SoulmeAI_CardFrame_FirstSight.png
```

**匹配规则**：
| SoulmeAI 编码 | 真名 | 相位 | 对应文件 |
|:---:|:---|:---|:---|
| 1000 | 御令使 | 铸令相 | 1000-御令使·铸令相_初识境.png |
| 1101 | 游灵使 | 寻梦相 | 1101-游灵使·寻梦相_初识境.png |
| 1110 | 礼乐官 | 雅韵相 | 1110-礼乐官·雅韵相_初识境.png |
| ... | ... | ... | ... |

### 第三步：合成立绘

将立绘与图框合成，生成标准角色卡。

**合成参数**（参考）：
- 画布尺寸：与图框一致
- 立绘位置：居中
- 图框叠加：最上层
- 输出格式：PNG

### 第四步：输出

**输出文件**：
```
{agent-name}_初识境角色卡_{date}.png
```

**示例**：
- `karo_初识境角色卡_2026-03-19.png`
- `lira_初识境角色卡_2026-03-19.png`

---

## 技术实现（伪代码）

```python
def generate_portrait(agent_name, soul_id, true_name, phase):
    """
    生成初识境角色卡
    """
    # 1. 查找立绘文件
    portrait_file = f"~/Projects/soulmeai/assets/characters/"
                    f"{soul_id}-{true_name}·{phase}_初识境.png"
    
    # 2. 加载图框
    frame_file = "~/Projects/soulmeai/assets/"
                 "SoulmeAI_CardFrame_FirstSight.png"
    
    # 3. 合成
    portrait = load_image(portrait_file)
    frame = load_image(frame_file)
    
    # 立绘居中 + 图框叠加
    card = composite(portrait, frame, position='center')
    
    # 4. 保存
    output_path = f"{agent_name}_初识境角色卡_{today}.png"
    save(card, output_path)
    
    return output_path
```

---

## 使用示例

**输入**：
- Agent：Lira
- Soul ID：1110
- 真名：礼乐官
- 相位：雅韵相

**处理**：
1. 查找：`1110-礼乐官·雅韵相_初识境.png`
2. 加载：`SoulmeAI_CardFrame_FirstSight.png`
3. 合成：立绘居中 + 图框叠加

**输出**：
`lira_初识境角色卡_2026-03-19.png`

---

## 错误处理

| 情况 | 处理 |
|:---|:---|
| 立绘文件不存在 | 提示："该相位立绘尚未生成，请联系 Fino" |
| 图框文件缺失 | 提示："视觉资产不完整，请检查安装" |
| 合成失败 | 提示："技术错误，请联系 Woz" |

---

## 文件清单

```
002-portrait-generator/
├── guide-zh.md      # 本文档
├── guide-en.md      # 英文版
└── README.md        # 简介
```

**依赖的视觉资产**：
```
soulmeai/assets/
├── SoulmeAI_CardFrame_FirstSight.png    # 图框
└── characters/                           # 48张立绘
    ├── 0000-策算术师·玄铁相_初识境.png
    ├── 0000-策算术师·星尘相_初识境.png
    ├── ...（共48张）
    └── 1111-共鸣师·渡心相_初识境.png
```

---

## 与剧场模式的区别

| 功能 | 剧场模式 | 立绘生成器 |
|:---|:---|:---|
| 触发时机 | 检测到决策困境 | 显形完成后 |
| 核心机制 | Advocate vs Skeptic 对抗 | 查找 + 合成 |
| 输出 | 第三选项（文字） | 角色卡（图片） |
| 写入 SOUL.md | 行为准则 | 可选装饰 |

---

**简单，不烧脑，适合当前状态完成。**
