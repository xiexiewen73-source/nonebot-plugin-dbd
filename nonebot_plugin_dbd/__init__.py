import json
from asyncio import Lock
from pathlib import Path

from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.exception import FinishedException
from nonebot.params import CommandArg
from nonebot.plugin import PluginMetadata
from nonebot_plugin_localstore import get_plugin_data_dir

__plugin_meta__ = PluginMetadata(
    name="黎明杀机地图查询",
    description="支持查询所有官方地图",
    usage="发送 /查询 地图名，/添加别名 原关键词 新别名",
    type="application",
    homepage="https://github.com/xiexiewen73-source/nonebot-plugin-dbd",
    supported_adapters={"~onebot.v11"},
)

# ==================== 1. 路径 ====================
# 静态资源与插件同捆，随 wheel 一起分发，不依赖工作目录
PLUGIN_DIR = Path(__file__).resolve().parent
STATIC_FOLDER = PLUGIN_DIR / "static" / "DBD_Map"

# 别名数据写进 NoneBot 标准数据目录（localstore），不污染工作区
ALIAS_FILENAME = "dbd_aliases.json"

# 并发写别名文件的锁（读-改-写三步必须原子化）
_ALIAS_LOCK = Lock()

# 单个别名的最大长度，防止有人灌超长键把 JSON 撑爆
MAX_ALIAS_LENGTH = 32


_alias_path_cache: Path | None = None


def _alias_file() -> Path | None:
    """解析别名文件路径。

    两点考虑：
    1. 惰性 + 缓存。localstore 靠调用栈推断插件名，而这个函数每次查询都会走到，
       不能每次都做一遍栈回溯；且插件导入期尚未注册，那时调用会直接抛异常。
    2. 解析失败返回 None 而不是抛异常。别名是可选功能，不能因为它挂掉整个查图。
    """
    global _alias_path_cache
    if _alias_path_cache is None:
        try:
            _alias_path_cache = get_plugin_data_dir() / ALIAS_FILENAME
        except Exception as e:
            logger.error("DBD 无法解析 localstore 数据目录，自定义别名功能不可用：{}", e)
            return None
    return _alias_path_cache


