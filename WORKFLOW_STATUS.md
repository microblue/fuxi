# 🎬 伏羲纪元 工作流状态与缺失清单

**最后更新**：2025年2月5日
**完成度**：约 35%（基础资产与音频系统完成）

---

## 📊 整体进度总览

```
剧本编写          ████████████████████ 100% ✅
角色定义          ████████████████████ 100% ✅
场景定义          ████████████████████ 100% ✅
音频系统          ████████████████████ 100% ✅
  ├─ 配音合成       100% ✅
  ├─ 音效管理       100% ✅
  └─ 声音混合       100% ✅

分镜工具          ████████████░░░░░░░░ 60% ⚠️
  ├─ 脚本→分镜     100% ✅
  └─ T2I提示词     0%   ❌

视觉资产定义      ██░░░░░░░░░░░░░░░░░░ 10% ❌
  ├─ 创意资产库     0%   ❌
  ├─ 道具定义       0%   ❌
  ├─ 特效目录       0%   ❌
  └─ 配色方案       0%   ❌

编排系统          ░░░░░░░░░░░░░░░░░░░░ 0%   ❌
  ├─ 主编排脚本     0%   ❌
  ├─ 字幕生成       0%   ❌
  └─ 视频合成       0%   ❌

文档体系          ░░░░░░░░░░░░░░░░░░░░ 0%   ❌
```

---

## ✅ 已完成组件详细清单

### 📚 剧本与核心资产（100%）
- [x] **script_full_30eps.md** - 完整30集、约1.7万行剧本
  - 包含所有30集的完整台词与舞台指示
  - 已覆盖所有主角与配角

- [x] **characters.json** - 12个主要角色
  - 包含外观、性格、声音、情感弧线、关键关系等
  - 每个角色都有TTS配置与T2I提示词模板

- [x] **scenes.json** - 28个独特地点、120+场景
  - 包含时间、氛围、特效需求、场景变体
  - 涵盖3大时代的视觉设定

### 🎵 音频系统（100%）
- [x] **synth_voice.py** - 配音合成引擎
  - ✅ Fish Audio集成（已测试，可用）
  - ✅ Edge TTS备选方案
  - ✅ 新/旧对话格式兼容
  - ✅ 情感与语速参数提取
  - ✅ 单镜头生成：`pixi run python -m pipeline.synth_voice ep001 fish S05`
  - ✅ 完整集数生成：`pixi run python -m pipeline.synth_voice ep001 fish`

- [x] **gen_sound.py** - 完整声音管道
  - ✅ 配音生成
  - ✅ 音效处理
  - ✅ BGM集成
  - ✅ 多轨混音

- [x] **manage_sfx.py** - 音效与BGM管理
  - ✅ 音效库管理
  - ✅ BGM调度

### 🔧 工具与工具函数（80%）
- [x] **gen_shots.py** - 脚本→分镜转换
  - ✅ 支持Claude（opus/sonnet/haiku）
  - ✅ 自动生成shots.json
  - ✅ 交互式审阅模式

- [x] **gen_character_json.py** - 剧本→角色定义
  - ✅ 从完整剧本提取角色
  - ✅ 生成structured JSON

- [x] **utils.py** - 基础工具函数
  - ✅ 路径管理
  - ✅ 数据加载

---

## ⚠️ 关键缺失组件

### 🔴 最高优先级（核心系统缺失）

#### 1. **generate_episode.py** - 完整编排脚本
**状态**：❌ 完全缺失
**重要性**：🔴 致命（没有它无法连接各模块）
**预期工作量**：5-7天

**责任**：
```python
1. 读取 script.md（完整剧本）
2. 调用 gen_shots.py → 生成 shots.json（分镜）
3. 为每个镜头生成 T2I 提示词 → 调用 Flux 模型
   - 提取场景、角色、道具信息
   - 结合 style_bible 生成完整提示
4. 生成 I2V 提示词 → 调用 LTX-2 模型
   - 基于关键帧生成视频序列
   - 控制镜头运动与时长
5. 调用 synth_voice.py → 生成配音
6. 调用 build_subtitles.py → 生成字幕
7. 调用 render_video.py → 合成最终视频
8. 生成 report.md（质量自检）
```

