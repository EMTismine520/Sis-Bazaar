# Sis Bazaar 更新与发布指南

这份文档记录网页 v2.0.0 的经济、订单、商店和存档规则，以及本地验证、提交和 GitHub Pages 发布步骤。本次只更新网页和相关测试、文档，Pygame 版本不变。

## 项目结构

- `web/index.html`：GitHub Pages 实际发布的网页入口。
- `tests/test_web_game.py`：网页合成、烹饪、包次数、资源、图鉴，以及 v2 奖励、订单、解锁、存档和交互回归测试。
- `.github/workflows/deploy-pages.yml`：`main` 分支推送后，把 `web/` 部署到 GitHub Pages。
- 在线地址：<https://emtismine520.github.io/Sis-Bazaar/>

## v2.0.0 规则与验收范围

1. 新游戏为第 1 天、120 金币。合成成功 +3 金币；出锅 +料理等级 × 3。每提交一份订单目标立即获得 `16 + 订单等级 × 8`，最后一份再额外获得固定 16 金币。整单总额为 `份数 × (16 + 等级 × 8) + 16`，不增加食材包，两类包各保留 1000 次。
2. 蔬菜与肉类 Lv.1–Lv.3 初始开放；Lv.4 起按各自路线逐级购买，价格为 `60 + (等级 - 4) × 30` 金币。余额不足和前置未解锁时禁止购买并显示原因。购买后才可合成该等级，首次获得才算发现。
3. 当天等级为 `min(8, 1 + floor((天数 - 1) / 2))`，份数为 `min(等级, 3)`。路线目标不受购买和发现限制；已发现的同级锅料理可参与候选，未发现锅料理不加入。先随机排列不同目标，不足时循环补足；当天候选只有两项时，三份订单会让其中一项出现两份。生成后固定目标，购买、合成、刷新不会重抽；预告只显示下一天等级/份数。展示订单不标记发现。
4. 从棋盘逐份拖入目标到订单卡，成功立即消耗一格、增加进度并发放一份金币；失败保留原格且不发奖。最后一份额外发放完成奖励 16 金币、天数加一并生成下一单；重复拖放不能重复领奖。卡片完整显示三份目标、提交进度、每份奖励、完成奖励、剩余可得金币和明日预告，并随内容撑高。
5. 商店为底部独立弹窗，显示当前金币、两条路线下一可买等级及价格。图鉴区分“未解锁”“已解锁但未发现”和“已发现”。
6. `localStorage` 继续使用键 `sis-bazaar-game-v2`、schema 2、版本 `2.0.0`。快照新增 `orderRule: daily-v1`；订单保存 `orderRule`、`items`、`submitted`、`level`、`quantity`、`reward`、`perItemReward`、`completionReward`。每次提交后立即保存，刷新恢复已付金币和进度。新订单允许未购买/未发现的路线目标，棋盘与锅内内容仍校验合法性和解锁状态。
7. “重新开始”确认后删除旧 v2 存档并保存初始状态；取消保留进度。本地、线上、不同设备和浏览器各自存档。

已有多目标订单保留原目标和部分进度，迁移为 `legacy-v2`，继续按旧奖励 `16 + 等级 × 8 + (份数 - 1) × 8` 完成一次，部分提交不发奖；下一单采用 `daily-v1`，不重置进度、不追补历史奖励。旧单目标订单包装为一份未提交目标后按旧规则完成。损坏或不兼容存档回退新游戏。

| 天数 | 等级 | 份数 | 路线候选 | 整单金币 |
| --- | --- | --- | --- | --- |
| 1–2 | Lv.1 | 1 | 包菜、鸡腿 | 40 |
| 3–4 | Lv.2 | 2 | 番茄、培根 | 80 |
| 5–6 | Lv.3 | 3 | 彩椒、肉丸 | 136 |
| 7–8 | Lv.4 | 3 | 胡萝卜、厚切牛排 | 160 |
| 9–10 | Lv.5 | 3 | 香菇、排骨 | 184 |
| 11–12 | Lv.6 | 3 | 玉米、猪排 | 208 |
| 13–14 | Lv.7 | 3 | 土豆、烤肉卷 | 232 |
| 15 起 | Lv.8 | 3 | 紫甘蓝、带骨牛排 | 256 |

Lv.8 一份路线食材需要 128 份基础食材，三份共 384 份。本次不新增补给，有限开包资源不保证无限天数游玩。

## 保留的图鉴布局约定

v2 保留此前图鉴弹窗的布局修复，并让商店使用类似的窄屏尺寸与独立内容滚动。

