const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "GeoIntern-Agent";
pres.title = "暑期专业实习每日记录";

// ---- 配色（Warm Terracotta 岩土系） ----
const C = {
  primary: "B85042",    // 陶土红棕
  primaryDark: "7A3429",// 深陶土
  sand: "E7E8D1",       // 沙色
  cream: "F7F3EA",      // 米白背景
  sage: "A7BEAE",       // 鼠尾草绿
  ink: "3A2E2A",        // 深棕文字
  gray: "8A7F7A",       // 灰
  white: "FFFFFF",
};

const FONT = "Microsoft YaHei";

// ---- 岩层装饰 motif：底部三条横线 ----
function strataFooter(slide) {
  const y = 7.08;
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y, w: 13.33, h: 0.07, fill: { color: C.primary } });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: y + 0.1, w: 13.33, h: 0.05, fill: { color: C.sage } });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: y + 0.18, w: 13.33, h: 0.24, fill: { color: C.sand } });
}

// ---- DAY 标签 chip ----
function dayChip(slide, label) {
  slide.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 0.6, w: 1.5, h: 0.5, fill: { color: C.primary } });
  slide.addText(label, { x: 0.6, y: 0.6, w: 1.5, h: 0.5, fontFace: FONT, fontSize: 15, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
}

const shadow = () => ({ type: "outer", color: "5A4A44", blur: 8, offset: 3, angle: 90, opacity: 0.22 });

// ===================== 数据 =====================
const days = [
  {
    label: "DAY 1", date: "2026年7月5日 · 峨眉山 路线一",
    route: "清音电站 → 龙门硐电站",
    img: "temp_ppt_assets/d1.jpg", ratio: 4 / 3, cap: "图1-1 玄武岩柱状节理素描",
    points: "玄武岩柱状节理 · 回龙山逆断层 · 牛背山背斜",
    record: "沿清音电站至龙门硐电站，观察峨眉山玄武岩的气孔、杏仁、微晶细晶结构及六边形柱状节理，识别回龙山走向逆断层、挖断山逆断层与牛背山背斜，实测产状两组、绘制素描四幅，区分杏仁状填充与斑晶。",
    feel: "第一次在野外把“柱状节理”从课本名词变成眼前的实物——岩浆冷凝收缩把玄武岩切成一根根六边形柱体。顺带纠正了一个误区：杏仁状填充是后期矿物充填气孔，不是斑晶。",
  },
  {
    label: "DAY 2", date: "2026年7月6日 · 峨眉山 路线二",
    route: "龙门硐电站 → 龙门硐口",
    img: "temp_ppt_assets/d2.jpg", ratio: 3 / 4, cap: "图2-1 砂岩交错层理素描",
    points: "地层界线 · 楔状交错层理 · 火焰构造 · 包卷层理",
    record: "龙门硐电站至龙门硐口，先后识别宣威组、东川组、飞仙关组、嘉陵江组、雷口坡组、须家河组六处地层界线，观察楔状交错层理、重荷模与火焰构造、包卷层理等沉积构造，并依据构造反推地层倒转。",
    feel: "沉积构造是会说话的记录：交错层理的收敛方向指示地层顶底，火焰构造和重荷模记录了软沉积物受挤压的瞬间。学会用它们反推地层是否倒转，比死记岩石名称有用得多。",
  },
  {
    label: "DAY 3", date: "2026年7月7日 · 峨眉山 路线三",
    route: "五显岗 → 清音阁 → 洪椿坪",
    img: "temp_ppt_assets/d3.jpg", ratio: 4 / 3, cap: "图3-1 路线示意图",
    points: "木鱼山向斜 · 万年寺断层 · 小峨眉山花岗岩",
    record: "五显岗经清音阁至洪椿坪，观察木鱼山向斜转折端及“向斜成山”的地形倒置现象，认识万年寺断层带内的构造透镜体与角砾岩，实测深切曲流节理，并识别8.5亿年前的小峨眉山花岗岩，共记录九个观察点。",
    feel: "木鱼山“向斜成山”颠覆了“向斜成谷”的直觉——核部岩层抗风化能力强，反而抬升成山。断层带里被压扁拉长的构造透镜体，让我第一次直观看到剪切变形留下的痕迹。",
  },
  {
    label: "DAY 4", date: "2026年7月8日 · 峨眉山 路线四",
    route: "四溪沟",
    img: "temp_ppt_assets/d4.jpg", ratio: 4 / 3, cap: "图4-1 钟乳石、石笋、石柱素描",
    points: "岩溶地貌 · 干溶洞/湿溶洞 · 裂隙下降泉",
    record: "四溪沟观察白云岩岩溶地貌，进财神洞看钟乳石、石笋、石柱，判断其因地下暗河被截断而成干溶洞；喷月泉看裂隙下降泉成因，老君洞辨湿溶洞，理解碳酸钙溶解—沉淀的化学平衡原理。",
    feel: "岩溶化学方程式 CaCO₃+H₂O+CO₂⇌Ca(HCO₃)₂ 终于有了实物对应。同一个溶洞，暗河有没有被断层截断，决定了它是“干”还是“湿”——地质作用环环相扣，缺一环结论就反了。",
  },
  {
    label: "DAY 5", date: "2026年7月22日 · 周口店 L06",
    route: "八角寨 → 拴马桩桥",
    img: "temp_ppt_assets/d5.jpg", ratio: 4 / 3, cap: "包心菜状叠层石（D0605）",
    points: "地层序列 · 燧石条带 · 叠层石 · 平行不整合",
    record: "八角寨至拴马桩桥，沿周张公路观察雾迷山组、洪水庄组、铁岭组、下马岭组、长龙山组完整地层序列，识别燧石条带与包心菜状叠层石，判断铁岭组与下马岭组间的平行不整合，记录七个点位、绘图三幅。",
    feel: "一整天串起了蓟县系到青白口系的地层演化，从白云岩、炭质板岩到石英砂岩，地层像翻书一样在眼前展开。叠层石的同心纹层记录了远古潮汐，铁质古风化壳则定格了一次地壳抬升——岩石真会“说话”。",
  },
];

// ===================== 封面 =====================
{
  const s = pres.addSlide();
  s.background = { color: C.primaryDark };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 13.33, h: 0.35, fill: { color: C.primary } });
  s.addText("暑期专业实习 · 每日记录", { x: 1, y: 2.2, w: 11.33, h: 1.1, fontFace: FONT, fontSize: 44, bold: true, color: C.white, align: "center", margin: 0 });
  s.addText("连续 14 天野外地质实习 · 峨眉山 + 周口店", { x: 1, y: 3.45, w: 11.33, h: 0.6, fontFace: FONT, fontSize: 20, color: C.sand, align: "center", margin: 0 });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.66, y: 4.35, w: 2.0, h: 0.04, fill: { color: C.sage } });
  s.addText([
    { text: "姓  名：________     ", options: { breakLine: false } },
    { text: "学  号：________", options: { breakLine: true } },
    { text: "学  院：________", options: {} },
  ], { x: 1, y: 5.2, w: 11.33, h: 1.0, fontFace: FONT, fontSize: 16, color: C.sand, align: "center", margin: 0 });
  strataFooter(s);
}

