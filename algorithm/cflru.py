import collections

# ==========================================
# CFLRU 演算法實作 (符合 Framework 介面)
# ==========================================

class Page:
    """基本頁面物件"""
    def __init__(self, page_id, is_dirty=False):
        self.page_id = page_id
        self.is_dirty = is_dirty

    def __repr__(self):
        return f"Page({self.page_id}, D={self.is_dirty})"

class CFLRUAlgorithm:
    def __init__(self, capacity, window_size_ratio=0.25, mode='static', dynamic_period=1000):
        self.capacity = capacity
        # OrderedDict: 右邊是 MRU (最新)，左邊是 LRU (最舊)
        self.cache = collections.OrderedDict() 
        
        # CFLRU 特有參數
        self.mode = mode # 'static' or 'dynamic'
        # 初始視窗大小 (依據論文建議，約為 Cache 的 1/4 或 1/2)
        self.window_size = int(capacity * window_size_ratio)
        
        # --- Dynamic 調整專用參數 (僅供內部演算法調整視窗使用) ---
        # 注意：這些不是給 Framework 計分用的，是給演算法自己「爬山」用的
        self.dynamic_period = dynamic_period
        self.op_count = 0
        self.prev_period_cost = float('inf')
        self.window_direction = 1 
        self.window_step = max(1, int(capacity * 0.05))
        self.period_reads = 0
        self.period_writes = 0

    def get_name(self):
        return f"CFLRU-{self.mode.capitalize()}"

    def get_current_window_size(self):
        return max(0, min(self.capacity, self.window_size))

    def access_page(self, page_id, is_write):
        """
        Framework 呼叫此函式。
        回傳: (is_hit, victim_page)
        """
        self.op_count += 1
        
        is_hit = False
        victim = None
        
        # 1. Check Hit/Miss
        if page_id in self.cache:
            # === HIT ===
            is_hit = True
            page = self.cache.pop(page_id)
            if is_write:
                page.is_dirty = True
            self.cache[page_id] = page # Move to MRU
        else:
            # === MISS ===
            is_hit = False
            # 內部計數，供動態調整參考
            self.period_reads += 1 
            
            # 檢查容量
            if len(self.cache) >= self.capacity:
                victim = self.evict() # 呼叫踢人邏輯
            
            # 建立新頁面並加入 MRU
            new_page = Page(page_id, is_dirty=is_write)
            self.cache[page_id] = new_page

        # 2. Dynamic Adjustment (如果是 dynamic 模式，每隔一段時間調整一次)
        if self.mode == 'dynamic' and self.op_count % self.dynamic_period == 0:
            self.adjust_window()

        # 3. 回傳結果給 Framework
        return is_hit, victim

    def evict(self):
        """
        CFLRU 核心踢人邏輯：
        在 LRU 端 (List 頭部) 的 Window 範圍內，優先找乾淨的踢。
        回傳: 被踢掉的 Page 物件
        """
        window_size = self.get_current_window_size()
        
        # 取得 LRU 端的前 window_size 個候選頁面 (OrderedDict keys 回傳順序為 LRU->MRU)
        candidates = list(self.cache.keys())[:window_size] 
        
        victim_id = None
        
        # 策略：優先找 Clean Page
        for pid in candidates:
            if not self.cache[pid].is_dirty:
                victim_id = pid
                break
        
        # 如果沒找到 (全髒) 或 Window=0，退化回標準 LRU (踢最舊的)
        if victim_id is None:
            victim_id = next(iter(self.cache))
            
        # 執行移除
        victim_page = self.cache.pop(victim_id)
        
        # 如果踢掉的是髒頁面，記錄內部成本供動態調整參考
        if victim_page.is_dirty:
            self.period_writes += 1
            
        return victim_page

    def adjust_window(self):
        """
        動態調整視窗大小 (Hill Climbing 演算法)
        """
        # 計算本週期成本 (Cost = Read + 8 * Write)
        current_cost = self.period_reads + 8 * self.period_writes
        
        # 如果成本變高了，代表上次調整方向錯誤，反轉方向
        if current_cost > self.prev_period_cost:
            self.window_direction *= -1
        
        # 應用調整
        self.window_size += (self.window_direction * self.window_step)
        
        # 邊界檢查
        self.window_size = max(0, min(self.capacity, self.window_size))
        
        # 重置週期數據
        self.prev_period_cost = current_cost
        self.period_reads = 0
        self.period_writes = 0