# mlx-stt Homebrew Tap

`mlx-stt` 的 Homebrew 安装源，让 Apple Silicon Mac 可以一键安装本地中文语音转文字 CLI。

[![CI](https://github.com/wizicer/homebrew-tap/actions/workflows/ci.yml/badge.svg)](https://github.com/wizicer/homebrew-tap/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

[`mlx-stt`](https://github.com/wizicer/mlx-stt) 基于 MLX、mlx-audio、Qwen3-ASR 和 Qwen3-ForcedAligner，在本地完成语音识别并生成逐字时间戳。这个仓库只负责 Homebrew 分发。

## 安装

```bash
brew tap wizicer/tap git@github.com:wizicer/homebrew-tap.git
brew install wizicer/tap/mlx-stt
```

确认安装：

```bash
mlx-stt --version
mlx-stt probe
```

开始转写：

```bash
mlx-stt transcribe input.wav -o result.json
```

## 使用须知

- 仅支持搭载 Apple Silicon 的 macOS arm64。
- 首次使用会下载模型；默认模型约 3.75 GB。
- 模型缓存独立于 Homebrew 安装目录，升级不会重复下载，卸载软件也不会删除模型。
- 如果模型下载较慢，可先执行：

  ```bash
  export HF_ENDPOINT=https://hf-mirror.com
  ```

- 处理 MP3、M4A 或其他非 WAV 输入前，请安装：

  ```bash
  brew install ffmpeg
  ```

更多命令和输出格式请查看 [`mlx-stt` 的文档](https://github.com/wizicer/mlx-stt)。

## 升级与卸载

```bash
brew upgrade mlx-stt
```

```bash
brew uninstall mlx-stt
```

<details>
<summary>维护者说明</summary>

更新 Formula：

```bash
python3 scripts/update_formula.py \
  --version <version> \
  --sha256 <artifact-sha256>
```

运行维护者测试：

```bash
python3 -m unittest discover -s tests -v
```

本地 artifact 验证：

```bash
./scripts/local_brew_test.sh /path/to/mlx-stt-<version>-macos-arm64.tar.gz
```

开发 clone：

```bash
git clone git@github.com:wizicer/homebrew-tap.git
```

</details>

## License

[MIT](LICENSE)