`web/index.html` 的关键改动：

1. 图鉴最大宽度从 `650px` 改为和棋盘一致的 `480px`，并使用 `calc(100vw - 32px)` 保留窄窗口左右边距。
2. 桌面弹窗使用 `80vh` 后备值，再由 `80dvh` 覆盖；移动端使用 `78vh` 后备值和 `78dvh`，同时限制视口上下边距。
3. 固定遮罩增加 `overflow:hidden`，页面本身不再随图鉴内容滚动。
4. 标题栏和关闭按钮放在 `.catalog-content` 外，内容区独立使用 `overflow-y:auto`、`touch-action:pan-y`、`overscroll-behavior:contain` 和移动端惯性滚动。
5. 每次点击打开图鉴时，将 `catalogContent.scrollTop` 和 `scrollLeft` 重置为 `0`，重新从顶部开始查看。

`tests/test_web_game.py` 增加了桌面宽度、`vh/dvh` 后备高度、移动端尺寸、遮罩禁止滚动和打开时重置滚动位置的静态回归检查。

## 本地修改与测试

在 PowerShell 中进入仓库根目录：

~~~powershell
cd "C:\Users\23815\Desktop\Sis Bazaar"
.\.venv\Scripts\Activate.ps1
~~~

先检查是否有其他未提交改动：

~~~powershell
git -c safe.directory='C:/Users/23815/Desktop/Sis Bazaar' status --short --branch
~~~

运行完整测试：

~~~powershell
.\.venv\Scripts\python.exe -m pytest -q
~~~

检查补丁格式：

~~~powershell
git -c safe.directory='C:/Users/23815/Desktop/Sis Bazaar' diff --check
~~~

本地启动网页预览：

~~~powershell
python serve.py
~~~

打开 <http://127.0.0.1:8000/>。端口被占用时可以使用 `python serve.py 8001`。分别在桌面和 320–390px 窄屏检查以下项目；测试使用独立浏览器配置，避免覆盖正常游戏存档：

- 页面显示 `v2.0.0`，HUD、棋盘、订单卡和底部三个按钮不溢出。
- 两份同级食材合成只奖励 3 金币；移动和无效合成不奖励。未解锁 Lv.4 时合成被阻止且食材保留。
- 打开商店，检查两条路线 Lv.4 均为 60 金币；先购买蔬菜 Lv.4，肉类仍停在 Lv.3；Lv.5 价格为 90。越级和余额不足无法购买，购买后能继续合成。
- 烹饪出锅只奖励一次等级 × 3 金币。按上表检查第 1–16 天和后期封顶；第 3 天在番茄/培根未发现时仍有两个 Lv.2 目标，第 7 天未买 Lv.4 时显示“需先在商店解锁 Lv.4”，购买后显示“合成后提交”。购买、合成和刷新不改变目标。
- 逐份拖入匹配食材，金币立即增加 `16 + 等级 × 8`、棋盘对应格变空、进度增长、天数不变；错误提交保留食材。最后一份额外 +16 恰好一次，天数加一，重复拖放不领奖。检查每份/完成/剩余金币和明日预告；三目标卡片在桌面和 320、360、390px 窄屏完整显示且不覆盖棋盘。
- 图鉴区分三个发现/解锁状态，桌面不宽于棋盘；窄屏可看到标题、关闭按钮，图鉴与商店内容独立滚动，锅料理仍能查看到 Lv.6。
- 部分提交且有锅内食材时刷新，检查金币、棋盘、订单目标/进度/奖励规则、天数、包次数、解锁、发现和锅内内容均恢复，已交目标不再奖励。另载入旧版部分订单，确认不追补金币、仍按旧规则发一次整单奖励，随后生成新规则订单。
- 点击重新开始并取消，检查存档不变；再次点击并确认，检查第 1 天、120 金币、两条路线 Lv.3 和初始包次数恢复，再刷新确认新进度。

自动回归通过 Python 调用 Node 执行真实网页脚本，覆盖第 1–16 天及 Lv.8 上限、路线/锅料理候选、不同目标优先与重复补足、固定目标、逐份即时奖励与完成奖励仅一次、失败/重复提交、旧规则过渡、完整/部分存档恢复、损坏存档、合成/烹饪奖励、购买限制、确认重置和指针入口。完成后在服务终端按 `Ctrl+C` 停止服务。

## 常规同步到 GitHub

确认本地测试通过后，查看差异并提交需要发布的文件：