// ===================== 目录 =====================
{
  const s = pres.addSlide();
  s.background = { color: C.cream };
  dayChip(s, "总览");
  s.addText("实习日程总览", { x: 0.6, y: 1.25, w: 12, h: 0.7, fontFace: FONT, fontSize: 30, bold: true, color: C.ink, margin: 0 });

  const rows = [];
  const done = [
    ["Day 1", "7月5日", "峨眉山 路线一 清音电站→龙门硐电站", "✓ 已完成"],
    ["Day 2", "7月6日", "峨眉山 路线二 龙门硐电站→龙门硐口", "✓ 已完成"],
    ["Day 3", "7月7日", "峨眉山 路线三 五显岗→洪椿坪", "✓ 已完成"],
    ["Day 4", "7月8日", "峨眉山 路线四 四溪沟", "✓ 已完成"],
    ["Day 5", "7月22日", "周口店 L06 八角寨→拴马桩桥", "✓ 已完成"],
  ];
  for (let i = 6; i <= 14; i++) {
    rows.push([`Day ${i}`, "____", "（待补充）", "□ 待补"]);
  }
  const head = [
    { text: "天次", options: { fill: { color: C.primary }, color: C.white, bold: true, align: "center" } },
    { text: "日期", options: { fill: { color: C.primary }, color: C.white, bold: true, align: "center" } },
    { text: "路线 / 内容", options: { fill: { color: C.primary }, color: C.white, bold: true } },
    { text: "状态", options: { fill: { color: C.primary }, color: C.white, bold: true, align: "center" } },
  ];
  const body = [];
  done.forEach(d => body.push([
    { text: d[0], options: { bold: true, color: C.primary, align: "center" } },
    { text: d[1], options: { align: "center", color: C.ink } },
    { text: d[2], options: { color: C.ink } },
    { text: d[3], options: { align: "center", color: "5A7A3A", bold: true } },
  ]));
  rows.forEach(r => body.push([
    { text: r[0], options: { bold: true, color: C.gray, align: "center" } },
    { text: r[1], options: { align: "center", color: C.gray } },
    { text: r[2], options: { color: C.gray } },
    { text: r[3], options: { align: "center", color: C.gray } },
  ]));
  s.addTable([head, ...body], {
    x: 0.6, y: 2.1, w: 12.1, colW: [1.6, 1.9, 6.1, 2.5],
    fontFace: FONT, fontSize: 12, valign: "middle",
    border: { pt: 0.5, color: "D8CFC4" },
    rowH: 0.32,
  });
  strataFooter(s);
}