# ==================== 2. 基础地图数据（官方中文名 + 文件名） ====================
# 约定：zh 必须唯一，否则后写的会把先写的顶掉，导致该地图永远查不到。
BASE_MAP_DATA = {
    "gas_heaven": {"zh": "天堂加油站", "file": "gas_heaven.jpg"},
    "forgotten_ruins": {"zh": "被遗忘的废墟", "file": "forgotten_ruins.jpg"},
    "the_shattered_square": {"zh": "破碎广场", "file": "the_shattered_square.jpg"},
    "azarovs_resting_place": {"zh": "阿扎罗夫长眠处", "file": "azarovs_resting_place.jpg"},
    "thompson_house": {"zh": "汤普森之家", "file": "thompson_house.jpg"},
    "ormond_lake_mine": {"zh": "奥蒙德湖矿场", "file": "ormond_lake_mine.jpg"},
    "the_game": {"zh": "游戏", "file": "the_game.jpg"},
    "the_game_2": {"zh": "游戏 II", "file": "the_game_2.jpg"},
    "greenville_square": {"zh": "格林维尔广场", "file": "greenville_square.jpg"},
    "mount_ormond_resort": {"zh": "奥蒙德度假村", "file": "mount_ormond_resort.jpg"},
    "mount_ormond_resort_v1": {"zh": "奥蒙德度假村 v1", "file": "mount_ormond_resort_v1.jpg"},
    "mount_ormond_resort_v2": {"zh": "奥蒙德度假村 v2", "file": "mount_ormond_resort_v2.jpg"},
    "garden_of_joy": {"zh": "欢乐花园", "file": "garden_of_joy.jpg"},
    "ironworks_of_misery": {"zh": "苦难铁厂", "file": "ironworks_of_misery.jpg"},
    "ironworks_of_misery_ii": {"zh": "苦难铁厂 II", "file": "ironworks_of_misery_ii.jpg"},
    "father_cambells_chapel": {"zh": "坎贝尔神父教堂", "file": "father_cambells_chapel.jpg"},
    "sanctum_of_wrath": {"zh": "愤怒圣所", "file": "sanctum_of_wrath.jpg"},
    "sanctum_of_wrath_v1": {"zh": "愤怒圣所 v1", "file": "sanctum_of_wrath_v1.jpg"},
    "the_underground_complex": {"zh": "地下综合体", "file": "the_underground_complex.jpg"},
    "the_pale_rose": {"zh": "苍白玫瑰", "file": "the_pale_rose.jpg"},
    "badham_preschool_1": {"zh": "巴德姆幼儿园 I", "file": "badham_preschool_1.jpg"},
    "suffocation_pit": {"zh": "窒息矿井", "file": "suffocation_pit.jpg"},
    "suffocation_pit_ii": {"zh": "窒息矿井 II", "file": "suffocation_pit_ii.jpg"},
    "midwich_elementary_school": {"zh": "米德维奇小学", "file": "midwich_elementary_school.jpg"},
    "midwich_elementary_school_2": {
        "zh": "米德维奇小学 II",
        "file": "midwich_elementary_school_2.jpg",
    },
    "forgotten_ruins_dnd": {"zh": "被遗忘的废墟 (D&D)", "file": "forgotten_ruins_dnd.jpg"},
    "shelter_woods": {"zh": "庇护林", "file": "shelter_woods.jpg"},
    "family_residence": {"zh": "家族住所", "file": "family_residence.jpg"},
    "family_residence_v1": {"zh": "家族住所 v1", "file": "family_residence_v1.jpg"},
    "dead_sands": {"zh": "死亡沙地", "file": "dead_sands.jpg"},
    "raccoon_city_police_station": {
        "zh": "浣熊市警察局",
        "file": "raccoon_city_police_station_1.jpg",
    },
    "raccoon_city_police_station_2": {
        "zh": "浣熊市警察局 II",
        "file": "raccoon_city_police_station_2.jpg",
    },
    "the_temple_of_purgation": {"zh": "净化神庙", "file": "the_temple_of_purgation.jpg"},
    "mothers_dwelling": {"zh": "母亲之屋", "file": "mothers_dwelling.jpg"},
    "mothers_dwelling_1": {"zh": "母亲之屋 II", "file": "mothers_dwelling_1.jpg"},
    "rotten_fields": {"zh": "腐烂田野", "file": "rotten_fields.jpg"},
    "toba_landing": {"zh": "托巴登陆点", "file": "toba_landing.jpg"},
    "freddy_fazbears_pizza": {"zh": "弗莱迪披萨店", "file": "freddy_fazbears_pizza.jpg"},
    "torment_creek": {"zh": "折磨溪流", "file": "torment_creek.jpg"},
    "fractured_cowshed": {"zh": "破碎牛棚", "file": "fractured_cowshed.jpg"},
    "nostromo_wreckage": {"zh": "诺斯特罗莫残骸", "file": "nostromo_wreckage.jpg"},
    "dead_dawg_saloon": {"zh": "死狗酒馆", "file": "dead_dawg_saloon.jpg"},
    "blood_lodge": {"zh": "血腥小屋", "file": "blood_lodge.jpg"},
    "coal_tower_i": {"zh": "煤塔 I", "file": "coal_tower_i.jpg"},
    "coal_tower_ii": {"zh": "煤塔 II", "file": "coal_tower_ii.jpg"},
    "rancid_abattoir": {"zh": "腐臭屠宰场", "file": "rancid_abattoir.jpg"},
    "crotus_prenn_asylum": {"zh": "克劳图斯精神病院", "file": "crotus_prenn_asylum.jpg"},
    "eyrie_of_crows": {"zh": "乌鸦之巢", "file": "eyrie_of_crows.jpg"},
    "treatment_theatre": {"zh": "治疗剧院", "file": "treatment_theatre.jpg"},
    "grim_pantry": {"zh": "阴暗储藏室", "file": "grim_pantry.jpg"},
    "wreckers_yard": {"zh": "废车场", "file": "wreckers_yard.jpg"},
    "wretched_shop": {"zh": "悲惨商店", "file": "wretched_shop.jpg"},
}

