# -*- coding: utf-8 -*-
"""
HỆ THỐNG TỰ ĐỘNG CHO XE DỌN RÁC DI CHUYỂN VÀ THU GOM RÁC
TRONG MÔI TRƯỜNG CÓ VẬT CẢN ĐỘNG, TẦM NHÌN GIỚI HẠN
Mô phỏng tại: Khuôn viên Trường Đại học Sư phạm Kỹ thuật TP.HCM (HCMUTE)
              (Tiền thân ĐH Sư phạm Kỹ thuật - ĐH Công nghệ Kỹ thuật)

Thành viên thực hiện:
- Nguyễn Ngọc Hải Yến - MSSV: 25139062 (Thuật toán quét bao phủ, A*, cập nhật đường đi)
- Trương Cảnh Hào     - MSSV: 25139011 (Xử lý vật cản động, thu gom rác, trực quan hóa Pygame)
"""

import sys
import os
import math
import random
import heapq
import time
from collections import deque
import pygame

# Cấu hình UTF-8 cho console Windows
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Khởi tạo pygame
pygame.init()
pygame.font.init()

# 1.CẤU HÌNH HỆ THỐNG & KÍCH THƯỚC (CONFIG & RESOLUTION)
GRID_COLS = 36          # 36 cột
GRID_ROWS = 28          # 28 hàng
CELL_SIZE = 26          # Kích thước mỗi ô lưới (pixel)

MAP_WIDTH = GRID_COLS * CELL_SIZE   # 936 px
MAP_HEIGHT = GRID_ROWS * CELL_SIZE  # 728 px
SIDEBAR_WIDTH = 440                 # Bảng điều khiển HUD bên phải
TOPBAR_HEIGHT = 68                  # Thanh tiêu đề phía trên

WINDOW_WIDTH = MAP_WIDTH + SIDEBAR_WIDTH  # 1376 px
WINDOW_HEIGHT = TOPBAR_HEIGHT + MAP_HEIGHT # 796 px

# Cấu hình cảm biến và vận hành của xe
SENSOR_RADIUS = 3.8     # Bán kính cảm biến tầm nhìn (đơn vị ô lưới)
ROBOT_SPEED_DELAY = 100 # ms mỗi bước của xe (có thể tăng giảm realtime bằng phím +/-)
MAX_WAIT_STEPS = 3      # Giới hạn số bước chờ khi tránh va chạm trước khi tìm đường khác
TRASH_SPAWN_INTERVAL = 3.0 # Số giây tự động xuất hiện rác ngẫu nhiên

# Bảng màu sắc đồ họa sắc nét cao cấp (Color Palette)
COLOR_BG = (15, 20, 30)               # Nền ứng dụng (Dark Slate Blue)
COLOR_TOPBAR = (20, 26, 38)           # Nền Topbar
COLOR_SIDEBAR = (18, 24, 35)          # Nền Sidebar
COLOR_CARD = (26, 34, 48)             # Nền Card thông tin
COLOR_CARD_BORDER = (42, 54, 76)      # Viền Card
COLOR_TEXT_WHITE = (245, 248, 252)    # Chữ sáng chính
COLOR_TEXT_MUTED = (140, 155, 175)    # Chữ phụ
COLOR_TEXT_ACCENT = (56, 189, 248)    # Xanh neon Sky Blue
COLOR_ACCENT_GREEN = (52, 211, 153)   # Xanh lục bảo sạch
COLOR_ACCENT_ORANGE = (251, 146, 60)  # Cam cứu hộ
COLOR_ACCENT_RED = (248, 113, 113)    # Đỏ cảnh báo
COLOR_ACCENT_YELLOW = (250, 204, 21)  # Vàng chú ý
COLOR_ACCENT_PURPLE = (192, 132, 252) # Tím công nghệ

# Màu sắc bản đồ khuôn viên HCMUTE
COLOR_ROAD = (220, 226, 235)          # Đường nhựa/bê tông nội bộ sáng sắc nét
COLOR_ROAD_CLEAN = (195, 245, 225)    # Đường đã được quét sạch bóng
COLOR_ROAD_BORDER = (185, 192, 202)   # Viền gạch lát đường
COLOR_GRASS = (115, 185, 105)         # Thảm cỏ xanh mát
COLOR_WATER = (56, 189, 248)          # Hồ nước / đài phun nước

# Phông chữ hệ thống hỗ trợ tiếng Việt sắc nét
FONT_TITLE = pygame.font.SysFont("segoeui", 17, bold=True)
FONT_SUBTITLE = pygame.font.SysFont("segoeui", 12, bold=False)
FONT_HEADING = pygame.font.SysFont("segoeui", 13, bold=True)
FONT_NORMAL = pygame.font.SysFont("segoeui", 12, bold=False)
FONT_BOLD = pygame.font.SysFont("segoeui", 12, bold=True)
FONT_SMALL = pygame.font.SysFont("segoeui", 10, bold=False)
FONT_TINY = pygame.font.SysFont("segoeui", 9, bold=False)

# 2.KHỞI TẠO BẢN ĐỒ KHUÔN VIÊN TRƯỜNG ĐH SPKT (HCMUTE CAMPUS MAP)
CELL_EMPTY_ROAD = 0   # Đường đi (Xe có thể di chuyển)
CELL_BUILDING   = 1   # Tòa nhà (Vật cản cố định)
CELL_GARDEN     = 2   # Bồn hoa / Thảm cỏ (Không đi được)
CELL_WATER      = 3   # Hồ nước cảnh quan / Đài phun nước (Không đi được)
CELL_SPORTS     = 4   # Sân vận động / Sân bóng đá mini cỏ nhân tạo

class BuildingInfo:
    def __init__(self, name, rect, code, sub_code, color, border_color):
        self.name = name           # Tên đầy đủ
        self.rect = rect           # (col, row, width, height) tính theo ô
        self.code = code           # Ký hiệu chính (TT, KHU A, KHU B...)
        self.sub_code = sub_code   # Ký hiệu phụ (12 TẦNG, GIẢNG ĐƯỜNG...)
        self.color = color         # Màu mái
        self.border_color = border_color

