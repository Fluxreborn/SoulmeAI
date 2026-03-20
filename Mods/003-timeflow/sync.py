#!/usr/bin/env python3
"""
Timeflow Sync - 从 OpenClaw 会话同步交互数据到 timeflow

用法:
  python3 sync.py [--agent karo] [--user fable]

功能:
  1. 读取 OpenClaw 会话文件 (~/.openclaw/agents/{agent}/sessions/*.jsonl)
  2. 解析交互记录，计算 density_contribution
  3. 追加到 timeflow history.jsonl
  4. 触发 profile 更新（如果达到阈值）
"""

import json
import os
import sys
import glob
from datetime import datetime, timezone
from pathlib import Path

# 配置
DEFAULT_AGENT = "karo"
DEFAULT_USER = "fable"
OPENCLAW_DIR = Path.home() / ".openclaw"
TIMEFLOW_DIR = Path.home() / ".openclaw/workspace/timeflow"

# 交互类型判断规则
EVENT_TYPES = {
    "query": {
        "keywords": ["状态", "如何", "怎么样", "?", "？", "查询", "分析"],
        "default_contribution": 0.5
    },
    "deep_work": {
        "keywords": ["设计", "实现", "开发", "代码", "架构", "重构", "算法"],
        "default_contribution": 1.0
    },
    "decision": {
        "keywords": ["决策", "选择", "确定", "决定", "是否", "方案"],
        "default_contribution": 0.8
    },
    "implementation": {
        "keywords": ["执行", "完成", "提交", "推送", "部署", "修复"],
        "default_contribution": 1.0
    }
}

def classify_event(content: str) -> tuple:
    """
    根据消息内容判断事件类型和 density_contribution
    返回: (event_type, contribution)
    """
    if not content:
        return ("query", 0.3)
    
    content_lower = content.lower()
    
    # 检查各类型关键词
    for event_type, config in EVENT_TYPES.items():
        for keyword in config["keywords"]:
            if keyword in content_lower:
                return (event_type, config["default_contribution"])
    
    # 默认：简单查询
    # 如果消息很短（<20字），认为是简单确认
    if len(content) < 20:
        return ("query", 0.3)
    
    # 中等长度，一般查询
    return ("query", 0.5)

def parse_openclaw_session(session_file: Path) -> list:
    """
    解析 OpenClaw 会话文件，提取有效交互
    返回: [{timestamp, event, contribution, metadata}, ...]
    """
    records = []
    
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                # 只处理 user message
                if data.get("type") != "message":
                    continue
                
                msg = data.get("message", {})
                if msg.get("role") != "user":
                    continue
                
                content_blocks = msg.get("content", [])
                if not content_blocks:
                    continue
                
                # 提取文本内容
                content_text = ""
                for block in content_blocks:
                    if isinstance(block, dict) and block.get("type") == "text":
                        content_text = block.get("text", "")
                        break
                
                if not content_text:
                    continue
                
                # 解析时间戳
                timestamp = data.get("timestamp", datetime.now(timezone.utc).isoformat())
                
                # 判断事件类型
                event_type, contribution = classify_event(content_text)
                
                # 生成记录
                record = {
                    "timestamp": timestamp,
                    "event": event_type,
                    "density_contribution": contribution,
                    "metadata": {
                        "content_preview": content_text[:100] + "..." if len(content_text) > 100 else content_text,
                        "source_file": session_file.name
                    }
                }
                records.append(record)
                
    except Exception as e:
        print(f"⚠️  解析文件失败 {session_file}: {e}", file=sys.stderr)
    
    return records

def load_existing_history(history_file: Path) -> set:
    """加载已存在的历史记录时间戳，用于去重"""
    existing_timestamps = set()
    
    if not history_file.exists():
        return existing_timestamps
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    existing_timestamps.add(data.get("timestamp"))
                except:
                    pass
    except Exception as e:
        print(f"⚠️  读取历史文件失败: {e}", file=sys.stderr)
    
    return existing_timestamps

