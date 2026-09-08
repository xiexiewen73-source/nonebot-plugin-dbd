from nonebot.plugin import PluginMetadata
import os
import json
from nonebot import on_command,get_driver
from nonebot.adapters.onebot.v11 import Message, MessageEvent, MessageSegment,Bot
from nonebot.params import CommandArg
from nonebot.exception import FinishedException
from pathlib import Path
__plugin_meta__ = PluginMetadata(
    name="黎明杀机地图查询",
    description="支持查询所有官方地图",
    usage="发送 /查询 地图名&添加别名详见md",
    type="application",
    homepage="https://github.com/你的用户名/nonebot-plugin-dbdmap",
    supported_adapters={"~onebot.v11"}
)
# ==================== 1. 基础地图数据（官方中文名 + 文件名） ====================
base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent.parent

# 拼接静态资源路径
STATIC_FOLDER = base_dir / "static" / "DBD_Map"
BASE_MAP_DATA = {
    "gas_heaven": {"zh": "天堂加油站", "file": "gas_heaven.jpg"},
    "forgotten_ruins": {"zh": "被遗忘的废墟", "file": "forgotten_ruins.jpg"},
    "the_shattered_square": {"zh": "破碎广场", "file": "the_shattered_square.jpg"},
    "azarovs_resting_place": {"zh": "阿扎罗夫长眠处", "file": "azarovs_resting_place.jpg"},
    "thompson_house": {"zh": "汤普森之家", "file": "thompson_house.jpg"},
    "ormond_lake_mine": {"zh": "奥蒙德湖矿场", "file": "ormond_lake_mine.jpg"},
    "the_game": {"zh": "游戏", "file": "the_game.jpg"},
    "greenville_square": {"zh": "格林维尔广场", "file": "greenville_square.jpg"},
    "mount_ormond_resort_v1": {"zh": "奥蒙德度假村 v1", "file": "mount_ormond_resort_v1.jpg"},
    "garden_of_joy": {"zh": "欢乐花园", "file": "garden_of_joy.jpg"},
    "ironworks_of_misery": {"zh": "苦难铁厂", "file": "ironworks_of_misery.jpg"},
    "father_cambells_chapel": {"zh": "坎贝尔神父教堂", "file": "father_cambells_chapel.jpg"},
    "sanctum_of_wrath": {"zh": "愤怒圣所", "file": "sanctum_of_wrath.jpg"},
    "the_underground_complex": {"zh": "地下综合体", "file": "the_underground_complex.jpg"},
    "sanctum_of_wrath_v1": {"zh": "愤怒圣所 v1", "file": "sanctum_of_wrath_v1.jpg"},
    "the_pale_rose": {"zh": "苍白玫瑰", "file": "the_pale_rose.jpg"},
    "badham_preschool_1": {"zh": "巴德姆幼儿园 I", "file": "badham_preschool_1.jpg"},
    "suffocation_pit": {"zh": "窒息矿井", "file": "suffocation_pit.jpg"},
    "midwich_elementary_school": {"zh": "米德维奇小学", "file": "midwich_elementary_school.jpg"},
    "forgotten_ruins_dnd": {"zh": "被遗忘的废墟 (D&D)", "file": "forgotten_ruins_dnd.jpg"},
    "mount_ormond_resort": {"zh": "奥蒙德度假村", "file": "mount_ormond_resort.jpg"},
    "mount_ormond_resort_v2": {"zh": "奥蒙德度假村 v2", "file": "mount_ormond_resort_v2.jpg"},
    "shelter_woods_2": {"zh": "庇护林", "file": "shelter_woods_2.jpg"},
    "family_residence": {"zh": "家族住所", "file": "family_residence.jpg"},
    "dead_sands": {"zh": "死亡沙地", "file": "dead_sands.jpg"},
    "raccoon_city_police_station": {"zh": "浣熊市警察局", "file": "raccoon_city_police_station.jpg"},
    "the_temple_of_purgation": {"zh": "净化神庙", "file": "the_temple_of_purgation.jpg"},
    "mothers_dwelling": {"zh": "母亲之屋", "file": "mothers_dwelling.jpg"},
    "rotten_fields": {"zh": "腐烂田野", "file": "rotten_fields.jpg"},
    "toba_landing": {"zh": "托巴登陆点", "file": "toba_landing.jpg"},
    "suffocation_pit_ii": {"zh": "窒息矿井", "file": "suffocation_pit_ii.jpg"},
    "freddy_fazbears_pizza": {"zh": "弗莱迪披萨店", "file": "freddy_fazbears_pizza.jpg"},
    "torment_creek": {"zh": "折磨溪流", "file": "torment_creek.jpg"},
    "family_residence_v1": {"zh": "家族住所 v1", "file": "family_residence_v1.jpg"},
    "fractured_cowshed": {"zh": "破碎牛棚", "file": "fractured_cowshed.jpg"},
    "nostromo_wreckage": {"zh": "诺斯特罗莫残骸", "file": "nostromo_wreckage.jpg"},
    "dead_dawg_saloon": {"zh": "死狗酒馆", "file": "dead_dawg_saloon.jpg"},
    "blood_lodge": {"zh": "血腥小屋", "file": "blood_lodge.jpg"},
    "coal_tower_i": {"zh": "煤塔", "file": "coal_tower_i.jpg"},
    "coal_tower_ii": {"zh": "煤塔", "file": "coal_tower_ii.jpg"},
    "shelter_woods": {"zh": "庇护林", "file": "shelter_woods.jpg"},
    "ironworks_of_misery_ii": {"zh": "苦难铁厂", "file": "ironworks_of_misery_ii.jpg"},
    "rancid_abattoir": {"zh": "腐臭屠宰场", "file": "rancid_abattoir.jpg"},
    "crotus_prenn_asylum": {"zh": "克劳图斯精神病院", "file": "crotus_prenn_asylum.jpg"},
    "eyrie_of_crows": {"zh": "乌鸦之巢", "file": "eyrie_of_crows.jpg"},
    "treatment_theatre": {"zh": "治疗剧院", "file": "treatment_theatre.jpg"},
    "grim_pantry": {"zh": "阴暗储藏室", "file": "grim_pantry.jpg"},
    "wreckers_yard": {"zh": "废车场", "file": "wreckers_yard.jpg"},
    "wretched_shop": {"zh": "悲惨商店", "file": "wretched_shop.jpg"},
}

