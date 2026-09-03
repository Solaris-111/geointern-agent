# CHANGELOG

## v0.5.0 (2026-07-27)

### 周口店新路线

- **L04 太平山南坡** — 完整野簿预稿 + KML（5个观察点，O₁m→P₁y 上古生界序列）
  - D0402 平行不整合（O₁m/C₂b）为路线核心看点
  - 往年野簿实测数据（GPS + 产状 + 岩性描述）全文提取
  - 路线小结模板 + 常见坑提醒
- **L08 太平山背斜** — 信手剖面出图 + KML + 地形剖面 CSV
- **L01 踏勘路线** — 剖面脚本 + 地层点位 KML
- **实测剖面预稿** — 新产出物类型：`实测剖面预稿_L04_太平山南坡.md`
  - 1:1000 实测剖面预分层方案（4组27层，每层标注分层依据和注意事项）
  - 往年周口店报告附图III完整逐层数据（C₂b→P₁s 共~190m）
  - 人员分工表 + 导线测量记录表 + 分层记录表模板
  - 实测前装备清单 + 现场操作提醒

### 四条路线地层对比

- 识别 L01/L04/L05/L08 四条路线均围绕太平山同一套上古生界地层
- 对比分析写入 L04 预稿：路线对比表 + 地层-路线关注点矩阵 + 报告写作建议
- 结论：L04 是整个太平山上古生界的标准剖面，后续路线叠加不同问题

### GemPy + GemGIS 三维地质建模

