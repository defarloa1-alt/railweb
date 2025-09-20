"""Generate ffmpeg commands to stitch multiple audio segments into a single file."""
from typing import List


def generate_ffmpeg_concat_cmd(segment_paths: List[str], out_path: str) -> List[str]:
    # Use ffmpeg concat demuxer (create a file list)
    filelist_path = out_path + ".txt"
    with open(filelist_path, "w", encoding="utf-8") as f:
        for p in segment_paths:
            f.write(f"file '{p}'\n")
    cmd = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        filelist_path,
        "-c",
        "copy",
        out_path,
    ]
    return cmd


if __name__ == "__main__":
    print("Example:")
    print(generate_ffmpeg_concat_cmd(["/tmp/a.mp3", "/tmp/b.mp3"], "/tmp/out.mp3"))
