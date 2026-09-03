// GeoIntern 周口店野外路线可视化
// 底图：OpenFreeMap · 地形：AWS Terrain Tiles（Terrarium 编码）· 数据：data/*.geojson

const ZHOUKOUDIAN_CENTER = [115.908, 39.69];

const map = new maplibregl.Map({
  container: 'map',
  style: 'https://tiles.openfreemap.org/styles/liberty',
  center: ZHOUKOUDIAN_CENTER,
  zoom: 13,
  pitch: 55,
  bearing: 0,
  hash: true,
});
window.map = map; // 暴露给调试和后续联动（聊天界面跳转到某点）

map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right');
map.addControl(new maplibregl.ScaleControl(), 'bottom-right');

map.on('load', async () => {
  // 1. 3D 地形（Terrarium 编码，免 key）
  map.addSource('terrain-dem', {
    type: 'raster-dem',
    tiles: ['https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'],
    encoding: 'terrarium',
    tileSize: 256,
    maxzoom: 15,
  });
  map.setTerrain({ source: 'terrain-dem', exaggeration: 1.3 });

  // 2. 加载预转换的 GeoJSON
  const [routes, points] = await Promise.all([
    fetch('data/routes.geojson').then((r) => r.json()),
    fetch('data/points.geojson').then((r) => r.json()),
  ]);

  // 3. 轨迹线
  map.addSource('routes', { type: 'geojson', data: routes });
  map.addLayer({
    id: 'routes',
    type: 'line',
    source: 'routes',
    layout: { 'line-join': 'round', 'line-cap': 'round' },
    paint: { 'line-color': '#e63946', 'line-width': 3 },
  });

  // 4. 观察点（重点点黄色，普通点绿色）
  map.addSource('points', { type: 'geojson', data: points });
  map.addLayer({
    id: 'points',
    type: 'circle',
    source: 'points',
    paint: {
      'circle-radius': ['case', ['get', 'key'], 8, 6],
      'circle-color': ['case', ['get', 'key'], '#e6a700', '#2f6b4f'],
      'circle-stroke-width': 2,
      'circle-stroke-color': '#ffffff',
    },
  });
  map.addLayer({
    id: 'point-labels',
    type: 'symbol',
    source: 'points',
    layout: {
      'text-field': ['get', 'point_id'],
      'text-size': 11,
      'text-offset': [0, 1.3],
      'text-anchor': 'top',
    },
    paint: { 'text-halo-color': '#ffffff', 'text-halo-width': 1.5 },
  });

  // 5. 路线开关（从数据里动态生成）
  buildRouteSwitches(routes);

  // 6. 点击弹窗
  map.on('click', 'points', (e) => {
    const feat = e.features[0];
    const p = feat.properties;
    const coord = feat.geometry.coordinates;
    new maplibregl.Popup({ offset: 12 })
      .setLngLat(coord)
      .setHTML(`
        <div class="popup">
          <h3>${p.point_id}</h3>
          <div class="desc">${p.description || '观察点'}</div>
          <table>
            <tr><td>路线</td><td>${p.route}</td></tr>
            <tr><td>经度</td><td>${p.lng.toFixed(6)}</td></tr>
            <tr><td>纬度</td><td>${p.lat.toFixed(6)}</td></tr>
            ${p.ele ? `<tr><td>海拔</td><td>${p.ele} m</td></tr>` : ''}
          </table>
        </div>`)
      .addTo(map);
  });

  map.on('mouseenter', 'points', () => (map.getCanvas().style.cursor = 'pointer'));
  map.on('mouseleave', 'points', () => (map.getCanvas().style.cursor = ''));
});

// 从轨迹数据的 route 字段去重，生成开关
function buildRouteSwitches(routes) {
  const names = [...new Set(routes.features.map((f) => f.properties.route))];
  const list = document.getElementById('route-list');
  names.forEach((name) => {
    const label = document.createElement('label');
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.checked = true;
    cb.dataset.route = name;
    cb.addEventListener('change', () => {
      map.setLayoutProperty('routes', 'visibility', cb.checked ? 'visible' : 'none');
    });
    label.appendChild(cb);
    label.appendChild(document.createTextNode(name));
    list.appendChild(label);
  });
}