def sync_sessions(agent_name: str = DEFAULT_AGENT, user_id: str = DEFAULT_USER) -> dict:
    """
    同步 OpenClaw 会话到 timeflow
    返回同步统计
    """
    # 路径
    sessions_dir = OPENCLAW_DIR / f"agents/{agent_name}/sessions"
    storage_dir = TIMEFLOW_DIR / f"storage/{user_id}"
    history_file = storage_dir / "history.jsonl"
    
    # 确保目录存在
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    # 加载已存在的时间戳（去重）
    existing_timestamps = load_existing_history(history_file)
    
    # 查找所有会话文件
    session_files = list(sessions_dir.glob("*.jsonl"))
    if not session_files:
        print(f"⚠️  未找到会话文件: {sessions_dir}")
        return {"synced": 0, "skipped": 0, "errors": 0}
    
    print(f"📁 找到 {len(session_files)} 个会话文件")
    
    # 解析所有会话
    all_records = []
    for session_file in sorted(session_files):
        print(f"  解析: {session_file.name}")
        records = parse_openclaw_session(session_file)
        all_records.extend(records)
    
    # 去重并按时间排序
    new_records = []
    for record in all_records:
        if record["timestamp"] not in existing_timestamps:
            new_records.append(record)
    
    new_records.sort(key=lambda x: x["timestamp"])
    
    # 追加到新文件
    if new_records:
        with open(history_file, 'a', encoding='utf-8') as f:
            for record in new_records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        print(f"✅ 新增 {len(new_records)} 条记录到 {history_file}")
    else:
        print(f"✓ 没有新记录需要同步")
    
    # 返回统计
    return {
        "total_parsed": len(all_records),
        "existing": len(existing_timestamps),
        "new_synced": len(new_records),
        "history_file": str(history_file)
    }

def check_profile_update_needed(user_id: str = DEFAULT_USER) -> bool:
    """检查是否需要更新 profile（达到阈值）"""
    storage_dir = TIMEFLOW_DIR / f"storage/{user_id}"
    history_file = storage_dir / "history.jsonl"
    profile_file = storage_dir / "profile.json"
    
    if not history_file.exists():
        return False
    
    # 统计记录数
    record_count = 0
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    record_count += 1
    except:
        pass
    
    # 阈值：100条记录或7天
    if record_count >= 100:
        print(f"📊 记录数达到 {record_count}，建议更新 profile")
        return True
    
    # 检查上次更新时间
    if profile_file.exists():
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            last_updated = profile.get("meta", {}).get("updated_at", "")
            if last_updated:
                last_date = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                days_since = (datetime.now(timezone.utc) - last_date).days
                if days_since >= 7:
                    print(f"📅 距上次更新 {days_since} 天，建议更新 profile")
                    return True
        except:
            pass
    
    return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Sync OpenClaw sessions to timeflow')
    parser.add_argument('--agent', default=DEFAULT_AGENT, help='Agent name (default: karo)')
    parser.add_argument('--user', default=DEFAULT_USER, help='User ID (default: fable)')
    parser.add_argument('--check-update', action='store_true', help='Check if profile update needed')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🕐 Timeflow Sync - OpenClaw 会话同步")
    print("=" * 60)
    print(f"Agent: {args.agent}")
    print(f"User: {args.user}")
    print()
    
    # 执行同步
    stats = sync_sessions(args.agent, args.user)
    
    print()
    print("=" * 60)
    print("📊 同步统计")
    print("=" * 60)
    print(f"解析记录: {stats.get('total_parsed', 0)}")
    print(f"已存在:   {stats.get('existing', 0)}")
    print(f"新增同步: {stats.get('new_synced', 0)}")
    print(f"历史文件: {stats.get('history_file', 'N/A')}")
    
    # 检查是否需要更新 profile
    if args.check_update or stats.get('new_synced', 0) > 0:
        print()
        if check_profile_update_needed(args.user):
            print("💡 提示: 记录数或时间达到阈值，建议运行 '时相更新' 重新计算 profile")
        else:
            print("✓ Profile 无需更新")
    
    print()
    print("✅ 同步完成")

if __name__ == "__main__":
    main()