**预期命令**：
```bash
pixi run python -m pipeline.generate_episode ep001
# 或
pixi run python -m pipeline.generate_episode ep001 --preview  # 仅生成预览
```

---

#### 2. **build_subtitles.py** - 字幕生成与时间对齐
**状态**：❌ 完全缺失
**重要性**：🔴 高（视频质量的关键）
**预期工作量**：3-4天

**功能**：
```python
1. 从 shots.json 提取所有对话
2. 调用 synth_voice 获取音频时长
3. 自动对齐字幕时间码（SRT/VTT格式）
4. 应用中文字幕规则：
   - 每行 ≤16 字
   - 保留标点符号
   - 避免在词中断行
5. 输出 subtitles.srt / subtitles.vtt
```

---

#### 3. **render_video.py** - 最终视频合成
**状态**：❌ 完全缺失
**重要性**：🔴 高（生产最终输出）
**预期工作量**：4-5天

**功能**：
```python
1. 加载 I2V 生成的视频镜头序列
2. 序列合成为连续视频
3. 混合配音轨道（synth_voice 输出）
4. 混合音效与 BGM 轨道
5. 添加字幕轨道（build_subtitles 输出）
6. 输出最终 MP4（1920×1080, 24fps）
```

---

### 🟠 高优先级（创意资产库）

#### 4. **style_bible/** - 创意资产与指导文档
**状态**：❌ 完全缺失
**重要性**：🟠 高（指导所有视觉生成）
**预期工作量**：5-7天

**需要文件**：
```
style_bible/
├─ world.md                # 世界观规则
│  ├─ 时间线设定
│  ├─ 地理与建筑风格
│  ├─ 科技体系
│  ├─ 社会结构
│  └─ 核心冲突与主题
│
├─ tone.md                 # 整体风格指导
│  ├─ 视觉基调
│  ├─ 叙事语言
│  ├─ 情感节奏
│  └─ 戏剧张力
│
├─ camera_language.md      # 摄影与景别约定
│  ├─ 景别定义与用法
│  ├─ 运镜风格
│  ├─ 光线处理
│  └─ 特殊摄影技巧
│
├─ prompt_templates.md     # T2I/I2V提示词模板
│  ├─ 场景模板
│  ├─ 角色模板
│  ├─ 动作模板
│  └─ 特效模板
│
├─ color_bible.md          # 配色系统
│  ├─ 色调分布
│  ├─ 场景配色
│  └─ 情感色彩映射
│
├─ lighting_guide.md       # 光影指导
│
└─ sfx_bgm_library.md      # 音效与BGM库
```

---

#### 5. **props.json** - 道具资产定义
**状态**：❌ 完全缺失
**重要性**：🟠 高（T2I生成细节）
**预期工作量**：2-3天
**预期条目数**：>100个道具

**包含信息**：
```json
{
  "prop_id": {
    "zh_name": "中文名称",
    "appearance": "视觉描述",
    "materials": "材质",
    "color": "颜色",
    "size": "大小",
    "scenes": ["出现的场景"],
    "visual_keywords": ["关键词"],
    "tech_level": "科技水平（原始/代码/混合）"
  }
}
```

---

### 🟡 中优先级（其他视觉资产）

#### 6. **vfx_effects.json** - 特效目录
**状态**：❌ 缺失
**重要性**：🟡 中
**预期条目数**：30-50个特效

#### 7. **color_schemes.json** - 场景配色方案
**状态**：❌ 缺失
**重要性**：🟡 中

#### 8. **costume_designs.json** - 服装设计参考
**状态**：❌ 缺失
**重要性**：🟡 中

---

### 📖 文档与指南（优先级：低-中）