# ==================== 2. 动态别名文件管理 ====================
current_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(current_dir)
ALIAS_FILE = os.path.join(base_dir, "data", "dbd_aliases.json")

# 确保 data 文件夹存在
os.makedirs(os.path.dirname(ALIAS_FILE), exist_ok=True)


# 读取自定义别名
def load_custom_aliases():
    if os.path.exists(ALIAS_FILE):
        with open(ALIAS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# 保存自定义别名
def save_custom_aliases(aliases):
    with open(ALIAS_FILE, "w", encoding="utf-8") as f:
        json.dump(aliases, f, ensure_ascii=False, indent=4)


# 构建当前所有别名（基础中文 + 自定义别名）
def get_all_aliases():
    aliases = {}
    # 基础中文名
    for info in BASE_MAP_DATA.values():
        aliases[info["zh"]] = info["file"]
    # 自定义别名
    custom = load_custom_aliases()
    aliases.update(custom)
    return aliases


# ==================== 3. 查询指令 ====================
query_cmd = on_command("查询", aliases={"地图", "查图"}, priority=1, block=True)


@query_cmd.handle()
async def handle_query(event: MessageEvent,bot:Bot,args: Message = CommandArg()):
    keyword = args.extract_plain_text().strip()

    if not keyword:
        await query_cmd.finish("请输入地图名称，例如：/查询 阿扎罗夫长眠处")
        return

    # 查找别名对应的图片
    aliases = get_all_aliases()
    filename = aliases.get(keyword)

    if not filename:
        # 如果没找到，尝试匹配英文名
        if keyword.lower() in BASE_MAP_DATA:
            filename = BASE_MAP_DATA[keyword.lower()]["file"]
        else:
            await query_cmd.finish(f"没有找到地图【{keyword}】，请尝试其他关键词。")
            return

    # 拼接图片路径（使用动态绝对路径）
    img_path = os.path.join(base_dir, "static", "DBD_Map", filename)

    try:
        # 尝试发送图片
        await query_cmd.send(MessageSegment.image(f"file:///{img_path}"))

    except FinishedException as e:  # 3. 直接在这里“捕获”它，不需要赋值！
        error_msg = f"事件已经被其他插件结束 (FinishedException)\n可能被抢答：{img_path}"
        global_config = get_driver().config

        async def send_error_to_master(bot: Bot, error_msg: str):
            # 遍历所有超级用户的 QQ 号，发给每一个
            for master_id in global_config.superusers:
                try:
                    await bot.call_api(
                        "send_private_msg",
                        user_id=int(master_id),
                        message=f"⚠️ DBD地图查询被拦截了！\n\n错误详情：\n{error_msg}"
                    )
                    print(f"[报错上报] 已私聊通知主人：{master_id}")
                except Exception as e:
                    print(f"[报错上报失败] 无法私聊主人 {master_id}，原因：{e}")
        print(f"[DBD地图] 遭遇 FinishedException，已上报主人。")

    except Exception as e:  # 4. 其他普通错误，直接回复用户
        await query_cmd.finish(f"图片发送失败：{e}")


# ==================== 4. 添加别名管理指令 ====================
add_alias_cmd = on_command("添加别名", aliases={"别名"}, priority=1, block=True)


@add_alias_cmd.handle()
async def handle_add_alias(event: MessageEvent, args: Message = CommandArg()):
    input_text = args.extract_plain_text().strip()
    if not input_text:
        await add_alias_cmd.finish("请输入格式：/添加别名 原关键词 新别名")
        return

    parts = input_text.split()
    if len(parts) != 2:
        await add_alias_cmd.finish("格式错误！请输入：/添加别名 原关键词 新别名（用空格隔开）")
        return

    original_keyword, new_alias = parts[0], parts[1]

    # 查找原关键词对应的图片文件名
    all_aliases = get_all_aliases()
    target_file = all_aliases.get(original_keyword) or BASE_MAP_DATA.get(original_keyword.lower(), {}).get("file")

    if not target_file:
        await add_alias_cmd.finish(f"找不到原关键词【{original_keyword}】，请确认它是否存在。")
        return

    # 更新并保存自定义别名
    custom_aliases = load_custom_aliases()
    custom_aliases[new_alias] = target_file
    save_custom_aliases(custom_aliases)

    await add_alias_cmd.finish(f"✅ 成功添加别名！以后发送“{new_alias}”也能查到“{original_keyword}”对应的地图了。")