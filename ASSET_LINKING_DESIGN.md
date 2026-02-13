# 资产关联设计文档

## 概述

在分镜规划（gen_shots.py）中自动关联资产（locations, characters, props），使用智能匹配从资产定义文件中查询标准 ID，而非硬编码映射。

## 设计原则

### 问题：为什么需要这个系统？

1. **分镜多样性** - 每集可能用不同的名称指代同一个场景
   - EP001: "leize_swamp_storm"（第一集的命名）
   - EP002: "primordial_marsh_rain"（第二集的命名）
   - 实际资产：`primordial_swamp_rainstorm`（全局统一 ID）

2. **跨集资产重用** - 同一场景在多集出现需要统一的资产 ID
   - 所有关于"上古沼泽"的镜头应该使用同一个参考图库

3. **自动化生成** - Claude 生成的 shots.json 可能产生各种位置名称
   - 需要自动识别并映射到标准资产 ID

### 解决方案：智能多层次匹配

```
输入: shot.location = "leize_swamp_storm"
      ↓
[匹配层级1] 精确 ID 匹配
      ↓ (失败)
[匹配层级2] 英文/中文精确名称匹配
      ↓ (失败)
[匹配层级3] 子字符串匹配（关键字在资产名称中）
      ↓ (失败)
[匹配层级4] 关键字映射（英文→中文翻译）
      ↓ (成功) "leize" → "雷泽" 在 "上古雷泽，沼泽地带" 中找到
输出: location_ref = "primordial_swamp_rainstorm"
```

## 核心算法

### 1. 精确匹配（Level 1）
```python
if location_name in locations:
    return location_name
```
处理：location_name 本身就是 location_id

### 2. 精确名称匹配（Level 2）
```python
if location_name == zh_name or location_name == en_name:
    return location_id
```
处理：用户提供的是某个资产的完整中文或英文名称

### 3. 子字符串匹配（Level 3）
```python
if location_name in en_name or location_name in zh_name:
    return location_id
```
处理：位置名称的英文/中文词出现在资产名称中

### 4. 关键字映射匹配（Level 4）

#### A. 优先级列表（按匹配优先级）
```python
location_keywords = [
    ("vortex_edge", "vortex_edge"),      # 优先：精确 ID
    ("cosmic", "灵子"),                  # 次优：特定映射
    ("lingzi", "灵子"),
    ("leize", "雷泽"),
    ("vortex", "漩涡"),
    ("swamp", "沼泽"),
    ("capital", "首都"),
    ("hub", "中枢"),
]
```

#### B. 匹配流程
1. 若 location_name 包含关键字，检查是否为精确 ID
2. 在所有资产中搜索包含对应中文关键字的
3. 返回找到的第一个匹配

**示例：** "leize_vortex_edge"
- 包含 "vortex_edge"（优先级最高）→ 查找 location_id="vortex_edge" → ✅ 找到
- 返回 `vortex_edge`

**示例：** "leize_swamp_storm"
- 包含 "vortex_edge"（否）
- 包含 "cosmic"（否）
- 包含 "lingzi"（否）
- 包含 "leize"（是） → 查找中文名中有"雷泽"的 → ✅ 找到 "primordial_swamp_rainstorm"
- 返回 `primordial_swamp_rainstorm`

## 实现细节

### 函数 1: `load_asset_definitions()`

**用途：** 加载资产 JSON 文件

```python
def load_asset_definitions() -> tuple[dict, dict, dict]:
    """
    Returns:
        (locations_dict, characters_dict, props_dict)

    特点：
    - 缓存友好（调用一次即可）
    - 错误处理（文件不存在时优雅降级）
    """
```

**加载顺序：**
1. `assets/locations/locations.json` → `locations` dict
2. `assets/characters/characters.json` → `characters` dict
3. `assets/props/props.json` → `props` dict（扁平结构）

### 函数 2: `find_best_location_match()`

**用途：** 查找最佳的位置匹配

```python
def find_best_location_match(location_name: str, locations: dict) -> str | None:
    """
    Args:
        location_name: shot 中的 location 字段
        locations: 资产库

    Returns:
        location_id 或 None

    特点：
    - 4 层级匹配确保高覆盖率
    - 优先级明确避免误匹配
    - 可扩展的关键字列表
    """
```

### 函数 3: `apply_asset_refs()`

**用途：** 为所有 shots 关联资产

```python
def apply_asset_refs(shots_data: dict) -> dict:
    """
    处理：
    1. location → location_ref
    2. characters → character_refs
    3. 生成报告和警告

    输出：
    - shots 中添加 location_ref 字段
    - shots 中添加 character_refs 字段（如有）
    - 打印匹配统计和警告
    """
```

