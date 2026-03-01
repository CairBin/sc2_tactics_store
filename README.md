

## 目录结构

```
sc2_tactics_store/
├── README.md               # 仓库说明、使用文档、贡献指南
├── index.json              # 全局主索引（核心！前端优先加载这个）
├── index_schema.json       # 索引文件的JSON Schema（校验索引格式）
├── store/                  # 战术文件主存储目录
│   ├── author_zhang/       # 上传者目录（示例：作者zhang）
│   │   ├── zvt_rush_2024.json    # 具体战术文件（ZvT rush 2024版本）
│   │   ├── pvp_defense.json      # 具体战术文件（PvP 防守战术）
│   │   └── author_index.json     # 该作者的本地索引（可选，辅助维护）
│   ├── author_li/          # 上传者目录（示例：作者li）
│   │   ├── tvp_mech.json         # 具体战术文件（TvP 机械化）
│   │   └── author_index.json     # 该作者的本地索引
│   └── author_wang/        # 更多上传者...
├── category/               # 按对战类型分类的索引（可选，前端可按需加载）
│   ├── pvp_index.json      # PvP 战术索引
│   ├── pvt_index.json      # PvT 战术索引
│   └── ...（其他对战类型）
└── version/                # 按适用版本分类的索引（可选，前端可按需加载）
    ├── 4.10_index.json     # 4.10版本适用的战术索引
    ├── 5.0_index.json      # 5.0版本适用的战术索引
    └── ...（其他版本）
```