// ===================== 每天 2 页 =====================
days.forEach((d, idx) => {
  // ---- 照片页 ----
  {
    const s = pres.addSlide();
    s.background = { color: C.cream };
    dayChip(s, d.label);
    s.addText(d.date, { x: 0.6, y: 1.2, w: 12, h: 0.65, fontFace: FONT, fontSize: 26, bold: true, color: C.ink, margin: 0 });
    s.addText(d.route, { x: 0.6, y: 1.85, w: 12, h: 0.4, fontFace: FONT, fontSize: 15, color: C.gray, margin: 0 });

    const imgH = 4.15;
    const imgW = imgH * d.ratio;
    s.addImage({ path: d.img, x: 0.7, y: 2.5, w: imgW, h: imgH, sizing: { type: "contain", w: imgW, h: imgH }, shadow: shadow() });
    s.addText(d.cap, { x: 0.7, y: 2.5 + imgH + 0.08, w: imgW, h: 0.35, fontFace: FONT, fontSize: 11, italic: true, color: C.gray, align: "center", margin: 0 });

    // 右侧要点
    const rx = imgW + 1.1;
    const rw = 13.33 - rx - 0.7;
    s.addText("本日看点", { x: rx, y: 2.7, w: rw, h: 0.4, fontFace: FONT, fontSize: 15, bold: true, color: C.primary, margin: 0 });
    const pts = d.points.split(" · ");
    s.addText(pts.map((p, i) => ({ text: p, options: { bullet: { code: "2022", indent: 14 }, breakLine: i < pts.length - 1, color: C.ink } })),
      { x: rx, y: 3.2, w: rw, h: 2.6, fontFace: FONT, fontSize: 13, paraSpaceAfter: 8, margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: rx, y: 6.1, w: rw, h: 0.06, fill: { color: C.sage } });
    s.addText("当日 1 张代表性照片 · 50 字说明见下页", { x: rx, y: 6.2, w: rw, h: 0.35, fontFace: FONT, fontSize: 11, italic: true, color: C.gray, margin: 0 });
    strataFooter(s);
  }

  // ---- 说明 + 心得页 ----
  {
    const s = pres.addSlide();
    s.background = { color: C.cream };
    dayChip(s, d.label);
    s.addText(d.date + " · 当日记录与心得", { x: 0.6, y: 1.2, w: 12, h: 0.6, fontFace: FONT, fontSize: 24, bold: true, color: C.ink, margin: 0 });

    // 左：说明
    const cardW = 5.8, cardH = 4.2, cardY = 2.1;
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: cardY, w: cardW, h: cardH, fill: { color: C.white }, line: { color: C.sand, width: 1 }, shadow: shadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: cardY, w: 0.12, h: cardH, fill: { color: C.primary } });
    s.addText("当日记录（50字+）", { x: 0.9, y: cardY + 0.25, w: cardW - 0.5, h: 0.4, fontFace: FONT, fontSize: 15, bold: true, color: C.primary, margin: 0 });
    s.addText(d.record, { x: 0.9, y: cardY + 0.75, w: cardW - 0.6, h: cardH - 0.95, fontFace: FONT, fontSize: 13.5, color: C.ink, valign: "top", lineSpacingMultiple: 1.35, margin: 0 });

    // 右：心得
    const rx2 = 0.6 + cardW + 0.5;
    s.addShape(pres.shapes.RECTANGLE, { x: rx2, y: cardY, w: cardW, h: cardH, fill: { color: C.sand }, line: { color: "D8D0BC", width: 1 }, shadow: shadow() });
    s.addShape(pres.shapes.RECTANGLE, { x: rx2, y: cardY, w: 0.12, h: cardH, fill: { color: C.sage } });
    s.addText("实践心得 · 感悟", { x: rx2 + 0.3, y: cardY + 0.25, w: cardW - 0.5, h: 0.4, fontFace: FONT, fontSize: 15, bold: true, color: "4A6B4F", margin: 0 });
    s.addText(d.feel, { x: rx2 + 0.3, y: cardY + 0.75, w: cardW - 0.6, h: cardH - 0.95, fontFace: FONT, fontSize: 13.5, color: "3F3A32", valign: "top", lineSpacingMultiple: 1.35, margin: 0 });
    strataFooter(s);
  }
});

