from collections import OrderedDict

class Page:
    """代表一個記憶體頁面"""
    def __init__(self, page_id, is_dirty=False):
        self.page_id = page_id
        self.is_dirty = is_dirty

    def __repr__(self):
        return f"Page({self.page_id}, Dirty={self.is_dirty})"

class LRUAlgorithm:
    def __init__(self, capacity):
        self.capacity = capacity
        # 使用 OrderedDict 來模擬 LRU
        # order: [LRU (最舊) ... MRU (最新)]
        self.cache_map = OrderedDict()

    def get_name(self):
        return "Standard LRU"

    def access_page(self, page_id, is_write):
        """
        輸入: page_id (int), is_write (bool)
        輸出: (is_hit, victim_page)
        """
        victim = None
        is_hit = False

        # --- Case 1: Hit (頁面已經在快取裡) ---
        if page_id in self.cache_map:
            is_hit = True
            # 1. 把頁面拿出來
            page = self.cache_map.pop(page_id)
            
            # 2. 如果這次是寫入，要把髒標記設為 True
            # (注意：如果原本就是髒的，它還是髒的；原本乾淨但這次寫入，變髒)
            if is_write:
                page.is_dirty = True
            
            # 3. 放回 Dictionary 的尾端 (標記為 MRU 最近剛用過)
            self.cache_map[page_id] = page

        # --- Case 2: Miss (頁面不在快取裡) ---
        else:
            is_hit = False
            
            # 1. 檢查空間是否滿了，滿了就要踢人
            if len(self.cache_map) >= self.capacity:
                # popitem(last=False) 會移除最前面(由左邊)的元素，也就是 LRU
                victim_id, victim_page = self.cache_map.popitem(last=False)
                victim = victim_page # 這就是我要回傳給你的「受害者」

            # 2. 建立新頁面
            new_page = Page(page_id, is_dirty=is_write)
            
            # 3. 放入快取 (會自動放到尾端 MRU)
            self.cache_map[page_id] = new_page

        # 回傳給 Framework
        return is_hit, victim