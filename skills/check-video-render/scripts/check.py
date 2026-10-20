#!/usr/bin/env python3
"""Gate a rendered video before anyone watches it.

    python3 check.py <video> [--frames N] [--fps 30] [--lufs -14] [--lufs-tol 1] [--tp -1] [--cuts] [--allow-silent-tail]

Prints one line per check and a JSON summary. Exit 0 when every check passes, 1 when any check
fails, and 2 when the file cannot be read or an argument is wrong.
The frame rate is checked only when --fps names the planned rate; otherwise it is printed.
Needs ffmpeg and ffprobe on PATH.
"""
import json
import re
import subprocess
import sys


def opt(name, default=None, cast=str):
    a = sys.argv
    if name not in a:
        return default
    i = a.index(name) + 1
    try:
        return cast(a[i])
    except (IndexError, ValueError):
        print(f"check.py: {name} needs a {cast.__name__} value", file=sys.stderr)
        sys.exit(2)


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def ff_filter(path, af=None, vf=None):
    args = ["ffmpeg", "-hide_banner", "-nostats", "-i", path]
    args += ["-af", af, "-vn"] if af else ["-vf", vf, "-an"]
    return run(*args, "-f", "null", "-").stderr


def moov_first(path):
    with open(path, "rb") as f:
        while True:
            head = f.read(8)
            if len(head) < 8:
                return False
            size, kind = int.from_bytes(head[:4], "big"), head[4:]
            if kind == b"moov":
                return True
            if kind == b"mdat":
                return False
            if size == 1:
                size = int.from_bytes(f.read(8), "big") - 8
            if size < 8:
                # 0 means the box runs to the end of the file, and under 8 is malformed. Either way no moov follows.
                return False
            f.seek(size - 8, 1)


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(__doc__.strip())
        sys.exit(0)
    if len(sys.argv) < 2 or sys.argv[1].startswith("-"):
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    path = sys.argv[1]
    want_fps, want = opt("--fps", None, float), opt("--frames", None, int)
    target, tol, tp_limit = opt("--lufs", -14, float), opt("--lufs-tol", 1, float), opt("--tp", -1, float)
    res = run("ffprobe", "-v", "error", "-count_frames", "-show_entries",
              "stream=codec_type,codec_name,profile,level,pix_fmt,width,height,r_frame_rate,nb_read_frames,duration"
              ":stream_tags=DURATION:format=duration", "-of", "json", path)
    if res.returncode or not res.stdout.strip():
        print(f"cannot read {path}: {res.stderr.strip()}", file=sys.stderr)
        sys.exit(2)
    streams = json.loads(res.stdout).get("streams", [])
    v = next((s for s in streams if s["codec_type"] == "video"), None)
    a = next((s for s in streams if s["codec_type"] == "audio"), None)
    if v is None:
        print(f"cannot read {path}: no video stream", file=sys.stderr)
        sys.exit(2)
    if a:
        # MKV and WebM keep a stream's length in a DURATION tag (H:MM:SS.ns), not in duration.
        h, m, sec = (a.get("tags", {}).get("DURATION") or "0:0:0").split(":")
        a["duration"] = a.get("duration") or str(int(h) * 3600 + int(m) * 60 + float(sec))
    results = []

    def check(name, ok, detail):
        results.append({"check": name, "ok": bool(ok), "detail": detail})
        print(f"{'PASS' if ok else 'FAIL'}  {name:18} {detail}")

    num, den = map(int, v["r_frame_rate"].split("/"))
    fps = num / den
    frames = int(v["nb_read_frames"])
    if want_fps is None:
        print(f"INFO  fps              {v['r_frame_rate']} (pass --fps to check it)")
    else:
        check("fps", abs(fps - want_fps) < 1e-3, f"{v['r_frame_rate']}, expected {want_fps:g}")
    check("frame count", want is None or frames == want, f"{frames} frames" + (f", expected {want}" if want is not None else ""))
    if a:
        gap = abs(float(a["duration"]) - frames / fps)
        check("audio covers video", gap <= 1 / fps, f"audio {float(a['duration']):.3f} s, video {frames / fps:.3f} s")
    else:
        check("audio covers video", False, "no audio stream")
    level = int(v.get("level", 0))
    browser_ok = v["codec_name"] == "h264" and v.get("pix_fmt") == "yuv420p" and 0 < level <= 51
    check("plays in browsers", browser_ok, f"{v['codec_name']} {v.get('profile')} level {level / 10:g} {v.get('pix_fmt')} (masters above level 5.1 fail in Chrome; judge them in a desktop player)")
    faststart = moov_first(path)
    check("faststart", faststart, "moov before mdat" if faststart else "run ffmpeg -c copy -movflags +faststart")

    if a:
        loud = ff_filter(path, af="ebur128=peak=true")
        i = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", loud)[-1])
        tp = float(re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", loud)[-1])
        check("loudness", abs(i - target) <= tol, f"{i} LUFS integrated, target {target} +/- {tol}")
        check("true peak", tp <= tp_limit, f"{tp} dBTP after encoding, limit {tp_limit:g}")
        sil = ff_filter(path, af="silencedetect=noise=-50dB:d=0.3")
        starts = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", sil)]
        ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", sil)]
        end_s = float(a["duration"])
        tail = starts[-1] if starts and (len(starts) > len(ends) or ends[-1] >= end_s - 0.05) else None
        allowed = "--allow-silent-tail" in sys.argv
        check("no silent tail", tail is None or allowed,
              "audio runs to the end" if tail is None
              else f"silent from {tail:.2f} s to the end, allowed by --allow-silent-tail" if allowed
              else f"silent from {tail:.2f} s to the end (a mix filter ended early?)")

    black = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", ff_filter(path, vf="blackdetect=d=0.1:pix_th=0.10"))
    print(f"INFO  black spans      {[(float(s), float(e)) for s, e in black] or 'none'}")
    if "--cuts" in sys.argv:
        cuts = re.findall(r"lavfi\.scd\.time: ([\d.]+)", ff_filter(path, vf="scale=320:-2,scdet=threshold=7"))
        print(f"INFO  cuts (scdet>7)   {len(cuts)}: {', '.join(cuts)}")

    print(json.dumps({"file": path, "frames": frames, "fps": fps, "results": results}))
    sys.exit(0 if all(r["ok"] for r in results) else 1)


if __name__ == "__main__":
    main()