// ===================== 成果图集锦 1（剖面图） =====================
{
  const s = pres.addSlide();
  s.background = { color: C.cream };
  dayChip(s, "成果");
  s.addText("野外成果 · 信手剖面图", { x: 0.6, y: 1.2, w: 12, h: 0.6, fontFace: FONT, fontSize: 26, bold: true, color: C.ink, margin: 0 });
  const figs = [
    { p: "temp_ppt_assets/sec_L03.png", t: "L03 黄院东山梁 寒武系→奥陶系" },
    { p: "temp_ppt_assets/sec_L06.png", t: "L06 八角寨-拴马桩桥 中→新元古界" },
    { p: "temp_ppt_assets/sec_L04.png", t: "L04 太平山南坡 实测剖面" },
  ];
  const gw = 3.8, gh = 2.7, gy = 2.3, gap = 0.35, x0 = 0.6;
  figs.forEach((f, i) => {
    const x = x0 + i * (gw + gap);
    s.addShape(pres.shapes.RECTANGLE, { x, y: gy, w: gw, h: gh, fill: { color: C.white }, line: { color: C.sand, width: 1 } });
    s.addImage({ path: f.p, x: x + 0.1, y: gy + 0.1, w: gw - 0.2, h: gh - 0.2, sizing: { type: "contain", w: gw - 0.2, h: gh - 0.2 } });
    s.addText(f.t, { x, y: gy + gh + 0.12, w: gw, h: 0.4, fontFace: FONT, fontSize: 11, color: C.gray, align: "center", margin: 0 });
  });
  strataFooter(s);
}

// ===================== 成果图集锦 2（柱状图 + 素描） =====================
{
  const s = pres.addSlide();
  s.background = { color: C.cream };
  dayChip(s, "成果");
  s.addText("野外成果 · 柱状图与露头素描", { x: 0.6, y: 1.2, w: 12, h: 0.6, fontFace: FONT, fontSize: 26, bold: true, color: C.ink, margin: 0 });
  const items = [
    { p: "temp_ppt_assets/col_L04.png", t: "L04 地层柱状图", w: 1.6, h: 3.6 },
    { p: "temp_ppt_assets/sk1.png", t: "图6-1 燧石条带先后关系", w: 3.4, h: 3.6 },
    { p: "temp_ppt_assets/sk2.png", t: "图6-2 包心菜状叠层石", w: 3.4, h: 3.6 },
  ];
  const gap = 0.45, x0 = 2.0, gy = 2.35;
  let cx = x0;
  items.forEach((it) => {
    s.addShape(pres.shapes.RECTANGLE, { x: cx, y: gy, w: it.w, h: it.h, fill: { color: C.white }, line: { color: C.sand, width: 1 } });
    s.addImage({ path: it.p, x: cx + 0.08, y: gy + 0.08, w: it.w - 0.16, h: it.h - 0.16, sizing: { type: "contain", w: it.w - 0.16, h: it.h - 0.16 } });
    s.addText(it.t, { x: cx, y: gy + it.h + 0.1, w: it.w, h: 0.4, fontFace: FONT, fontSize: 11, color: C.gray, align: "center", margin: 0 });
    cx += it.w + gap;
  });
  strataFooter(s);
}

// ===================== 待补说明页 =====================
{
  const s = pres.addSlide();
  s.background = { color: C.cream };
  dayChip(s, "待补");
  s.addText("待补天数说明", { x: 0.6, y: 1.25, w: 12, h: 0.6, fontFace: FONT, fontSize: 28, bold: true, color: C.ink, margin: 0 });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 2.3, w: 12.1, h: 1.9, fill: { color: C.sand }, line: { color: "D8D0BC", width: 1 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 2.3, w: 0.12, h: 1.9, fill: { color: C.sage } });
  s.addText([
    { text: "Day 6 ~ Day 14 的记录待补充。", options: { bold: true, breakLine: true } },
    { text: "已完成 Day 1–5（峨眉山路线一~四 + 周口店 L06），其余 9 天的照片、50 字说明与心得将在后续整理后补入。", options: {} },
  ], { x: 1.0, y: 2.55, w: 11.3, h: 1.5, fontFace: FONT, fontSize: 15, color: "3F3A32", valign: "top", lineSpacingMultiple: 1.4, margin: 0 });

  s.addText([
    { text: "每日补录要素提醒：", options: { bold: true, breakLine: true } },
    { text: "① 至少 1 张当日代表性照片  ② 50 字以上当日说明  ③ 实践心得与感悟", options: { color: C.gray } },
  ], { x: 0.6, y: 4.6, w: 12, h: 0.9, fontFace: FONT, fontSize: 13, valign: "top", lineSpacingMultiple: 1.4, margin: 0 });
  strataFooter(s);
}

