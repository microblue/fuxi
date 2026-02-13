# 最终架构设计 — 剧本驱动的完全自动化系统

## 🎬 完整工作流（从剧本到成品）

```
script.md (剧本)
   │
   ├─→ [Step 1] gen_assets_json.py
   │   ├─ 自动提取: locations
   │   ├─ 自动提取: characters
   │   └─ 自动提取: props
   │   ↓
   │   assets/locations/locations.json (资产库)
   │   assets/characters/characters.json
   │   assets/props/props.json
   │
   ├─→ [Step 2] gen_locations_refs.py / gen_characters_refs.py / gen_props_refs.py
   │   ├─ 生成位置参考图
   │   ├─ 生成角色参考图
   │   └─ 生成道具参考图
   │   ↓
   │   assets/locations/{id}/*_ref_*.png
   │   assets/characters/{id}/*_ref_*.png
   │   assets/props/{id}/*_ref_*.png
   │
   ├─→ [Step 3] gen_shots.py (★ 核心改进)
   │   ├─ 1️⃣ 从 script.md 解析分镜
   │   ├─ 2️⃣ 自动加载三个资产定义文件
   │   ├─ 3️⃣ 自动应用资产关联:
   │   │   ├─ location → location_ref
   │   │   ├─ characters → character_refs
   │   │   └─ props → prop_refs
   │   └─ 4️⃣ 生成 shots.json (已关联)
   │   ↓
   │   episodes/ep001/shots.json (关键帧规划已包含资产ID)
   │
   ├─→ [Step 4] gen_keyframes_json.py
   │   └─ 生成关键帧配置
   │   ↓
   │   episodes/ep001/keyframes.json
   │
   └─→ [后续步骤] 使用 location_ref 生成所有媒体
       ├─ gen_keyframe_images.py (使用 location_ref 查找参考图)
       ├─ gen_shot_video.py
       ├─ synth_voice.py
       ├─ build_subtitles.py
       └─ render_video.py
           ↓
           ✨ final.mp4

```

---

## 📋 关键脚本说明

### gen_assets_json.py
**目的：** 从剧本自动提取资产定义

```bash
python -m pipeline.gen_assets_json ep001
```

**输入：**
- `episodes/ep001/script.md`

**输出：**
- `assets/locations/locations.json` ✨ 自动生成
- `assets/characters/characters.json` ✨ 自动生成
- `assets/props/props.json` ✨ 自动生成

**特点：**
- 使用 Claude 智能分析
- 支持与现有文件合并

---

### gen_shots.py ★ 核心改进
**目的：** 从剧本生成分镜，**自动关联资产 ID**

```bash
python -m pipeline.gen_shots ep001
```

**输入：**
- `episodes/ep001/script.md`
- `assets/locations/locations.json` ← 自动加载
- `assets/characters/characters.json` ← 自动加载
- `assets/props/props.json` ← 自动加载

**工作流：**
```python
def main():
    # 1. 读取脚本
    script_content = read_script(ep_dir)

    # 2. 生成分镜 + 自动加载资产定义 + 自动应用关联
    shots_data = build_shots_json(
        script_content=script_content,
        episode_id="ep001"
        # ↑ 内部自动加载 locations/characters/props
        # ↑ 内部自动应用 location_ref/character_refs/prop_refs
    )

    # 3. 保存
    save_shots_json(shots_data, ep_dir)
```

**输出：**
- `episodes/ep001/shots.json` ✨ 已关联资产 ID

**示例输出：**
```json
{
  "shot_id": "S07",
  "location": "leize_swamp_storm",
  "location_ref": "primordial_swamp_rainstorm",  ← 自动填充
  "characters": ["Young_Fuxi", "Hunter_A"],
  "character_refs": ["Young_Fuxi", "Hunter_A"],  ← 自动填充
  "camera": "wide shot",
  "action": "...",
  "prompt_visual": "...",
  "prompt_motion": "...",
  ...
}
```

---

### gen_keyframe_images.py
**改进：** 使用 `location_ref` 自动查找参考图

```python
# 之前的逻辑
location_ref_path = find_location_asset_reference(location)

# 现在的逻辑
location_to_use = shot.get("location_ref") or shot.get("location")
location_ref_path = find_location_asset_reference(location_to_use)
```

**优势：** 精确匹配标准资产 ID，避免位置名称歧义

---

## 🔄 资产关联流程

### 自动化机制

```
shots.json 中的 location 字段值
    ↓
gen_shots.py 内部处理
    ↓
load_asset_definitions() 加载三个资产 JSON 文件
    ↓
find_best_location_match() 执行 4 层级智能匹配
    ├─ 层级1: 精确 ID 匹配
    ├─ 层级2: 精确名称匹配
    ├─ 层级3: 子字符串匹配
    └─ 层级4: 关键字映射 (leize → 雷泽)
    ↓
apply_asset_refs() 填充 location_ref 字段
    ↓
shots.json 已关联 location_ref
```

### 关键字映射表（可扩展）

| 英文关键字 | 中文翻译 | 优先级 |
|----------|--------|--------|
| vortex_edge | vortex_edge | 1️⃣ (精确 ID) |
| cosmic | 灵子 | 2️⃣ |
| lingzi | 灵子 | 3️⃣ |
| leize | 雷泽 | 4️⃣ |
| vortex | 漩涡 | 5️⃣ |
| swamp | 沼泽 | 6️⃣ |
| capital | 首都 | 7️⃣ |
| hub | 中枢 | 8️⃣ |