- **GemPy 2026.0.3** — 隐式三维构造建模引擎（势场法插值），9个内置例子（背斜、断层、地堑、组合）
- **GemGIS 1.1.9** — 地质数据空间处理（QGIS → GemPy 桥梁）
- **gempy_viewer 2026.0.3** — 3D 可视化 + 剖面切片 + 赤平投影
- **gemgis_tutorials/** — RWTH Aachen 本科课程全套 30+ Jupyter Notebook
  - 7个单元：基础建模→单斜→褶皱→断层→不整合→复合构造→专题
  - 直接对标周口店场景：褶皱(L08) + 不整合(L04) + 断层(L11) + 复合构造(L12)
- **PyVista 0.48.4 + GeoPandas 1.1.4** — 随 GemGIS 安装

### 新增脚本

- `cross_section_L08.py`：L08 太平山背斜信手剖面
- `cross_section_L01.py`：L01 踏勘路线剖面
- `demo_rhythm_column.py`：沉积旋回柱状图 Demo
- `demo_rhythm_section.py`：沉积旋回剖面 Demo
- `lithology_patterns.py`：FGDC 岩性花纹图库
- `fix_section_engine.py` / `fix_re_import.py`：引擎修复

---

## v0.4.0 (2026-07-22)

### 照片→地质素描管线（成果最好的画图管线）
- 野外露头照片 → 地质素描线稿全自动管线：`photo_to_sketch.py`（主管线）+ `sketch_engine.py`（引擎）+ `sketch_pencil.py`（铅笔手绘风格）+ `sketch_simplify.py`（线条简化）+ `final_sketches.py`（最终出图）+ `review_sketch.py`（质量审查）
- 预处理：OpenCV Canny 边缘检测 + bilateral filter 去噪保边
- 矢量化：VTracer（binary/polygon 双模式）+ potrace CLI 备选
- 已跑通 D0601 燧石条带白云岩（`sketch_D0601_chert.py`）和 D0605 叠层石（`sketch_D0605_stromatolite.py`）两个实例

### KML→地形剖面 + Section Engine
- `section_engine.py`（22KB）核心剖面引擎：50+ FGDC 岩性花纹、B&W 标准格式、自动视倾角换算
- `profile_from_kml.py`：KML 轨迹 → DEM 高程查询 → 地形剖面 CSV
- L03（`cross_section_L03.py`）和 L06（`cross_section_L06.py`）两条路线剖面已出图
- `prep_L03.py`：L03 Day2 准备（地形剖面+平卧褶皱素描）
- `reprofile_L03.py`：剖面调整/重生成
- `geo_plotting.py`：公共地质绘图库（比例尺、指北针、产状符号、图例、20种岩性颜色+花纹）

### AI视觉露头描述
- `describe_outcrop.py`：Qwen-VL 对 D0601 燧石条带露头做结构化地质描述（产状目估、条带分期、切割关系）
- `describe_stromatolite.py`：D0605 叠层石露头 AI 描述
- Prompt 设计专为地质观察维度优化（推断时序、识别比例参照物、输出结构化描述）

### 地质平面图 + 3D
- `geological_map.py`：Shapely + DEM 等高线 + 产状 → 平面地质图
- `geological_3d.py`：地层层面三维可视化
- `contour_map.py`：构造等值线图

### DXF 图层分离工具链
- `separate_dxf.py` 系列（v1-v3）：按图层/颜色拆分 DXF
- `separate_by_color.py` 系列（v1-v3）：按颜色分离
- `separate_v4_buffer.py`：缓冲区分离模式
- `vector_utils.py`：矢量工具函数

### QGIS MCP Server
- `mcp_qgis/`：完整的 QGIS MCP 服务器，已注册 `.mcp.json`
- 支持通过 MCP 协议操控 QGIS 桌面端

### 野簿转录 + 实测数据
- `transcribe_day1.py`：Day1 野簿转录管线
- `field_notebooks/周口店/day1/full_transcript.md`：L06 八角寨-拴马桩桥 Day1 9页完整转录
- D0601 燧石条带 + D0605 叠层石露头照片已归档（`output/`）
- L03、L06 KML 文件已提取

### SKILL.md 更新
- 画图管线新增：照片→地质素描、KML→剖面+Section Engine、AI视觉露头描述、地质平面图+3D 四个子节
- 工具感知表新增 7 项：VTracer、potrace、OpenCV、SRTM DEM、QGIS MCP、geo_plotting、Shapely
- 路线知识库状态表更新：L06 替换 L02（以2026实测路线号为准），L03/L06 状态更新为完整管线

---

## v0.3.0 (2026-07-22)

### 周口店野簿预稿系统
- **L02 八角寨—拴马庄桥**：完整野簿预稿，含路线头、8个观察点（D0201-D0208）、点间描述、路线小结模板
  - GPS坐标来自2022年实测，指导书点性原文逐条抄录
  - 覆盖雾迷山组(Jxw)→洪水庄组(Jxh)→铁岭组(Jxt)→下马岭组(Qbx)→长龙山组(Qbc)完整序列
- **L03 黄院东山梁**：完整野簿预稿，含寒武系→奥陶系全部组
  - 府君山组(∈₁f)→馒头组(∈₁m)→徐庄组(∈₂x)→张夏组(∈₂z)→冶里组(O₁y)→亮甲山组(O₁l)→马家沟组(O₁m)
- 野簿预稿模板：路线头（日期+天气+坐标+任务清单）→ 观察点（点号+点位+GPS+点性+描述+产状）→ 路线小结

### 周口店实测数据
- 2022年实习野簿 Qwen-VL-Max 完整转录（学习版，39页）
- 周口店完整野簿 OCR 转录（【私有数据】野簿转录）
- 周口店野外实习野簿 + 野簿预稿（全路线框架）

### 周口店报告
- 完整实习报告初稿（预制报告/周口店地质实习报告.md），含九章正文
- Qwen-VL-Max 优秀报告完整转录（122KB），提取8个关键写作技法

### 出图能力扩展
- 10+ 专项 Python 出图脚本（output/ 目录）：
  - 地层柱状图、信手剖面图、构造纲要图、赤平投影
  - 地质平面图、3D 地质模型
  - DXF 矢量图（ezdxf + pyautocad 双模式）
- DXF 图层分离工具链（separate_dxf / separate_by_color / separate_v4_buffer）
- 地形线提取、高程测量等辅助脚本

### SKILL.md 规则更新
- Layer 0 新增：资料查阅优先级（指导书 > 往年野簿 > QwenVL转录）
- Layer 0 新增：周口店以指导书第四章为准（16条路线权威来源）
- Layer 0 新增：野簿格式按标准模板（野簿格式.jpg）
- 路线知识库状态表更新：周口店已导入 + RAG索引已建

### RAG 管道增强
- 新增周口店目录索引（build_toc_zk.py + toc_zhoukoudian.md）
- 两本指导书合并索引 1327 chunks
- 新增：韧性剪切带 + 逆冲推覆构造决策树（shearzone_thrust.md）
- 新增：岩石花纹图例 + 构造符号表（symbols.md）

---

## v0.2.0 (2026-07-15)

### AutoCAD 集成
- 检测并连接本机 AutoCAD 2021 (Version 24.0)，通过 `pyautocad` COM 接口控制
- DXF 剖面图生成器 (`cad_plot.py`)：ezdxf 生成矢量 DXF，含真实 hatch 花纹、分层标注、图例
- 支持 16 种 FGDC 岩性花纹映射到 AutoCAD 原生 hatch pattern（ANSI31/32/33/37、AR-SAND、GRAVEL、EARTH）
- 视倾角自动换算，地层界线沿视倾角向地下延伸
- 输出文件可在 AutoCAD / CorelDRAW / QGIS / LibreCAD 中打开和编辑
- Agent 可在对话中通过 Python 直接操作 AutoCAD（画线、加文字、打开文件、缩放）

### 周口店知识库
- 载入《周口店地区地质实习指导书》（王根厚主编，126页），两本指导书总索引 1327 chunks
- 变质岩决策树：区域变质 + 热接触变质 + 动力变质，三种齐全，含周口店变质分带实例
- 韧性剪切带 + 逆冲推覆构造决策树（S-C组构/鞘褶皱/糜棱岩/飞来峰/构造窗/叠瓦状）
- 16 条路线速查（5 阶段，含教学目的和观察内容）
- 周口店目录索引

### 第5-6章提取
- 地质图绘制步骤（综合柱状图 + 构造纲要图）→ sketch.md
- 岩石花纹图例 + 构造符号表 → symbols.md 新建
- 地质点编号规范 + 周口店地层简表 → notebook.md
- 周口店报告 10000 字要求 + 8 章大纲 → report.md

### 画图决策树
- 信手剖面图 5 步法 + 岩性花纹要求 + 地层接触关系画法 + 检查清单
- 地层柱状图 6 步编制法
- 地质素描（露头 vs 构造）画法

### 多模态
- PaddleOCR 部署成功（PP-OCRv5_server），中文识别率 >90%
- 周口店优秀报告 39 页 Qwen-VL-Max 完整转录（122KB）
- 报告写作技法从优秀报告中提取 8 个关键技法

---

## v0.1.0 (2026-07-14)

### 项目创建 & 迁出
- 从 `d:\888\.claude\skills\geointern-agent` 迁至 `d:\geointern-agent`，独立于 888 项目
- 定位：最终做成交互式 app，非 Claude Code skill

### 架构设计
- 吸收 GeoSquire/GeoGPT/GeoMind 三个参考项目的架构思路
- SKILL.md：Layer 0-1 核心规则 + GeoMind 三段式工作流 + 5 大模块 + 观察点清单系统 + 画图管线
- 峨眉山 5 条路线文件（观察点清单框架已就绪，待真数据填充）

### RAG 管道 (pipeline.py)
- PDF 提取（pymupdf）+ 地学感知切分（按地质实体，非 token 窗口）
- 三层索引：精确匹配 + TF-IDF 语义 + 地层层级扩展
- 混合检索 + 路线偏序重排
- CLI 入口：`python pipeline.py index|search|toc`

### 指导书 OCR 索引
- 载入《峨眉山地质实习指导书》PDF（181 页，Pdg2Pic 扫描版）
- 安装 Tesseract OCR v5.4 + chi_sim 中文语言包，项目本地 tessdata
- pipeline.py 新增 OCR 回退：文字层为空时自动 OCR 提取
- 181 页全部 OCR，生成 802 个地质感知 chunk，30 个精确匹配键
- 每页保存 PNG 截图到 `references/rag/page_images/`（1019×1469），搜索命中时附带图片路径

### 目录索引 (build_toc.py)
- 混合模式：OCR 自动检测章节标题 + 已知结构兜底
- 覆盖 5 章 + 14 条路线，含 PDF 页码范围
- **第3章全部8条路线页码已通过关键词分布验证**（路线1→p84, 路线2→p90, 路线3→p98, 路线4→p108, 路线5→p115, 路线6→p122, 路线7→p128, 路线8→p132）
- **第3章全部观察点已提取**（共28个观察点，含名称和描述）
- 输出 `toc.json` + `toc.md`，`pipeline.py index` 自动触发
- 搜索结果带目录面包屑（如"第3章 教学路线 > 路线1 清音电站→龙门硐电站"）

### CLI 命令
```
python pipeline.py index                     # 建索引 + OCR + 页面截图 + 自动生成目录
python pipeline.py search "飞仙关组"          # 混合检索，结果带 TOC 定位 + 页面图片
python pipeline.py toc                        # 查看完整目录（含观察点）
python pipeline.py toc 路线1                  # 搜索目录关键词
python pipeline.py toc 84                     # 查某页属于哪个章节
```

### 野外技能知识库（第2章精读）
- 从 OCR 乱码中提取指导书第2章野外技能内容，写入结构化文件：
  - [compass.md](references/field-skills/compass.md) — 罗盘操作（磁偏角校正、倾向/倾角测量、后方交会法、产状格式）
  - [notebook.md](references/field-skills/notebook.md) — 野簿记录规范（7要素格式、岩性/构造/地层点描述模板、路线小结）
  - [sketch.md](references/field-skills/sketch.md) — 信手剖面画法（5步法）+ 地质素描规范 + 路线平面图

### 决策树知识库（岩石/构造/沉积/地层）
- 从指导书第2章提取四大鉴定决策树，写入结构化文件：
  - **岩石鉴定**：[igneous.md](references/rocks/igneous.md) 岩浆岩（5步决策树：颜色→结构→构造→矿物→SiO₂分类）+ [sedimentary.md](references/rocks/sedimentary.md) 沉积岩（4步决策树+HCl测试法）+ [metamorphic.md](references/rocks/metamorphic.md) 变质岩（3步决策树：构造→矿物→变斑晶）
  - **构造判读**：[faults.md](references/structures/faults.md) 断层（4步决策树：证据→类型→参数→记录）+ [folds.md](references/structures/folds.md) 褶皱（3步决策树：背斜vs向斜→倒转判断→参数）
  - **沉积相**：[structures.md](references/sediment/structures.md) 沉积构造（物理/化学/生物三类 + 顶底判断 + 古水流判断）
  - **地层识别**：[emeishan.md](references/stratigraphy/emeishan.md) 峨眉山完整地层序列（二叠系→白垩系各组） + 接触关系判断 + 各路线出露地层速查
- 每个文件均包含：决策树流程图 + 详细对照表 + 峨眉山本地实例 + 常见坑

### 已知限制
- 第4章路线9-14的观察点尚未提取，页码为估算
### 画图管线 (plotting.py)
- 四个出图模块，CLI 一键生成：
  - **地层柱状图** (`column`)：输入组名+厚度+岩性 → 标准柱状图（花纹自动填充+图例）
  - **赤平投影** (`stereonet`)：输入倾向/倾角 → 极点图+等密图+大圆图（mplstereonet）
  - **信手剖面图** (`section`)：输入地形线+地层界线+产状 → 地下地层延展+视倾角计算+岩性花纹填充
  - **岩性花纹图例** (`legend`)：16种 FGDC 标准花纹独立图例
- 视倾角自动换算：`apparent_dip = arctan(tan(α) × sin(θ))`
- 支持中文标题和标注（微软雅黑）
- 载入《周口店地区地质实习指导书》（王根厚主编，126页），两本指导书总索引 1327 chunks
- **变质岩决策树**：[metamorphic.md](references/rocks/metamorphic.md) 更新为四种类型：区域变质 + 热接触变质 + 动力变质 + 碎裂变质，含周口店变质分带实例
- **构造决策树补充**：[shearzone_thrust.md](references/structures/shearzone_thrust.md) — 韧性剪切带鉴定（S-C组构+鞘褶皱+糜棱岩）+ 逆冲推覆构造（飞来峰+构造窗+叠瓦状）
- **16条路线速查**：[zhoukoudian.md](references/routes/zhoukoudian.md) — 5阶段×16条路线，含教学目的+观察内容+路线对比
- 周口店目录索引：[toc_zhoukoudian.md](references/rag/index/toc_zhoukoudian.md)

### 目录结构
```
d:\geointern-agent\
├── SKILL.md
├── meta.json
├── CHANGELOG.md
└── references/
    ├── rocks/              # 岩性鉴定（3个：岩浆岩/沉积岩/变质岩，含决策树+峨眉山实例）
    ├── structures/         # 构造判读（2个：断层/褶皱，含决策树+峨眉山实例）
    ├── sediment/           # 沉积构造速查（物理/化学/生物成因+顶底判断+古水流）
    ├── stratigraphy/       # 峨眉山地层序列（二叠系→白垩系+接触关系+路线速查）
    ├── karst.md            # 岩溶（占位）
    ├── field-skills/       # 野外技能（3个：罗盘/野簿/剖面素描，从指导书第2章提取）
    ├── routes/             # 路线脚本（5个占位）
    ├── report/             # 报告模板
    └── rag/                # RAG 管道
        ├── pipeline.py     # 主程序（index/search/toc）
        ├── build_toc.py    # 目录提取器
        ├── index/          # 索引 + chunks.json + toc.json + toc.md
        ├── page_images/    # 181 张页面截图
        ├── tessdata/       # chi_sim 中文语言包
        ├── guidebook/      # ← 指导书 PDF 放这里
        ├── textbook/       # ← 教材 PDF 放这里
        └── notes/          # ← 个人笔记 (.md)
```
