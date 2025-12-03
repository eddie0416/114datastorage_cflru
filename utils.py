import csv

def analyze_trace(csv_file_path, page_size_kb=4):
    """
    分析 trace.csv 並輸出 CFLRU 論文 Table 3 的統計資訊
    
    Args:
        csv_file_path: trace CSV 檔案路徑
        page_size_kb: 頁面大小 (KB)，預設 4KB
    
    Returns:
        dict: 包含 mem_used, total, instruction, read, write 的統計資訊
    """
    total = 0
    instruction = 0  # 預留欄位，若 trace 未記錄指令存取則為 0
    read = 0
    write = 0
    unique_pages = set()
    
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            total += 1
            page_id = int(row['page_id'])
            unique_pages.add(page_id)
            
            is_write = int(row['is_write'])
            if is_write == 1:
                write += 1
            else:
                read += 1

    # 計算工作集大小 (Working Set Size)
    working_set_size = len(unique_pages)
    mem_used_mb = (working_set_size * page_size_kb) / 1024
    # 一個唯一page佔4kb 轉換成mb

    # 輸出格式對齊 CFLRU Table 3 的主要資訊
    print(f"CSV Path: {csv_file_path}")
    print(f"Memory used (MB): {mem_used_mb:.2f}")
    print(f"Total: {total:,}")
    print(f"Instruction Read: {instruction:,}")
    print(f"Data Read: {read:,} ({read/total*100:.1f}%)")
    print(f"Data Write: {write:,} ({write/total*100:.1f}%)")
    print(f"Working Set Size: {working_set_size:,} 頁")

    return {
        "mem_used_mb": mem_used_mb,
        "working_set_size": working_set_size,
        "total": total,
        "instruction": instruction,
        "read": read,
        "write": write,
    }

def main():
    # 測試參數設定
    csv_file_path = "traces_cleaned/valgrind/trace_du.csv"  # 修改為你的 trace 檔案路徑
    page_size_kb = 4  # 修改為實際的頁面大小
    
    print("=== Trace Analysis ===")
    result = analyze_trace(csv_file_path, page_size_kb)
    print("\n=== Result Dictionary ===")
    print(result)

if __name__ == "__main__":
    main()