def create_hcmute_campus():
    """
    Xây dựng sơ đồ khuôn viên Đại học Sư phạm Kỹ thuật TP.HCM (HCMUTE).
    Địa chỉ: Số 1 Võ Văn Ngân, TP. Thủ Đức, TP. Hồ Chí Minh.
    """
    grid = [[CELL_EMPTY_ROAD for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    
    # 1.Danh sách các tòa nhà & công trình cố định
    buildings = [
        # Tòa nhà Trung tâm Điều hành 12 tầng (Biểu tượng kiến trúc HCMUTE)
        BuildingInfo("TÒA NHÀ TRUNG TÂM", (13, 17, 10, 5), "TÒA TRUNG TÂM", "12 TẦNG ĐIỀU HÀNH", (45, 85, 140), (25, 55, 95)),
        
        # Giảng đường Khu A
        BuildingInfo("KHU GIẢNG ĐƯỜNG A", (4, 16, 6, 6), "KHU A", "GIẢNG ĐƯỜNG", (185, 80, 65), (135, 50, 40)),
        
        # Thư viện số (Phía Tây)
        BuildingInfo("THƯ VIỆN SỐ", (4, 9, 6, 4), "THƯ VIỆN SỐ", "DIGITAL LIBRARY", (55, 115, 110), (35, 80, 75)),
        
        # Giảng đường Khu B
        BuildingInfo("KHU GIẢNG ĐƯỜNG B", (13, 9, 10, 5), "KHU B", "GIẢNG ĐƯỜNG", (195, 125, 55), (145, 85, 30)),
        
        # Giảng đường Khu C
        BuildingInfo("KHU GIẢNG ĐƯỜNG C", (13, 2, 10, 4), "KHU C", "KHOA ĐIỆN - ĐT", (170, 105, 75), (120, 70, 45)),
        
        # Khu xưởng thực hành E (Khoa Cơ khí Chế tạo máy & Ô tô)
        BuildingInfo("KHU XƯỞNG CÔNG NGHỆ E", (26, 15, 7, 7), "XƯỞNG E", "CƠ KHÍ & ĐỘNG LỰC", (85, 95, 110), (55, 65, 80)),
        
        # Hội trường lớn & Căn tin sinh viên
        BuildingInfo("HỘI TRƯỜNG & CĂN TIN", (26, 8, 7, 4), "CĂN TIN", "DỊCH VỤ SINH VIÊN", (165, 135, 90), (120, 95, 60)),
        
        # Sân vận động cỏ nhân tạo HCMUTE
        BuildingInfo("SÂN BÓNG ĐÁ CỎ NHÂN TẠO", (26, 2, 7, 4), "SÂN BÓNG", "THỂ THAO HCMUTE", (40, 130, 50), (25, 90, 35)),
        
        # Nhà thi đấu thể thao đa năng (Phía Bắc giáp đường Lê Văn Chí)
        BuildingInfo("NHÀ THI ĐẤU ĐA NĂNG", (4, 2, 6, 4), "NHÀ THI ĐẤU", "SPORTS COMPLEX", (115, 80, 140), (80, 50, 100))
    ]
    
    # Gán các ô tòa nhà vào ma trận
    for b in buildings:
        col, row, w, h = b.rect
        for r in range(row, row + h):
            for c in range(col, col + w):
                if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
                    grid[r][c] = CELL_BUILDING

    # 2.Đài phun nước trước Tòa nhà Trung tâm
    water_area = (16, 24, 4, 2)
    for r in range(water_area[1], water_area[1] + water_area[3]):
        for c in range(water_area[0], water_area[0] + water_area[2]):
            grid[r][c] = CELL_WATER

    # 3.Thảm cỏ & Bồn hoa hoa viên
    gardens = [
        (13, 24, 2, 2),  # Cỏ bên trái đài phun nước
        (21, 24, 2, 2),  # Cỏ bên phải đài phun nước
        (14, 15, 8, 1),  # Bồn hoa ngăn Tòa TT và Khu B
        (14, 7, 8, 1),   # Bồn hoa ngăn Khu B và Khu C
        (4, 14, 6, 1),   # Thảm cỏ thư viện
        (26, 13, 7, 1)   # Cây xanh xưởng E
    ]
    for col, row, w, h in gardens:
        for r in range(row, row + h):
            for c in range(col, col + w):
                grid[r][c] = CELL_GARDEN

    return grid, buildings

# 3.THUẬT TOÁN TÌM ĐƯỜNG A* (A-STAR PATHFINDING)
def heuristic(a, b):
    """Khoảng cách Manhattan ước lượng"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(pos, grid, dynamic_obstacles_pos=None):
    """Danh sách các ô kề có thể đi (4 hướng)"""
    r, c = pos
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbors = []
    
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
            if grid[nr][nc] == CELL_EMPTY_ROAD:
                if dynamic_obstacles_pos and (nr, nc) in dynamic_obstacles_pos:
                    continue
                neighbors.append((nr, nc))
    return neighbors

def a_star_search(grid, start, goal, dynamic_obstacles_pos=None):
    """
    Tìm đường đi ngắn nhất từ start đến goal bằng thuật toán A*.
    Nếu bị chặn bởi vật cản động, thử lại với bản đồ tĩnh dự phòng.
    """
    if start == goal:
        return [start]
        
    def run_search(obs_set):
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}
        
        while frontier:
            _, current = heapq.heappop(frontier)
            
            if current == goal:
                break
                
            for next_node in get_neighbors(current, grid, obs_set):
                new_cost = cost_so_far[current] + 1
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + heuristic(goal, next_node)
                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current
                    
        if goal not in came_from:
            return None
            
        path = []
        curr = goal
        while curr is not None:
            path.append(curr)
            curr = came_from[curr]
        path.reverse()
        return path

    # Lần 1: Tránh hoàn toàn vật cản động
    path = run_search(dynamic_obstacles_pos)
    if path is not None:
        return path
        
    # Lần 2: Dự phòng theo bản đồ tĩnh nếu không có lối thoát
    return run_search(None)

# 4.CHIẾN LƯỢC QUÉT BAO PHỦ TOÀN DIỆN (BOUSTROPHEDON SWEEP PLANNER)
def generate_coverage_path(grid, start_pos=(GRID_ROWS - 2, 17)):
    """
    Sinh lộ trình quét phủ toàn bộ khuôn viên trường bắt đầu từ start_pos.
    Sử dụng kỹ thuật quét theo từng hàng Boustrophedon kết hợp A* Connector:
    Nối mượt mà các ô lối đi, đảm bảo không có bước nhảy gián đoạn.
    """
    walkable_cells = []
    for r in range(GRID_ROWS - 1, -1, -1):
        row_cells = []
        for c in range(GRID_COLS):
            if grid[r][c] == CELL_EMPTY_ROAD:
                row_cells.append((r, c))
        # Đảo chiều quét zigzag
        if (GRID_ROWS - 1 - r) % 2 == 1:
            row_cells.reverse()
        walkable_cells.extend(row_cells)

    if not walkable_cells:
        return [start_pos]

    full_path = [start_pos]
    current = start_pos
    remaining = [pt for pt in walkable_cells if pt != current]

    while remaining:
        best_idx = 0
        min_dist = float('inf')
        
        search_window = remaining[:25]
        for idx, pt in enumerate(search_window):
            d = abs(current[0] - pt[0]) + abs(current[1] - pt[1])
            if d < min_dist:
                min_dist = d
                best_idx = idx
                if d == 1:
                    break
                    
        next_target = remaining.pop(best_idx)

        if abs(current[0] - next_target[0]) + abs(current[1] - next_target[1]) == 1:
            full_path.append(next_target)
            current = next_target
        else:
            connector = a_star_search(grid, current, next_target)
            if connector and len(connector) > 1:
                full_path.extend(connector[1:])
                current = next_target
            else:
                full_path.append(next_target)
                current = next_target

    return full_path

# 5.ĐỐI TƯỢNG VẬT CẢN ĐỘNG (DYNAMIC OBSTACLE - SINH VIÊN / NGƯỜI ĐI BỘ)
class DynamicObstacle:
    """
    Đại diện cho sinh viên di chuyển trong sân trường:
    - Di chuyển tịnh tiến theo một hướng cố định.
    - Đổi hướng khi bị chặn hoặc kẹt.
    - Không chủ động né xe dọn rác.
    """
    CLOTHES_COLORS = [
        (37, 99, 235),   # Xanh dương HCMUTE
        (225, 29, 72),   # Đỏ
        (16, 185, 129),  # Xanh lục
        (147, 51, 234),  # Tím
        (245, 158, 11)   # Vàng cam
    ]

    def __init__(self, pos, grid):
        self.r, self.c = pos
        self.grid = grid
        self.direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        self.shirt_color = random.choice(self.CLOTHES_COLORS)
        self.backpack_color = (30, 41, 59)
        self.blocked_count = 0

    def get_pos(self):
        return (self.r, self.c)

    def predict_next_pos(self):
        """Dự đoán vị trí bước kế tiếp phục vụ tránh xung đột ngã rẽ"""
        nr, nc = self.r + self.direction[0], self.c + self.direction[1]
        if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and self.grid[nr][nc] == CELL_EMPTY_ROAD:
            return (nr, nc)
        return (self.r, self.c)

    def update(self, all_obstacles_pos, robot_pos):
        """Cập nhật vị trí tịnh tiến"""
        dr, dc = self.direction
        next_r, next_c = self.r + dr, self.c + dc
        
        is_valid = (
            0 <= next_r < GRID_ROWS and
            0 <= next_c < GRID_COLS and
            self.grid[next_r][next_c] == CELL_EMPTY_ROAD and
            (next_r, next_c) not in all_obstacles_pos and
            (next_r, next_c) != robot_pos
        )
        
        if is_valid:
            self.r, self.c = next_r, next_c
            self.blocked_count = 0
            if random.random() < 0.08:
                self.change_random_direction()
        else:
            self.blocked_count += 1
            self.change_random_direction()

    def change_random_direction(self):
        """Đổi hướng khi gặp vật cản"""
        candidates = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(candidates)
        for dr, dc in candidates:
            nr, nc = self.r + dr, self.c + dc
            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and self.grid[nr][nc] == CELL_EMPTY_ROAD:
                self.direction = (dr, dc)
                return

# 6.ĐỐI TƯỢNG RÁC (TRASH ITEM)
class TrashItem:
    """Các loại rác xuất hiện ngẫu nhiên trong khuôn viên trường"""
    ITEMS = [
        ("Vỏ lon nước ngọt", (239, 68, 68)),    # Đỏ
        ("Hộp sữa giấy", (59, 130, 246)),      # Xanh dương
        ("Ly trà sữa", (245, 158, 11)),        # Cam hổ phách
        ("Túi nilon", (220, 225, 235)),        # Trắng sáng
        ("Lá cây rụng", (101, 163, 13))        # Xanh rêu
    ]

    def __init__(self, pos):
        self.pos = pos # (r, c)
        name, color = random.choice(self.ITEMS)
        self.trash_type = name
        self.color = color
        self.spawn_time = time.time()

# 7.XE DỌN RÁC THÔNG MINH (CLEANING ROBOT AGENT)
class CleaningRobot:
    STATE_PATROLLING       = "ĐANG QUÉT BAO PHỦ"
    STATE_COLLECTING_TRASH = "ĐANG ĐI GOM RÁC"
    STATE_RESOLVING_BACKLOG = "ĐANG XỬ LÝ Ô BỎ SÓT"
    STATE_WAITING          = "CHỜ NHƯỜNG ĐƯỜNG"
    STATE_COMPLETED        = "HOÀN THÀNH CHU KỲ"

    def __init__(self, start_pos, grid, coverage_path):
        self.r, self.c = start_pos
        self.grid = grid
        self.coverage_path = coverage_path
        self.path_index = 0
        
        # Tập các ô đã quét và ô bị bỏ sót
        self.visited_cells = set()
        self.visited_cells.add((self.r, self.c))
        self.missed_cells = set()
        self.backlog_targets = deque()
        
        # Trạng thái và lộ trình phụ
        self.state = self.STATE_PATROLLING
        self.active_path = []
        self.active_target = None
        self.resume_path_index = None
        
        # Cảm biến và thống kê
        self.sensor_radius = SENSOR_RADIUS
        self.wait_count = 0
        self.total_steps = 0
        self.collected_trash_count = 0
        
        # Hiệu ứng đồ họa
        self.brush_angle = 0.0
        self.pulse_radius = 0.0
        self.event_logs = []
        self.log_event(f"Xe xuất phát tại Cổng Võ Văn Ngân ({self.r}, {self.c}). Bắt đầu quét khuôn viên!")

    def log_event(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.event_logs.append(f"[{timestamp}] {msg}")
        if len(self.event_logs) > 35:
            self.event_logs.pop(0)

    def get_pos(self):
        return (self.r, self.c)

    def is_in_sensor_range(self, target_pos):
        dr = target_pos[0] - self.r
        dc = target_pos[1] - self.c
        return math.sqrt(dr*dr + dc*dc) <= self.sensor_radius

    def step(self, trash_list, dynamic_obstacles):
        """Một chu kỳ điều khiển và ra quyết định của xe dọn rác"""
        self.brush_angle = (self.brush_angle + 35) % 360
        self.pulse_radius = (self.pulse_radius + 0.16) % self.sensor_radius
        self.total_steps += 1
        
        obstacles_pos = {obs.get_pos() for obs in dynamic_obstacles}
        obstacles_pred = {obs.predict_next_pos() for obs in dynamic_obstacles}

        # 1.Tự động thu gom rác nếu ô hiện tại của xe có rác
        collected_here = [t for t in trash_list if t.pos == (self.r, self.c)]
        for t in collected_here:
            trash_list.remove(t)
            self.collected_trash_count += 1
            self.log_event(f"Đã hút sạch {t.trash_type} tại ô hiện tại ({self.r}, {self.c})!")

        # 2.Quét cảm biến phát hiện rác trong tầm nhìn
        visible_trash = [t for t in trash_list if self.is_in_sensor_range(t.pos)]
        
        if visible_trash and self.state == self.STATE_PATROLLING:
            nearest_trash = min(visible_trash, key=lambda t: heuristic((self.r, self.c), t.pos))
            path_to_trash = a_star_search(self.grid, (self.r, self.c), nearest_trash.pos, obstacles_pos)
            
            if path_to_trash and len(path_to_trash) > 1:
                self.state = self.STATE_COLLECTING_TRASH
                self.resume_path_index = self.path_index
                self.active_path = path_to_trash[1:]
                self.active_target = nearest_trash.pos
                self.log_event(f"Phát hiện {nearest_trash.trash_type} tại ({nearest_trash.pos[0]}, {nearest_trash.pos[1]}). Tạm dừng quét để gom!")

        # 3.Xử lý di chuyển theo trạng thái
        next_pos = None

        if self.state == self.STATE_COLLECTING_TRASH:
            if self.active_path:
                candidate = self.active_path[0]
                if self.check_conflict(candidate, obstacles_pos, obstacles_pred):
                    self.handle_wait_or_reroute(candidate, self.active_target, obstacles_pos)
                    return
                else:
                    self.wait_count = 0
                    next_pos = self.active_path.pop(0)
            else:
                # Đã đến ô rác -> Thu gom
                collected = None
                for t in trash_list:
                    if t.pos == (self.r, self.c):
                        collected = t
                        break
                if collected:
                    trash_list.remove(collected)
                    self.collected_trash_count += 1
                    self.log_event(f"Đã gom rác thành công: {collected.trash_type}!")

                # Kiểm tra còn rác nào khác trong tầm cảm biến không
                rem_trash = [t for t in trash_list if self.is_in_sensor_range(t.pos)]
                if rem_trash:
                    nearest_t = min(rem_trash, key=lambda t: heuristic((self.r, self.c), t.pos))
                    p = a_star_search(self.grid, (self.r, self.c), nearest_t.pos, obstacles_pos)
                    if p and len(p) > 1:
                        self.active_path = p[1:]
                        self.active_target = nearest_t.pos
                        return

                # Quay lại vị trí đã ngắt lộ trình quét chính
                if self.resume_path_index is not None and self.resume_path_index < len(self.coverage_path):
                    target_checkpoint = self.coverage_path[self.resume_path_index]
                    return_path = a_star_search(self.grid, (self.r, self.c), target_checkpoint, obstacles_pos)
                    if return_path and len(return_path) > 1:
                        self.active_path = return_path[1:]
                        self.active_target = target_checkpoint
                        self.state = self.STATE_PATROLLING
                        self.path_index = self.resume_path_index
                        self.log_event(f"Gom xong rác. Quay lại lộ trình quét tại ({target_checkpoint[0]}, {target_checkpoint[1]}).")
                    else:
                        self.state = self.STATE_PATROLLING
                        self.path_index = self.resume_path_index
                else:
                    self.state = self.STATE_PATROLLING

        elif self.state in (self.STATE_PATROLLING, self.STATE_WAITING):
            # Nếu đang có lộ trình đi vòng né vật cản
            if self.active_path:
                candidate = self.active_path[0]
                if self.check_conflict(candidate, obstacles_pos, obstacles_pred):
                    self.handle_wait_or_reroute(candidate, self.active_target, obstacles_pos)
                    return
                else:
                    self.wait_count = 0
                    self.state = self.STATE_PATROLLING
                    next_pos = self.active_path.pop(0)
            elif self.path_index < len(self.coverage_path):
                target_cell = self.coverage_path[self.path_index]
                
                # Nếu đã ở vị trí này, chuyển sang ô tiếp theo
                if (self.r, self.c) == target_cell:
                    self.path_index += 1
                    if self.path_index < len(self.coverage_path):
                        target_cell = self.coverage_path[self.path_index]
                    else:
                        self.check_and_start_backlog()
                        return

                if self.check_conflict(target_cell, obstacles_pos, obstacles_pred):
                    self.handle_wait_or_reroute(target_cell, None, obstacles_pos)
                    return
                else:
                    self.wait_count = 0
                    self.state = self.STATE_PATROLLING
                    next_pos = target_cell
                    self.path_index += 1
            else:
                self.check_and_start_backlog()
                return

        elif self.state == self.STATE_RESOLVING_BACKLOG:
            if self.active_path:
                candidate = self.active_path[0]
                if self.check_conflict(candidate, obstacles_pos, obstacles_pred):
                    self.handle_wait_or_reroute(candidate, self.active_target, obstacles_pos)
                    return
                else:
                    self.wait_count = 0
                    next_pos = self.active_path.pop(0)
            else:
                self.missed_cells.discard((self.r, self.c))
                
                if self.backlog_targets:
                    next_backlog = self.backlog_targets.popleft()
                    while next_backlog in self.visited_cells and self.backlog_targets:
                        next_backlog = self.backlog_targets.popleft()
                        
                    if next_backlog not in self.visited_cells:
                        p = a_star_search(self.grid, (self.r, self.c), next_backlog, obstacles_pos)
                        if p and len(p) > 1:
                            self.active_path = p[1:]
                            self.active_target = next_backlog
                            self.log_event(f"Đang quét bù ô bỏ sót tại ({next_backlog[0]}, {next_backlog[1]}).")
                            return

                unvisited = [
                    (r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS)
                    if self.grid[r][c] == CELL_EMPTY_ROAD and (r, c) not in self.visited_cells
                ]
                if unvisited:
                    unvisited.sort(key=lambda pt: heuristic((self.r, self.c), pt))
                    self.backlog_targets.extend(unvisited[:8])
                    target = self.backlog_targets.popleft()
                    p = a_star_search(self.grid, (self.r, self.c), target, obstacles_pos)
                    if p and len(p) > 1:
                        self.active_path = p[1:]
                        self.active_target = target
                        return
                        
                self.state = self.STATE_COMPLETED
                self.log_event("HOÀN THÀNH XUẤT SẮC! Đã phủ 100% khuôn viên trường và dọn sạch các ô bỏ sót!")

        # 4.Cập nhật vị trí và đánh dấu đã quét
        if next_pos is not None:
            self.r, self.c = next_pos
            self.visited_cells.add((self.r, self.c))
            self.missed_cells.discard((self.r, self.c))

    def check_conflict(self, target_cell, obstacles_pos, obstacles_pred):
        """Dự đoán va chạm với vật cản động tại ngã rẽ"""
        if target_cell in obstacles_pos:
            return True
        if target_cell in obstacles_pred:
            return True
        return False

    def handle_wait_or_reroute(self, target_cell, ultimate_goal, obstacles_pos):
        """
        Quy tắc chờ nhường đường và tính dừng chống kẹt (Rerouting thông minh):
        - Nếu số bước chờ <= MAX_WAIT_STEPS: Xe đứng yên nhường đường cho người đi qua.
        - Nếu chờ quá giới hạn: Xe đánh dấu ô bị bỏ sót và dùng A* tìm đường vòng né tránh.
        """
        self.wait_count += 1
        if self.wait_count <= MAX_WAIT_STEPS:
            self.state = self.STATE_WAITING
            self.log_event(f"Vật cản tại ({target_cell[0]}, {target_cell[1]}). Chờ nhường đường ({self.wait_count}/{MAX_WAIT_STEPS})...")
        else:
            self.log_event(f"Vật cản chắn đường quá lâu. Bỏ qua ô ({target_cell[0]}, {target_cell[1]}) và tìm đường đi vòng!")
            self.missed_cells.add(target_cell)
            self.wait_count = 0
            
            # Tìm điểm kế tiếp trên lộ trình quét có thể đến được bằng A*
            if self.state in (self.STATE_PATROLLING, self.STATE_WAITING):
                found_reroute = False
                for offset in range(1, min(25, len(self.coverage_path) - self.path_index)):
                    future_idx = self.path_index + offset
                    future_cell = self.coverage_path[future_idx]
                    if future_cell not in obstacles_pos:
                        reroute = a_star_search(self.grid, (self.r, self.c), future_cell, obstacles_pos)
                        if reroute and len(reroute) > 1:
                            for skipped_idx in range(self.path_index, future_idx):
                                self.missed_cells.add(self.coverage_path[skipped_idx])
                            self.active_path = reroute[1:]
                            self.active_target = future_cell
                            self.path_index = future_idx
                            self.state = self.STATE_PATROLLING
                            found_reroute = True
                            self.log_event(f"Đã kích hoạt lộ trình vòng né vật cản tới ({future_cell[0]}, {future_cell[1]}).")
                            break
                if not found_reroute:
                    self.state = self.STATE_WAITING
            elif self.active_target:
                reroute = a_star_search(self.grid, (self.r, self.c), self.active_target, obstacles_pos)
                if reroute and len(reroute) > 1:
                    self.active_path = reroute[1:]

    def check_and_start_backlog(self):
        """Khởi động quét bù các ô bỏ sót sau khi quét xong lượt chính"""
        if self.missed_cells:
            unresolved = list(self.missed_cells)
            curr = (self.r, self.c)
            sorted_backlog = []
            
            while unresolved:
                nearest = min(unresolved, key=lambda pt: heuristic(curr, pt))
                sorted_backlog.append(nearest)
                unresolved.remove(nearest)
                curr = nearest

            self.backlog_targets = deque(sorted_backlog)
            self.state = self.STATE_RESOLVING_BACKLOG
            self.log_event(f"Hoàn thành lượt quét chính. Bắt đầu quay lại xử lý {len(self.backlog_targets)} ô bỏ sót!")
            
            first_target = self.backlog_targets.popleft()
            p = a_star_search(self.grid, (self.r, self.c), first_target)
            if p and len(p) > 1:
                self.active_path = p[1:]
                self.active_target = first_target
        else:
            self.state = self.STATE_COMPLETED
            self.log_event("Hoàn tất lượt quét. 100% diện tích đã được làm sạch!")

# 8.BỘ VẼ ĐỒ HỌA SẮC NÉT (HIGH-FIDELITY SHARP RENDERER)
class SharpRenderer:
    def __init__(self, screen, grid, buildings):
        self.screen = screen
        self.grid = grid
        self.buildings = buildings
        self.fog_enabled = False # Mặc định hiển thị toàn cảnh sắc nét (Bấm F để bật sương mù SLAM)
        
        self.static_map_surf = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
        self.render_static_map()

    def render_static_map(self):
        """Vẽ bản đồ nền khuôn viên trường HCMUTE sắc nét với độ phân giải cao"""
        surf = self.static_map_surf
        surf.fill(COLOR_GRASS)

        # 1.Vẽ các tuyến đường giao thông nội bộ
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.grid[r][c] == CELL_EMPTY_ROAD:
                    rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(surf, COLOR_ROAD, rect)
                    pygame.draw.rect(surf, COLOR_ROAD_BORDER, rect, 1)

        # 2.Thảm cỏ & Bồn hoa hoa viên
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.grid[r][c] == CELL_GARDEN:
                    rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(surf, (92, 172, 92), rect)
                    cx = c * CELL_SIZE + CELL_SIZE // 2
                    cy = r * CELL_SIZE + CELL_SIZE // 2
                    pygame.draw.circle(surf, (250, 220, 90), (cx, cy), 3)

        # 3.Đài phun nước cảnh quan
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.grid[r][c] == CELL_WATER:
                    rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(surf, COLOR_WATER, rect)
                    pygame.draw.rect(surf, (30, 140, 230), rect, 2)
                    cx = c * CELL_SIZE + CELL_SIZE // 2
                    cy = r * CELL_SIZE + CELL_SIZE // 2
                    pygame.draw.circle(surf, (225, 245, 255), (cx, cy), 4)

        # 4.Sân bóng đá cỏ nhân tạo
        for b in self.buildings:
            if "SÂN BÓNG" in b.name:
                col, row, w, h = b.rect
                pitch_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, w * CELL_SIZE, h * CELL_SIZE)
                pygame.draw.rect(surf, (34, 139, 34), pitch_rect)
                pygame.draw.rect(surf, (255, 255, 255), pitch_rect, 2)
                mid_x = pitch_rect.centerx
                pygame.draw.line(surf, (255, 255, 255), (mid_x, pitch_rect.top), (mid_x, pitch_rect.bottom), 1)
                pygame.draw.circle(surf, (255, 255, 255), pitch_rect.center, 14, 1)

        # 5.Các khối tòa nhà HCMUTE với hiệu ứng 3D khối và bóng đổ sắc nét
        for b in self.buildings:
            if "SÂN BÓNG" in b.name:
                continue
                
            col, row, w, h = b.rect
            bx = col * CELL_SIZE
            by = row * CELL_SIZE
            bw = w * CELL_SIZE
            bh = h * CELL_SIZE

            # Bóng đổ (Drop Shadow)
            shadow_rect = pygame.Rect(bx + 4, by + 5, bw, bh)
            shadow_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
            shadow_surf.fill((0, 0, 0, 75))
            surf.blit(shadow_surf, (bx + 4, by + 5))

            # Khối tòa nhà chính
            building_rect = pygame.Rect(bx, by, bw, bh)
            pygame.draw.rect(surf, b.color, building_rect, border_radius=5)
            pygame.draw.rect(surf, b.border_color, building_rect, width=2, border_radius=5)

            # Chi tiết kính phản quang đặc trưng của Tòa nhà Trung tâm 12 tầng HCMUTE
            if "TRUNG TÂM" in b.name:
                for yr in range(by + 8, by + bh - 8, 12):
                    for xc in range(bx + 8, bx + bw - 8, 14):
                        win_rect = pygame.Rect(xc, yr, 9, 7)
                        pygame.draw.rect(surf, (160, 220, 255), win_rect)
            else:
                inner_rect = pygame.Rect(bx + 4, by + 4, bw - 8, bh - 8)
                pygame.draw.rect(surf, (255, 255, 255, 35), inner_rect, 1)

            # Tên tòa nhà và chú thích rõ ràng
            label = FONT_BOLD.render(b.code, True, (255, 255, 255))
            label_shadow = FONT_BOLD.render(b.code, True, (0, 0, 0))
            lx = bx + (bw - label.get_width()) // 2
            ly = by + (bh - label.get_height()) // 2 - 6
            surf.blit(label_shadow, (lx + 1, ly + 1))
            surf.blit(label, (lx, ly))

            if b.sub_code:
                sub_lbl = FONT_TINY.render(b.sub_code, True, (230, 240, 255))
                slx = bx + (bw - sub_lbl.get_width()) // 2
                sly = ly + label.get_height() + 1
                surf.blit(sub_lbl, (slx, sly))

        # 6.Cổng vòm chào Cổng 1 (Đường Võ Văn Ngân) & Cổng 2 (Đường Lê Văn Chí)
        # Cổng 1: Đường Võ Văn Ngân (Phía Nam)
        p1_x, p2_x = 13 * CELL_SIZE, 22 * CELL_SIZE
        gate_y = (GRID_ROWS - 1) * CELL_SIZE + 4
        # Hai trụ cổng gạch đỏ đặc trưng HCMUTE
        pygame.draw.rect(surf, (150, 20, 20), (p1_x, gate_y - 4, 18, 22), border_radius=2)
        pygame.draw.rect(surf, (150, 20, 20), (p2_x + 8, gate_y - 4, 18, 22), border_radius=2)
        pygame.draw.rect(surf, (255, 215, 0), (p1_x, gate_y - 4, 18, 22), 1, border_radius=2)
        pygame.draw.rect(surf, (255, 215, 0), (p2_x + 8, gate_y - 4, 18, 22), 1, border_radius=2)

        # Biển hiệu vòm cổng đỏ chữ vàng
        gate_rect = pygame.Rect(p1_x + 18, gate_y, (p2_x - p1_x - 10), 18)
        pygame.draw.rect(surf, (185, 28, 28), gate_rect, border_radius=3)
        pygame.draw.rect(surf, (255, 215, 0), gate_rect, 1, border_radius=3)
        gate_lbl = FONT_BOLD.render("CỔNG 1: ĐƯỜNG VÕ VĂN NGÂN (HCMUTE)", True, (255, 255, 255))
        surf.blit(gate_lbl, (gate_rect.centerx - gate_lbl.get_width() // 2, gate_rect.centery - gate_lbl.get_height() // 2))

        # Cổng 2: Đường Lê Văn Chí (Phía Bắc)
        gate2_y = 4
        pygame.draw.rect(surf, (30, 50, 120), (p1_x, gate2_y - 2, 18, 20), border_radius=2)
        pygame.draw.rect(surf, (30, 50, 120), (p2_x + 8, gate2_y - 2, 18, 20), border_radius=2)
        pygame.draw.rect(surf, (255, 255, 255), (p1_x, gate2_y - 2, 18, 20), 1, border_radius=2)
        pygame.draw.rect(surf, (255, 255, 255), (p2_x + 8, gate2_y - 2, 18, 20), 1, border_radius=2)

        gate_rect2 = pygame.Rect(p1_x + 18, gate2_y, (p2_x - p1_x - 10), 16)
        pygame.draw.rect(surf, (30, 64, 175), gate_rect2, border_radius=3)
        pygame.draw.rect(surf, (255, 255, 255), gate_rect2, 1, border_radius=3)
        gate_lbl2 = FONT_BOLD.render("CỔNG 2: ĐƯỜNG LÊ VĂN CHÍ", True, (255, 255, 255))
        surf.blit(gate_lbl2, (gate_rect2.centerx - gate_lbl2.get_width() // 2, gate_rect2.centery - gate_lbl2.get_height() // 2))

    def draw(self, robot, trash_list, dynamic_obstacles, fps, elapsed_time):
        """Vẽ toàn bộ khung cảnh với chi tiết sắc nét"""
        # 1.Nền bản đồ tĩnh
        self.screen.blit(self.static_map_surf, (0, TOPBAR_HEIGHT))

        # 2.Vệt đường đã quét sạch (Cleaned trail)
        for (r, c) in robot.visited_cells:
            rx = c * CELL_SIZE
            ry = TOPBAR_HEIGHT + r * CELL_SIZE
            clean_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            clean_surf.fill((52, 211, 153, 75)) # Màu xanh ngọc sạch mát
            self.screen.blit(clean_surf, (rx, ry))
            if (r + c) % 4 == 0:
                pygame.draw.circle(self.screen, (255, 255, 255, 140), (rx + 6, ry + 6), 1)

        # 3.Các ô bị bỏ sót cần quay lại (Missed cells)
        for (r, c) in robot.missed_cells:
            rx = c * CELL_SIZE
            ry = TOPBAR_HEIGHT + r * CELL_SIZE
            miss_surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            miss_surf.fill((239, 68, 68, 130))
            self.screen.blit(miss_surf, (rx, ry))
            pygame.draw.rect(self.screen, (239, 68, 68), (rx, ry, CELL_SIZE, CELL_SIZE), 1)

        # 4.Đường đi dự kiến (Waypoints của xe)
        if robot.active_path:
            pts = [(robot.c * CELL_SIZE + CELL_SIZE // 2, TOPBAR_HEIGHT + robot.r * CELL_SIZE + CELL_SIZE // 2)]
            for (pr, pc) in robot.active_path:
                pts.append((pc * CELL_SIZE + CELL_SIZE // 2, TOPBAR_HEIGHT + pr * CELL_SIZE + CELL_SIZE // 2))
            if len(pts) >= 2:
                pygame.draw.lines(self.screen, (56, 189, 248), False, pts, 3)

        # 5.Điểm rác (Chỉ hiển thị nếu trong tầm cảm biến HOẶC tắt sương mù)
        for t in trash_list:
            is_visible = (not self.fog_enabled) or robot.is_in_sensor_range(t.pos)
            if is_visible:
                tx = t.pos[1] * CELL_SIZE + CELL_SIZE // 2
                ty = TOPBAR_HEIGHT + t.pos[0] * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.circle(self.screen, (0, 0, 0, 80), (tx + 1, ty + 2), 5)
                pygame.draw.circle(self.screen, t.color, (tx, ty), 6)
                pygame.draw.circle(self.screen, (255, 255, 255), (tx - 1, ty - 1), 2)

        # 6.Vật cản động (Sinh viên)
        for obs in dynamic_obstacles:
            is_visible = (not self.fog_enabled) or robot.is_in_sensor_range(obs.get_pos())
            if is_visible:
                ox = obs.c * CELL_SIZE + CELL_SIZE // 2
                oy = TOPBAR_HEIGHT + obs.r * CELL_SIZE + CELL_SIZE // 2
                
                # Bóng
                pygame.draw.circle(self.screen, (0, 0, 0, 85), (ox + 1, oy + 2), 7)
                # Người / Sinh viên
                pygame.draw.circle(self.screen, obs.shirt_color, (ox, oy), 7)
                # Balo
                pygame.draw.circle(self.screen, obs.backpack_color, (ox - 3, oy), 3)
                # Mũi tên hướng di chuyển
                dr, dc = obs.direction
                arrow_end = (ox + dc * 10, oy + dr * 10)
                pygame.draw.line(self.screen, (255, 255, 255), (ox, oy), arrow_end, 2)

        # 7.Xe dọn rác tự động (Cleaning Robot)
        rx = robot.c * CELL_SIZE + CELL_SIZE // 2
        ry = TOPBAR_HEIGHT + robot.r * CELL_SIZE + CELL_SIZE // 2

        # 7.1.Vòng tròn radar cảm biến
        sensor_px = int(robot.sensor_radius * CELL_SIZE)
        radar_surf = pygame.Surface((sensor_px * 2, sensor_px * 2), pygame.SRCALPHA)
        pygame.draw.circle(radar_surf, (56, 189, 248, 40), (sensor_px, sensor_px), sensor_px)
        pygame.draw.circle(radar_surf, (56, 189, 248, 190), (sensor_px, sensor_px), sensor_px, 1)
        
        wave_px = int(robot.pulse_radius * CELL_SIZE)
        if wave_px > 0:
            pygame.draw.circle(radar_surf, (56, 189, 248, 110), (sensor_px, sensor_px), wave_px, 1)
        self.screen.blit(radar_surf, (rx - sensor_px, ry - sensor_px))

        # 7.2.Thân xe kim loại cam
        body_rect = pygame.Rect(rx - 10, ry - 10, 20, 20)
        pygame.draw.rect(self.screen, (0, 0, 0, 95), (rx - 8, ry - 8, 20, 20), border_radius=4)
        pygame.draw.rect(self.screen, (255, 140, 0), body_rect, border_radius=4)
        pygame.draw.rect(self.screen, (200, 90, 0), body_rect, 2, border_radius=4)

        # 7.3.Hai chổi quét xoay tròn
        rad = math.radians(robot.brush_angle)
        for offset_x in [-7, 7]:
            bx = rx + offset_x
            by = ry - 8
            pygame.draw.circle(self.screen, (75, 85, 99), (bx, by), 5)
            b_end_x = int(bx + 4 * math.cos(rad))
            b_end_y = int(by + 4 * math.sin(rad))
            pygame.draw.line(self.screen, (250, 204, 21), (bx, by), (b_end_x, b_end_y), 2)

        # 7.4.Đèn tín hiệu nhấp nháy trên nóc
        led_color = (250, 204, 21) if (int(time.time() * 4) % 2 == 0) else (239, 68, 68)
        pygame.draw.circle(self.screen, led_color, (rx, ry + 2), 3)

        # 8.Sương mù tầm nhìn giới hạn (Fog of War) kiểu SLAM chuyên nghiệp
        if self.fog_enabled:
            fog_surf = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
            fog_surf.fill((15, 23, 42, 175))
            pygame.draw.circle(fog_surf, (0, 0, 0, 0), (rx, ry - TOPBAR_HEIGHT), sensor_px)
            pygame.draw.circle(fog_surf, (15, 23, 42, 90), (rx, ry - TOPBAR_HEIGHT), sensor_px, 14)
            self.screen.blit(fog_surf, (0, TOPBAR_HEIGHT))

        # 9.Topbar & Sidebar
        self.draw_topbar(fps, elapsed_time)
        self.draw_sidebar(robot, len(trash_list), len(dynamic_obstacles))

    def draw_topbar(self, fps, elapsed_time):
        """Vẽ thanh tiêu đề Header"""
        top_rect = pygame.Rect(0, 0, WINDOW_WIDTH, TOPBAR_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_TOPBAR, top_rect)
        pygame.draw.line(self.screen, COLOR_CARD_BORDER, (0, TOPBAR_HEIGHT), (WINDOW_WIDTH, TOPBAR_HEIGHT), 1)

        title_txt = FONT_TITLE.render("HỆ THỐNG XE DỌN RÁC TỰ ĐỘNG - KHUÔN VIÊN ĐẠI HỌC SƯ PHẠM KỸ THUẬT (HCMUTE)", True, COLOR_TEXT_WHITE)
        self.screen.blit(title_txt, (20, 10))

        sub_txt = FONT_SUBTITLE.render(
            "Tiền thân ĐH Sư phạm Kỹ thuật TP.HCM / ĐH Công nghệ Kỹ thuật  |  Môi trường vật cản động & Tầm nhìn giới hạn",
            True, COLOR_TEXT_ACCENT
        )
        self.screen.blit(sub_txt, (20, 38))

        author_txt = FONT_NORMAL.render("Sinh viên thực hiện: Nguyễn Ngọc Hải Yến (25139062) - Trương Cảnh Hào (25139011)", True, (250, 204, 21))
        self.screen.blit(author_txt, (WINDOW_WIDTH - author_txt.get_width() - 25, 12))

        mins = int(elapsed_time // 60)
        secs = int(elapsed_time % 60)
        status_line = f"Thời gian: {mins:02d}:{secs:02d}  |  FPS: {fps:.0f}"
        stat_render = FONT_SMALL.render(status_line, True, COLOR_TEXT_MUTED)
        self.screen.blit(stat_render, (WINDOW_WIDTH - stat_render.get_width() - 25, 38))

    def draw_sidebar(self, robot, trash_count, obstacle_count):
        """Vẽ Dashboard điều khiển bên phải"""
        side_rect = pygame.Rect(MAP_WIDTH, TOPBAR_HEIGHT, SIDEBAR_WIDTH, MAP_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR, side_rect)
        pygame.draw.line(self.screen, COLOR_CARD_BORDER, (MAP_WIDTH, TOPBAR_HEIGHT), (MAP_WIDTH, WINDOW_HEIGHT), 1)

        cur_y = TOPBAR_HEIGHT + 14
        margin_x = MAP_WIDTH + 16
        card_w = SIDEBAR_WIDTH - 32

        # 1.Trạng thái xe
        state_color = COLOR_ACCENT_GREEN
        if robot.state == CleaningRobot.STATE_COLLECTING_TRASH:
            state_color = COLOR_ACCENT_ORANGE
        elif robot.state == CleaningRobot.STATE_WAITING:
            state_color = COLOR_ACCENT_YELLOW
        elif robot.state == CleaningRobot.STATE_RESOLVING_BACKLOG:
            state_color = COLOR_ACCENT_PURPLE

        card1_rect = pygame.Rect(margin_x, cur_y, card_w, 65)
        pygame.draw.rect(self.screen, COLOR_CARD, card1_rect, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_CARD_BORDER, card1_rect, 1, border_radius=6)

        c1_title = FONT_SMALL.render("TRẠNG THÁI HOẠT ĐỘNG HIỆN TẠI", True, COLOR_TEXT_MUTED)
        self.screen.blit(c1_title, (margin_x + 12, cur_y + 8))
        
        pygame.draw.circle(self.screen, state_color, (margin_x + 20, cur_y + 38), 6)
        c1_state = FONT_HEADING.render(robot.state, True, state_color)
        self.screen.blit(c1_state, (margin_x + 34, cur_y + 28))

        cur_y += 76

        # 2.Tiến độ bao phủ (Coverage Progress Bar)
        total_walkable = sum(row.count(CELL_EMPTY_ROAD) for row in self.grid)
        coverage_pct = (len(robot.visited_cells) / total_walkable * 100) if total_walkable > 0 else 0.0

        card2_rect = pygame.Rect(margin_x, cur_y, card_w, 80)
        pygame.draw.rect(self.screen, COLOR_CARD, card2_rect, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_CARD_BORDER, card2_rect, 1, border_radius=6)

        c2_title = FONT_SMALL.render("TIẾN ĐỘ QUÉT BAO PHỦ KHUÔN VIÊN", True, COLOR_TEXT_MUTED)
        self.screen.blit(c2_title, (margin_x + 12, cur_y + 8))

        pct_txt = FONT_HEADING.render(f"{coverage_pct:.1f}%", True, COLOR_TEXT_WHITE)
        cells_txt = FONT_SMALL.render(f"({len(robot.visited_cells)} / {total_walkable} ô)", True, COLOR_TEXT_MUTED)
        self.screen.blit(pct_txt, (margin_x + 12, cur_y + 28))
        self.screen.blit(cells_txt, (margin_x + 12 + pct_txt.get_width() + 8, cur_y + 31))

        bar_x = margin_x + 12
        bar_y = cur_y + 54
        bar_w = card_w - 24
        bar_h = 10
        pygame.draw.rect(self.screen, (20, 25, 35), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
        fill_w = int(bar_w * (coverage_pct / 100.0))
        if fill_w > 0:
            pygame.draw.rect(self.screen, COLOR_ACCENT_GREEN, (bar_x, bar_y, fill_w, bar_h), border_radius=5)

        cur_y += 92

        # 3.Chỉ số hoạt động (Metrics Grid)
        card3_rect = pygame.Rect(margin_x, cur_y, card_w, 95)
        pygame.draw.rect(self.screen, COLOR_CARD, card3_rect, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_CARD_BORDER, card3_rect, 1, border_radius=6)

        c3_title = FONT_SMALL.render("CHỈ SỐ HOẠT ĐỘNG", True, COLOR_TEXT_MUTED)
        self.screen.blit(c3_title, (margin_x + 12, cur_y + 8))

        col1_x = margin_x + 12
        m1 = FONT_NORMAL.render(f"Rác đã thu gom: {robot.collected_trash_count}", True, COLOR_ACCENT_ORANGE)
        m2 = FONT_NORMAL.render(f"Rác tồn trên sân: {trash_count}", True, COLOR_TEXT_WHITE)
        self.screen.blit(m1, (col1_x, cur_y + 32))
        self.screen.blit(m2, (col1_x, cur_y + 56))

        col2_x = margin_x + card_w // 2 + 5
        m3 = FONT_NORMAL.render(f"Ô bỏ sót cần bù: {len(robot.missed_cells)}", True, COLOR_ACCENT_RED if robot.missed_cells else COLOR_TEXT_MUTED)
        m4 = FONT_NORMAL.render(f"Sinh viên (vật cản): {obstacle_count}", True, COLOR_TEXT_WHITE)
        self.screen.blit(m3, (col2_x, cur_y + 32))
        self.screen.blit(m4, (col2_x, cur_y + 56))

        cur_y += 106

        # 4.Hướng dẫn phím điều khiển
        card4_rect = pygame.Rect(margin_x, cur_y, card_w, 105)
        pygame.draw.rect(self.screen, COLOR_CARD, card4_rect, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_CARD_BORDER, card4_rect, 1, border_radius=6)

        c4_title = FONT_SMALL.render("PHÍM ĐIỀU KHIỂN TƯƠNG TÁC", True, COLOR_TEXT_MUTED)
        self.screen.blit(c4_title, (margin_x + 12, cur_y + 8))

        controls = [
            ("[SPACE]: Tạm dừng / Tiếp tục", f"[F]: Sương mù ({'BẬT' if self.fog_enabled else 'TẮT'})"),
            ("[R]: Sinh thêm rác ngẫu nhiên", "[O]: Thêm sinh viên di chuyển"),
            ("[+ / -]: Tăng / Giảm tốc độ xe", "[Click chuột]: Thả rác / Thêm người")
        ]
        line_y = cur_y + 28
        for left_c, right_c in controls:
            self.screen.blit(FONT_TINY.render(left_c, True, (200, 215, 235)), (margin_x + 12, line_y))
            self.screen.blit(FONT_TINY.render(right_c, True, (200, 215, 235)), (margin_x + card_w // 2 + 5, line_y))
            line_y += 22

        cur_y += 116

        # 5.Nhật ký sự kiện thời gian thực
        log_h = MAP_HEIGHT - (cur_y - TOPBAR_HEIGHT) - 15
        if log_h > 120:
            card5_rect = pygame.Rect(margin_x, cur_y, card_w, log_h)
            pygame.draw.rect(self.screen, COLOR_CARD, card5_rect, border_radius=6)
            pygame.draw.rect(self.screen, COLOR_CARD_BORDER, card5_rect, 1, border_radius=6)

            c5_title = FONT_SMALL.render("NHẬT KÝ SỰ KIỆN THỜI GIAN THỰC (REALTIME LOG)", True, COLOR_TEXT_MUTED)
            self.screen.blit(c5_title, (margin_x + 12, cur_y + 8))

            log_start_y = cur_y + 30
            max_lines = (log_h - 40) // 18
            visible_logs = robot.event_logs[-max_lines:]
            for log_msg in visible_logs:
                color = COLOR_TEXT_WHITE
                if "Phát hiện" in log_msg:
                    color = COLOR_ACCENT_ORANGE
                elif "thành công" in log_msg or "XUẤT SẮC" in log_msg or "hút sạch" in log_msg:
                    color = COLOR_ACCENT_GREEN
                elif "Chờ nhường đường" in log_msg or "Vật cản" in log_msg:
                    color = COLOR_ACCENT_YELLOW
                elif "bỏ sót" in log_msg or "vòng né" in log_msg:
                    color = COLOR_ACCENT_PURPLE

                log_render = FONT_TINY.render(log_msg, True, color)
                self.screen.blit(log_render, (margin_x + 12, log_start_y))
                log_start_y += 18

# 9.VÒNG LẶP CHÍNH CỦA CHƯƠNG TRÌNH (MAIN APPLICATION LOOP)
def main():
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("HCMUTE - Hệ thống xe dọn rác tự động trong môi trường có vật cản động & Tầm nhìn giới hạn")
    
    clock = pygame.time.Clock()

    # 1.Khởi tạo bản đồ khuôn viên HCMUTE
    grid, buildings = create_hcmute_campus()

    # 2.Khởi tạo xe tại Cổng chính Võ Văn Ngân
    start_pos = (GRID_ROWS - 2, 17)

    # 3.Sinh lộ trình quét bao phủ Boustrophedon
    coverage_path = generate_coverage_path(grid, start_pos)
    robot = CleaningRobot(start_pos, grid, coverage_path)

    # 4.Danh sách các ô đường có thể đi
    walkable_coords = [
        (r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS)
        if grid[r][c] == CELL_EMPTY_ROAD and (r, c) != start_pos
    ]

    # 5.Khởi tạo các điểm rác ngẫu nhiên ban đầu
    trash_list = []
    for _ in range(12):
        if walkable_coords:
            p = random.choice(walkable_coords)
            trash_list.append(TrashItem(p))

    # 6.Khởi tạo các vật cản động (Sinh viên HCMUTE)
    dynamic_obstacles = []
    for _ in range(8):
        if walkable_coords:
            p = random.choice(walkable_coords)
            dynamic_obstacles.append(DynamicObstacle(p, grid))

    # 7.Khởi tạo bộ vẽ sắc nét
    renderer = SharpRenderer(screen, grid, buildings)

    # Biến kiểm soát vòng lặp
    is_paused = False
    robot_delay = ROBOT_SPEED_DELAY
    last_robot_step_time = pygame.time.get_ticks()
    last_obstacle_step_time = pygame.time.get_ticks()
    last_trash_spawn_time = time.time()
    start_time = time.time()

    running = True
    while running:
        current_ticks = pygame.time.get_ticks()
        dt_sec = clock.tick(60) / 1000.0
        fps = clock.get_fps()
        elapsed = time.time() - start_time

        # Xử lý sự kiện từ người dùng
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    is_paused = not is_paused
                    robot.log_event("ĐÃ TẠM DỪNG MÔ PHỎNG" if is_paused else "TIẾP TỤC MÔ PHỎNG")
                elif event.key == pygame.K_f:
                    renderer.fog_enabled = not renderer.fog_enabled
                    robot.log_event(f"Sương mù tầm nhìn giới hạn (Fog of War): {'BẬT' if renderer.fog_enabled else 'TẮT'}")
                elif event.key == pygame.K_r:
                    if walkable_coords:
                        p = random.choice(walkable_coords)
                        t = TrashItem(p)
                        trash_list.append(t)
                        robot.log_event(f"Người dùng thêm {t.trash_type} tại ({p[0]}, {p[1]})")
                elif event.key == pygame.K_o:
                    if walkable_coords:
                        p = random.choice(walkable_coords)
                        dynamic_obstacles.append(DynamicObstacle(p, grid))
                        robot.log_event(f"Thêm 1 sinh viên di chuyển tại ({p[0]}, {p[1]})")
                elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    robot_delay = max(30, robot_delay - 20)
                    robot.log_event(f"Tăng tốc xe: {robot_delay}ms/bước")
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    robot_delay = min(400, robot_delay + 20)
                    robot.log_event(f"Giảm tốc xe: {robot_delay}ms/bước")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if 0 <= mx < MAP_WIDTH and TOPBAR_HEIGHT <= my < WINDOW_HEIGHT:
                    col = mx // CELL_SIZE
                    row = (my - TOPBAR_HEIGHT) // CELL_SIZE
                    if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
                        if grid[row][col] == CELL_EMPTY_ROAD:
                            if event.button == 1: # Chuột trái: Thả rác
                                t = TrashItem((row, col))
                                trash_list.append(t)
                                robot.log_event(f"Thả {t.trash_type} tại ({row}, {col})")
                            elif event.button == 3: # Chuột phải: Thêm sinh viên
                                dynamic_obstacles.append(DynamicObstacle((row, col), grid))
                                robot.log_event(f"Thêm sinh viên tại ({row}, {col})")

        # Cập nhật logic mô phỏng
        if not is_paused:
            # 1.Sinh rác tự động
            if time.time() - last_trash_spawn_time > TRASH_SPAWN_INTERVAL:
                last_trash_spawn_time = time.time()
                if len(trash_list) < 25 and walkable_coords:
                    new_pos = random.choice(walkable_coords)
                    trash_list.append(TrashItem(new_pos))

            # 2.Cập nhật sinh viên (vật cản động)
            if current_ticks - last_obstacle_step_time >= 260:
                last_obstacle_step_time = current_ticks
                all_obs_pos = {obs.get_pos() for obs in dynamic_obstacles}
                for obs in dynamic_obstacles:
                    obs.update(all_obs_pos, robot.get_pos())

            # 3.Cập nhật bước đi của xe dọn rác
            if current_ticks - last_robot_step_time >= robot_delay:
                last_robot_step_time = current_ticks
                robot.step(trash_list, dynamic_obstacles)

        # Vẽ giao diện sắc nét
        renderer.draw(robot, trash_list, dynamic_obstacles, fps, elapsed)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
