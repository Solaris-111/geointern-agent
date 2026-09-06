const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, AlignmentType,
} = require("docx");

// ---------- 图片数据（每天1张，共15张） ----------
const imgs = {
  emei: [
    { file: "image28", caption: "峨眉山 Day1 · 前往实习基地", w: 384, h: 289 },
    { file: "image27", caption: "峨眉山 Day2 · 清音电站—龙门硐电站（玄武岩柱状节理）", w: 269, h: 358 },
    { file: "image26", caption: "峨眉山 Day3 · 龙门硐电站—龙门硐口（峡谷溪流）", w: 269, h: 358 },
    { file: "image23", caption: "峨眉山 Day4 · 峨眉山景区（一线天栈道）", w: 269, h: 358 },
    { file: "image21", caption: "峨眉山 Day5 · 四溪沟（溶洞钟乳石）", w: 269, h: 358 },
    { file: "image20", caption: "峨眉山 Day6 · 川主庙—两河口（清晰露头）", w: 384, h: 289 },
    { file: "image17", caption: "峨眉山 Day7 · 自由活动（街头熟睡的小猫）", w: 269, h: 358 },
  ],
  zkd: [
    { file: "image16", caption: "周口店 Day1 · 八角寨垭口（岩层剖面）", w: 432, h: 194 },
    { file: "image13", caption: "周口店 Day2 · 黄院东山梁（陡崖）", w: 384, h: 289 },
    { file: "image9",  caption: "周口店 Day3 · 房山岩体（手持花岗岩标本）", w: 269, h: 358 },
    { file: "image8",  caption: "周口店 Day4 · 羊屎沟（红柱石角岩）", w: 269, h: 358 },
    { file: "image6",  caption: "周口店 Day5 · 太平山北坡（远眺）", w: 384, h: 289 },
    { file: "image4",  caption: "周口店 Day6 · 太平山南坡（陡坡）", w: 269, h: 358 },
    { file: "image3",  caption: "周口店 Day7 · 实测剖面（远眺层峦）", w: 384, h: 289 },
    { file: "image1",  caption: "周口店 Day8 · 自主填图（给流浪狗喂水）", w: 432, h: 194 },
  ],
};

// ---------- 辅助 ----------
const body = (text) => new Paragraph({
  spacing: { after: 160, line: 360 },
  indent: { firstLine: 480 },
  children: [new TextRun({ text, font: "SimSun", size: 24 })],
});

const caption = (text) => new Paragraph({
  spacing: { before: 40, after: 120 },
  alignment: AlignmentType.CENTER,
  children: [new TextRun({ text, font: "SimSun", size: 18, color: "808080" })],
});

const imgParagraph = (img) => {
  const data = fs.readFileSync(`temp_docx_media/${img.file}.png`);
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 80, after: 40 },
      children: [new ImageRun({
        type: "png",
        data,
        transformation: { width: img.w, height: img.h },
        altText: { title: img.caption, description: img.caption, name: img.caption },
      })],
    }),
    caption(img.caption),
  ];
};

const imgGroup = (list) => list.flatMap(imgParagraph);

// ---------- 文档内容 ----------
const children = [];

// 标题
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 240 },
  children: [new TextRun({ text: "翻山越岭的日子", font: "SimHei", size: 44, bold: true })],
}));

// 开篇
children.push(body("七月，我把课堂搬进了山里。"));

// 峨眉山 day1
children.push(body("峨眉山的第一个夜晚，是在与蚊虫蟑螂的搏斗中开始的。实习基地挨着度假区，远山如黛，近水含烟，本是避暑的好去处，只是宿舍里的“常住客”让人每夜不得安生。可天亮一出发，山风裹着草木的清气扑面而来，这些烦恼便抛在了脑后。"));
children.push(...imgGroup([imgs.emei[0]]));

// 峨眉山 day2-day3
children.push(body("第二天，从清音电站走到龙门硐电站，我第一次把课本上的“玄武岩柱状节理”认了出来——那些六边形的柱子，是岩浆冷凝时留下的指纹，成片立在路边，像谁把山体切成了竖琴。过桥时望见普贤船，听老师讲它的成因，才知一块石头也能有来历。路线清幽，河流尽头仿佛有人在洗衣服，村落、山泉、小桥，像走进一幅淡墨山水。"));
children.push(...imgGroup([imgs.emei[1], imgs.emei[2]]));

// 峨眉山 day4-day7
children.push(body("再往后，摩崖石刻、一线天、生态猴区，一路看过去。四溪沟里，财神洞是干洞，老君洞是湿洞，我们趴在洞口推想它们各自的成因。川主庙前的那片露头最是清晰，连不懂地质的路人也会驻足，感叹大自然的鬼斧神工。自由活动那天去了乐山，市区美食虽多，却都不是一个人能对付的分量，最后空腹而归，只在街头遇见一只熟睡的小猫，它蜷在石板路上，对来往的行人浑然不觉。"));
children.push(...imgGroup([imgs.emei[3], imgs.emei[4], imgs.emei[5], imgs.emei[6]]));

// 过渡
children.push(body("转到周口店，画风陡然硬朗起来。"));

// 周口店 day1-day4
children.push(body("头一天就下雨，没能出野外，在室内看视频，倒也收获不少。次日黄院东山梁，陡崖、攀岩、穿林、翻栅栏，采石场就在眼前，一身的泥点子成了当天的勋章。房山岩体那天，花岗岩、捕虏体、伟晶岩脉、球形风化，一个个名词落成了实物。"));
children.push(...imgGroup([imgs.zkd[0], imgs.zkd[1], imgs.zkd[2], imgs.zkd[3]]));

// 周口店 day5-day6
children.push(body("太平山北坡是最累的一天——海拔从不到百米爬到近三百米，全程穿林登崖，一刻不敢多停，因为林子里可能有虫有蛇。我们沿山脊翻过大砾岩山，穿过三个向斜、三个背斜，登上南极凹，回望时，整个北坡的全貌都在脚下。南坡两个陡坡更窄，只能容一人通过，有时得手脚并用，却能俯瞰来时蜿蜒的土路。"));
children.push(...imgGroup([imgs.zkd[4], imgs.zkd[5]]));

// 周口店 day7
children.push(body("实测剖面那天，又回到南坡。夕阳把余晖洒在泥土路上，映着山向阳的一面。平视右方，太阳正缓缓下沉，停在千里江山的尽头——温度刚刚好，不昏暗也不刺眼，落日与晚风，像在为我们送行。"));
children.push(...imgGroup([imgs.zkd[6]]));

// 周口店 day8
children.push(body("最后一天自主填图，一只大狗从山上跟到山下，又领我们回基地。下山时它浑身湿漉漉、吐着舌头，我们猜它渴了，便有人递上水。"));
children.push(...imgGroup([imgs.zkd[7]]));

// 结尾
children.push(body("十五个日出日落，我从把地质名词认成实物，走到能和一座山对望。那些泥泞、陡崖和汗，最后都化成了山风里一句轻轻的“原来如此”。"));

// ---------- 生成 ----------
const doc = new Document({
  styles: {
    default: { document: { run: { font: "SimSun", size: 24 } } },
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 }, // A4
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
      },
    },
    children,
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync("翻山越岭的日子.docx", buffer);
  console.log("生成成功: 翻山越岭的日子.docx");
});
