import os
import sys
import csv
from pathlib import Path


# 頁面大小常數 (4KB = 4096 bytes)
PAGE_SIZE = 4096


def parse_trace_line(line):
    """
    解析單行 trace 資料，提取地址和操作類型
    
    Returns:
        tuple: (地址十六進位字串, is_write) 或 (None, None) 如果無效
    """
    line = line.strip()
    if not line:
        return None, None
    
    parts = line.split()
    if len(parts) < 2:
        return None, None
    
    operation = parts[0].upper()
    address = parts[1].replace(',', '')  # 移除逗號分隔符
    
    # 將操作類型對應到 is_write (0=讀取, 1=寫入)
    # i/l/0 -> 0 (讀取)
    # s/m/1 -> 1 (寫入)
    read_ops = ['I', 'L', '0']
    write_ops = ['S', 'M', '1']
    
    if operation in read_ops:
        is_write = 0
    elif operation in write_ops:
        is_write = 1
    else:
        return None, None
    
    return address, is_write


def calculate_page_id(address_hex):
    """
    從十六進位地址計算 page ID
    
    Args:
        address_hex: 十六進位格式的地址 (可有或無 0x 前綴)
    
    Returns:
        int: Page ID
    """
    # 移除 '0x' 前綴（如果存在）
    if address_hex.startswith('0x'):
        address_hex = address_hex[2:]
    
    # 轉換為整數並計算 page ID
    address_int = int(address_hex, 16)
    page_id = address_int // PAGE_SIZE
    
    return page_id


def process_trace_file(input_path, output_path, preview_rows=3):
    """
    處理單個 trace 檔案並轉換為清理後的 CSV 格式
    """
    print(f"讀取檔案: {input_path}")
    print("=" * 80)
    
    try:
        # 預覽前 N 行 - 使用 UTF-8 編碼並忽略錯誤
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            preview_count = 0
            for i, line in enumerate(f):
                if preview_count >= preview_rows:
                    break
                if line.strip():
                    print(f"第 {i+1} 行: {line.rstrip()}")
                    preview_count += 1
        
        print("=" * 80)
        
        # 處理並寫入 CSV
        processed_count = 0
        skipped_count = 0
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 同樣使用 UTF-8 編碼處理主檔案
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as infile, \
             open(output_path, 'w', newline='') as outfile:
            csv_writer = csv.writer(outfile)
            csv_writer.writerow(['page_id', 'is_write'])
            
            for line in infile:
                address, is_write = parse_trace_line(line)
                
                if address is None:
                    skipped_count += 1
                    continue
                
                try:
                    page_id = calculate_page_id(address)
                    csv_writer.writerow([page_id, is_write])
                    processed_count += 1
                except ValueError as e:
                    skipped_count += 1
                    continue
        
        print(f"✓ 已處理 {processed_count} 行")
        if skipped_count > 0:
            print(f"  跳過 {skipped_count} 行無效資料")
        print(f"✓ 輸出儲存至: {output_path}")
        print()
        
        return True
        
    except FileNotFoundError:
        print(f"✗ 錯誤: 找不到檔案 '{input_path}'")
        print()
        return False
    except Exception as e:
        print(f"✗ 處理檔案時發生錯誤: {e}")
        print()
        return False



def find_trace_files(root_dir):
    """
    在 traces 目錄中尋找所有 .trace 和 .txt 檔案
    
    Args:
        root_dir: 根目錄路徑 (例如: 'traces')
    
    Returns:
        list: Path 物件列表，包含所有 trace 檔案
    """
    root_path = Path(root_dir)
    
    if not root_path.exists():
        print(f"錯誤: 找不到目錄 '{root_dir}'")
        return []
    
    trace_files = []
    
    # 尋找所有 .trace 和 .txt 檔案
    for ext in ['*.trace', '*.txt']:
        trace_files.extend(root_path.rglob(ext))
    
    return sorted(trace_files)


def main():
    """
    主函數：處理 traces 目錄下的所有 trace 檔案
    
    使用方式: 
        python data_clean.py                    # 處理 'traces' 目錄下的所有檔案
        python data_clean.py <自訂目錄>          # 處理自訂目錄下的所有檔案
    """
    # 決定輸入目錄
    if len(sys.argv) >= 2:
        input_dir = sys.argv[1]
    else:
        input_dir = 'traces'
    
    print(f"在 '{input_dir}' 目錄中搜尋 trace 檔案...")
    print()
    
    # 尋找所有 trace 檔案
    trace_files = find_trace_files(input_dir)
    
    if not trace_files:
        print(f"在 '{input_dir}' 中找不到 .trace 或 .txt 檔案")
        return
    
    print(f"找到 {len(trace_files)} 個 trace 檔案:")
    for f in trace_files:
        print(f"  - {f}")
    print()
    print("=" * 80)
    print()
    
    # 處理每個檔案
    success_count = 0
    
    for trace_file in trace_files:
        # 建立輸出路徑：將 'traces' 替換為 'traces_cleaned'
        relative_path = trace_file.relative_to(input_dir)
        output_file = Path('traces_cleaned') / relative_path
        
        # 將副檔名改為 .csv
        output_file = output_file.with_suffix('.csv')
        
        # 處理檔案
        if process_trace_file(trace_file, output_file):
            success_count += 1
    
    # 總結
    print("=" * 80)
    print(f"\n處理完成！")
    print(f"成功處理 {success_count}/{len(trace_files)} 個檔案")
    print(f"輸出目錄: traces_cleaned/")


if __name__ == "__main__":
    main()