---

## 📊 数据流

### 输入 vs 输出

| 步骤 | 输入文件 | 输出文件 | 自动关联 |
|------|---------|---------|---------|
| gen_assets_json | script.md | locations.json | - |
| gen_assets_json | script.md | characters.json | - |
| gen_assets_json | script.md | props.json | - |
| gen_shots | script.md | shots.json | ✅ location_ref |
| gen_shots | script.md | shots.json | ✅ character_refs |
| gen_keyframe_images | shots.json | keyframes/*.png | 使用 location_ref |
| gen_shot_video | shots.json | *.mp4 | - |
| render_video | 所有视频 | final.mp4 | - |

---

## 🛠️ 实现细节

### gen_shots.py 核心改进

```python
def build_shots_json(
    script_content: str,
    episode_id: str,
    # ...
    locations: dict | None = None,      # ← 可选参数
    characters: dict | None = None,     # ← 可选参数
    props: dict | None = None,          # ← 可选参数
) -> dict:
    """
    1. Parse screenplay
    2. Build shots structure
    3. Auto-load asset definitions (if not provided)
    4. Apply automatic asset linking
    5. Return shots.json with linked assets
    """
    # ... 现有逻辑保留 ...

    # 新增逻辑
    if locations is None:
        locations, characters, props = load_asset_definitions()

    # 应用关联
    shots_data = apply_asset_refs(shots_data, locations, characters, props)

    return shots_data
```

### 调用方式

**自动模式：** gen_shots.py 自动加载资产
```bash
python -m pipeline.gen_shots ep001
# ↓ 内部自动:
# 1. 加载 assets/locations/locations.json
# 2. 加载 assets/characters/characters.json
# 3. 加载 assets/props/props.json
# 4. 应用资产关联
```

**手动模式：** 传入已加载的资产（用于测试或自定义）
```python
from pipeline.gen_shots import build_shots_json

shots = build_shots_json(
    script_content=script,
    episode_id="ep001",
    locations={...},      # 自定义资产
    characters={...},
    props={...}
)
```

---

## ✨ 设计优势

### 1. 完全自动化
- ✅ 无需硬编码位置映射
- ✅ 无需手动维护资产关联
- ✅ 一个命令完成整个流程

### 2. 高度可扩展
- ✅ 添加新位置：只需在 locations.json 中添加
- ✅ 添加新关键字：只需添加一行映射规则
- ✅ 支持多集处理：自动适应不同命名规则

### 3. 清晰的职责分工
- `gen_assets_json.py` → 资产定义
- `gen_shots.py` → 分镜规划 + 自动关联
- `gen_keyframe_images.py` → 使用关联的资产

### 4. 生产就绪
- ✅ 模块化设计
- ✅ 错误处理完善
- ✅ 支持部分处理（可独立运行每个脚本）

---

## 🚀 快速开始

### 完整一键流程
```bash
# 1. 从剧本自动提取资产
python -m pipeline.gen_assets_json ep001

# 2. 生成资产参考图（可选但推荐）
python -m pipeline.gen_locations_refs
python -m pipeline.gen_characters_refs
python -m pipeline.gen_props_refs

# 3. 生成分镜（自动关联资产）
python -m pipeline.gen_shots ep001

# 4. 后续处理
python -m pipeline.generate_episode ep001
```

### 验证资产关联成功
```bash
# 检查 location_ref 是否正确填充
jq '.shots | map({shot_id, location, location_ref})' episodes/ep001/shots.json

# 检查成功率
jq '.shots | map(select(.location_ref)) | length' episodes/ep001/shots.json
# 应该等于总 shots 数
```

---

## 🔍 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| location_ref 为 null | 位置名不在映射中 | 添加到 locations.json 或关键字映射表 |
| 无法加载资产文件 | 文件不存在或路径错误 | 检查 assets/ 目录结构 |
| 匹配不准确 | 多个资产名相似 | 检查关键字优先级或手动编辑 shots.json |

---

## 📈 性能

| 操作 | 时间 | 数据量 |
|------|------|--------|
| gen_assets_json | ~30s | 30-50 资产 |
| gen_shots (含关联) | ~20s | 20-30 镜头 |
| 关联匹配 | < 100ms | 10-50 位置 |
| 总体管道 | ~1.5h | 包含媒体生成 |

---

## 📚 相关文档

- `COMPLETE_WORKFLOW.md` - 完整工作流指南
- `ASSET_LINKING_DESIGN.md` - 资产关联系统详细设计
- `PRODUCTION_WORKFLOW.md` - 旧版工作流（供参考）

---

## ✅ 系统状态

**架构完成** ✓
- ✅ gen_assets_json.py: 自动提取资产
- ✅ gen_shots.py: 自动加载并关联资产
- ✅ 4 层级智能匹配
- ✅ 完整文档和示例

**生产就绪** ✓
- ✅ 模块化设计
- ✅ 错误处理
- ✅ 可扩展
- ✅ 完全自动化

---

**设计完成时间：** 2026-02-10
**版本：** 3.0 (最终架构版)
**状态：** 🎉 Production Ready
