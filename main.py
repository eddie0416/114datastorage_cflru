from algorithm.lru_algo import LRUAlgorithm
from algorithm.cflru import CFLRUAlgorithm
from algorithm.beladys_min_algo import BeladyMINAlgorithm
import csv
from tqdm import tqdm 
from utils import analyze_trace

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
    algo.trace = trace # 對應belady min(因為需要未來資訊)
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
'''
if __name__ == "__main__":
    csv_file_path = 'traces_cleaned/valgrind/trace_du.csv'
    result = analyze_trace(csv_file_path) # {'mem_used_mb': 13.734375, 'working_set_size': 3516, 'total': 757360, 'instruction': 0, 'read': 697439, 'write': 59921}

    # 情境 1: 跑大數據實驗 (關閉 verbose，顯示進度條)
    # 這裡的 Capacity 設大一點比較符合真實 gcc 的規模
    print("--- Running Full Simulation ---")
    algo = CFLRUAlgorithm(capacity=10) 
    test_framework(algo, csv_file_path, verbose=False)

    print("\n" + "="*50 + "\n")
'''
if __name__ == "__main__":
    # 1. 指定 Trace 檔案與分析
    csv_file_path = 'swap_system_traces_cleaned/dataset/mcf.csv'
    result = analyze_trace(csv_file_path)

    # 2. 定義三個測試級距 (0.1%, 1%, 10%)
    # 這些比例是為了適應 Trace 的區域性 [0.01, 0.05, 0.1]
    ratios = [0.001, 0.01, 0.1] 

    print("\n--- Running Scientific Simulation ---")

    for r in ratios:
        # 動態計算 Capacity
        cap = int(result['working_set_size'] * r)
        
        # 安全保護：避免 capacity 太小 (例如變成 0 或 1)
        if cap < 5: 
            cap = 5 
        
        print(f"\n{'='*20} Testing Ratio {r:.1%} (Capacity={cap}) {'='*20}")

        # --- 第二跑：CFLRU (實驗組) ---
        # 依據論文建議，Window Size 設為 Cache 的 1/4 (0.25)
        algo = BeladyMINAlgorithm(capacity=cap) 
        test_framework(algo, csv_file_path, verbose=False)
