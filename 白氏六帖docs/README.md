# 白孔六帖_结构化.json 说明文档 / Documentation

## 1. 文件简介 / Overview

`白孔六帖_结构化.json` 是《白孔六帖》资料的结构化整理结果。  
`白孔六帖_结构化.json` is a structured dataset derived from the materials of *Bai-Kong Liutie*.

文件顶层为 JSON 数组，数组中的每个对象代表一条独立词条记录，适合用于检索、统计分析、部类研究，以及与其他古籍或诗文语料进行对照。  
The top-level structure is a JSON array. Each object in the array represents one independent entry, making the file suitable for retrieval, statistical analysis, category-based research, and comparison with other classical texts or poetry corpora.

## 2. 数据概况 / Dataset Summary

- 文件名 / Filename: `白孔六帖_结构化.json`
- 编码 / Encoding: `UTF-8`
- 顶层结构 / Top-level structure: `List[Object]`
- 记录总数 / Total records: `55,823`
- 唯一卷名数 / Unique volume labels: `96`
- 唯一部类数 / Unique category labels: `1,370`
- 作者字段取值 / Values in `作者`: `白` = `55,190`，`孔` = `633`
- `部类附名` 非空记录 / Non-empty `部类附名`: `18,463`
- `注文` 非空记录 / Non-empty `注文`: `50,297`

说明 / Notes:

- 卷名范围覆盖卷`一`至卷`一百`，但当前数据中缺少卷`五`、卷`二十四`、卷`八十一`、卷`八十二`。  
  Volume labels range from `一` to `一百`, but the current dataset does not contain volumes `五`, `二十四`, `八十一`, and `八十二`.
- `作者` 字段目前仅见 `白` 与 `孔` 两种取值，可作为区分不同来源层次的重要标记；如需进一步学术解释，建议结合原始整理规则再作界定。  
  The `作者` field currently contains only two values, `白` and `孔`. These can be used as important markers for distinguishing source layers, but any stricter scholarly interpretation should still be checked against the original curation rules.

## 3. 字段结构 / Schema

每条记录包含以下字段：  
Each record contains the following fields:

| 字段名 / Field | 类型 / Type | 中文说明 | English Description | 示例 / Example |
| --- | --- | --- | --- | --- |
| `卷` | `string` | 卷次，使用中文数字表示 | Volume number written in Chinese numerals | `一` |
| `部类` | `string` | 词条所属主部类 | Main category of the entry | `天` |
| `部类序号` | `string` | 该部类在当前卷中的序号，使用中文数字表示 | Category sequence number within the volume, written in Chinese numerals | `一` |
| `部类附名` | `string \| null` | 对部类的补充说明、附属名目或细分标签 | Supplementary category label, attached title, or subcategory tag | `地理土附` |
| `作者` | `string` | 当前记录的来源标记，目前见 `白`、`孔` | Source marker of the record, currently `白` or `孔` | `白` |
| `词条` | `string` | 结构化后的核心词条或摘句 | Core entry term or extracted phrase | `天尊` |
| `注文` | `string \| null` | 与词条对应的注文、释文或续句 | Annotation, gloss, or continuation attached to the entry | `地卑` |

## 4. 数据示例 / Example Records

```json
{
  "卷": "一",
  "部类": "天",
  "部类序号": "一",
  "部类附名": null,
  "作者": "白",
  "词条": "天尊",
  "注文": "地卑"
}
```

带有 `部类附名` 的记录示例：  
Example of a record with a non-empty `部类附名`:

```json
{
  "卷": "一",
  "部类": "地",
  "部类序号": "二",
  "部类附名": "地理土附",
  "作者": "白",
  "词条": "地卑",
  "注文": null
}
```

## 5. 使用建议 / Usage Notes

- 读取时请显式指定 `UTF-8` 编码，避免中文或异体字显示异常。  
  Always read the file with explicit `UTF-8` encoding to avoid garbled Chinese text or variant character display issues.
- `卷` 与 `部类序号` 均使用中文数字；若要进行排序、分卷统计或可视化，建议先转换为阿拉伯数字字段。  
  Both `卷` and `部类序号` are stored in Chinese numerals. For sorting, aggregation, or visualization, it is recommended to convert them into Arabic numerals first.
- `部类附名` 与 `注文` 存在 `null` 或空值，处理时应做好缺失值判断。  
  `部类附名` and `注文` may contain `null` or empty values, so missing-value handling should be included in downstream processing.
- 卷号并非连续齐备，不能默认按 `1` 到 `100` 完整展开。  
  Volume numbering is not fully continuous, so do not assume a complete sequence from `1` to `100`.
- 文本中保留了部分古籍常见字形或异体字，如 `髙`、`隂`、`黙` 等；若要进行现代汉字归一化，建议保留原文字段，另建标准化字段，避免覆盖原始信息。  
  The dataset preserves some traditional or variant character forms common in classical sources, such as `髙`, `隂`, and `黙`. If modern normalization is needed, keep the original text and create separate normalized fields instead of overwriting the source text.

## 6. Python 读取示例 / Python Example

```python
import json
from pathlib import Path

path = Path("白孔六帖_结构化.json")

with path.open("r", encoding="utf-8") as f:
    data = json.load(f)

print(f"记录总数 / Total records: {len(data)}")
print(data[0])
```

如需按部类或作者筛选，可进一步写成：  
To filter by category or source marker, you can further write:

```python
filtered = [
    item for item in data
    if item["部类"] == "酒" and item["作者"] == "白"
]
```

## 7. 适用场景 / Use Cases

本文件尤其适合以下用途：  
This dataset is especially suitable for the following uses:

- 《白孔六帖》的部类分布统计 / Category distribution analysis of *Bai-Kong Liutie*
- 白、孔两类材料的比较研究 / Comparative study of `白` and `孔` materials
- 与《白香山诗集》或其他古籍语料的互文检索 / Intertextual retrieval against *Bai Xiangshan Shiji* or other classical corpora
- 词条级别的知识组织、标签分析与可视化 / Entry-level knowledge organization, tag analysis, and visualization

如后续对该 JSON 做增补、清洗或归一化，建议在保留原始文件的基础上另存新版本，以便追溯处理过程。  
If the JSON is later expanded, cleaned, or normalized, it is recommended to save a new version while preserving the original file for traceability.