~~~powershell
git -c safe.directory='C:/Users/23815/Desktop/Sis Bazaar' diff -- web/index.html tests/test_web_game.py README.md UPDATE_GUIDE.md
git -c safe.directory='C:/Users/23815/Desktop/Sis Bazaar' add web/index.html tests/test_web_game.py README.md UPDATE_GUIDE.md
git -c safe.directory='C:/Users/23815/Desktop/Sis Bazaar' commit -m "Adjust daily order progression and per-item rewards"
~~~

推送到 `main`：

~~~powershell
git -c safe.directory='C:/Users/23815/Desktop/Sis Bazaar' -c http.version=HTTP/1.1 push origin main
~~~

推送完成后确认本地和远端状态：

~~~powershell
git -c safe.directory='C:/Users/23815/Desktop/Sis Bazaar' status --short --branch
git -c safe.directory='C:/Users/23815/Desktop/Sis Bazaar' log --oneline --decorate -3
~~~

正常情况下，`main` 应该和 `origin/main` 同步，且最新提交信息与本次修改一致。

## 命令行推送失败时的远端同步方案

此前发布时，命令行曾出现以下网络错误：

~~~text
Recv failure: Connection was reset
Failed to connect to github.com port 443
~~~

这表示代码可以正常提交，但当前终端到 GitHub 的网络链路不可用。不要因此重复修改代码或强制推送。可以使用已登录的 GitHub 网页完成同样的远端同步：

1. 打开仓库 <https://github.com/EMTismine520/Sis-Bazaar>，确认分支为 `main`。
2. 进入需要更新的文件，例如 `web/index.html` 或 `tests/test_web_game.py`，点击 **Edit this file**。
3. 编辑前先读取 `main` 分支当前文件内容。可以打开对应的 Raw 地址，确保网页编辑以远端最新内容为基础，避免覆盖其他人的更新。
4. 只应用本次本地差异。网页编辑器中确认关键字符串已经出现，例如：
   - `const GAME_VERSION='2.0.0'` 和 `const SAVE_SCHEMA=2`
   - `function buyIngredient`、`function submitOrder` 和 `localStorage.setItem`
   - `width:min(480px, calc(100vw - 32px))` 和 `height:min(78dvh, 680px)`
5. 点击 **Commit changes...**，选择 **Commit directly to the main branch**，填写与本地一致的提交说明，然后提交。
6. 每个网页编辑提交都会生成新的提交哈希。记录这些哈希，并打开对应的提交页面确认文件内容已经更新。所有修改文件都同步完成后再验证最终部署，不依赖本地旧的 `origin/main` 引用判断是否已发布。

网页提交完成后，命令行仓库的 `origin/main` 可能仍是旧的本地跟踪引用，`git status` 可能暂时显示 `ahead 1`。这不代表 GitHub 远端没有更新。网络恢复后先执行：

~~~powershell
git -c safe.directory='C:/Users/23815/Desktop/Sis Bazaar' fetch origin
git -c safe.directory='C:/Users/23815/Desktop/Sis Bazaar' log --graph --oneline --decorate --all -8
~~~

比较本地提交和远端提交后再决定是否需要合并或整理分支。不要在没有确认历史关系时使用 `git push --force`。

## GitHub Pages 发布验证

仓库的 `.github/workflows/deploy-pages.yml` 会在 `main` 推送后自动部署 `web/`。提交完成后按以下顺序验证：

1. 在仓库的 **Actions** 页面确认 `Deploy web game to GitHub Pages` 运行成功。
2. 用提交哈希作为查询参数打开线上页面，绕过浏览器缓存：

   ~~~text
   https://emtismine520.github.io/Sis-Bazaar/?v=<commit-sha>
   ~~~

3. 确认页面显示 `v2.0.0`，存在每份/完成/剩余金币和明日预告；用独立测试存档按上表验证等级与份数、未发现/未购买提示、逐份到账、最后额外 +16、刷新恢复及旧档过渡。查询参数仅绕过页面缓存，不清除站点存档。
4. 打开图鉴与商店，确认桌面和手机均无横向溢出、内容能滚动；图鉴关闭后再打开，滚动位置回到顶部。使用测试存档验证确认重置。
5. 如需确认静态源码，可打开提交对应的 Raw 地址：

   ~~~text
   https://raw.githubusercontent.com/EMTismine520/Sis-Bazaar/<commit-sha>/web/index.html
   ~~~

只有对应提交的 Actions 成功，并且带提交哈希的线上页面实际显示 v2.0.0 及新功能，才算完成一次网页版本发布。