// ===================== 待补占位页 ×3 =====================
const pendingGroups = [
  ["Day 6", "Day 7", "Day 8"],
  ["Day 9", "Day 10", "Day 11"],
  ["Day 12", "Day 13", "Day 14"],
];
pendingGroups.forEach((grp, gi) => {
  const s = pres.addSlide();
  s.background = { color: C.cream };
  dayChip(s, "待补");
  s.addText(`待补占位（${grp[0]} ~ ${grp[grp.length - 1]}）`, { x: 0.6, y: 1.25, w: 12, h: 0.6, fontFace: FONT, fontSize: 26, bold: true, color: C.ink, margin: 0 });
  const cw = 3.9, chh = 3.6, cy = 2.4, gap = 0.25;
  grp.forEach((g, i) => {
    const x = 0.6 + i * (cw + gap);
    s.addShape(pres.shapes.RECTANGLE, { x, y: cy, w: cw, h: chh, fill: { color: "FFFFFF" }, line: { color: "D8CFC4", width: 1, dashType: "dash" } });
    s.addText(g, { x, y: cy + 1.1, w: cw, h: 0.5, fontFace: FONT, fontSize: 22, bold: true, color: C.gray, align: "center", margin: 0 });
    s.addText("照片 · 说明 · 心得\n（待补）", { x, y: cy + 1.7, w: cw, h: 0.8, fontFace: FONT, fontSize: 13, color: "B8ACA4", align: "center", lineSpacingMultiple: 1.3, margin: 0 });
  });
  strataFooter(s);
});

// ===================== 总结 =====================
{
  const s = pres.addSlide();
  s.background = { color: C.primaryDark };
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 13.33, h: 0.35, fill: { color: C.primary } });
  s.addText("实习小结", { x: 1, y: 0.9, w: 11.33, h: 0.7, fontFace: FONT, fontSize: 30, bold: true, color: C.white, margin: 0 });
  s.addText([
    { text: "两段实习，覆盖了岩浆岩、沉积岩、构造与岩溶四个方向：", options: { breakLine: true } },
    { text: "峨眉山四天，从玄武岩柱状节理、沉积构造、褶皱断层，一路看到岩溶地貌；", options: { breakLine: true } },
    { text: "周口店一天，沿一条公路串起蓟县系到青白口系完整地层序列。", options: {} },
  ], { x: 1, y: 1.9, w: 11.33, h: 2.2, fontFace: FONT, fontSize: 16, color: C.sand, valign: "top", lineSpacingMultiple: 1.5, margin: 0 });
  s.addShape(pres.shapes.RECTANGLE, { x: 1, y: 4.6, w: 11.33, h: 0.04, fill: { color: C.sage } });
  s.addText("把课堂上的名词，变成野外看得见、摸得着、能亲手测量的实物——这是本次实习最大的收获。", { x: 1, y: 4.9, w: 11.33, h: 0.8, fontFace: FONT, fontSize: 15, italic: true, color: C.sage, align: "center", margin: 0 });
  strataFooter(s);
}

// ===================== 结束页 =====================
{
  const s = pres.addSlide();
  s.background = { color: C.primaryDark };
  s.addText("谢谢观看", { x: 1, y: 2.7, w: 11.33, h: 1.0, fontFace: FONT, fontSize: 40, bold: true, color: C.white, align: "center", margin: 0 });
  s.addShape(pres.shapes.RECTANGLE, { x: 5.66, y: 3.95, w: 2.0, h: 0.04, fill: { color: C.sage } });
  s.addText("以学院为单位提交 · 附信息汇总表（附件2）", { x: 1, y: 4.3, w: 11.33, h: 0.5, fontFace: FONT, fontSize: 14, color: C.sand, align: "center", margin: 0 });
  strataFooter(s);
}

pres.writeFile({ fileName: "暑期专业实习每日记录.pptx" }).then(f => console.log("生成成功:", f));
