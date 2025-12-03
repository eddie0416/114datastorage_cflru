from collections import OrderedDict, defaultdict, deque
import math

class Page:
    """代表一個記憶體頁面"""
    def __init__(self, page_id, is_dirty=False):
        self.page_id = page_id
        self.is_dirty = is_dirty

    def __repr__(self):
        return f"Page({self.page_id}, Dirty={self.is_dirty})"


class BeladyMINAlgorithm:
    """
    Belady's MIN / OPT
    介面完全比照 LRU:
      - __init__(capacity)
      - access_page(page_id, is_write) -> (is_hit, victim_page)

    需要未來 trace，但不在 __init__ 傳。
    Framework 只要在跑之前做:
        algo.trace = trace
    第一次 access_page 會自動 preprocess。
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache_map = OrderedDict()  # page_id -> Page

        # 由 framework 塞進來的完整 trace
        self.trace = None

        # positions[page_id] = deque([future_index1, future_index2, ...])
        self.positions = defaultdict(deque)

        self.t = 0
        self._built = False

    def get_name(self):
        return "Belady MIN (OPT)"

    def _build_positions(self):
        """根據 self.trace 建未來位置表（只做一次）"""
        if self.trace is None:
            raise RuntimeError(
                "BeladyMINAlgorithm requires full future trace.\n"
                "Please set algo.trace = trace in framework before simulation."
            )

        self.positions.clear()
        for idx, (pid, _) in enumerate(self.trace):
            self.positions[pid].append(idx)

        self.t = 0
        self._built = True

    def _consume_now(self, page_id):
        """把現在這次出現的位置從佇列移掉"""
        dq = self.positions[page_id]
        if dq and dq[0] == self.t:
            dq.popleft()

    def _next_use(self, page_id):
        """回傳下一次使用時間點，若不再使用則 inf"""
        dq = self.positions[page_id]
        return dq[0] if dq else math.inf

    def access_page(self, page_id, is_write):
        """
        輸入: page_id (int), is_write (bool)
        輸出: (is_hit, victim_page)
        """
        if not self._built:
            self._build_positions()

        victim = None
        is_hit = False

        # 先消耗掉現在這次 access 的位置
        self._consume_now(page_id)

        # --- Case 1: Hit ---
        if page_id in self.cache_map:
            is_hit = True
            page = self.cache_map[page_id]
            if is_write:
                page.is_dirty = True

        # --- Case 2: Miss ---
        else:
            is_hit = False

            if len(self.cache_map) >= self.capacity:
                # 受害者 = next use 最晚(或不再使用)
                victim_id = None
                farthest = -1

                for pid_in_cache in self.cache_map.keys():
                    nu = self._next_use(pid_in_cache)
                    if nu > farthest:
                        farthest = nu
                        victim_id = pid_in_cache

                victim = self.cache_map.pop(victim_id)

            new_page = Page(page_id, is_dirty=is_write)
            self.cache_map[page_id] = new_page

        self.t += 1
        return is_hit, victim
