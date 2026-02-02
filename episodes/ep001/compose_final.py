#!/usr/bin/env python3
"""
compose_final.py — Fuxi EP001 Video Composition
────────────────────────────────────────────────
Reads shots.json, normalizes all shots to 1080×1920,
applies slowmo / trim, scene transitions, mixes audio.
Output: video/final_draft.mp4
"""
import json, os, subprocess, sys, shutil
from pathlib import Path

# ── Paths ──
BASE = Path("/home/dz/fuxi/episodes/ep001")
VIDEO = BASE / "video"
AUDIO = BASE / "audio"
TEMP = VIDEO / "temp_compose"
OUTPUT = VIDEO / "final_draft.mp4"
W, H, FPS = 1080, 1920, 24

# ── Scene-boundary transitions ──
# Derived from shots.json notes:
#   S05 → S06: "闪白转场到下一场" → fadewhite
#   S08 → S09: continuous action  → dissolve
#   S12 → S13: "氛围急转"        → hard_cut (dramatic break)
#   S19 → S20: end card           → fadeblack
SCENE_TRANSITIONS = {
    "S05->S06": {"type": "fadewhite", "dur": 0.5},
    "S08->S09": {"type": "dissolve", "dur": 0.5},
    "S12->S13": {"type": "hard_cut",  "dur": 0},
    "S19->S20": {"type": "fadeblack", "dur": 1.0},
}
HARD_CUT = {"type": "hard_cut", "dur": 0}


# ════════════════════════════════════════════
# Helpers
# ════════════════════════════════════════════
def run_ff(cmd, desc=""):
    tag = f"[{desc}] " if desc else ""
    print(f"  {tag}{cmd[:130]}…")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"  ✗ FAILED:\n{r.stderr[-600:]}")
        sys.exit(1)
    return r


def get_dur(path):
    r = subprocess.run(
        f'ffprobe -v quiet -show_entries format=duration -of csv=p=0 "{path}"',
        shell=True, capture_output=True, text=True,
    )
    return float(r.stdout.strip()) if r.stdout.strip() else 0.0


def find_source(sid):
    """Prefer _video.mp4 (img2vid), fallback to .mp4 (original render)."""
    for name in [f"{sid}_video.mp4", f"{sid}.mp4"]:
        p = VIDEO / name
        if p.exists():
            return p
    return None


def find_audio(sid):
    """Return list of audio files for a shot."""
    out = []
    for name in [f"{sid}.wav", f"{sid}_narration.wav"]:
        p = AUDIO / name
        if p.exists():
            out.append(p)
    return out


