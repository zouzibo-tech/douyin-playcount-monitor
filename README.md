# 抖音播放量监控

> 输入抖音视频链接，自动追踪**该视频所属合集的总播放量**，以及**合集里每一集的单独播放量**。
> 每天跑一次，保留历史快照，用来观察增长趋势。

- ✅ **不需要登录**任何抖音账号
- ✅ **不依赖任何 AI 服务**，纯本地运行，数据不出本机
- ✅ **下载即用**：单个 exe，目标电脑零安装（复用系统自带的 Edge）

---

## ⬇️ 下载使用

到 **[Releases](../../releases)** 页面下载最新版的 `抖音合集播放量监控（发布包）.zip`：

1. 解压，得到 `抖音监控` 文件夹和一份使用手册
2. 把 `抖音监控` 文件夹放到电脑上（例如 `D:\抖音监控`）
3. 双击 `抖音监控.exe` → 黑色窗口保持打开 → 浏览器自动打开操作界面
4. 在「清单」页粘贴视频链接 → 导入 → 到「抓取」页点「立即抓取」

> ⚠️ 一定要解压**整个文件夹**，不能只拿 exe —— 同目录的 `_internal` 里放着运行库。
>
> 详细图文步骤见手册：下载「使用手册（发给同事）.docx」，或直接看
> [使用手册（发给同事）.md](使用手册（发给同事）.md)

**运行要求**：Windows 10 / 11 + 系统自带的 Microsoft Edge。不需要装 Python、不需要注册。

---

## 功能

| 页面 | 能做什么 |
|---|---|
| 清单 | 批量粘贴链接导入（自动去重）、识别每条属于哪个合集、停用/删除 |
| 抓取 | 一键「立即抓取」，实时进度与日志；可随时停止，已采数据不丢 |
| 结果 | 合集总览（总播放/日增/收藏/集数/更新至）、**分集明细**（每一集的播放量、增量、占合集比） |
| 导出 | Excel 日报（合集总览 / 分集明细 / 账号汇总 三个工作表）、单文件 HTML 看板 |
| 设置 | 定时时间点（可留空，纯手动）、抓取间隔、重试次数、输出目录 |

其他特性：

- **边采边存**：每采完一个合集立刻落库，中断或崩溃不会丢掉已采到的数据
- **错过自动补跑**：开机晚于设定时间点、或电脑当时在睡眠，只要当天还没采到数据会自动补一次
- **单实例保护**：重复双击不会起第二个进程，直接打开已有界面
- 界面完全离线、只监听 `127.0.0.1`，公司内网可用

---

## 为什么能拿到播放量

抖音的播放量只在**特定接口**里公开。实测（2026-10）同一批视频，不同接口返回的
`play_count` 完全不同：

| 接口 | 单条 `play_count` |
|---|---|
| `aweme/detail` 视频详情 | `0`（不公开） |
| `aweme/post` 账号作品列表 | `0`（不公开） |
| `aweme/related` 相关推荐 | `0`（不公开） |
| **`mix/aweme` 合集内视频列表** | **真实值** ✅ |

所以：**只要视频发布在合集里，就能拿到每一集的真实播放量。**

合集的总播放量来自 `mix/list` 的 `statis.play_vv`，与「各集求和」互为校验
（实测差异 < 2%）。不在合集里的视频，平台不公开其播放量，程序会在日志里
**明确指出是哪一条**，不会静默丢弃。

### 免签名的实现方式

抖音网页是 JS 反爬壳（`_$jsvmprt` 混淆），接口需要 `a_bogus` 签名，
**纯 HTTP 请求拿不到数据**。

本项目**不逆向签名算法**，而是用 Playwright 打开页面，
监听浏览器自身发出的接口响应，直接取回 JSON：

```python
def on_response(resp):
    if "/aweme/v1/web/" not in resp.url:
        return
    key = resp.url.split("?")[0].rsplit("/web/", 1)[-1].replace("/", "_")
    cap.setdefault(key, []).append(resp.json())

page.on("response", on_response)
```

好处是浏览器会自动完成签名，**不会因为签名算法变更而失效**。

用到的三个接口：

| 接口 | 用途 |
|---|---|
| `/aweme/v1/web/aweme/detail/` | 作者 `sec_uid`、所属合集 `mix_id` / `mix_name` |
| `/aweme/v1/web/mix/aweme/` | 合集内每个视频的**真实播放量** |
| `/aweme/v1/web/mix/list/` | 账号各合集的**官方总播放量** |

---

## 从源码运行

```bash
pip install playwright openpyxl
python -m playwright install chromium     # 或直接用系统 Edge

python src/app.py
# 浏览器会自动打开 http://127.0.0.1:8765/
```

自行打包成 exe：

```bash
pyinstaller --noconfirm --onedir --name "抖音监控" --console \
  --paths src --collect-all playwright --add-data "src/webui;webui" \
  --hidden-import store --hidden-import analyze --hidden-import pipeline \
  --hidden-import report --hidden-import dashboard --hidden-import collector \
  --hidden-import resolve --hidden-import scheduler --hidden-import config \
  src/app.py
```

---

## 目录结构

```
├─ src/
│   ├─ app.py          主入口：本地服务 + 自动打开界面
│   ├─ pipeline.py     一次抓取的完整流程（边采边存）
│   ├─ collector.py    采集内核（浏览器响应监听）
│   ├─ resolve.py      链接解析与缓存
│   ├─ store.py        SQLite 存储
│   ├─ analyze.py      汇总与增量计算
│   ├─ report.py       Excel 导出
│   ├─ dashboard.py    单文件 HTML 看板
│   ├─ scheduler.py    定时 + 错过补跑
│   ├─ config.py       配置与路径
│   └─ webui/          操作界面（离线，无外部依赖）
├─ scripts/
│   ├─ make_manual.py  生成使用手册（docx + md）
│   └─ make_release.py 生成发布包（zip）
├─ 使用说明.md          面向维护者
├─ 使用手册（发给同事）.md  面向终端使用者
└─ 启动.bat / 立即抓取一次.bat
```

---

## 已知限制

- 不在合集中的视频，单集播放量平台不公开，取不到
- 超大合集（几十集）依赖滚动加载，极端情况可能取不全（日志会给出提示）
- 抖音前端改版可能导致接口路径变化，集中在 `src/collector.py` 顶部，改一处即可
- 同一天重复抓取会覆盖当天数据（刻意设计，避免把半天的增长当成一整天）

---

## 说明

仅供学习与自有账号数据管理使用。程序只读取公开页面，不登录、不绕过任何访问控制。
请遵守目标平台的服务条款，控制抓取频率。