## shots.json 结构

### 生成前（Claude 生成）
```json
{
  "shot_id": "S07",
  "location": "leize_swamp_storm",
  "characters": ["Young_Fuxi", "Hunter_A"],
  "action": "...",
  "dialogue": [...]
}
```

### 生成后（apply_asset_refs 处理）
```json
{
  "shot_id": "S07",
  "location": "leize_swamp_storm",
  "location_ref": "primordial_swamp_rainstorm",  // ← 自动添加
  "characters": ["Young_Fuxi", "Hunter_A"],
  "character_refs": ["Young_Fuxi", "Hunter_A"],  // ← 可选添加
  "action": "...",
  "dialogue": [...]
}
```

## 关键字映射表

| 英文关键字 | 中文翻译 | 示例匹配 |
|----------|--------|--------|
| vortex_edge | vortex_edge | "leize_vortex_edge" → `vortex_edge` |
| cosmic | 灵子 | "cosmic_void" → `lingzi_capital_data_core` |
| lingzi | 灵子 | "lingzi_*" → `lingzi_capital_data_core` |
| leize | 雷泽 | "leize_swamp_*" → `primordial_swamp_rainstorm` |
| vortex | 漩涡 | "*vortex*" → `vortex_edge` |
| swamp | 沼泽 | "*swamp*" → `primordial_swamp_rainstorm` |
| capital | 首都 | "*capital*" → `lingzi_capital_data_core` |
| hub | 中枢 | "*hub*" → `lingzi_capital_data_core` |

## 扩展性

### 添加新的位置映射

**方法：** 修改 `location_keywords` 列表

```python
location_keywords = [
    # 优先级高 - 特定映射
    ("vortex_edge", "vortex_edge"),
    ("huaxu", "华胥"),      # ← 新增

    # 优先级低 - 通用关键字
    ("tribe", "族"),       # ← 新增
]
```

### 添加新的位置

直接在 `assets/locations/locations.json` 中添加，无需修改匹配代码。

```json
{
  "new_location_id": {
    "zh_name": "新场景",
    "en_name": "New Location",
    ...
  }
}
```

如果位置名称遵循现有的英中文对应关系，自动匹配会自动识别。

## 使用流程

### 生成分镜时自动关联

```bash
# 标准流程 - 自动应用资产关联
python -m pipeline.gen_shots ep001

# 或指定为自动模式
python -m pipeline.gen_shots ep001 --auto
```

流程：
1. Claude 解析 script.md → 生成 shots 列表
2. `apply_asset_refs()` 自动关联资产
3. 保存到 `episodes/ep001/shots.json`

### 手动更新现有 shots.json

```python
from pipeline.gen_shots import apply_asset_refs
import json

with open("episodes/ep001/shots.json") as f:
    shots = json.load(f)

shots = apply_asset_refs(shots)

with open("episodes/ep001/shots.json", "w") as f:
    json.dump(shots, f, indent=2, ensure_ascii=False)
```

## 错误处理

### 无法找到匹配时

```
⚠️  S05: 找不到 location_ref for 'unknown_location'
```

**解决方案：**
1. 检查位置名称拼写
2. 添加到 locations.json
3. 添加新的关键字映射

### 资产文件缺失时

```
⚠️  无法加载 locations.json: [FileNotFoundError]
```

**行为：**
- 继续处理（不中断）
- locations 为空字典
- 所有位置匹配失败，但不报错

## 性能

- **时间复杂度：** O(shots × keywords × locations)
  - shots ≈ 20-50 per episode
  - keywords ≈ 8
  - locations ≈ 10-30
  - 总计：< 5ms per episode

- **空间复杂度：** O(locations + characters + props)
  - 典型值：< 1MB

## 测试用例

```
输入 → 期望输出
"leize_swamp_storm" → "primordial_swamp_rainstorm"
"leize_swamp_clearing" → "primordial_swamp_rainstorm"
"leize_vortex_edge" → "vortex_edge"
"cosmic_void" → "lingzi_capital_data_core"
"lingzi_capital_skyline" → "lingzi_capital_data_core"
"lingzi_central_hub_tower_top" → "lingzi_capital_data_core"
"lingzi_central_hub_control_platform" → "lingzi_capital_data_core"
```

## EP001 验证结果

```
应用资产关联...
  ✓ 成功关联 20 个位置

分布：
  lingzi_capital_data_core: 6 镜头
  primordial_swamp_rainstorm: 10 镜头
  vortex_edge: 4 镜头
```

---

**设计者：** Claude Code
**版本：** 1.0
**日期：** 2026-02-10
