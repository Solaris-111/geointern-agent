# RAG 知识库

此目录是 agent 的地学知识检索源。私有/版权数据**不随仓库分发**，已移到仓库外的私有目录：

```
D:\geointern-data-private\
├── references\rag\
│   ├── guidebook\      # 实习指导书 PDF（版权）
│   ├── page_images\    # 指导书逐页图（版权派生）
│   ├── index\          # PDF 派生索引（chunks.json 等）
│   ├── reports\        # 学生报告 PDF/md（隐私）
│   └── field-notes\    # 往年野簿（隐私）
├── temp_notebook_pages\  # 野簿照片（隐私）
├── 预制报告\             # 学生报告（隐私）
├── 野簿预稿\             # 含往年实测数据的预稿（隐私）
└── 周口店*.md            # 往年野簿（隐私）
```

## 目录结构

```
rag/
├── guidebook/     # 实习指导书 PDF（私有，需自行放入）
├── textbook/      # 教材 PDF（私有，需自行放入）
└── notes/         # 用户自己的笔记 (.md)
```

## 使用方式

要启用 RAG 检索，把私有数据从 `D:\geointern-data-private\` 拷回对应目录，或自行准备 PDF 放入 `guidebook/`、`textbook/`，再运行索引脚本生成 `index/`。

⚠️ 私有数据（版权 PDF、往年野簿、学生报告）**不要提交到公开仓库**。