# ════════════════════════════════════════════
# Main
# ════════════════════════════════════════════
def main():
    # Clean temp
    if TEMP.exists():
        shutil.rmtree(TEMP)
    TEMP.mkdir(parents=True)

    with open(BASE / "shots.json") as f:
        data = json.load(f)

    shots = data["shots"]
    all_ids = [s["shot_id"] for s in shots]
    target_dur = {s["shot_id"]: s["duration_s"] for s in shots}

    # ───────────────────────────────────────
    # Phase 1 — Normalize each shot
    # ───────────────────────────────────────
    print("\n" + "═" * 52)
    print("  Phase 1: Normalize shots → 1080×1920")
    print("═" * 52)

    norm = {}   # sid → path
    ndur = {}   # sid → actual duration

    for shot in shots:
        sid = shot["shot_id"]
        src = find_source(sid)
        if not src:
            print(f"  ⚠  {sid}: no source video — skipping")
            continue

        out = TEMP / f"{sid}.mp4"
        vf = []

        # Duration adjustment
        if sid in ("S01", "S02"):
            vf.append(f"trim=0:{target_dur[sid]},setpts=PTS-STARTPTS")
        elif sid == "S20":
            pass  # already 1080×1920 @ 2 s
        else:
            # S03–S19: 2× slowmo (~2 s → ~4 s)
            vf.append("setpts=2*PTS")

        # Scale / pad to target resolution
        vf += [
            f"scale={W}:{H}:force_original_aspect_ratio=decrease",
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black",
            f"fps={FPS}",
            "setsar=1",
        ]

        cmd = (
            f'ffmpeg -y -i "{src}" '
            f'-vf "{",".join(vf)}" '
            f"-c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p "
            f'-an "{out}"'
        )
        run_ff(cmd, f"Norm {sid}")

        d = get_dur(out)
        norm[sid] = out
        ndur[sid] = d
        print(f"  ✓ {sid}: {d:.2f}s  (target {target_dur[sid]}s)")

    avail = [sid for sid in all_ids if sid in norm]
    print(f"\n  Shots ready: {len(avail)}/{len(all_ids)}")

    # ───────────────────────────────────────
    # Phase 2 — Transition plan
    # ───────────────────────────────────────
    print("\n" + "═" * 52)
    print("  Phase 2: Transition plan")
    print("═" * 52)

    cut_trans = {}  # index → transition dict
    for i in range(len(avail) - 1):
        key = f"{avail[i]}->{avail[i+1]}"
        t = SCENE_TRANSITIONS.get(key, HARD_CUT)
        cut_trans[i] = t
        if t["type"] != "hard_cut":
            print(f"  {key}: {t['type']} ({t['dur']}s)")

    # Group consecutive hard-cuts
    groups = []           # list of [sid, …]
    group_trans = []      # transition AFTER each group (except last)
    cur = [avail[0]]

    for i in range(1, len(avail)):
        t = cut_trans.get(i - 1, HARD_CUT)
        if t["type"] == "hard_cut":
            cur.append(avail[i])
        else:
            groups.append(cur)
            group_trans.append(t)
            cur = [avail[i]]
    groups.append(cur)

    for gi, g in enumerate(groups):
        tr = group_trans[gi]["type"] if gi < len(group_trans) else "—"
        print(f"  Group {gi}: {g[0]}…{g[-1]} ({len(g)} shots)  → {tr}")

    # ───────────────────────────────────────
    # Phase 3 — Concat within groups
    # ───────────────────────────────────────
    print("\n" + "═" * 52)
    print("  Phase 3: Hard-cut concat within groups")
    print("═" * 52)

    gfiles = []
    gdurs = []

    for gi, group in enumerate(groups):
        if len(group) == 1:
            gf = str(norm[group[0]])
            gfiles.append(gf)
            gdurs.append(ndur[group[0]])
            print(f"  Group {gi}: {group[0]} (single)")
        else:
            gf = str(TEMP / f"group_{gi}.mp4")
            clist = TEMP / f"concat_{gi}.txt"
            with open(clist, "w") as f:
                for sid in group:
                    f.write(f"file '{norm[sid]}'\n")

            cmd = f'ffmpeg -y -f concat -safe 0 -i "{clist}" -c copy "{gf}"'
            run_ff(cmd, f"Concat grp {gi}")

            d = get_dur(gf)
            gfiles.append(gf)
            gdurs.append(d)
            print(f"  Group {gi}: {len(group)} shots → {d:.2f}s")

    # ───────────────────────────────────────
    # Phase 4 — Xfade between groups
    # ───────────────────────────────────────
    print("\n" + "═" * 52)
    print("  Phase 4: Xfade transitions between groups")
    print("═" * 52)

    if len(gfiles) == 1:
        video_only = gfiles[0]
    else:
        inputs = " ".join(f'-i "{f}"' for f in gfiles)

        fparts = []
        accum = gdurs[0]
        prev = "[0:v]"

        for i, tr in enumerate(group_trans):
            td = tr["dur"]
            offset = max(0, accum - td)
            last = i == len(group_trans) - 1
            out = "[vout]" if last else f"[v{i}]"

            fparts.append(
                f"{prev}[{i+1}:v]xfade=transition={tr['type']}:"
                f"duration={td}:offset={offset:.3f}{out}"
            )
            accum = accum + gdurs[i + 1] - td
            prev = out

        fc = ";".join(fparts)
        video_only = str(TEMP / "video_no_audio.mp4")

        cmd = (
            f"ffmpeg -y {inputs} "
            f'-filter_complex "{fc}" '
            f'-map "[vout]" -c:v libx264 -preset fast -crf 18 '
            f'-pix_fmt yuv420p "{video_only}"'
        )
        run_ff(cmd, "Xfade")

        d = get_dur(video_only)
        print(f"  Video assembled: {d:.2f}s")

    # ───────────────────────────────────────
    # Phase 5 — Mix audio
    # ───────────────────────────────────────
    print("\n" + "═" * 52)
    print("  Phase 5: Audio mix")
    print("═" * 52)

    # Build shot timeline with correct offsets
    timeline = []
    ofs = 0.0
    for i, sid in enumerate(avail):
        d = ndur[sid]
        if i > 0:
            t = cut_trans.get(i - 1, HARD_CUT)
            if t["type"] != "hard_cut":
                ofs -= t["dur"]
        timeline.append({"sid": sid, "start": ofs, "dur": d})
        ofs += d

    # Collect audio inputs
    ainputs = []
    afilters = []
    aidx = 1  # index 0 = video

    for e in timeline:
        for af in find_audio(e["sid"]):
            ms = max(0, int(e["start"] * 1000))
            ainputs.append(f'-i "{af}"')
            afilters.append(
                f"[{aidx}:a]adelay={ms}|{ms},apad[a{aidx}]"
            )
            aidx += 1
            print(f"  🔊 {af.name} → {e['start']:.2f}s")

    if ainputs:
        labels = "".join(f"[a{i}]" for i in range(1, aidx))
        n = aidx - 1
        afilters.append(
            f"{labels}amix=inputs={n}:duration=first:normalize=0[aout]"
        )

        fc = ";".join(afilters)
        ai = " ".join(ainputs)

        cmd = (
            f'ffmpeg -y -i "{video_only}" {ai} '
            f'-filter_complex "{fc}" '
            f'-map 0:v -map "[aout]" '
            f"-c:v copy -c:a aac -b:a 192k "
            f'-shortest "{OUTPUT}"'
        )
        run_ff(cmd, "Audio mix")
    else:
        subprocess.run(
            f'ffmpeg -y -i "{video_only}" -c copy "{OUTPUT}"',
            shell=True,
        )
        print("  (no audio files found)")

    # ───────────────────────────────────────
    # Report
    # ───────────────────────────────────────
    fdur = get_dur(OUTPUT)
    fsize = os.path.getsize(OUTPUT)

    print(f"\n{'═'*52}")
    print(f"  ✅  {OUTPUT}")
    print(f"      Duration : {fdur:.1f}s  ({fdur/60:.1f} min)")
    print(f"      Size     : {fsize/1024/1024:.1f} MB")
    print(f"      Shots    : {len(avail)}")
    print(f"{'═'*52}")

    print("\n  Timeline:")
    for e in timeline:
        has_a = "🔊" if find_audio(e["sid"]) else "  "
        print(f"    {e['start']:7.2f}s  {has_a}  {e['sid']:4s}  ({e['dur']:.2f}s)")


if __name__ == "__main__":
    main()
