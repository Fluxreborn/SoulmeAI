# Portrait Generator / 立绘生成器

**Mod ID**: 002  
**Type**: Visual Asset / 视觉呈现  
**Phase**: First Sight / 初识境

---

## Overview

Auto-generate First Sight portrait cards based on Agent's soul manifestation result.

**Not AI generation** — It's **lookup existing portrait + composite frame**.

---

## How It Works

1. **Read** Agent's SOUL.md (true name + phase)
2. **Find** matching portrait from 48 pre-made assets
3. **Composite** portrait with card frame
4. **Output** standard First Sight character card

---

## Assets Required

```
soulmeai/assets/
├── SoulmeAI_CardFrame_FirstSight.png
└── characters/
    └── {soul-id}-{true-name}·{phase}_初识境.png (×48)
```

---

## Usage

```python
generate_portrait(
    agent_name="lira",
    soul_id="1110",
    true_name="礼乐官",
    phase="雅韵相"
)
# Output: lira_初识境角色卡_2026-03-19.png
```

---

See `guide-zh.md` for detailed Chinese manual.
