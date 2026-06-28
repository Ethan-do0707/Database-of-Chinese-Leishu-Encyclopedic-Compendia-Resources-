# 多识模型《白氏六帖》傅藏本 × 白居易诗歌互文计算结果（v5 注文类型口径）

本目录保存《白氏六帖事类集》（傅藏本）与白居易诗歌之间的“多识”向量互文计算结果。数据来自本地输出目录 `output_duoshi_fuzang_baijuyi_v5_note_type_35340`，采用 `note_type_aware_channels` 口径。

## 数据规模

- 类书记录：`35,340` 条
- 白居易规范化诗作：`2,804` 首
- 白居易句级单位：`32,941` 个
- 诗级矩阵：`35,340 × 2,804`
- 句级矩阵：`35,340 × 32,941`
- 向量维度：`1024`
- 矩阵 dtype：`float16`

## 方法说明

类书侧采用注文类型感知的多通道策略：

- `补足下文`：词条与解析注文合并为整体语义文本后编码。
- `对仗`：以解析注文作为主要语义通道。
- `解释文意`、`出处原文`：词条、注文、部类/部类附名三通道加权。
- `出处典籍`：抽取书名，与诗歌注释引书和共同典源作独立统计。
- `互见`：先解析 `見上注`、`並見上注`、`見某門/具某門` 等注文互见，再进入加权计算。

## 展示阈值与样本数

- 诗级展示阈值：`>= 0.6689`
- 句级展示阈值：`>= 0.7134`
- 诗级高相似样本：`451` 条
- 句级高相似样本：`6,154` 条
- 候选互文：`100` 组

## 目录内容

- `run_summary.json`、`matrix_metadata_*.json`：计算配置、矩阵形状、索引路径与模型信息。
- `row_index_白氏六帖.csv`、`column_index_白居易_*.csv`：矩阵行列索引。
- `白氏六帖_白居易_论文展示版.xlsx`：论文展示用高相似样本、候选互文、诗作统计和部类统计。
- `论文插图_多识_*.png/pdf/csv`：论文图表及其数据。
- `多识_傅藏本_结果分析报告.md` 与六份论文写作草稿：用于正文分析与方法反思。
- `排除共同典源后的*`：排除《初学记》《艺文类聚》共同典源后的排他性统计与代表样本。
- `白氏六帖_白居易_分主题类书部类分析报告.md`、`白氏六帖_白居易_分诗歌类型分析报告.md`：按部类主题和诗歌类型生成的专题报告。
- `large_files_manifest.json`：文件清单、Git LFS 大文件说明、句级完整矩阵分片信息。

## 大文件说明

GitHub 普通仓库不适合直接存放大型二进制文件；超过 100MiB 的文件会被阻止，超过 50MiB 的文件也会触发警告。因此，本目录中超过 50MiB 的矩阵、向量和大型 Excel 文件均按 Git LFS 处理。其中句级完整矩阵 `similarity_matrix_白氏六帖_x_白居易_line_float16.npy` 超过 2GiB，发布时拆分为 `large_file_parts/` 下的分片文件。

| 文件 | 大小 | 发布方式 |
| --- | ---: | --- |
| `similarity_matrix_白氏六帖_x_白居易_line_float16.npy` | 2.168 GiB | Git LFS；句级完整矩阵发布为 `large_file_parts/*.part*` 分片 |
| `similarity_matrix_白氏六帖_x_白居易_poem_float16.npy` | 189.0 MiB | Git LFS；句级完整矩阵发布为 `large_file_parts/*.part*` 分片 |
| `vec_baijuyi_line.npy` | 128.7 MiB | Git LFS；句级完整矩阵发布为 `large_file_parts/*.part*` 分片 |
| `vec_白氏六帖.npy` | 138.0 MiB | Git LFS；句级完整矩阵发布为 `large_file_parts/*.part*` 分片 |
| `vec_白氏六帖_category.npy` | 138.0 MiB | Git LFS；句级完整矩阵发布为 `large_file_parts/*.part*` 分片 |
| `vec_白氏六帖_headword.npy` | 138.0 MiB | Git LFS；句级完整矩阵发布为 `large_file_parts/*.part*` 分片 |
| `vec_白氏六帖_headword_note_combined.npy` | 138.0 MiB | Git LFS；句级完整矩阵发布为 `large_file_parts/*.part*` 分片 |
| `vec_白氏六帖_note.npy` | 138.0 MiB | Git LFS；句级完整矩阵发布为 `large_file_parts/*.part*` 分片 |
| `白氏六帖_白居易_句级Top20相似度表.xlsx` | 77.6 MiB | Git LFS；句级完整矩阵发布为 `large_file_parts/*.part*` 分片 |
| `白氏六帖_白居易_诗级完整相似度矩阵.xlsx` | 519.1 MiB | Git LFS；句级完整矩阵发布为 `large_file_parts/*.part*` 分片 |

如需在本地恢复句级完整矩阵，可在下载所有分片后按顺序合并：

```python
from pathlib import Path

target = Path("similarity_matrix_白氏六帖_x_白居易_line_float16.npy")
parts = sorted(Path("large_file_parts").glob("similarity_matrix_白氏六帖_x_白居易_line_float16.npy.part*"))
with target.open("wb") as out:
    for part in parts:
        with part.open("rb") as src:
            for chunk in iter(lambda: src.read(8 * 1024 * 1024), b""):
                out.write(chunk)
```

## 引用建议

若在论文或数据说明中引用本结果，建议注明：

> 本数据采用本地“多识”向量模型，对《白氏六帖事类集》（傅藏本）`35,340` 条类书记录与白居易 `2,804` 首诗、`32,941` 个句级单位进行余弦相似度计算，并在类书侧采用注文类型感知的多通道加权策略。

## 注意事项

- 本结果用于数字人文研究中的互文候选发现，不等同于自动判定直接取材关系。
- 涉及《初学记》《艺文类聚》共同典源的情况，应结合 `排除共同典源后的排他性统计.json` 与代表样本继续人工复核。
- SikuBERT 相关材料仅作为历史/模型参照，不应与本目录 v5 注文类型口径作绝对同口径比较。
