from lru_algo import LRUAlgorithm
from cflru import CFLRUAlgorithm
import csv
from tqdm import tqdm  # pip install tqdm

def test_framework(algo, csv_path, verbose=False):
    """
    Framework 主程式
    :param algo: 演算法物件 (LRUAlgorithm or CFLRUAlgorithm)
    :param csv_path: Trace CSV 的路徑
    :param verbose: True 顯示詳細 Log, False 顯示進度條
    """
    
    print(f"=== Testing {algo.get_name()} (Capacity={algo.capacity}) ===")
    
    # 1. 讀取 Trace 資料
    trace = []
    try:
        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                page_id = int(row['page_id'])
                is_write = bool(int(row['is_write']))  # 0 -> False, 1 -> True
                trace.append((page_id, is_write))
    except FileNotFoundError:
        print(f"Error: 找不到檔案 {csv_path}")
        return

    # 統計變數
    total_miss = 0
    total_cost = 0
    total_access = len(trace)
    flash_writes = 0
    
    # 2. 設定 Iterator
    # 如果是 verbose 模式，直接用 list (因為要 print，不需要進度條干擾)
    # 如果不是 verbose，使用 tqdm 包裝 list 顯示進度條
    iterator = trace if verbose else tqdm(trace, desc=f"Simulating {algo.get_name()}", unit="ops")

    # 3. 主迴圈
    for pid, is_w in iterator:
        op = "Write" if is_w else "Read"
        
        # === 呼叫演算法 ===
        is_hit, victim = algo.access_page(pid, is_w)
        # ==================
        
        # 計分邏輯
        if not is_hit:
            total_miss += 1
            total_cost += 1  # Miss Read Cost
            
            if victim and victim.is_dirty:
                total_cost += 8  # Dirty Eviction Write Cost
                flash_writes += 1

        # === Log 輸出控制 ===
        if verbose:
            status = "HIT" if is_hit else "MISS"
            victim_info = f"Evicted: {victim}" if victim else "No Eviction"
            
            print(f"[{op} {pid}]: {status}. {victim_info}")
            # 如果 Cache 太大，印出來會很亂，建議只在小容量測試時印出內容
            if algo.capacity <= 20: 
                print(f"   Current Cache: {list(algo.cache.values())}")
            print("-" * 30)

    # 4. 輸出最終統計結果
    print(f"\nSimulation Finished!")
    print(f"Algorithm: {algo.get_name()}")
    print(f"Total Access: {total_access}")
    print(f"Miss Rate: {total_miss/total_access:.2%}")
    print(f"Total Cost: {total_cost}")
    print(f"Flash Writes: {flash_writes}")

if __name__ == "__main__":
    csv_file_path = r"traces_cleaned\valgrind\trace_tr.csv"
    
    # 情境 1: 跑大數據實驗 (關閉 verbose，顯示進度條)
    # 這裡的 Capacity 設大一點比較符合真實 gcc 的規模
    print("--- Running Full Simulation ---")
    algo = CFLRUAlgorithm(capacity=30) 
    test_framework(algo, csv_file_path, verbose=False)

    print("\n" + "="*50 + "\n")