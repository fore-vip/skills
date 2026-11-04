#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sim-life · 人生样本抽样器

分层加权抽样：区域 -> 国家 -> 城乡 -> 家庭阶层 -> 姓名/性格/天赋
权重为近似口径，用于叙事多样性，不作为统计引用。

用法:
  python3 sample_life.py                      # 随机种子
  python3 sample_life.py --seed 42            # 可复现
  python3 sample_life.py --country CN --birth-year 1975
  python3 sample_life.py --age-max 80         # 放开年龄上限（默认 0-40，保证可玩轮次）
"""

import argparse
import json
import random
import secrets
import sys
import unicodedata
from datetime import datetime

# ---------------------------------------------------------------- 国家数据表
# (代称, 人口权重%, 预期寿命, 城市化率, 收入档 H/UM/LM/L, 文化圈, 地名样本)
COUNTRIES = [
    ("CN", "中国", 18.2, 78.6, 0.66, "UM", "east_asia",
     ["四川 绵阳", "河南 周口", "广东 湛江", "浙江 温州", "陕西 汉中",
      "黑龙江 齐齐哈尔", "山东 临沂", "湖南 邵阳", "福建 莆田", "云南 曲靖"]),
    ("IN", "印度", 18.0, 70.1, 0.36, "LM", "south_asia",
     ["北方邦 坎普尔", "比哈尔 巴特那", "马哈拉施特拉 纳格浦尔",
      "泰米尔纳德 马杜赖", "西孟加拉 阿桑索尔", "喀拉拉 特里凡得琅"]),
    ("US", "美国", 4.25, 78.4, 0.83, "H", "anglo",
     ["得州 拉伯克", "俄亥俄 代顿", "加州 弗雷斯诺", "纽约州 布法罗",
      "密西西比 杰克逊", "华盛顿州 塔科马"]),
    ("ID", "印度尼西亚", 3.50, 68.3, 0.58, "LM", "southeast_asia",
     ["东爪哇 泗水外围", "中爪哇 梭罗", "北苏门答腊 棉兰", "南苏拉威西 望加锡"]),
    ("PK", "巴基斯坦", 3.10, 66.4, 0.38, "LM", "south_asia",
     ["旁遮普 木尔坦", "信德 海得拉巴", "开伯尔 白沙瓦"]),
    ("NG", "尼日利亚", 2.85, 54.5, 0.54, "LM", "africa",
     ["拉各斯 伊凯贾", "卡诺 卡诺", "河流州 哈科特港"]),
    ("BR", "巴西", 2.65, 75.9, 0.87, "UM", "latin",
     ["圣保罗 瓜鲁柳斯", "巴伊亚 萨尔瓦多", "米纳斯 贝洛奥里藏特"]),
    ("BD", "孟加拉国", 2.15, 73.7, 0.40, "LM", "south_asia",
     ["达卡 纳拉扬甘杰", "吉大港 科克斯巴扎尔"]),
    ("RU", "俄罗斯", 1.80, 73.2, 0.75, "UM", "slavic",
     ["莫斯科州 波多利斯克", "新西伯利亚 伊斯基季姆", "罗斯托夫 塔甘罗格"]),
    ("ET", "埃塞俄比亚", 1.60, 65.6, 0.23, "L", "africa",
     ["奥罗米亚 阿达玛", "阿姆哈拉 贡德尔"]),
    ("MX", "墨西哥", 1.60, 75.1, 0.81, "UM", "latin",
     ["哈利斯科 特拉克帕克", "墨西哥州 内萨瓦尔科约特尔", "恰帕斯 圣克里斯托瓦尔"]),
    ("JP", "日本", 1.55, 84.5, 0.92, "H", "east_asia",
     ["大阪 堺", "爱知 丰田", "北海道 旭川", "福冈 北九州"]),
    ("PH", "菲律宾", 1.45, 69.8, 0.48, "LM", "southeast_asia",
     ["甲米地 巴科奥", "宿务 曼达维", "棉兰老 达沃"]),
    ("EG", "埃及", 1.40, 70.2, 0.43, "LM", "arab",
     ["吉萨 十月六日城", "上埃及 索哈杰"]),
    ("CD", "刚果（金）", 1.30, 62.4, 0.47, "L", "africa",
     ["金沙萨 马西纳", "上加丹加 利卡西"]),
    ("VN", "越南", 1.25, 74.6, 0.39, "LM", "southeast_asia",
     ["河内 河东", "胡志明 平政", "义安 荣市"]),
    ("IR", "伊朗", 1.10, 74.6, 0.77, "LM", "arab",
     ["德黑兰 卡拉季", "伊斯法罕 霍梅尼沙赫尔"]),
    ("TR", "土耳其", 1.07, 76.0, 0.77, "UM", "arab",
     ["伊斯坦布尔 于斯屈达尔", "安纳托利亚 科尼亚"]),
    ("DE", "德国", 1.05, 81.4, 0.78, "H", "west_europe",
     ["北威 多特蒙德", "萨克森 开姆尼茨"]),
    ("TH", "泰国", 0.89, 76.4, 0.53, "UM", "southeast_asia",
     ["曼谷 暖武里", "依善 孔敬"]),
    ("GB", "英国", 0.86, 81.3, 0.84, "H", "anglo",
     ["曼彻斯特 索尔福德", "威尔士 斯旺西"]),
    ("FR", "法国", 0.85, 83.0, 0.81, "H", "west_europe",
     ["马赛 欧巴涅", "上法兰西 鲁贝"]),
    ("TZ", "坦桑尼亚", 0.85, 66.9, 0.37, "LM", "africa",
     ["达累斯萨拉姆 基农多尼", "姆万扎"]),
    ("ZA", "南非", 0.78, 62.3, 0.68, "UM", "africa",
     ["豪登 索韦托", "东开普 姆丹察内"]),
    ("IT", "意大利", 0.74, 83.5, 0.71, "H", "west_europe",
     ["那不勒斯 卡索里亚", "西西里 卡塔尼亚"]),
    ("KE", "肯尼亚", 0.70, 63.6, 0.29, "LM", "africa",
     ["内罗毕 基贝拉", "基苏木"]),
    ("MM", "缅甸", 0.68, 66.1, 0.32, "LM", "southeast_asia",
     ["仰光 莱达雅", "曼德勒 敏建"]),
    ("CO", "哥伦比亚", 0.66, 77.7, 0.82, "UM", "latin",
     ["波哥大 苏巴", "安蒂奥基亚 麦德林"]),
    ("KR", "韩国", 0.65, 83.5, 0.81, "H", "east_asia",
     ["釜山 沙上", "大邱 达西"]),
    ("UG", "乌干达", 0.62, 63.4, 0.26, "L", "africa",
     ["坎帕拉 卡文佩", "古卢"]),
    ("ES", "西班牙", 0.60, 83.7, 0.81, "H", "west_europe",
     ["安达卢西亚 塞维利亚郊区", "马德里 帕尔拉"]),
    ("SD", "苏丹", 0.60, 66.3, 0.36, "L", "africa",
     ["喀土穆 恩图曼", "达尔富尔 法希尔"]),
    ("DZ", "阿尔及利亚", 0.58, 77.1, 0.75, "LM", "arab",
     ["阿尔及尔 巴布祖瓦尔", "奥兰"]),
    ("AR", "阿根廷", 0.57, 76.6, 0.92, "UM", "latin",
     ["布宜诺斯艾利斯 拉马坦萨", "科尔多瓦"]),
    ("IQ", "伊拉克", 0.57, 70.4, 0.71, "LM", "arab",
     ["巴格达 萨德尔城", "摩苏尔"]),
    ("AF", "阿富汗", 0.53, 62.9, 0.26, "L", "south_asia",
     ["喀布尔 帕格曼", "坎大哈"]),
    ("CA", "加拿大", 0.49, 82.1, 0.82, "H", "anglo",
     ["安大略 汉密尔顿", "魁北克 拉瓦尔"]),
    ("MA", "摩洛哥", 0.47, 74.8, 0.65, "LM", "arab",
     ["卡萨布兰卡 西迪伯努尔", "非斯"]),
    ("PL", "波兰", 0.46, 77.0, 0.60, "UM", "slavic",
     ["西里西亚 扎布热", "马佐夫舍 拉多姆"]),
    ("AO", "安哥拉", 0.46, 62.1, 0.68, "LM", "africa",
     ["罗安达 卡夸科", "本格拉"]),
    ("UZ", "乌兹别克斯坦", 0.45, 72.0, 0.50, "LM", "slavic",
     ["塔什干 奇兰扎尔", "撒马尔罕"]),
    ("UA", "乌克兰", 0.45, 71.0, 0.70, "LM", "slavic",
     ["哈尔科夫 罗根", "利沃夫"]),
    ("MY", "马来西亚", 0.43, 75.0, 0.78, "UM", "southeast_asia",
     ["雪兰莪 巴生", "沙巴 亚庇"]),
    ("PE", "秘鲁", 0.43, 77.0, 0.79, "UM", "latin",
     ["利马 圣胡安德卢里甘乔", "库斯科"]),
    ("SA", "沙特阿拉伯", 0.42, 78.7, 0.85, "H", "arab",
     ["利雅得 南部区", "吉达"]),
    ("MZ", "莫桑比克", 0.42, 63.1, 0.38, "L", "africa",
     ["马普托 马托拉", "楠普拉"]),
    ("GH", "加纳", 0.42, 64.1, 0.59, "LM", "africa",
     ["阿克拉 阿善提", "库马西"]),
    ("YE", "也门", 0.42, 66.0, 0.39, "L", "arab",
     ["萨那", "塔伊兹"]),
    ("NP", "尼泊尔", 0.37, 70.4, 0.22, "LM", "south_asia",
     ["加德满都 拉利特普尔", "特莱 比尔根杰"]),
    ("VE", "委内瑞拉", 0.35, 72.5, 0.88, "LM", "latin",
     ["加拉加斯 佩塔雷", "苏利亚 马拉开波"]),
    ("AU", "澳大利亚", 0.33, 83.2, 0.86, "H", "anglo",
     ["新南威尔士 纽卡斯尔", "昆士兰 洛根"]),
    ("KP", "朝鲜", 0.33, 73.6, 0.63, "L", "east_asia",
     ["平壤 万景台", "咸兴"]),
    ("NG2", "", 0.0, 0, 0, "", "", []),  # 占位，保持表结构对齐
    ("TW", "中国台湾", 0.29, 80.9, 0.80, "H", "east_asia",
     ["台北 新北", "高雄 凤山"]),
    ("SY", "叙利亚", 0.29, 72.1, 0.57, "L", "arab",
     ["大马士革 杜马", "阿勒颇"]),
    ("ML", "马里", 0.29, 60.5, 0.45, "L", "africa",
     ["巴马科 卡蒂", "塞古"]),
    ("LK", "斯里兰卡", 0.28, 76.6, 0.19, "LM", "south_asia",
     ["科伦坡 芒特拉维利亚", "康提"]),
    ("BF", "布基纳法索", 0.28, 60.4, 0.32, "L", "africa",
     ["瓦加杜古", "博博迪乌拉索"]),
    ("MW", "马拉维", 0.26, 62.9, 0.18, "L", "africa",
     ["利隆圭", "布兰太尔"]),
    ("ZM", "赞比亚", 0.26, 62.4, 0.46, "LM", "africa",
     ["卢萨卡 卡布韦", "铜带省"]),
    ("KZ", "哈萨克斯坦", 0.25, 74.4, 0.58, "UM", "slavic",
     ["阿拉木图 塔尔迪库尔干", "奇姆肯特"]),
    ("CL", "智利", 0.25, 80.7, 0.88, "UM", "latin",
     ["圣地亚哥 迈普", "瓦尔帕莱索"]),
    ("RO", "罗马尼亚", 0.24, 75.6, 0.55, "UM", "slavic",
     ["布加勒斯特 第 6 区", "巴克乌"]),
    ("EC", "厄瓜多尔", 0.23, 77.0, 0.65, "UM", "latin",
     ["瓜亚基尔 杜兰", "基多"]),
    ("GT", "危地马拉", 0.22, 72.2, 0.53, "UM", "latin",
     ["危地马拉城 米斯科", "克萨尔特南戈"]),
    ("SN", "塞内加尔", 0.22, 68.6, 0.49, "LM", "africa",
     ["达喀尔 皮金", "捷斯"]),
    ("NL", "荷兰", 0.22, 82.0, 0.93, "H", "west_europe",
     ["鹿特丹 斯希丹", "北布拉班特 蒂尔堡"]),
    ("KH", "柬埔寨", 0.21, 70.1, 0.25, "LM", "southeast_asia",
     ["金边 森速", "暹粒"]),
    ("ZW", "津巴布韦", 0.20, 62.8, 0.32, "LM", "africa",
     ["哈拉雷 奇通圭扎", "布拉瓦约"]),
    ("TN", "突尼斯", 0.15, 76.5, 0.70, "LM", "arab",
     ["突尼斯市", "斯法克斯"]),
    ("BE", "比利时", 0.15, 81.9, 0.98, "H", "west_europe",
     ["布鲁塞尔 莫伦贝克", "安特卫普"]),
    ("SE", "瑞典", 0.13, 83.1, 0.88, "H", "west_europe",
     ["斯德哥尔摩 伦比", "哥德堡"]),
    ("PT", "葡萄牙", 0.13, 81.4, 0.67, "H", "west_europe",
     ["里斯本 阿马多拉", "波尔图"]),
    ("AE", "阿联酋", 0.13, 79.2, 0.87, "H", "arab",
     ["迪拜 德拉", "沙迦"]),
    ("IL", "以色列", 0.12, 82.7, 0.93, "H", "arab",
     ["特拉维夫 巴特亚姆", "海法"]),
    ("HU", "匈牙利", 0.12, 75.2, 0.73, "H", "slavic",
     ["布达佩斯 第 8 区", "德布勒森"]),
    ("RS", "塞尔维亚", 0.08, 74.9, 0.57, "UM", "slavic",
     ["贝尔格莱德 泽蒙", "诺维萨德"]),
]

COUNTRIES = [c for c in COUNTRIES if c[1]]

# 阶层权重：贫困 / 温饱 / 工薪 / 中产 / 富裕
CLASS_W = {
    "H":  [6, 12, 26, 40, 16],
    "UM": [12, 22, 32, 28, 6],
    "LM": [24, 30, 28, 15, 3],
    "L":  [42, 30, 20, 7, 1],
}
CLASSES = ["贫困", "温饱", "工薪", "中产", "富裕"]

# 各阶层基准属性：健康 / 财富 / 关系 / 心境 / 本事 / 声量
CLASS_BASE = {
    "贫困": (44, 8, 55, 42, 34, 3),
    "温饱": (56, 22, 58, 50, 42, 5),
    "工薪": (64, 38, 60, 55, 50, 8),
    "中产": (72, 58, 62, 60, 60, 14),
    "富裕": (78, 82, 60, 62, 68, 26),
}

# ---------------------------------------------------------------- 姓名池
NAMES = {
    "east_asia": {
        "family": ["王", "李", "张", "刘", "陈", "杨", "黄", "赵", "周", "吴",
                   "徐", "孙", "马", "朱", "胡", "林", "郭", "何", "高", "罗"],
        "male": ["建国", "志强", "伟", "涛", "磊", "鹏", "浩然", "宇", "俊杰", "明",
                 "晓东", "海生", "文斌", "振宇", "子轩"],
        "female": ["秀英", "丽", "静", "敏", "雪", "婷", "雨欣", "思彤", "婉", "佳怡",
                   "小满", "桂芳", "晓霞", "诗涵", "若曦"],
        # 1990 年后出生按新名池，避免「1998 年生的建国」这类失真
        "male_new": ["浩然", "宇轩", "俊杰", "宇航", "子轩", "泽宇", "嘉豪", "梓豪", "一鸣", "朗"],
        "female_new": ["雨欣", "思彤", "若曦", "佳怡", "诗涵", "欣怡", "梓涵", "一诺", "语桐", "晴"],
    },
    "south_asia": {
        "family": ["Sharma", "Verma", "Gupta", "Singh", "Khan", "Patel", "Reddy",
                   "Das", "Rahman", "Hossain", "Yadav", "Nair"],
        "male": ["Arjun", "Rahul", "Vikram", "Imran", "Sanjay", "Ravi", "Aditya", "Kabir"],
        "female": ["Priya", "Anjali", "Fatima", "Meera", "Sneha", "Nadia", "Kavya", "Rukhsana"],
    },
    "southeast_asia": {
        "family": ["Nguyen", "Tran", "Le", "Pham", "Santos", "Reyes", "Cruz",
                   "Suharto", "Wijaya", "Chai", "Somchai", "Lim"],
        "male": ["Minh", "Duc", "Bayu", "Andi", "Jose", "Ramon", "Somchai", "Ariff"],
        "female": ["Linh", "Mai", "Siti", "Dewi", "Maria", "Luz", "Ploy", "Nurul"],
    },
    "arab": {
        "family": ["Al-Hassan", "Khalil", "Mansour", "Rahimi", "Yildiz", "Demir",
                   "Farouk", "Sabbagh", "Nasser", "Zayed"],
        "male": ["Omar", "Yusuf", "Karim", "Mehmet", "Ali", "Hassan", "Tariq", "Emre"],
        "female": ["Layla", "Amira", "Zeynep", "Fatma", "Noor", "Salma", "Elif", "Huda"],
    },
    "africa": {
        "family": ["Okafor", "Adeyemi", "Mensah", "Mwangi", "Dlamini", "Banda",
                   "Toure", "Diallo", "Kabila", "Abebe", "Nkosi", "Owusu"],
        "male": ["Chidi", "Kwame", "Sekou", "Juma", "Thabo", "Emeka", "Kofi", "Musa"],
        "female": ["Ngozi", "Ama", "Fatou", "Zanele", "Aisha", "Chioma", "Thandi", "Aminata"],
    },
    "latin": {
        "family": ["Garcia", "Rodriguez", "Martinez", "Silva", "Santos", "Oliveira",
                   "Ramirez", "Torres", "Flores", "Castro"],
        "male": ["Diego", "Carlos", "Mateo", "Joao", "Luis", "Andres", "Miguel", "Rafael"],
        "female": ["Maria", "Sofia", "Camila", "Ana", "Lucia", "Valentina", "Isabel", "Fernanda"],
    },
    "anglo": {
        "family": ["Smith", "Johnson", "Williams", "Brown", "Miller", "Davis",
                   "Wilson", "Anderson", "Taylor", "Clark"],
        "male": ["James", "Michael", "David", "Daniel", "Chris", "Ryan", "Ethan", "Noah"],
        "female": ["Emily", "Sarah", "Jessica", "Ashley", "Megan", "Chloe", "Hannah", "Grace"],
    },
    "west_europe": {
        "family": ["Müller", "Schmidt", "Dubois", "Bernard", "Rossi", "Ferrari",
                   "De Jong", "Van Dijk", "Silva", "Costa"],
        "male": ["Lukas", "Pierre", "Marco", "Jan", "Thomas", "Julien", "Matteo", "Bram"],
        "female": ["Anna", "Camille", "Giulia", "Sanne", "Lea", "Emma", "Chiara", "Fleur"],
    },
    "slavic": {
        "family": ["Ivanov", "Petrov", "Kowalski", "Nowak", "Popescu", "Ilic",
                   "Sokolov", "Kuznetsov", "Horvath", "Nagy"],
        "male": ["Dmitri", "Piotr", "Ivan", "Andrei", "Marek", "Nikola", "Tomasz", "Sergei"],
        "female": ["Olga", "Natalia", "Katarzyna", "Elena", "Milica", "Agnieszka", "Irina", "Zofia"],
    },
}

# 按国家覆盖姓名池：避免「越南人叫 Andi Suharto」
NAME_BY_COUNTRY = {
    "JP": {"family": ["佐藤", "铃木", "高桥", "田中", "渡边", "伊藤", "山本", "中村", "小林", "加藤"],
           "male": ["大辅", "翔太", "健太", "拓海", "悠真", "直树", "和也", "凉介"],
           "female": ["美咲", "结衣", "阳菜", "爱子", "千夏", "真由", "优子", "凛"]},
    "KR": {"family": ["金", "李", "朴", "崔", "郑", "姜", "赵", "尹", "张", "林"],
           "male": ["俊浩", "民秀", "志勋", "东健", "成民", "泰亨", "在贤", "相佑"],
           "female": ["智媛", "秀晶", "恩雨", "宥真", "敏智", "瑞妍", "河娜", "多恩"]},
    "KP": {"family": ["金", "李", "朴", "崔", "郑", "姜", "赵", "尹"],
           "male": ["正哲", "明浩", "英男", "光日", "成泽"],
           "female": ["英姬", "顺玉", "明淑", "春实", "银姬"]},
    "VN": {"family": ["Nguyen", "Tran", "Le", "Pham", "Hoang", "Vo", "Dang", "Bui"],
           "male": ["Minh", "Duc", "Tuan", "Huy", "Quang", "Long", "Nam", "Khanh"],
           "female": ["Linh", "Mai", "Huong", "Thao", "Lan", "Ngoc", "Trang", "Yen"]},
    "TH": {"family": ["Srisuk", "Chaiyaporn", "Wongchai", "Rattanakul", "Suwan", "Phromma"],
           "male": ["Somchai", "Niran", "Kittisak", "Anan", "Chai", "Wichai"],
           "female": ["Ploy", "Siriporn", "Nok", "Malee", "Kanya", "Pim"]},
    "PH": {"family": ["Santos", "Reyes", "Cruz", "Dela Cruz", "Bautista", "Garcia", "Mendoza"],
           "male": ["Jose", "Ramon", "Elias", "Marlon", "Rico", "Andres"],
           "female": ["Maria", "Luz", "Rosario", "Jessa", "Angel", "Divina"]},
    "ID": {"family": ["Suharto", "Wijaya", "Santoso", "Hidayat", "Pratama", "Kusuma"],
           "male": ["Bayu", "Andi", "Budi", "Agus", "Rizky", "Dimas"],
           "female": ["Siti", "Dewi", "Ayu", "Rina", "Putri", "Indah"]},
    "MY": {"family": ["Abdullah", "Rahman", "Tan", "Lim", "Ibrahim", "Yusof"],
           "male": ["Ariff", "Hafiz", "Wei Ming", "Jun Hao", "Amir"],
           "female": ["Nurul", "Aisyah", "Mei Ling", "Xin Yi", "Sofia"]},
    "NG": {"family": ["Okafor", "Adeyemi", "Balogun", "Eze", "Okonkwo", "Abubakar"],
           "male": ["Chidi", "Emeka", "Musa", "Tunde", "Ifeanyi", "Sani"],
           "female": ["Ngozi", "Chioma", "Aisha", "Yetunde", "Adaeze", "Halima"]},
    "ET": {"family": ["Abebe", "Tesfaye", "Bekele", "Haile", "Girma", "Mekonnen"],
           "male": ["Dawit", "Yohannes", "Bereket", "Tesfaye", "Solomon"],
           "female": ["Tigist", "Marta", "Hana", "Selam", "Bethlehem"]},
    "EG": {"family": ["El-Sayed", "Farouk", "Hassan", "Ibrahim", "Mostafa"],
           "male": ["Omar", "Ahmed", "Youssef", "Karim", "Tarek"],
           "female": ["Fatma", "Aya", "Nour", "Salma", "Mariam"]},
    "AF": {"family": ["Ahmadzai", "Karimi", "Nazari", "Rahimi", "Popal", "Stanikzai"],
           "male": ["Hamid", "Rahim", "Naseer", "Wali", "Sami", "Zabih"],
           "female": ["Zahra", "Maryam", "Laila", "Farzana", "Nadia", "Roya"]},
    "PK": {"family": ["Khan", "Malik", "Chaudhry", "Sheikh", "Butt", "Abbasi"],
           "male": ["Imran", "Asif", "Bilal", "Faisal", "Zubair", "Hamza"],
           "female": ["Ayesha", "Sana", "Hina", "Mahnoor", "Rabia", "Zainab"]},
    "BD": {"family": ["Rahman", "Hossain", "Islam", "Ahmed", "Karim", "Chowdhury"],
           "male": ["Rafiq", "Shakib", "Tanvir", "Mizan", "Arif", "Sohel"],
           "female": ["Nasrin", "Rumana", "Shirin", "Taslima", "Farhana", "Mim"]},
}


def pick_name(rng, code, culture, sex, birth_year):
    pool = NAME_BY_COUNTRY.get(code) or NAMES.get(culture)
    if not pool:
        return "—"
    family = rng.choice(pool["family"])
    key = "male" if sex == "男" else "female"
    if code == "CN" and birth_year >= 1990:
        key = "male_new" if sex == "男" else "female_new"
    given = rng.choice(pool.get(key) or pool["male"])
    if code in ("CN", "JP", "KR", "KP"):
        return f"{family}{given}"
    return f"{given} {family}"


TRAITS = [
    "谨慎", "莽撞", "记性好", "嘴笨", "耐痛", "心软", "好胜", "怕生",
    "坐得住", "爱张罗", "认死理", "会看人眼色", "手巧", "易冲动", "能忍",
    "爱笑", "记仇", "话少", "爱管闲事", "沉得住气", "爱较真", "随大流",
    "不合群", "有耐心", "冲动", "细致",
]

GIFTS = [
    ("数理直觉", "intellect"), ("绝对音感", "art"), ("长跑耐力", "body"),
    ("过目不忘", "intellect"), ("共情力强", "social"), ("手上有活", "craft"),
    ("语言天赋", "intellect"), ("胆子大", "body"), ("生得好看", "social"),
]

HOUSING = {
    "贫困": ["土坯房", "棚屋", "城中村单间", "亲戚家借住", "铁皮屋"],
    "温饱": ["老式居民楼", "砖瓦房", "公租房", "合租房"],
    "工薪": ["单位家属院", "县城自建房", "老小区两居", "郊区公寓"],
    "中产": ["市区商品房", "带电梯的公寓", "学区内三居", "联排小楼"],
    "富裕": ["独栋别墅", "市中心大平层", "带院子的老宅", "高层顶层复式"],
}

STRUCTURE_W = [("双亲", 68), ("父母离异", 12), ("单亲", 9), ("隔代抚养", 8), ("机构/寄养", 3)]


def pick_weighted(rng, items, weights):
    return rng.choices(items, weights=weights, k=1)[0]


def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


def sample_age(rng, age_min, age_max):
    """按全球年龄结构加权（0-14 / 15-29 / 30-44 / 45-59 / 60+）"""
    bands = [((0, 14), 25), ((15, 29), 24), ((30, 44), 20), ((45, 59), 16), ((60, 95), 15)]
    bands = [((max(a, age_min), min(b, age_max)), w) for (a, b), w in bands]
    bands = [x for x in bands if x[0][0] <= x[0][1]]
    (lo, hi), _ = pick_weighted(rng, bands, [w for _, w in bands])
    return rng.randint(lo, hi)


def build(seed: str, country: str = None, birth_year: int = None,
          age_min: int = 0, age_max: int = 40, now_year: int = None):
    rng = random.Random(seed)
    now_year = now_year or datetime.now().year

    # 国家
    if country:
        row = next((c for c in COUNTRIES if c[0] == country.upper()), None)
        if not row:
            raise SystemExit(f"未知国家代码: {country}（用 --list-countries 查看）")
    else:
        row = pick_weighted(rng, COUNTRIES, [c[2] for c in COUNTRIES])
    code, zh, w, le, urban_rate, income, culture, places = row

    # 年龄 / 出生年
    if birth_year:
        age_now = now_year - birth_year
    else:
        age_now = sample_age(rng, age_min, age_max)
        birth_year = now_year - age_now
    age_now = max(0, now_year - birth_year)

    # 城乡
    urban = rng.random() < urban_rate
    if urban:
        settlement = pick_weighted(rng, ["城区", "郊区", "城中村"], [55, 25, 20])
    else:
        settlement = pick_weighted(rng, ["村庄", "乡镇"], [60, 40])

    # 阶层
    cls = pick_weighted(rng, CLASSES, CLASS_W[income])
    if settlement == "村庄" and cls in ("富裕",):
        cls = "中产"
    if settlement == "城中村" and cls == "富裕":
        cls = "中产"

    # 性别
    sex = "男" if rng.random() < 0.505 else "女"

    # 姓名
    full = pick_name(rng, code, culture, sex, birth_year)

    # 属性
    base = CLASS_BASE[cls]
    attrs = {
        "health": clamp(base[0] + rng.randint(-14, 12) + (2 if urban else -2)),
        "wealth": clamp(base[1] + rng.randint(-8, 10)),
        "bond":   clamp(base[2] + rng.randint(-16, 14)),
        "spirit": clamp(base[3] + rng.randint(-14, 14)),
        "skill":  clamp(base[4] + rng.randint(-12, 12)),
        "fame":   clamp(base[5] + rng.randint(0, 6)),
    }

    traits = rng.sample(TRAITS, 2)
    gift = None
    if rng.random() < 0.14:
        gift = dict(zip(("name", "kind"), rng.choice(GIFTS)))

    structure = pick_weighted(rng, [s for s, _ in STRUCTURE_W], [w for _, w in STRUCTURE_W])
    siblings = 0 if structure in ("机构/寄养",) else rng.choices(
        [0, 1, 2, 3, 4, 5], weights=[22, 33, 22, 13, 7, 3], k=1)[0]
    if structure == "隔代抚养":
        siblings = min(siblings, 3)

    place = rng.choice(places) if places else "未记录"
    life_exp = round(le + rng.uniform(-9, 9) + (attrs["health"] - 60) * 0.06, 1)
    life_exp = clamp(life_exp, 32, 98)

    return {
        "id": "life-" + datetime.now().strftime("%Y%m%d%H%M%S"),
        "seed": str(seed),
        "created": datetime.now().isoformat(timespec="seconds"),
        "name": full,
        "sex": sex,
        "birth": {
            "year": birth_year,
            "age_now": age_now,
            "country": code,
            "country_zh": zh,
            "place": place,
            "settlement": settlement,
            "urban": urban,
        },
        "culture": culture,
        "region_income": income,
        "family": {
            "structure": structure,
            "siblings": siblings,
            "class": cls,
            "housing": rng.choice(HOUSING[cls]),
        },
        "attrs": attrs,
        "traits": traits,
        "gift": gift,
        "life_expectancy": life_exp,
        "start_age": age_now,
    }


def main():
    ap = argparse.ArgumentParser(description="sim-life 人生样本抽样器")
    ap.add_argument("--seed", default=None, help="随机种子，省略则自动生成")
    ap.add_argument("--country", default=None, help="指定国家代码，如 CN / IN / NG")
    ap.add_argument("--birth-year", type=int, default=None)
    ap.add_argument("--age-min", type=int, default=0)
    ap.add_argument("--age-max", type=int, default=40)
    ap.add_argument("--now-year", type=int, default=None)
    ap.add_argument("--list-countries", action="store_true")
    ap.add_argument("--pretty", action="store_true", help="带缩进输出")
    a = ap.parse_args()

    if a.list_countries:
        for c in sorted(COUNTRIES, key=lambda x: -x[2]):
            print(f"{c[0]:<4}{c[1]:<10}{c[2]:>6.2f}%  寿命 {c[3]:>4}  城镇 {c[4]:.0%}  {c[5]}")
        return

    seed = a.seed or str(secrets.randbits(48))
    data = build(seed, a.country, a.birth_year, a.age_min, a.age_max, a.now_year)
    print(json.dumps(data, ensure_ascii=False, indent=2 if a.pretty else None))


if __name__ == "__main__":
    main()
