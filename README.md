# GeoIntern-Agent

野外地质实习的 AI 助手 —— 把岩石鉴定、剖面出图、野簿记录这些重复活交给 AI。

> **定位**：AI + GIS + 野外地质 的交叉项目。作者是地质专业学生、自学 AI，这个项目最初是给自己野外实习用的，现在整理出来，想看看能不能帮到同样跑野外的人。

## 它能干什么

- **拍照鉴岩**：拍张岩石照片，AI 描述岩性、猜类型、给判断依据（Qwen-VL）
- **剖面 / 柱状图出图**：给地层数据，自动出标准信手剖面、柱状图、赤平投影
- **照片转地质素描**：露头照片 → 铅笔风素描线稿（OpenCV 边缘检测 + VTracer 矢量化）
- **地学 RAG 问答**：按路线 + 观察点切分的地学知识库，回答必须引用出处
- **路线可视化**：KML 轨迹 + 观察点铺到交互地图，带 3D 地形

## 截图预览

**信手剖面出图** — 周口店八角寨—拴马桩桥

![信手剖面图](docs/images/section-profile.png)

**KML 轨迹 → 地形剖面**

![轨迹处理](docs/images/track-processing.png)

**野外构造分析** — 黄院东山梁

![构造分析](docs/images/structure-analysis.png)

**QGIS 工具集成**

![QGIS 工具](docs/images/qgis-tools.png)

**露头识图** — 燧石条带白云岩

![燧石条带](docs/images/chert-bands.jpg)

**地质素描** — 包心菜状叠层石

![叠层石素描](docs/images/stromatolite.jpg)

**对话问答** — Web Demo 实操（手机也能用，支持上传图片识别）

![对话实操：功能总览](docs/images/chat/chat-01.png)
![对话实操：多模块推理链](docs/images/chat/chat-04.png)
![对话实操：野簿指导](docs/images/chat/chat-11.png)

> 完整 11 张实操截图见 [`docs/images/chat/`](docs/images/chat/)

## 目录结构

```
geointern-agent/
├── web/            # demo 入口：FastAPI 对话 + RAG + 识图
├── webmap/         # 路线可视化地图（静态，可挂 GitHub Pages）
├── references/     # 领域知识库（岩石/构造/沉积/地层的决策树 + 野外技能）
├── core/           # 可复用引擎（出图 + 素描 + 视觉 + KML 工具）
├── examples/       # 一次性脚本当示例（各路线剖面、点位素描、转录清洗）
└── output/         # 出图结果（demo 图）
```

## 快速开始

### 1. Web demo（对话 + 识图）

```bash
cd web
pip install -r requirements.txt
cp .env.example .env        # 填上你的 key
python app.py               # 默认 0.0.0.0:8000
```

`.env` 需要两个 key：

```env
DEEPSEEK_API_KEY=sk-你的key          # 对话（默认 deepseek-v4-pro）
DASHSCOPE_API_KEY=sk-你的key         # 识图（qwen-vl-max）
```

### 2. 路线地图（webmap）

```bash
cd webmap
python -m http.server 8000
# 浏览器打开 http://localhost:8000
```

> 不能直接双击 index.html（file:// 会拦本地 JSON），务必走静态服务器。

### 3. 出图引擎（core）

```bash
# 依赖 numpy / matplotlib，先装
python examples/cross_section_L04.py   # 示例：L04 路线信手剖面
```

`examples/` 里的脚本已注入 `core/` 到 sys.path，直接跑即可。

## 技术栈

- **后端**：Python · FastAPI
- **AI**：DeepSeek（对话/流式）· Qwen-VL（多模态识图）
- **RAG**：地学感知切分 + TF-IDF 语义检索（scikit-learn）
- **GIS/制图**：matplotlib · KML/GeoJSON · Leaflet
- **图像**：OpenCV · VTracer

## 现状与诚实说明

这个项目是从一整个暑假的野外实习里长出来的，不是从零设计的商业产品。有些地方还没收拾干净：

- `examples/` 里很多脚本是「某条路线的一次性成品」，不一定开箱即用，需要按具体数据调
- 知识库（`references/`）目前以周口店、峨眉山两条实习路线为主，没覆盖其他地区
- 依赖清单还没收敛成一个统一的 `requirements.txt`（`core/` 引擎的依赖没列全）

如果你也是地质相关专业、或者在做地质信息化，欢迎提 issue 聊聊——尤其是「你们野外最想甩掉的重复活是什么」。

## License

[TODO：还没定，MIT / GPL / 其他待选]
