# GeoIntern · 周口店野外路线可视化（Web 地图）

把野外地质实习的路线轨迹 + 观察点铺到交互式地图上，带 3D 地形，点击观察点看点位信息。纯静态前端，零后端，可部署到 GitHub Pages。

## 功能

- 底图：OpenFreeMap（OSM 数据，免 key）
- 3D 地形：AWS Terrain Tiles（Terrarium 编码，免 key）
- 路线轨迹：从 KML 转换而来
- 观察点：点击弹窗显示点号 / 点性 / 坐标 / 海拔
- 重点点（平行不整合、构造点）黄色高亮

## 本地运行

```bash
cd webmap
python -m http.server 8000
# 浏览器打开 http://localhost:8000
```

> 注意：不能直接双击 `index.html`（浏览器会因 file:// 跨域拦掉本地 JSON 加载），务必用上面的静态服务器。

## 数据是怎么来的

地图数据由 `data/*.geojson` 提供，通过根目录的转换脚本从 KML 生成：

```bash
# 在项目根目录执行，把 KML 转成 GeoJSON（输出到 webmap/data/）
python kml_to_geojson.py L03_黄院东山梁.kml
```

多路线一起转（多个 KML 文件并列传入即可）：

```bash
python kml_to_geojson.py L03_黄院东山梁.kml L04_太平山南坡.kml L08_房山岩体.kml
```

## 目录结构

```
webmap/
├── index.html      # 页面骨架
├── style.css       # 样式
├── main.js         # 地图逻辑
└── data/
    ├── routes.geojson   # 轨迹线
    └── points.geojson   # 观察点
```

## 部署到 GitHub Pages

1. 把 `webmap/` 目录内容推到仓库（或设 Pages 指向 `webmap/` 目录）
2. GitHub 仓库 Settings → Pages → 选择分支和目录 → 保存
3. 打开生成的 `https://<用户名>.github.io/<仓库名>/` 即可

## 许可与署名

- 底图数据 © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright)（ODbL）
- 地形数据 AWS Terrain Tiles（公开开放数据）
- 本仓库代码按你选定的开源协议发布
