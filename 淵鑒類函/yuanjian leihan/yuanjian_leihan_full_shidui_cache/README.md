# 渊鉴类函全文诗对缓存库

本仓库是“古典诗词典故工具”中的《渊鉴类函》结构化缓存数据集，面向典故检索、诗对联想、古籍文本分析与二次开发场景。

当前目录以数据文件为主，不包含完整应用入口代码；核心内容为按页切分的 `JSON` 分片，每个文件都保留了页面分类、正文摘录与词目分组信息，适合直接被脚本、服务端程序或检索系统读取。为避免 GitHub 单目录显示截断，当前发布版本已将数据分散到多个编号子目录中。

## 仓库简介

一句话简介：

> 《渊鉴类函》结构化缓存数据仓，适用于古典诗词用典检索、诗对联想、古籍语料构建与数字人文研究。

如果你需要直接复制到 GitHub 仓库设置页，可参考 [REPO_DESCRIPTION.md](./REPO_DESCRIPTION.md) 中提供的精简版、标准版简介与推荐标签。

## 项目特点

- 一页一文件，结构清晰，便于批量处理与增量构建。
- 按编号分目录存放，便于在 GitHub 页面中完整浏览。
- 同时提供正文摘录与 `groups` 词目分组，适合典故匹配与诗对推荐。
- 全部文件使用 UTF-8 编码，适合跨平台读取与 GitHub 托管。

## 数据规模

| 项目 | 数值 |
| --- | ---: |
| JSON 文件数量 | 2743 |
| 正文条目总数 `explain_rows` | 27500 |
| 词目分组总数 `groups` | 34772 |
| 含 `groups` 的文件数 | 1095 |
| 数据总大小 | 约 30.08 MB |
| 文件编号范围 | `0000.json` - `2742.json` |

示例起始页：

- `0000-0999/0000.json`：目錄 / 序，提要
- `0000-0999/0001.json`：目錄 / 凡例
- `0000-0999/0002.json`：天 / 天

## 仓库结构

```text
.
├── 0000-0999/
│   ├── 0000.json
│   ├── 0001.json
│   ├── ...
│   └── 0999.json
├── 1000-1999/
│   ├── 1000.json
│   ├── 1001.json
│   ├── ...
│   └── 1999.json
├── 2000-2742/
│   ├── 2000.json
│   ├── 2001.json
│   ├── ...
│   └── 2742.json
├── LICENSE
├── README.md
└── REPO_DESCRIPTION.md
```

文件名使用零填充编号，数据按编号区间拆分到子目录中，既保留顺序扫描特性，也能避免 GitHub 对超大单目录的列表截断。

## 数据格式

每个 `JSON` 文件的基础结构如下：

```json
{
  "page": {
    "section_bu": "帝王",
    "section_lei": "帝王总载",
    "category_path": "帝王/帝王总载"
  },
  "explain_rows": [
    {
      "section": "帝王总载一",
      "text": "增易乾大象曰夫大人者与天地合其德..."
    }
  ],
  "groups": [
    {
      "section": "帝王总载三",
      "source_label": "原",
      "terms": ["牺轩", "炎昊"],
      "comment": "并详总载二"
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `page.section_bu` | `string` | 部类名称，如“天”“帝王”“蟲豸” |
| `page.section_lei` | `string` | 细分类名称 |
| `page.category_path` | `string` | 由部类与分类拼接出的路径 |
| `explain_rows` | `array` | 页面正文摘录列表 |
| `explain_rows[].section` | `string` | 所属小节名 |
| `explain_rows[].text` | `string` | 古籍正文或整理后的连续文本 |
| `groups` | `array` | 从页面中整理出的词目、典故或对仗分组 |
| `groups[].source_label` | `string` | 条目标记，如“原”“增” |
| `groups[].terms` | `array` | 词目列表，可用于联想、匹配、索引 |
| `groups[].comment` | `string` | 对词目出处或语义的补充说明 |

## 快速开始

### Python 读取示例

```python
import json
from pathlib import Path

root = Path(".")
data = json.loads((root / "0000-0999" / "0152.json").read_text(encoding="utf-8"))

print(data["page"]["category_path"])
print(data["explain_rows"][0]["section"])
print(data["explain_rows"][0]["text"][:60])

if data["groups"]:
    print(data["groups"][0]["terms"])
    print(data["groups"][0]["comment"])
```

### Node.js 读取示例

```javascript
const fs = require("fs");
const path = require("path");

const raw = fs.readFileSync(path.join("0000-0999", "0152.json"), "utf8");
const data = JSON.parse(raw);

console.log(data.page.category_path);
console.log(data.explain_rows[0].section);
console.log(data.explain_rows[0].text.slice(0, 60));

if (data.groups.length > 0) {
  console.log(data.groups[0].terms);
  console.log(data.groups[0].comment);
}
```

## 适用场景

- 古典诗词创作中的典故检索与用典扩展
- 对仗词组、诗对素材与相关条目联想
- 古籍文本结构化整理与语料构建
- 搜索引擎、知识库、问答系统的数据底座
- 数字人文研究中的分类统计与文本分析

## 分目录规则

- `0000-0999`：收录 `0000.json` 到 `0999.json`
- `1000-1999`：收录 `1000.json` 到 `1999.json`
- `2000-2742`：收录 `2000.json` 到 `2742.json`
- 根目录仅保留说明文档与许可证文件

如果你需要批量处理全部数据，建议使用递归方式遍历所有子目录中的 `json` 文件。

## 数据来源与说明

- 当前发布版本已移除所有 `source_url` 字段，不再在数据文件内附带外部页面链接。
- 数据内容保留古籍文本风格，可能包含异体字、古字形、繁简并存与无现代标点现象。
- `groups` 更适合用于词目联想、典故提示与检索增强；如需严格校勘，请结合来源页面或原始古籍再次核对。
- 本仓库对第三方来源内容不作超出法定范围的额外授权，具体使用边界请参见 [LICENSE](./LICENSE)。
- 本仓库更适合作为“结构化缓存数据仓”发布，而不是独立应用程序仓库。

## 发布建议

如果你准备将本目录作为独立 GitHub 仓库公开发布，建议同时补充以下内容：

- 仓库简介：可直接使用 [REPO_DESCRIPTION.md](./REPO_DESCRIPTION.md) 中的文案。
- 仓库标签与简介：突出“古籍数据集 / 典故检索 / 诗对语料”等关键词。
- Release 说明：记录数据来源、生成时间、字段变更与兼容性说明。

## 许可证

本仓库已附带 [LICENSE](./LICENSE)。发布、转载、镜像或二次分发前，建议先通读其关于“仓库整理成果”和“第三方来源内容”的边界说明。
