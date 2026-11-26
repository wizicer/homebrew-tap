# wizicer Homebrew Tap

wizicer 的个人 Homebrew tap，用来分发 macOS 命令行工具和小型应用。当前包含第一个 Formula：[`mlx-stt`](https://github.com/wizicer/mlx-stt)。

[![CI](https://github.com/wizicer/homebrew-tap/actions/workflows/ci.yml/badge.svg)](https://github.com/wizicer/homebrew-tap/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 使用这个 tap

```bash
brew tap wizicer/tap git@github.com:wizicer/homebrew-tap.git
```

之后可以安装 tap 中提供的 Formula：

```bash
brew install wizicer/tap/<formula>
```

## 可用 Formula

| Formula | 说明 | 安装 |
| --- | --- | --- |
| `mlx-stt` | Apple Silicon 本地中文语音转文字 CLI，基于 MLX、mlx-audio、Qwen3-ASR 与 ForcedAligner | `brew install wizicer/tap/mlx-stt` |

## mlx-stt 快速示例

```bash
brew install wizicer/tap/mlx-stt
mlx-stt --version
mlx-stt transcribe input.wav -o result.json
```

`mlx-stt` 仅支持 macOS arm64。首次使用会下载模型；默认模型约 3.75 GB。处理 MP3、M4A 或其他非 WAV 输入前，请安装 `ffmpeg`：

```bash
brew install ffmpeg
```

更多使用方法请查看 [`mlx-stt` 的文档](https://github.com/wizicer/mlx-stt)。

## 升级与卸载

升级某个 Formula：

```bash
brew upgrade <formula>
```

卸载某个 Formula：

```bash
brew uninstall <formula>
```

<details>
<summary>维护者说明</summary>

仓库结构：

```text
Formula/                  每个软件一个 .rb Formula
scripts/update_formula.py 更新版本、URL 和 sha256
scripts/local_brew_test.sh 用本地 artifact 验证 mlx-stt Formula
tests/                    Formula helper 测试
```

更新 `mlx-stt` Formula：

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
