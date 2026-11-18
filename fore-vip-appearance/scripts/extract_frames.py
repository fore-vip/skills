#!/usr/bin/env python3
"""
视频均匀抽帧脚本（fore-vip-appearance）

用途：把一段含人物的视频按时间均匀抽取若干关键帧，供后续逐帧图像分析。
仅本地处理：不联网、不上传、不做人脸识别、不落库。

用法：
    python3 extract_frames.py <视频路径> [--out 输出目录] [--count 帧数]

参数：
    视频路径    必填，待抽帧的视频文件
    --out       输出目录，默认 <视频所在目录>/<视频名>_frames
    --count     抽取帧数，默认 6

输出：
    在输出目录生成 frame_01.jpg ... frame_NN.jpg，并在标准输出打印每行一个帧路径。

依赖：ffmpeg / ffprobe 需在 PATH 中（本机 /usr/local/bin 已具备）。
"""

import argparse
import os
import subprocess
import sys


def run(cmd):
    """执行命令，返回 stdout；失败时打印错误并退出。"""
    try:
        return subprocess.check_output(cmd, stderr=subprocess.PIPE).decode("utf-8", "replace").strip()
    except FileNotFoundError:
        sys.exit("错误：未找到 ffmpeg / ffprobe，请先安装并确保在 PATH 中。")
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode("utf-8", "replace").strip() if exc.stderr else ""
        sys.exit("错误：命令执行失败：%s\n%s" % (" ".join(cmd), detail))


def get_duration(video):
    """用 ffprobe 读取视频时长（秒）；读取失败返回 None。"""
    out = run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video,
    ])
    try:
        return float(out)
    except (TypeError, ValueError):
        return None


def main():
    parser = argparse.ArgumentParser(description="视频均匀抽帧")
    parser.add_argument("video", help="视频文件路径")
    parser.add_argument("--out", help="输出目录（默认与视频同级的 <视频名>_frames）")
    parser.add_argument("--count", type=int, default=6, help="抽取帧数（默认 6）")
    args = parser.parse_args()

    video = os.path.abspath(os.path.expanduser(args.video))
    if not os.path.isfile(video):
        sys.exit("错误：视频文件不存在：%s" % video)
    if args.count < 1:
        sys.exit("错误：--count 必须大于等于 1")

    out_dir = args.out or os.path.join(os.path.dirname(video),
                                       os.path.splitext(os.path.basename(video))[0] + "_frames")
    out_dir = os.path.abspath(os.path.expanduser(out_dir))
    os.makedirs(out_dir, exist_ok=True)

    # 用 fps 滤镜在整段时长内均匀取帧，-frames:v 限制总帧数。
    duration = get_duration(video)
    if duration and duration > 0:
        fps = args.count / duration
        vf = "fps=%0.6f" % fps
    else:
        # 时长读取失败时的兜底：每 3 秒一帧，最多 count 帧。
        vf = "fps=1/3"

    run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", video,
        "-vf", vf,
        "-frames:v", str(args.count),
        "-q:v", "2",
        os.path.join(out_dir, "frame_%02d.jpg"),
    ])

    frames = sorted(
        os.path.join(out_dir, f)
        for f in os.listdir(out_dir)
        if f.startswith("frame_") and f.lower().endswith((".jpg", ".jpeg"))
    )
    if not frames:
        sys.exit("错误：未抽取到任何帧，请检查视频是否可正常解码。")

    for path in frames:
        print(path)


if __name__ == "__main__":
    main()