# 合法文件名白名单：既是可用图片的集合，也是防目录穿越的最后一道闸
VALID_FILES = {info["file"] for info in BASE_MAP_DATA.values()}

# 内置名称（中文名 + 英文名）：自定义别名不得覆盖它们
BUILTIN_NAMES = {info["zh"] for info in BASE_MAP_DATA.values()} | set(BASE_MAP_DATA)


def _startup_check() -> None:
    """启动自检：把「条目指向缺失图片」和「图片没被索引」都摆到日志里。"""
    if not STATIC_FOLDER.is_dir():
        logger.error("DBD 静态资源目录不存在，插件将无法出图：{}", STATIC_FOLDER)
        return

    broken = sorted(f for f in VALID_FILES if not (STATIC_FOLDER / f).is_file())
    if broken:
        logger.warning(
            "DBD 有 {} 个地图条目指向缺失图片，这些地图将查不到：{}",
            len(broken),
            "、".join(broken),
        )

    extra = sorted(
        p.name for p in STATIC_FOLDER.iterdir() if p.is_file() and p.name not in VALID_FILES
    )
    if extra:
        logger.debug("DBD 静态目录中有 {} 个未被索引的图片：{}", len(extra), "、".join(extra))

    logger.debug("DBD 地图插件就绪，共 {} 张地图", len(BASE_MAP_DATA))


_startup_check()


