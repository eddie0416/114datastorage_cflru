class Page:
    """代表一個記憶體頁面"""
    def __init__(self, page_id, is_dirty=False):
        self.page_id = page_id
        self.is_dirty = is_dirty

    def __repr__(self):
        return f"Page({self.page_id}, Dirty={self.is_dirty})"

class ReplacementAlgorithm:
    """所有演算法都必須繼承這個父類別"""
    def __init__(self, capacity):
        self.capacity = capacity  # Cache 最大容量
        self.cache = []           # 存放 Page 物件的列表

    def access_page(self, page_id, is_write):
        """
        當 CPU 存取頁面時呼叫此函式。
        回傳值: (is_hit, victim_page)
        - is_hit: True 代表命中, False 代表 Miss
        - victim_page: 如果發生置換(Eviction)，回傳被踢掉的 Page 物件；否則回傳 None
        """
        raise NotImplementedError("請實作這個函式！")

    def get_name(self):
        """回傳演算法名稱"""
        return "Unknown Algorithm"