- [ ] **WORKFLOW.md** - 完整工作流文档（在CLAUDE.md中提到）
- [ ] **PROMPT_GUIDE.md** - T2I/I2V提示词编写指南
- [ ] **CHARACTER_GUIDE.md** - 角色定妆指导手册
- [ ] **SCENE_GUIDE.md** - 场景美术指导

---

### 🛠️ 辅助工具（优先级：低）

- [ ] **preview_generation.py** - 快速预览镜头效果
- [ ] **quality_check.py** - 质量检查脚本
- [ ] **asset_validator.py** - 资产完整性检查

---

## 🎯 推荐执行计划

### **方案 C：混合版（推荐）- 4-6周完成**

#### **第1周：核心系统架构**
**目标**：让整个工作流可以串联起来
1. ✏️ 创建 **generate_episode.py** 框架
   - 主流程控制
   - 模块调用逻辑
   - 错误处理与日志

2. ✏️ 创建 **style_bible/world.md**
   - 时间线与年代背景
   - 三大时代的视觉风格
   - 科技与自然的融合规则

3. ✏️ 创建 **props.json** 基础版
   - 优先添加高频出现的100+道具
   - 关键场景的重要道具

**成果**：整个编排系统可以跑起来（虽然还有部分模块缺失）

---

#### **第2周：字幕与视频系统**
**目标**：完成从音频到视频的最后一公里

1. ✏️ 创建 **build_subtitles.py**
   - 基础版（手动对齐）
   - 完整版（自动对齐）

2. ✏️ 创建 **render_video.py**
   - I2V序列合成
   - 多轨混音
   - 字幕添加

3. ✏️ 完成 **style_bible/tone.md** 与 **camera_language.md**

**成果**：可以输出完整的短视频（虽然视觉部分还需要T2I/I2V的支持）

---

#### **第3周+：完善资产与文档**
**目标**：补齐所有创意资产与工具

1. ✏️ 完成 style_bible 其他文件
   - color_bible.md
   - lighting_guide.md
   - prompt_templates.md
   - sfx_bgm_library.md

2. ✏️ 完成其他 JSON 资产
   - vfx_effects.json
   - color_schemes.json
   - costume_designs.json

3. ✏️ 编写文档与指南
   - WORKFLOW.md
   - PROMPT_GUIDE.md
   - CHARACTER_GUIDE.md
   - SCENE_GUIDE.md

4. ✏️ 开发辅助工具
   - preview_generation.py
   - quality_check.py
   - asset_validator.py

---

## 🚀 立即可采取的行动

### 这周内必须做的 3 件事：

1. **开始 generate_episode.py**
   ```bash
   touch /home/dz/fuxi/pipeline/generate_episode.py
   # 编写框架与主流程
   ```

2. **开始 style_bible/world.md**
   ```bash
   mkdir -p /home/dz/fuxi/style_bible
   touch /home/dz/fuxi/style_bible/world.md
   # 根据剧本编写世界观
   ```

3. **开始 props.json**
   ```bash
   touch /home/dz/fuxi/doc/props.json
   # 从剧本和scenes.json中提取道具
   ```

---

## 📈 完成度里程碑

```
当前:        35%  ████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
第1周后:     50%  ██████▒▒▒▒▒▒▒▒▒▒▒▒▒▒
第2周后:     70%  ███████████▒▒▒▒▒▒▒▒
第3周后:     90%  ██████████████████▒▒
最终完成:    100% ████████████████████
```

---

## 💡 关键建议

1. **优先完成编排系统**（generate_episode.py）
   - 这是其他一切的"胶水"
   - 没有它，各个模块无法有效协作

2. **style_bible 要早建立**（world.md）
   - 它是指导所有T2I/I2V生成的基础
   - 越早明确，生成质量越好

3. **测试驱动开发**
   - 每完成一个模块，立即测试集成
   - 发现问题立即修改，不要堆积

4. **资产的可复用性**
   - props.json 中的道具应该在多个场景复用
   - 角色的服装/形态应该保持一致
   - 这样能降低后期制作工作量

---

**下一步建议**：选择 Option C，从 generate_episode.py 开始着手？
