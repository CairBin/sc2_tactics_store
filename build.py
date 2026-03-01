import json
import os
import shutil
from pathlib import Path
from datetime import datetime

# ===================== 配置项 =====================
# 根目录相关
ROOT_DIR = Path(".")
STORE_DIR = ROOT_DIR / "store"
# 索引输出目录
CATEGORY_INDEX_DIR = ROOT_DIR / "category"
VERSION_INDEX_DIR = ROOT_DIR / "version"
# 全局索引文件
GLOBAL_INDEX_FILE = ROOT_DIR / "index.json"

# 合法值校验
ALLOWED_MATCHUPS = {"pvp", "pvt", "pvz", "zvt", "zvp", "zvz", "tvz", "tvp", "tvt"}  # 对战类型
ALLOWED_TACTIC_TYPES = {"Timeline", "Step"}  # 战术类型（对应LTacticEnum）

# ===================== 工具函数 =====================
def ensure_dir_exists(dir_path: Path):
    """确保目录存在，不存在则创建"""
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"创建目录：{dir_path}")

def clean_old_indexes():
    """清空旧的分类/版本索引（避免残留无效文件）"""
    # 清空category目录
    if CATEGORY_INDEX_DIR.exists():
        shutil.rmtree(CATEGORY_INDEX_DIR)
    # 清空version目录
    if VERSION_INDEX_DIR.exists():
        shutil.rmtree(VERSION_INDEX_DIR)

def get_tactic_basic_info(tactic_data: dict, tactic_file: Path) -> dict:
    """提取战术的基础索引信息（校验+格式化）"""
    # 1. 校验必填字段
    required_fields = [
        "Id", "Name", "Author", "Matchup", "ApplicableVersion",
        "TacticType", "TacVersion", "ModName", "ModVersion", "UpdateTime"
    ]
    for field in required_fields:
        if field not in tactic_data:
            raise ValueError(f"文件{tactic_file}缺失必填字段：{field}")
    
    # 2. 校验字段合法性
    matchup = tactic_data["Matchup"].lower()
    if matchup not in ALLOWED_MATCHUPS:
        raise ValueError(f"文件{tactic_file}的对战类型无效：{tactic_data['Matchup']}（仅允许：{ALLOWED_MATCHUPS}）")
    
    tactic_type = tactic_data["TacticType"]
    if tactic_type not in ALLOWED_TACTIC_TYPES:
        raise ValueError(f"文件{tactic_file}的战术类型无效：{tactic_type}（仅允许：{ALLOWED_TACTIC_TYPES}）")
    
    # 3. 提取并格式化索引字段
    return {
        "id": tactic_data["Id"],
        "name": tactic_data["Name"],
        "author": tactic_data["Author"],
        "matchup": matchup,
        "applicableVersion": tactic_data["ApplicableVersion"],
        "tacticType": tactic_type,
        "tacVersion": tactic_data["TacVersion"],
        "modName": tactic_data["ModName"],
        "modVersion": tactic_data["ModVersion"],
        "updateTime": tactic_data["UpdateTime"],
        "filePath": str(tactic_file).replace(os.sep, "/")  # 统一路径分隔符为/
    }

# ===================== 核心逻辑 =====================
def generate_all_indexes():
    """生成所有索引：全局+分类+版本"""
    # 1. 初始化准备
    clean_old_indexes()  # 清空旧索引
    ensure_dir_exists(CATEGORY_INDEX_DIR)
    ensure_dir_exists(VERSION_INDEX_DIR)
    
    # 2. 遍历store目录，收集所有战术的索引信息
    global_tactics = []  # 全局索引列表
    category_map = {}    # 分类索引映射：{matchup: [tactic_info, ...]}
    version_map = {}     # 版本索引映射：{version: [tactic_info, ...]}
    
    # 遍历所有上传者目录
    for author_dir in STORE_DIR.iterdir():
        if not author_dir.is_dir():
            continue
        
        # 遍历该作者的所有战术文件
        for tactic_file in author_dir.glob("*.json"):
            try:
                # 读取战术文件
                with open(tactic_file, "r", encoding="utf-8") as f:
                    tactic_data = json.load(f)
                
                # 提取基础索引信息（带校验）
                tactic_info = get_tactic_basic_info(tactic_data, tactic_file)
                global_tactics.append(tactic_info)
                
                # 3. 填充分类映射
                matchup = tactic_info["matchup"]
                if matchup not in category_map:
                    category_map[matchup] = []
                category_map[matchup].append(tactic_info)
                
                # 4. 填充版本映射
                version = tactic_info["applicableVersion"]
                if version not in version_map:
                    version_map[version] = []
                version_map[version].append(tactic_info)
                
            except Exception as e:
                print(f"⚠️ 处理文件{tactic_file}失败：{str(e)}")
                continue
    
    # 5. 生成全局索引文件
    global_index = {
        "meta": {
            "version": "1.0",
            "updateTime": datetime.now().isoformat(),
            "totalTactics": len(global_tactics)
        },
        "tactics": global_tactics
    }
    with open(GLOBAL_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(global_index, f, ensure_ascii=False, indent=2)
    print(f"✅ 全局索引已生成：{GLOBAL_INDEX_FILE}（共{len(global_tactics)}个战术）")
    
    # 6. 生成分类索引文件
    for matchup, tactics in category_map.items():
        category_index_file = CATEGORY_INDEX_DIR / f"{matchup}_index.json"
        category_index = {
            "meta": {
                "category": matchup,
                "updateTime": datetime.now().isoformat(),
                "totalTactics": len(tactics)
            },
            "tactics": tactics
        }
        with open(category_index_file, "w", encoding="utf-8") as f:
            json.dump(category_index, f, ensure_ascii=False, indent=2)
        print(f"✅ 分类索引已生成：{category_index_file}（共{len(tactics)}个战术）")
    
    # 7. 生成版本索引文件
    for version, tactics in version_map.items():
        # 版本名处理（避免特殊字符，如4.10 -> 4.10_index.json）
        version_safe = version.replace(".", "_").replace(" ", "_")  # 替换点/空格为下划线
        version_index_file = VERSION_INDEX_DIR / f"{version_safe}_index.json"
        version_index = {
            "meta": {
                "version": version,
                "updateTime": datetime.now().isoformat(),
                "totalTactics": len(tactics)
            },
            "tactics": tactics
        }
        with open(version_index_file, "w", encoding="utf-8") as f:
            json.dump(version_index, f, ensure_ascii=False, indent=2)
        print(f"✅ 版本索引已生成：{version_index_file}（共{len(tactics)}个战术）")

# ===================== 执行入口 =====================
if __name__ == "__main__":
    # 检查store目录是否存在
    if not STORE_DIR.exists():
        print(f"❌ 错误：{STORE_DIR} 目录不存在，请先创建并放入战术文件！")
    else:
        generate_all_indexes()
        print("\n🎉 所有索引生成完成！")