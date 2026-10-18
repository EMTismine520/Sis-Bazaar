# Sis Bazaar 更新与发布指南

这份文档记录网页版本的常规更新方法，以及本次图鉴弹窗修复时采用的远端同步方案。后续修改网页、测试或素材时，可以按同一流程执行。

## 项目结构

- `web/index.html`：GitHub Pages 实际发布的网页入口。
- `tests/test_web_game.py`：网页逻辑、包次数、合成、烹饪、资源和图鉴静态回归测试。
- `.github/workflows/deploy-pages.yml`：`main` 分支推送后，把 `web/` 部署到 GitHub Pages。
- 在线地址：<https://emtismine520.github.io/Sis-Bazaar/>

## 本次图鉴修复做了什么

本次只调整图鉴弹窗的布局和测试，没有改变图鉴数据、解锁状态、棋盘拖拽、合成、烹饪或食材包次数逻辑。

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
python -m pytest -q
~~~

检查补丁格式：

~~~powershell
git -c safe.directory='C:/Users/23815/Desktop/Sis Bazaar' diff --check
~~~

本地启动网页预览：

~~~powershell
python serve.py
~~~

打开 <http://127.0.0.1:8000/>。端口被占用时可以使用 `python serve.py 8001`。测试移动端布局时，使用浏览器的窄屏或设备预览；打开图鉴后检查标题、关闭按钮、内容滚动和 Lv.6 内容。完成后在服务终端按 `Ctrl+C` 停止服务。

## 常规同步到 GitHub

确认本地测试通过后，查看差异并提交需要发布的文件：

~~~powershell
git -c safe.directory='C:/Users/23815/Desktop/Sis Bazaar' diff -- web/index.html tests/test_web_game.py UPDATE_GUIDE.md
git -c safe.directory='C:/Users/23815/Desktop/Sis Bazaar' add web/index.html tests/test_web_game.py UPDATE_GUIDE.md
git -c safe.directory='C:/Users/23815/Desktop/Sis Bazaar' commit -m "Describe the change"
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

本次更新时，命令行多次出现以下网络错误：

~~~text
Recv failure: Connection was reset
Failed to connect to github.com port 443
~~~

这表示代码可以正常提交，但当前终端到 GitHub 的网络链路不可用。不要因此重复修改代码或强制推送。可以使用已登录的 GitHub 网页完成同样的远端同步：

1. 打开仓库 <https://github.com/EMTismine520/Sis-Bazaar>，确认分支为 `main`。
2. 进入需要更新的文件，例如 `web/index.html` 或 `tests/test_web_game.py`，点击 **Edit this file**。
3. 编辑前先读取 `main` 分支当前文件内容。可以打开对应的 Raw 地址，确保网页编辑以远端最新内容为基础，避免覆盖其他人的更新。
4. 只应用本次本地差异。网页编辑器中确认关键字符串已经出现，例如：
   - `width:min(480px, calc(100vw - 32px))`
   - `height:min(78vh, 680px)` 和 `height:min(78dvh, 680px)`
   - `$('catalogContent').scrollTop=0`
5. 点击 **Commit changes...**，选择 **Commit directly to the main branch**，填写与本地一致的提交说明，然后提交。
6. 每个网页编辑提交都会生成新的提交哈希。记录这些哈希，并打开对应的提交页面确认文件内容已经更新。本次网页文件提交为 `46b12f1`，测试文件提交为 `6108e87`。

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

3. 打开图鉴，确认桌面宽度不超过棋盘，手机窄屏仍能看到标题和关闭按钮，内容可以拖动到 Lv.6。
4. 点击关闭后重新打开，确认滚动位置回到顶部。
5. 如需确认静态源码，可打开提交对应的 Raw 地址：

   ~~~text
   https://raw.githubusercontent.com/EMTismine520/Sis-Bazaar/<commit-sha>/web/index.html
   ~~~

只有 Actions 成功并且线上页面实际显示新布局，才算完成一次网页版本发布。