# ==================== 3. 动态别名文件管理 ====================
def load_custom_aliases() -> dict[str, str]:
    """读别名。

    三重防御：文件不存在 / JSON 损坏 / 内容被手改脏，都退化成空字典而不是抛异常，
    否则一条脏数据会让所有查询指令静默失败。
    """
    alias_file = _alias_file()
    if alias_file is None or not alias_file.is_file():
        return {}

    try:
        data = json.loads(alias_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
        logger.error("DBD 别名文件损坏，已按空别名处理：{}（{}）", alias_file, e)
        return {}

    if not isinstance(data, dict):
        logger.error("DBD 别名文件不是对象结构，已按空别名处理：{}", alias_file)
        return {}

    clean: dict[str, str] = {}
    for key, value in data.items():
        # 只接受「字符串键 -> 白名单内的文件名」，其余一律丢弃
        if isinstance(key, str) and isinstance(value, str) and value in VALID_FILES:
            clean[key] = value
        else:
            logger.warning("DBD 忽略非法别名记录：{!r} -> {!r}", key, value)
    return clean


def save_custom_aliases(aliases: dict[str, str]) -> bool:
    """写别名：先写临时文件再原子替换，避免写一半崩掉把整个别名库毁掉。

    返回是否写入成功，失败时由调用方告知用户。
    """
    alias_file = _alias_file()
    if alias_file is None:
        return False
    try:
        alias_file.parent.mkdir(parents=True, exist_ok=True)
        tmp_file = alias_file.with_name(alias_file.name + ".tmp")
        tmp_file.write_text(
            json.dumps(aliases, ensure_ascii=False, indent=4),
            encoding="utf-8",
        )
        tmp_file.replace(alias_file)
    except OSError as e:
        logger.error("DBD 别名写入失败：{}（{}）", alias_file, e)
        return False
    return True


def get_all_aliases() -> dict[str, str]:
    """内置名优先于自定义别名，防止有人把官方名顶掉导致所有人都查错图。"""
    aliases = load_custom_aliases()
    for info in BASE_MAP_DATA.values():
        aliases[info["zh"]] = info["file"]
    return aliases


# ==================== 4. 查询指令 ====================
query_cmd = on_command("查询", aliases={"地图", "查图"}, priority=1, block=True)


@query_cmd.handle()
async def handle_query(args: Message = CommandArg()):
    keyword = args.extract_plain_text().strip()
    if not keyword:
        await query_cmd.finish("请输入地图名称，例如：/查询 阿扎罗夫长眠处")

    filename = get_all_aliases().get(keyword)
    if not filename:
        info = BASE_MAP_DATA.get(keyword.lower())
        if info:
            filename = info["file"]
        else:
            await query_cmd.finish(f"没有找到地图【{keyword}】，请尝试其他关键词。")

    # 出图前再次确认文件名干净且在白名单内（防目录穿越 / 脏数据）
    if filename not in VALID_FILES or filename != Path(filename).name:
        logger.error("DBD 拒绝非法文件名，已阻止出图：{!r}", filename)
        await query_cmd.finish("地图数据异常，已阻止本次出图。")

    img_path = STATIC_FOLDER / filename
    if not img_path.is_file():
        logger.warning("DBD 地图图片缺失：{}", img_path)
        await query_cmd.finish(f"地图图片不存在：{filename}")

    try:
        # as_uri() 会对空格/中文做百分号编码，比手拼 "file:///" 稳
        await query_cmd.send(MessageSegment.image(img_path.as_uri()))
    except FinishedException:
        # 其它插件先一步结束事件，属于 NoneBot 正常流转，不是故障
        logger.debug("DBD 查询被其它插件先行结束：{}", keyword)
    except Exception as e:
        logger.opt(exception=True).error("DBD 图片发送失败：{}", img_path)
        await query_cmd.finish(f"图片发送失败：{e}")


# ==================== 5. 添加别名管理指令 ====================
add_alias_cmd = on_command("添加别名", aliases={"别名"}, priority=1, block=True)


@add_alias_cmd.handle()
async def handle_add_alias(args: Message = CommandArg()):
    input_text = args.extract_plain_text().strip()
    if not input_text:
        await add_alias_cmd.finish("请输入格式：/添加别名 原关键词 新别名")

    parts = input_text.split()
    if len(parts) != 2:
        await add_alias_cmd.finish("格式错误！请输入：/添加别名 原关键词 新别名（用空格隔开）")

    original_keyword, new_alias = parts[0], parts[1]

    # 别名合法性：非空、限长、不含控制字符
    if not new_alias or len(new_alias) > MAX_ALIAS_LENGTH:
        await add_alias_cmd.finish(f"别名长度需在 1~{MAX_ALIAS_LENGTH} 之间。")
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in new_alias):
        await add_alias_cmd.finish("别名不能包含控制字符。")

    # 不许覆盖内置名，否则官方名会被永久劫持
    if new_alias in BUILTIN_NAMES:
        await add_alias_cmd.finish(f"【{new_alias}】是内置地图名，不能用它做别名。")

    target_file = get_all_aliases().get(original_keyword) or BASE_MAP_DATA.get(
        original_keyword.lower(), {}
    ).get("file")
    if not target_file:
        await add_alias_cmd.finish(f"找不到原关键词【{original_keyword}】，请确认它是否存在。")

    # 读-改-写加锁，避免两个人同时加别名时互相覆盖
    async with _ALIAS_LOCK:
        custom_aliases = load_custom_aliases()
        custom_aliases[new_alias] = target_file
        if not save_custom_aliases(custom_aliases):
            await add_alias_cmd.finish("别名保存失败，请查看机器人日志。")

    logger.info("DBD 新增别名：{} -> {}", new_alias, target_file)
    await add_alias_cmd.finish(
        f"✅ 成功添加别名！以后发送“{new_alias}”也能查到“{original_keyword}”对应的地图了。"
    )
