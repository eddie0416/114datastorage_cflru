#用於清理buffer cache的data
import os

# ====== 你只需要改這裡 ======
INPUT_PATH = "buffer_cache_trace/FileSystemBufferCache/WebSearch3.spc"          # 原始 trace 路徑
OUTPUT_PATH = "buffer_cache_trace_cleaned/WebSearch3.csv"   # 輸出路徑

LBA_SIZE = 512     # 固定 512B per LBA
PAGE_SIZE = 4096   # 模擬器 page 大小（需要的話改）
# ============================


def parse_records(text: str):
    """
    接受整段文字（可有空白/換行），回傳每筆 (asu, lba, size, op, ts)
    """
    # 允許空白或換行分隔多筆
    tokens = text.split()
    for tok in tokens:
        parts = tok.split(',')
        if len(parts) != 5:
            continue
        asu_str, lba_str, size_str, op_str, ts_str = parts
        yield (
            int(asu_str),
            int(lba_str),
            int(size_str),
            op_str.strip().lower(),
            float(ts_str),
        )


def convert():
    # 確保輸出資料夾存在
    out_dir = os.path.dirname(OUTPUT_PATH)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # 讀取輸入
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        text = f.read().strip()

    out_lines = ["page_id,is_write"]

    for asu, lba, size, op, ts in parse_records(text):
        is_write = 1 if op == "w" else 0

        start_addr = lba * LBA_SIZE
        end_addr = start_addr + size  # bytes

        start_page = start_addr // PAGE_SIZE
        end_page = (end_addr - 1) // PAGE_SIZE  # inclusive

        for pid in range(start_page, end_page + 1):
            out_lines.append(f"{pid},{is_write}")

    # 寫出輸出
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))

    print(f"Done. Wrote {len(out_lines)-1} lines to {OUTPUT_PATH}")


if __name__ == "__main__":
    convert()
