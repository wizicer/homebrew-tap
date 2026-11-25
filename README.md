# homebrew-tap

这是 `mlx-stt` 的私人 Homebrew tap。仓库名保持为 `homebrew-tap` 时，GitHub owner 为 `Icer` 的 tap 名称是 `Icer/tap`。

## 用户安装

在 `mlx-stt` 仓库创建 GitHub Release、上传 artifact，并更新本仓库 Formula 后：

```bash
brew tap Icer/tap git@github.com:Icer/homebrew-tap.git
brew install mlx-stt
```

tap 完成后也可以直接执行 `brew install Icer/tap/mlx-stt`。私人仓库需要本机 SSH key 已获得访问权限。

常用命令：

```bash
mlx-stt --version
mlx-stt probe
mlx-stt transcribe input.wav -o result.json
mlx-stt transcribe input.wav -o result.json --no-align
```

模型权重不包含在 brew 包内。默认 ASR + forced aligner 约 3.75 GB，会进入 Hugging Face 共享缓存；`brew uninstall` 不删除模型，`brew upgrade` 也不需要重复下载。

中国网络环境建议使用镜像：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

非 16 kHz mono PCM WAV 输入需要：

```bash
brew install ffmpeg
```

## 仓库布局

```text
Formula/mlx-stt.rb          Homebrew Formula
scripts/update_formula.py   更新版本、URL 和 sha256；也可生成本地测试 Formula
scripts/local_brew_test.sh  用本地 tar.gz 执行 brew install/test/uninstall 冒烟验证
tests/                      update_formula 的单元测试
```

## 本地验证

先在 sibling 仓库 `mlx-stt` 中构建：

```bash
cd ../mlx-stt
uv sync --extra dev --extra build
uv run python scripts/build_release.py
```

然后在本仓库执行：

```bash
./scripts/local_brew_test.sh ../mlx-stt/dist/mlx-stt-0.1.0-macos-arm64.tar.gz
```

脚本会：

1. 将 committed Formula 渲染成临时 `file://` Formula；
2. 计算本地 artifact sha256；
3. 在 Homebrew taps 目录创建临时 `mlx-stt-local/tap`；
4. 执行 `brew install mlx-stt-local/tap/mlx-stt`；
5. 执行 `brew test mlx-stt-local/tap/mlx-stt` 和 `mlx-stt --version`；
6. 退出前卸载本次安装的 `mlx-stt` 并删除临时 tap。

当前 Formula 的 `test do` 不只检查 `--version`，还会执行 `probe` 并断言 Metal 可用、程序处于 frozen 模式，以及 `libmlx.dylib` / `mlx.metallib` 都位于 `_internal/mlx/lib/`。

committed Formula 始终保留未来 GitHub Release 的 `https://` URL，不把本机路径提交进去。

## 发布更新流程

在 `mlx-stt` GitHub Release 上传 artifact 后，在本仓库运行：

```bash
python3 scripts/update_formula.py \
  --version 0.1.0 \
  --sha256 <artifact-sha256>
```

如果 GitHub owner 不是 `Icer`：

```bash
python3 scripts/update_formula.py \
  --owner <owner> \
  --version 0.1.0 \
  --sha256 <artifact-sha256>
```

随后在 `mlx-stt` sibling 仓库存在对应 artifact 时运行单元测试和本地 brew 验证：

```bash
python3 -m unittest discover -s tests -v
./scripts/local_brew_test.sh /path/to/mlx-stt-0.1.0-macos-arm64.tar.gz
```

## 开发 clone

推送后建议使用 SSH：

```bash
git clone git@github.com:Icer/homebrew-tap.git
```

不要把本地 `file://` Formula、release artifact 或机器绝对路径提交到本仓库。
