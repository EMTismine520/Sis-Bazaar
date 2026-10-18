# 肥鹅美食街风格合成小游戏

这是一个 Python + Pygame-ce 的移动端竖屏合成小游戏原型。项目没有外部素材依赖，食材使用系统字体 emoji 占位，后续可替换成 PNG。

## 在线试玩

网页版本已配置 GitHub Pages 自动部署，发布地址为：

<https://emtismine520.github.io/Sis-Bazaar/>

用手机浏览器打开即可游玩。网页使用指针拖拽操作：将相同食材拖到一起合成，把食材拖入棋盘上的烹饪锅后点击开火。点击“图鉴”可以查看已发现的蔬菜、肉类和锅料理。

仓库的 `main` 分支每次推送都会通过 GitHub Actions 发布 `web/` 目录。首次启用仓库时，在 GitHub 的 Settings → Pages 中将发布来源设为 GitHub Actions。

## 本地运行

在项目根目录 PowerShell 执行：

```powershell
.\.venv\Scripts\Activate.ps1
python -m game.main
```

## 浏览器运行

推荐使用不依赖 WASM/CDN 的快速网页版本：

```powershell
.\.venv\Scripts\Activate.ps1
python serve.py
```

浏览器会自动打开 `http://127.0.0.1:8000/`。这个入口启动很快，适合手机试玩。
如果提示 8000 端口被占用，改用：`python serve.py 8001`，然后打开 `http://127.0.0.1:8001/`。

原 Pygame/pygbag 版本仍可这样运行，但首次启动会下载和编译 WASM，速度较慢：

```powershell
.\.venv\Scripts\Activate.ps1
$env:PYTHONUTF8='1'
python -m pygbag game
```

终端显示本地地址后，用手机或电脑浏览器打开该地址。手机与电脑需要在同一局域网，手机访问电脑的局域网 IP 和终端显示的端口，例如 `http://192.168.1.20:8000/`。

## 测试

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q
```

点击蔬菜包或肉类包生成食材；每类包最多开启 100 次，棋盘普通格放满后包格会自动禁用。将相同食材拖到一起合成。棋盘第三格是烹饪锅，把蔬菜、肉类或已完成料理拖入锅内，再点击锅打开界面并开火。当前锅料理采用 B「手绘料理图鉴」路线：5 道 Lv.4 基础料理、3 道 Lv.5 双料理和 2 道 Lv.6 三料理；订单卡需要的食材可以拖到订单区域提交。
