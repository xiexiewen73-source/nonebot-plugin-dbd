# NoneBot-Plugin-DBD-Map

一款基于 [NoneBot2](https://v2.nonebot.dev/) 框架的《黎明杀机》官方地图平面图插件。内置 52 张地图，支持中英文双关键词查询，并可自定义别名。

## ✨ 功能特性

- **全面覆盖**：内置 52 张《黎明杀机》地图平面图，含多个版本变体（如 `煤塔 I / II`、`浣熊市警察局 / II`）。
- **双语检索**：支持官方英文原名与中文译名查询，英文不区分大小写。
- **动态扩展**：支持通过指令添加自定义别名，无需修改源码或重启机器人。
- **开箱即用**：静态图片与插件一同打包，无需手动放置 `static/` 目录。
- **数据隔离**：用户别名写入 NoneBot 标准数据目录，不污染工作区。

## 📦 安装

**方式一：通过 NoneBot CLI 安装（推荐）**

在项目根目录下运行：

```bash
nb plugin install nonebot-plugin-dbdmap
```

**方式二：通过 pip 安装**

```bash
pip install nonebot-plugin-dbdmap
```

## 🎮 使用说明

### 指令一览

| 指令 | 说明 | 示例 |
| :--- | :--- | :--- |
| `/查询 [关键词]` | 根据关键词检索地图并发送图片 | `/查询 阿扎罗夫长眠处` |
| `/地图 [关键词]` | 同 `/查询`，简写形式 | `/地图 天堂加油站` |
| `/添加别名 [原关键词] [新别名]` | 为地图添加自定义别名 | `/添加别名 阿扎罗夫长眠处 阿扎` |

### 触发规则

- 群聊中：需 `@机器人` 并附带指令内容。
- 私聊中：直接发送指令内容即可。

### 添加别名的规则

- 别名长度 1~32 个字符，不能包含控制字符，也不能含空格（用空格分隔原关键词和别名）。
- **不能把别名设成已有的内置地图名**（中文名或英文名都不行），否则会永久劫持官方名。
- 内置名始终优先于自定义别名，即使别名文件被手改，官方名也不会被顶掉。

### ⚙️ 配置说明

**静态资源**

地图图片随插件一起打包，**无需手动配置**。资源位于 `nonebot_plugin_dbd/static/DBD_Map/` 目录内，文件名采用官方英文名（如 `azarovs_resting_place.jpg`）。

**数据目录**

别名数据通过 [nonebot-plugin-localstore](https://github.com/nonebot/plugin-localstore) 的 `get_plugin_data_dir()` 写入，实际路径可用 `nb localstore` 查看，典型位置为：

- Windows：`%LOCALAPPDATA%\nonebot2\nonebot_plugin_dbd\dbd_aliases.json`
- Linux：`~/.local/share/nonebot2/nonebot_plugin_dbd/dbd_aliases.json`
- macOS：`~/Library/Application Support/nonebot2/nonebot_plugin_dbd/dbd_aliases.json`

### 🛡️ 隐私与安全

- 地图图片资源由插件开发者整理，仅供学习交流使用。
- 插件只会读取自身包内的图片，并在出图前校验文件名白名单；别名文件中指向未知文件的记录会被忽略。
- 请勿将插件用于任何商业用途。

### 🐛 常见问题（FAQ）

**Q1：查询时提示"图片发送失败"是什么原因？**

A：图片路径已由插件自动解析，通常是协议端（如 go-cqhttp）无法访问该文件。若机器人与协议端不在同一台机器或不同容器内，`file://` 本地路径不可用，需改为同一文件系统部署或改用可访问的图床。

**Q2：添加别名后，为什么提示"找不到原关键词"？**

A：请确认原关键词是插件内置的官方中文名或英文名，而不是你自己上一次添加的别名。

**Q3：别名数据存放在哪里？**

A：见上文「数据目录」一节，或运行 `nb localstore` 查看。

**Q4：启动日志里提示"有 N 个地图条目指向缺失图片"怎么办？**

A：说明包内的 `static/DBD_Map/` 不完整（例如被精简过的安装）。这些地图会查不到，其余地图不受影响。重新安装完整插件即可。

### 📄 许可证

本项目遵循 [MIT License](LICENSE) 协议。

### 📮 联系方式

- **主页**：[https://github.com/xiexiewen73-source/nonebot-plugin-dbd](https://github.com/xiexiewen73-source/nonebot-plugin-dbd)
- **作者**：77_77
