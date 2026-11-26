class MlxStt < Formula
  desc "Local Chinese speech-to-text CLI powered by MLX and Qwen3-ASR"
  homepage "https://github.com/wizicer/mlx-stt"
  version "0.1.1"

  on_tahoe :or_newer do
    url "https://github.com/wizicer/mlx-stt/releases/download/v0.1.1/mlx-stt-0.1.1-macos26-arm64.tar.gz"
    sha256 "f5ecea97baa96a9c6eadf0313a43f0b923d3b1794fc22b3fcccd691b8a1c6c7e"
  end

  on_sequoia do
    url "https://github.com/wizicer/mlx-stt/releases/download/v0.1.1/mlx-stt-0.1.1-macos15-arm64.tar.gz"
    sha256 "a326866a1607f0fe7ce1301e0ebead296a59be594faa1d89bacbfe510cedddba"
  end

  license "MIT"

  depends_on macos: :sequoia
  depends_on arch: :arm64

  def install
    libexec.install "mlx-stt"
    libexec.install "_internal"
    libexec.install "VERSION"
    libexec.install "build-info.json"
    bin.write_exec_script libexec/"mlx-stt"
  end

  def caveats
    <<~EOS
      Model weights are not bundled. On first use, mlx-stt downloads about
      3.75 GB for the default ASR and forced-aligner models into the shared
      Hugging Face cache. The models are not removed by brew uninstall or
      downloaded again by brew upgrade.

      To use the Hugging Face mirror:
        export HF_ENDPOINT=https://hf-mirror.com

      16 kHz mono PCM WAV is supported directly. For other audio formats:
        brew install ffmpeg
    EOS
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/mlx-stt --version")

    probe_output = shell_output("#{bin}/mlx-stt probe")
    assert_includes probe_output, '"metal_available": true'
    assert_includes probe_output, '"frozen": true'
    assert_path_exists libexec/"_internal/mlx/lib/libmlx.dylib"
    assert_path_exists libexec/"_internal/mlx/lib/mlx.metallib"
  end
end
