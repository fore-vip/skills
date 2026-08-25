# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
fore-vip-tts · 文字转语音统一脚本

引擎优先级（auto 模式）：
  1. edge-tts  —— 免费网络引擎（微软 Edge TTS），音色自然、数量多，需 pip install edge-tts
  2. macOS say —— 免费本地引擎，开箱即用，仅 macOS 可用
  3. 均不可用 → 退出码 3，由 Agent 走付费方案兜底（见 references/paid-tts-providers.md）

用法：
  python3 tts.py --text "你好世界" --out ./out.mp3          # 自动选引擎+默认音色
  python3 tts.py --text "你好" --engine say --voice Tingting
  python3 tts.py --file input.txt --out ./out.mp3           # 长文本从文件读
  python3 tts.py --list-voices                              # 列出可用音色（JSON）
  python3 tts.py --list-voices --engine say                 # 仅列本地引擎音色

输出：统一转码为 mp3（say 的 aiff 经 ffmpeg/afconvert 转码；edge-tts 原生 mp3）
退出码：0 成功 | 1 参数/运行错误 | 2 指定音色不存在 | 3 无可用引擎
"""
import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile

# ---------- 引擎探测 ----------

def edge_available() -> bool:
    try:
        import edge_tts  # noqa: F401
        return True
    except ImportError:
        return False


def say_available() -> bool:
    return sys.platform == "darwin" and shutil.which("say") is not None


def pick_engine(prefer: str):
    """返回 (engine, 提示)。auto: edge 优先，say 兜底。"""
    if prefer != "auto":
        return prefer, None
    if edge_available():
        return "edge", "edge-tts（免费网络引擎，音色更自然）"
    if say_available():
        return "say", "macOS say（免费本地引擎）"
    return None, "无可用免费引擎"


# ---------- 音色列举 ----------

def list_say_voices(lang: str = "zh"):
    """解析 `say -v '?'`，返回中文音色列表。"""
    try:
        out = subprocess.run(["say", "-v", "?"], capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return []
    voices = []
    for line in out.splitlines():
        # 行格式: "Tingting            zh_CN    # 你好，我叫婷婷。"
        m = line.rsplit("#", 1)
        head = m[0].rsplit(None, 1)
        if len(head) != 2:
            continue
        name, locale = head[0].strip(), head[1].strip()
        if locale.lower().startswith(lang.lower()):
            voices.append({
                "engine": "say",
                "voice": name,
                "locale": locale,
                "sample": m[1].strip() if len(m) > 1 else "",
            })
    return voices


def list_edge_voices(lang: str = "zh"):
    """edge-tts 音色（需已安装且可联网）。失败返回 []。"""
    try:
        import edge_tts
    except ImportError:
        return []

    async def _fetch():
        vm = await edge_tts.VoicesManager.create()
        return vm.find(Language=lang)

    try:
        items = asyncio.get_event_loop().run_until_complete(_fetch())
    except Exception:
        try:
            items = asyncio.run(_fetch())
        except Exception:
            return []
    return [
        {
            "engine": "edge",
            "voice": v["ShortName"],          # 如 zh-CN-XiaoxiaoNeural
            "locale": v["Locale"],
            "gender": v.get("Gender", ""),
        }
        for v in items
    ]


# ---------- 合成 ----------

def tts_say(text: str, voice: str, out_path: str) -> str:
    """macOS say → aiff → mp3"""
    tmp_aiff = tempfile.mktemp(suffix=".aiff")
    cmd = ["say", "-v", voice, "-o", tmp_aiff, text]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"say 合成失败: {r.stderr.strip()[:200]}")
    _to_mp3(tmp_aiff, out_path)
    os.unlink(tmp_aiff)
    return out_path


def tts_edge(text: str, voice: str, out_path: str) -> str:
    """edge-tts → mp3"""
    import edge_tts

    async def _gen():
        await edge_tts.Communicate(text, voice).save(out_path)

    try:
        asyncio.get_event_loop().run_until_complete(_gen())
    except RuntimeError:
        asyncio.run(_gen())
    return out_path


def _to_mp3(src: str, dst: str):
    """aiff → mp3：优先 ffmpeg，兜底 afconvert（转 m4a 时改扩展名）。"""
    if shutil.which("ffmpeg"):
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-codec:a", "libmp3lame", "-qscale:a", "2", dst],
            check=True, capture_output=True,
        )
        return
    if shutil.which("afconvert"):
        base, _ = os.path.splitext(dst)
        m4a = base + ".m4a"
        subprocess.run(["afconvert", "-f", "m4af", "-d", "aac", src, m4a], check=True, capture_output=True)
        raise RuntimeError(f"MP3_NOT_DIRECT|{m4a}")  # 上层捕获后改写输出路径
    raise RuntimeError("无 ffmpeg / afconvert 可用于音频转码")


# ---------- 主流程 ----------

def main():
    ap = argparse.ArgumentParser(description="fore-vip-tts 文字转语音")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="待转换文本")
    g.add_argument("--file", help="从文件读取文本（长文本推荐）")
    g.add_argument("--list-voices", action="store_true", help="列出可用音色（JSON）")
    ap.add_argument("--engine", default="auto", choices=["auto", "edge", "say"], help="TTS 引擎")
    ap.add_argument("--voice", default=None, help="音色名；缺省用引擎默认音色")
    ap.add_argument("--out", default=None, help="输出 mp3 路径（默认当前目录 tts-<时间戳>.mp3）")
    args = ap.parse_args()

    # 音色列举模式
    if args.list_voices:
        result = {"engines": {}, "voices": []}
        if args.engine in ("auto", "say") and say_available():
            v = list_say_voices()
            result["engines"]["say"] = {"available": True, "count": len(v)}
            result["voices"] += v
        elif args.engine in ("auto", "say"):
            result["engines"]["say"] = {"available": False}
        if args.engine in ("auto", "edge") and edge_available():
            v = list_edge_voices()
            result["engines"]["edge"] = {"available": True, "count": len(v)}
            result["voices"] += v
        elif args.engine in ("auto", "edge"):
            result["engines"]["edge"] = {"available": False}
        print(json.dumps(result, ensure_ascii=False))
        return

    # 文本读取
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read().strip()
    else:
        text = (args.text or "").strip()
    if not text:
        print(json.dumps({"ok": False, "error": "文本为空"}, ensure_ascii=False))
        sys.exit(1)

    # 引擎选择
    engine, hint = pick_engine(args.engine)
    if engine is None:
        print(json.dumps({"ok": False, "error": "NO_ENGINE", "hint": "无免费引擎可用，走付费方案（references/paid-tts-providers.md）"}, ensure_ascii=False))
        sys.exit(3)
    if args.engine == "edge" and not edge_available():
        print(json.dumps({"ok": False, "error": "edge-tts 未安装，请先: pip3 install edge-tts"}, ensure_ascii=False))
        sys.exit(3)
    if args.engine == "say" and not say_available():
        print(json.dumps({"ok": False, "error": "say 仅 macOS 可用"}, ensure_ascii=False))
        sys.exit(3)

    # 音色校验与默认值
    voice = args.voice
    if voice:
        if engine == "say":
            known = [v["voice"] for v in list_say_voices()]
        else:
            known = [v["voice"] for v in list_edge_voices()]
        if known and voice not in known:
            print(json.dumps({"ok": False, "error": f"音色不存在: {voice}", "available": known}, ensure_ascii=False))
            sys.exit(2)
    else:
        voice = "Tingting" if engine == "say" else "zh-CN-XiaoxiaoNeural"

    # 输出路径
    import time
    out = args.out or f"tts-{int(time.time())}.mp3"
    out_dir = os.path.dirname(os.path.abspath(out))
    os.makedirs(out_dir, exist_ok=True)

    try:
        fn = tts_say if engine == "say" else tts_edge
        real_out = fn(text, voice, out)
        size = os.path.getsize(real_out)
        print(json.dumps({
            "ok": True, "engine": engine, "voice": voice,
            "file": os.path.abspath(real_out), "bytes": size, "chars": len(text),
        }, ensure_ascii=False))
    except RuntimeError as e:
        # afconvert 只能出 m4a 的情况：改写输出并按成功处理
        if str(e).startswith("MP3_NOT_DIRECT|"):
            m4a = str(e).split("|", 1)[1]
            print(json.dumps({
                "ok": True, "engine": engine, "voice": voice,
                "file": os.path.abspath(m4a), "bytes": os.path.getsize(m4a),
                "chars": len(text), "note": "无 ffmpeg，输出为 m4a",
            }, ensure_ascii=False))
        else:
            print(json.dumps({"ok": False, "error": str(e)[:300]}, ensure_ascii=False))
            sys.exit(1)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)[:300]}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
