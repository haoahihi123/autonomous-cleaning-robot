# -*- coding: utf-8 -*-
"""
Các thực thể trong mô phỏng:
- CleaningRobot: Xe dọn rác tự hành
- DynamicObstacle: Sinh viên đi lại trong trường (vật cản động)
- TrashItem, CampusTrashManager: Quản lý các loại rác
"""

import math
import random
import time
from collections import deque
from config import (
    GRID_ROWS, GRID_COLS, CELL_EMPTY_ROAD, SENSOR_RADIUS, MAX_WAIT_STEPS,
    TOA_DO_TRAM_SAC, PIN_TOI_DA, PIN_TIEU_HAO_MOI_BUOC,
    NGUONG_PIN_YEU, SO_BUOC_SAC_PIN,
    CHARGING_STATION_POS, BATTERY_MAX, BATTERY_DRAIN_PER_STEP,
    BATTERY_LOW_THRESHOLD, CHARGE_DURATION_STEPS
)
from algorithms import (
    heuristic, has_line_of_sight, a_star_search, check_collision_conflict,
    get_nearest_missed_cell, generate_coverage_path, generate_zonal_coverage_path
)

# Các khu vực sinh viên tập trung hay có rác
CAMPUS_HOTSPOTS = {
    "CĂN TIN & HỘI TRƯỜNG": {
        "rows": (18, 24), "cols": (14, 33),
        "items": [
            ("Ly trà sữa trân châu", (245, 158, 11)),
            ("Hộp cơm trưa xốp", (220, 225, 235)),
            ("Túi nilon bánh tráng", (200, 210, 225)),
            ("Ống hút nhựa", (239, 68, 68))
        ]
    },
    "SÂN BÓNG & THỂ THAO": {
        "rows": (24, 34), "cols": (33, 46),
        "items": [
            ("Vỏ lon nước tăng lực", (239, 68, 68)),
            ("Chai nước khoáng rỗng", (59, 130, 246)),
            ("Khăn giấy lau mồ hôi", (245, 245, 245))
        ]
    },
    "ĐÀI PHUN NƯỚC & HOA VIÊN": {
        "rows": (29, 34), "cols": (16, 32),
        "items": [
            ("Lá cây bàng rụng", (101, 163, 13)),
            ("Ly cà phê mang đi", (180, 120, 70)),
            ("Vỏ chai trà xanh", (16, 185, 129))
        ]
    },
    "CỔNG CHÍNH VÕ VĂN NGÂN": {
        "rows": (33, 34), "cols": (19, 29),
        "items": [
            ("Tờ rơi quảng cáo câu lạc bộ", (250, 204, 21)),
            ("Vé giữ xe sinh viên", (240, 240, 240)),
            ("Vỏ kẹo cao su", (236, 72, 153))
        ]
    }
}

class TrashItem:
    """Điểm rác xuất hiện trên đường"""
    def __init__(self, pos, name=None, color=None, zone="Đường nội bộ"):
        self.pos = pos # (r, c)
        if name and color:
            self.trash_type = name
            self.color = color
        else:
            default_items = [
                ("Vỏ lon nước ngọt", (239, 68, 68)),
                ("Hộp sữa giấy", (59, 130, 246)),
                ("Ly trà sữa", (245, 158, 11)),
                ("Túi nilon", (220, 225, 235)),
                ("Lá cây rụng", (101, 163, 13))
            ]
            self.trash_type, self.color = random.choice(default_items)
        self.zone = zone
        self.spawn_time = time.time()

class CampusTrashManager:
    """Tạo rác theo điểm nóng hoặc rải ngẫu nhiên"""
    @staticmethod
    def spawn_random(grid, walkable_coords, existing_trash_positions):
        available = [p for p in walkable_coords if p not in existing_trash_positions]
        if not available:
            return None

        if random.random() < 0.75:
            hotspot_name = random.choice(list(CAMPUS_HOTSPOTS.keys()))
            hs = CAMPUS_HOTSPOTS[hotspot_name]
            r_min, r_max = hs["rows"]
            c_min, c_max = hs["cols"]
            hs_cells = [
                p for p in available
                if r_min <= p[0] <= r_max and c_min <= p[1] <= c_max
            ]
            if hs_cells:
                target_cell = random.choice(hs_cells)
                item_name, item_color = random.choice(hs["items"])
                return TrashItem(target_cell, item_name, item_color, hotspot_name)

        target_cell = random.choice(available)
        return TrashItem(target_cell)

    @staticmethod
    def spawn_burst(grid, walkable_coords, existing_trash_positions, hotspot_name="CĂN TIN & HỘI TRƯỜNG", count=4):
        """Sinh một cụm rác (giờ giải lao)"""
        if hotspot_name not in CAMPUS_HOTSPOTS:
            return []
        hs = CAMPUS_HOTSPOTS[hotspot_name]
        r_min, r_max = hs["rows"]
        c_min, c_max = hs["cols"]
        available = [
            p for p in walkable_coords
            if p not in existing_trash_positions and r_min <= p[0] <= r_max and c_min <= p[1] <= c_max
        ]
        if not available:
            return []
        
        spawned = []
        sample_k = min(count, len(available))
        chosen_cells = random.sample(available, sample_k)
        for cell in chosen_cells:
            item_name, item_color = random.choice(hs["items"])
            spawned.append(TrashItem(cell, item_name, item_color, hotspot_name))
        return spawned

# Các mốc địa điểm sinh viên hay đi đến trong trường
CAMPUS_WAYPOINTS = [
    ("Cổng chính Võ Văn Ngân", (34, 24)),
    ("Cổng phụ Võ Văn Ngân", (34, 9)),
    ("Cổng KTX Lê Văn Chí", (2, 40)),
    ("Cổng phụ Lê Văn Chí (Xưởng)", (10, 45)),
    ("Cổng phụ Lê Văn Chí (Toyota)", (22, 45)),
    ("Khối phòng học Khu B", (3, 18)),
    ("Khối Thư Viện", (8, 18)),
    ("Sân giữa Khối A", (13, 22)),
    ("Hội Trường Lớn", (20, 17)),
    ("Khối A10 & Sân Việt Đức", (20, 24)),
    ("Khoa Điện - ĐT Khu C & D", (5, 18)),
    ("Căn tin E.2 & Khối E", (18, 12)),
    ("Khu Maker Space & Xưởng", (16, 35)),
    ("Sân bóng đá ngoài trời", (23, 34)),
    ("Tòa Trung tâm A1", (25, 21))
]

class DynamicObstacle:
    """Sinh viên di chuyển giữa các địa điểm trong trường (vật cản động)"""
    CLOTHES_COLORS = [
        (37, 99, 235),   # Xanh dương
        (225, 29, 72),   # Đỏ
        (16, 185, 129),  # Xanh lục
        (147, 51, 234),  # Tím
        (245, 158, 11),  # Vàng cam
        (71, 85, 105)    # Xám
    ]

    def __init__(self, pos, grid, is_follower=False, leader=None):
        self.r, self.c = pos
        self.grid = grid
        self.direction = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        self.shirt_color = random.choice(self.CLOTHES_COLORS)
        self.backpack_color = (30, 41, 59)
        self.blocked_count = 0
        
        self.is_follower = is_follower
        self.leader = leader
        self.current_goal_name = ""
        self.current_goal_pos = None
        self.rest_steps = 0
        self.pick_new_waypoint()

    def pick_new_waypoint(self):
        """Chọn địa điểm tiếp theo để đi tới"""
        valid_waypoints = [wp for wp in CAMPUS_WAYPOINTS if wp[1] != (self.r, self.c)]
        if valid_waypoints:
            name, pos = random.choice(valid_waypoints)
            self.current_goal_name = name
            self.current_goal_pos = pos

    def get_pos(self):
        return (self.r, self.c)

    def predict_next_pos(self):
        """Dự đoán ô tiếp theo sinh viên sẽ bước tới"""
        nr, nc = self.r + self.direction[0], self.c + self.direction[1]
        if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and self.grid[nr][nc] == CELL_EMPTY_ROAD:
            return (nr, nc)
        return (self.r, self.c)

    def update(self, all_obstacles_pos, robot_pos):
        """Cập nhật bước đi của sinh viên"""
        if self.rest_steps > 0:
            self.rest_steps -= 1
            return

        if self.is_follower and self.leader:
            target_pos = self.leader.get_pos()
        else:
            target_pos = self.current_goal_pos

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        valid_moves = []
        for dr, dc in directions:
            nr, nc = self.r + dr, self.c + dc
            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                if self.grid[nr][nc] == CELL_EMPTY_ROAD:
                    if (nr, nc) not in all_obstacles_pos and (nr, nc) != robot_pos:
                        valid_moves.append((dr, dc, nr, nc))

        if not valid_moves:
            self.blocked_count += 1
            return

        if target_pos:
            valid_moves.sort(
                key=lambda m: abs(m[2] - target_pos[0]) + abs(m[3] - target_pos[1])
            )
            if len(valid_moves) > 1 and random.random() < 0.20:
                chosen = valid_moves[1]
            else:
                chosen = valid_moves[0]
        else:
            chosen = random.choice(valid_moves)

        self.direction = (chosen[0], chosen[1])
        self.r, self.c = chosen[2], chosen[3]
        self.blocked_count = 0

        if target_pos and (self.r, self.c) == target_pos:
            self.rest_steps = random.randint(3, 7)
            self.pick_new_waypoint()

    def change_random_direction(self):
        candidates = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        random.shuffle(candidates)
        for dr, dc in candidates:
            nr, nc = self.r + dr, self.c + dc
            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS and self.grid[nr][nc] == CELL_EMPTY_ROAD:
                self.direction = (dr, dc)
                return

# Lớp xe dọn rác tự động
class CleaningRobot:
    """
    Xe dọn rác tự động:
    - Quét bao phủ sân trường theo hàng hoặc phân khu
    - Cảm biến có giới hạn bán kính và không nhìn xuyên tường
    - Tự ngắt quét chính để gom rác khi phát hiện rác trong tầm nhìn
    - Nhường đường và tránh xung đột với sinh viên
    - Tự về trạm sạc tòa D khi pin yếu
    """
    STATE_PATROLLING          = "ĐANG QUÉT BAO PHỦ"
    STATE_COLLECTING_TRASH    = "ĐANG ĐI GOM RÁC"
    STATE_RESOLVING_BACKLOG   = "ĐANG XỬ LÝ Ô BỎ SÓT"
    STATE_WAITING             = "CHỜ NHƯỜNG ĐƯỜNG"
    STATE_RESETTING_CYCLE     = "BẮT ĐẦU CHU KỲ MỚI"
    STATE_RETURNING_TO_CHARGE = "VỀ TRẠM SẠC TÒA D"
    STATE_CHARGING            = "ĐANG SẠC PIN (TÒA D)"

    def __init__(self, start_pos, grid, coverage_path):
        self.r, self.c = start_pos
        self.start_pos = start_pos
        self.grid = grid
        self.coverage_path = coverage_path
        self.path_index = 0
        
        self.cycle_count = 1
        self.strategy_mode = "zonal" # Mặc định quét theo vùng, bấm Z đổi sang luống cày
        self.visited_cells = set()
        self.visited_cells.add((self.r, self.c))
        self.missed_cells = set()
        self.backlog_targets = deque()
        
        # Hướng quét ngang (1: sang phải, -1: sang trái)
        self.direction = 1
        self.step_since_missed = 0
        
        self.phan_tram_pin = PIN_TOI_DA
        self.vi_tri_tram_sac = TOA_DO_TRAM_SAC
        self.thoi_gian_sac = SO_BUOC_SAC_PIN
        self.tien_do_sac = 0
        
        self.state = self.STATE_PATROLLING
        self.previous_state = None
        self.active_path = []
        self.active_target = None
        self.resume_path_index = None
        
        self.sensor_radius = SENSOR_RADIUS
        self.wait_count = 0
        self.total_steps = 0
        self.collected_trash_count = 0
        
        self.brush_angle = 0.0
        self.pulse_radius = 0.0
        self.event_logs = []
        self.log_event(f"Xe xuất phát tại Cổng Võ Văn Ngân ({self.r}, {self.c}). Bắt đầu Chu kỳ quét #1!")

    @property
    def battery(self):
        return self.phan_tram_pin

    @battery.setter
    def battery(self, value):
        self.phan_tram_pin = value

    @property
    def charging_station_pos(self):
        return self.vi_tri_tram_sac

    @charging_station_pos.setter
    def charging_station_pos(self, value):
        self.vi_tri_tram_sac = value

    @property
    def charging_duration(self):
        return self.thoi_gian_sac

    @charging_duration.setter
    def charging_duration(self, value):
        self.thoi_gian_sac = value

    @property
    def charging_progress(self):
        return self.tien_do_sac

    @charging_progress.setter
    def charging_progress(self, value):
        self.tien_do_sac = value

    def log_event(self, msg):
        """Ghi nhận sự kiện hiển thị trên sidebar"""
        timestamp = time.strftime("%H:%M:%S")
        self.event_logs.append(f"{timestamp}   {msg}")
        if len(self.event_logs) > 35:
            self.event_logs.pop(0)

    def get_pos(self):
        return (self.r, self.c)

    def is_in_sensor_range(self, target_pos):
        """Kiểm tra ô mục tiêu có trong bán kính và không bị tòa nhà che khuất"""
        dr = target_pos[0] - self.r
        dc = target_pos[1] - self.c
        if math.sqrt(dr * dr + dc * dc) > self.sensor_radius:
            return False
        return has_line_of_sight(self.grid, (self.r, self.c), target_pos)

    def step(self, trash_list, dynamic_obstacles):
        """Một bước xử lý logic của xe dọn rác"""
        self.brush_angle = (self.brush_angle + 35) % 360
        self.pulse_radius = (self.pulse_radius + 0.16) % self.sensor_radius
        self.total_steps += 1
        
        obstacles_pos = {obs.get_pos() for obs in dynamic_obstacles}
        obstacles_pred = {obs.predict_next_pos() for obs in dynamic_obstacles}

        # 1.Hút rác tại ô hiện tại nếu có
        collected_here = [t for t in trash_list if t.pos == (self.r, self.c)]
        for t in collected_here:
            trash_list.remove(t)
            self.collected_trash_count += 1
            self.log_event(f"Đã hút sạch {t.trash_type} tại ({self.r}, {self.c})!")

        # 2.Cảm biến phát hiện rác hoặc ô bỏ sót gần xe
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

        elif self.missed_cells and self.state == self.STATE_PATROLLING and not self.active_path:
            nearby_free_missed = [
                m for m in self.missed_cells
                if m not in obstacles_pos and heuristic((self.r, self.c), m) <= 3
            ]
            if nearby_free_missed:
                target_m, _ = get_nearest_missed_cell((self.r, self.c), self.direction, nearby_free_missed)
                path_m = a_star_search(self.grid, (self.r, self.c), target_m, obstacles_pos)
                if path_m and 1 < len(path_m) <= 4:
                    self.resume_path_index = self.path_index
                    self.active_path = path_m[1:]
                    self.active_target = target_m
                    self.log_event(f"Ô bỏ sót ({target_m[0]}, {target_m[1]}) đã trống, xe ghé dọn bù ngay!")

        # 3.Quản lý mức pin và xử lý các trạng thái hoạt động
        if self.state not in (self.STATE_CHARGING, self.STATE_WAITING):
            self.phan_tram_pin = max(0.0, self.phan_tram_pin - PIN_TIEU_HAO_MOI_BUOC)

        if self.phan_tram_pin <= NGUONG_PIN_YEU and self.state in (self.STATE_PATROLLING, self.STATE_RESOLVING_BACKLOG):
            path_charge = a_star_search(self.grid, (self.r, self.c), self.vi_tri_tram_sac, obstacles_pos)
            if path_charge and len(path_charge) > 1:
                self.resume_path_index = self.path_index
                self.active_path = path_charge[1:]
                self.active_target = self.vi_tri_tram_sac
                self.state = self.STATE_RETURNING_TO_CHARGE
                self.log_event(f"Pin yếu ({self.phan_tram_pin:.1f}%). Tạm dừng lộ trình, quay về Trạm sạc Tòa D!")
                return

        next_pos = None

        if self.state == self.STATE_CHARGING:
            self.tien_do_sac += 1
            sac_moi_nhip = (PIN_TOI_DA - NGUONG_PIN_YEU) / max(1, self.thoi_gian_sac)
            self.phan_tram_pin = min(PIN_TOI_DA, self.phan_tram_pin + sac_moi_nhip)
            
            if self.tien_do_sac >= self.thoi_gian_sac:
                self.phan_tram_pin = PIN_TOI_DA
                self.log_event("Pin đã sạc đầy 100% tại Trạm Tòa D! Xe tiếp tục tuần tra.")
                self.tien_do_sac = 0
                
                if self.resume_path_index is not None:
                    while (self.resume_path_index < len(self.coverage_path) and
                           self.coverage_path[self.resume_path_index] in self.visited_cells):
                        self.resume_path_index += 1

                if self.resume_path_index is not None and self.resume_path_index < len(self.coverage_path):
                    target_checkpoint = self.coverage_path[self.resume_path_index]
                    return_path = a_star_search(self.grid, (self.r, self.c), target_checkpoint, obstacles_pos)
                    if return_path and len(return_path) > 1:
                        self.active_path = return_path[1:]
                        self.active_target = target_checkpoint
                        self.state = self.STATE_PATROLLING
                        self.path_index = self.resume_path_index
                        self.log_event(f"Tiếp nối lộ trình quét tại ({target_checkpoint[0]}, {target_checkpoint[1]}).")
                    else:
                        self.state = self.STATE_PATROLLING
                        self.path_index = self.resume_path_index
                else:
                    self.state = self.STATE_PATROLLING
            return

        elif self.state == self.STATE_RETURNING_TO_CHARGE:
            if self.active_path:
                candidate = self.active_path[0]
                if check_collision_conflict(candidate, obstacles_pos, obstacles_pred):
                    self.handle_wait_or_reroute(candidate, self.vi_tri_tram_sac, obstacles_pos)
                    return
                else:
                    self.wait_count = 0
                    next_pos = self.active_path.pop(0)
            else:
                self.state = self.STATE_CHARGING
                self.tien_do_sac = 0
                self.log_event(f"Đã cập bến Trạm sạc Tòa D ({self.vi_tri_tram_sac[0]}, {self.vi_tri_tram_sac[1]}). Bắt đầu sạc pin ⚡...")
                return

        elif self.state == self.STATE_WAITING:
            mission = self.previous_state or self.STATE_PATROLLING

            check_target = None
            if self.active_path:
                check_target = self.active_path[0]
            elif mission in (self.STATE_PATROLLING, self.STATE_RESETTING_CYCLE) and self.path_index < len(self.coverage_path):
                check_target = self.coverage_path[self.path_index]

            if check_target is not None:
                if check_collision_conflict(check_target, obstacles_pos, obstacles_pred):
                    self.handle_wait_or_reroute(check_target, self.active_target, obstacles_pos)
                    return
                else:
                    self.state = mission
                    self.previous_state = None
                    self.wait_count = 0
                    self.log_event("Vật cản đã nhường đường. Xe tiếp tục lộ trình!")
                    if self.active_path:
                        next_pos = self.active_path.pop(0)
                    else:
                        next_pos = check_target
                        self.path_index += 1
            else:
                self.state = mission
                self.previous_state = None
                self.wait_count = 0

        elif self.state == self.STATE_COLLECTING_TRASH:
            if self.active_path:
                candidate = self.active_path[0]
                if check_collision_conflict(candidate, obstacles_pos, obstacles_pred):
                    self.handle_wait_or_reroute(candidate, self.active_target, obstacles_pos)
                    return
                else:
                    self.wait_count = 0
                    next_pos = self.active_path.pop(0)
            else:
                collected = None
                for t in trash_list:
                    if t.pos == (self.r, self.c):
                        collected = t
                        break
                if collected:
                    trash_list.remove(collected)
                    self.collected_trash_count += 1
                    self.log_event(f"Đã gom rác thành công: {collected.trash_type}!")

                rem_trash = [t for t in trash_list if self.is_in_sensor_range(t.pos)]
                if rem_trash:
                    nearest_t = min(rem_trash, key=lambda t: heuristic((self.r, self.c), t.pos))
                    p = a_star_search(self.grid, (self.r, self.c), nearest_t.pos, obstacles_pos)
                    if p and len(p) > 1:
                        self.active_path = p[1:]
                        self.active_target = nearest_t.pos
                        return

                if self.resume_path_index is not None:
                    while (self.resume_path_index < len(self.coverage_path) and
                           self.coverage_path[self.resume_path_index] in self.visited_cells):
                        self.resume_path_index += 1

                if self.resume_path_index is not None and self.resume_path_index < len(self.coverage_path):
                    target_checkpoint = self.coverage_path[self.resume_path_index]
                    return_path = a_star_search(self.grid, (self.r, self.c), target_checkpoint, obstacles_pos)
                    if return_path and len(return_path) > 1:
                        self.active_path = return_path[1:]
                        self.active_target = target_checkpoint
                        self.state = self.STATE_PATROLLING
                        self.path_index = self.resume_path_index
                        self.log_event(f"Gom xong rác. Tiếp nối lộ trình quét tại ({target_checkpoint[0]}, {target_checkpoint[1]}).")
                    else:
                        self.state = self.STATE_PATROLLING
                        self.path_index = self.resume_path_index
                else:
                    self.state = self.STATE_PATROLLING

        elif self.state in (self.STATE_PATROLLING, self.STATE_RESETTING_CYCLE):
            if self.active_path:
                candidate = self.active_path[0]
                if check_collision_conflict(candidate, obstacles_pos, obstacles_pred):
                    self.handle_wait_or_reroute(candidate, self.active_target, obstacles_pos)
                    return
                else:
                    self.wait_count = 0
                    self.state = self.STATE_PATROLLING
                    next_pos = self.active_path.pop(0)
            elif self.path_index < len(self.coverage_path):
                target_cell = self.coverage_path[self.path_index]
                
                if (self.r, self.c) == target_cell:
                    self.path_index += 1
                    if self.path_index < len(self.coverage_path):
                        target_cell = self.coverage_path[self.path_index]
                    else:
                        self.check_and_start_backlog(obstacles_pos)
                        return

                dist = abs(self.r - target_cell[0]) + abs(self.c - target_cell[1])
                if dist > 1:
                    connector = a_star_search(self.grid, (self.r, self.c), target_cell, obstacles_pos)
                    if connector and len(connector) > 1:
                        self.active_path = connector[1:]
                        self.active_target = target_cell
                        candidate = self.active_path[0]
                        if check_collision_conflict(candidate, obstacles_pos, obstacles_pred):
                            self.handle_wait_or_reroute(candidate, self.active_target, obstacles_pos)
                            return
                        else:
                            self.wait_count = 0
                            next_pos = self.active_path.pop(0)
                    else:
                        self.handle_wait_or_reroute(target_cell, None, obstacles_pos)
                        return
                else:
                    if check_collision_conflict(target_cell, obstacles_pos, obstacles_pred):
                        self.handle_wait_or_reroute(target_cell, None, obstacles_pos)
                        return
                    else:
                        self.wait_count = 0
                        self.state = self.STATE_PATROLLING
                        next_pos = target_cell
                        self.path_index += 1
            else:
                self.check_and_start_backlog(obstacles_pos)
                return

        elif self.state == self.STATE_RESOLVING_BACKLOG:
            if self.active_path:
                candidate = self.active_path[0]
                if check_collision_conflict(candidate, obstacles_pos, obstacles_pred):
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
                    unvisited_set = set(unvisited)
                    top_targets = []
                    curr_u = (self.r, self.c)
                    for _ in range(min(8, len(unvisited_set))):
                        best_u, _ = get_nearest_missed_cell(curr_u, self.direction, unvisited_set)
                        if best_u:
                            top_targets.append(best_u)
                            unvisited_set.remove(best_u)
                            curr_u = best_u
                    self.backlog_targets.extend(top_targets)
                    target = self.backlog_targets.popleft()
                    p = a_star_search(self.grid, (self.r, self.c), target, obstacles_pos)
                    if p and len(p) > 1:
                        self.active_path = p[1:]
                        self.active_target = target
                        return
                        
                # ĐÃ HOÀN THÀNH 100% DIỆN TÍCH -> TỰ ĐỘNG RESET BẮT ĐẦU CHU KỲ MỚI!
                self.start_new_patrol_cycle(obstacles_pos)
                return

        # 4.CẬP NHẬT VỊ TRÍ, HƯỚNG VÀ ĐÁNH DẤU Ô ĐÃ QUÉT
        if next_pos is not None:
            dc = next_pos[1] - self.c
            if dc > 0:
                self.direction = 1
            elif dc < 0:
                self.direction = -1

            self.r, self.c = next_pos
            self.visited_cells.add((self.r, self.c))
            self.missed_cells.discard((self.r, self.c))

        if self.missed_cells:
            self.step_since_missed += 1
        else:
            self.step_since_missed = 0

    def handle_wait_or_reroute(self, target_cell, ultimate_goal, obstacles_pos):
        """Xử lý khi bị vướng vật cản: chờ nhường đường hoặc tìm đường vòng"""
        if self.state != self.STATE_WAITING:
            self.previous_state = self.state

        self.wait_count += 1
        if self.wait_count <= MAX_WAIT_STEPS:
            self.state = self.STATE_WAITING
            self.log_event(f"Vật cản tại ({target_cell[0]}, {target_cell[1]}). Chờ nhường đường ({self.wait_count}/{MAX_WAIT_STEPS})...")
            return

        self.wait_count = 0
        prior_state = self.previous_state or self.STATE_PATROLLING
        self.previous_state = None

        # 1.Đang về trạm sạc mà bị chặn
        if prior_state == self.STATE_RETURNING_TO_CHARGE:
            self.log_event(f"Bị chặn đường về trạm sạc. Tìm đường vòng...")
            reroute = a_star_search(self.grid, (self.r, self.c), self.vi_tri_tram_sac, obstacles_pos)
            if reroute and len(reroute) > 1:
                self.active_path = reroute[1:]
                self.state = self.STATE_RETURNING_TO_CHARGE
                self.log_event("Đã tìm được đường vòng về trạm sạc Tòa D.")
            else:
                self.state = self.STATE_WAITING

        # 2.Đang đi nhặt rác mà bị chặn
        elif prior_state == self.STATE_COLLECTING_TRASH and self.active_target:
            self.log_event(f"Bị chặn đường gom rác tại ({target_cell[0]}, {target_cell[1]}). Tìm đường vòng...")
            reroute = a_star_search(self.grid, (self.r, self.c), self.active_target, obstacles_pos)
            if reroute and len(reroute) > 1:
                self.active_path = reroute[1:]
                self.state = self.STATE_COLLECTING_TRASH
                self.log_event(f"Tìm được đường vòng tới rác tại ({self.active_target[0]}, {self.active_target[1]}).")
            else:
                self.log_event(f"Không thể tiếp cận rác, quay lại lộ trình quét.")
                self.state = self.STATE_PATROLLING
                self.active_target = None
                self.active_path = []
                
                if self.resume_path_index is not None:
                    while (self.resume_path_index < len(self.coverage_path) and
                           self.coverage_path[self.resume_path_index] in self.visited_cells):
                        self.resume_path_index += 1
                        
                    if self.resume_path_index < len(self.coverage_path):
                        target_checkpoint = self.coverage_path[self.resume_path_index]
                        return_path = a_star_search(self.grid, (self.r, self.c), target_checkpoint, obstacles_pos)
                        if return_path and len(return_path) > 1:
                            self.active_path = return_path[1:]
                            self.active_target = target_checkpoint
                        self.path_index = self.resume_path_index

        # 3.Đang đi quét bù mà bị chặn
        elif prior_state == self.STATE_RESOLVING_BACKLOG and self.active_target:
            self.log_event(f"Bị chặn đường quét bù. Tìm đường vòng...")
            reroute = a_star_search(self.grid, (self.r, self.c), self.active_target, obstacles_pos)
            if reroute and len(reroute) > 1:
                self.active_path = reroute[1:]
                self.state = self.STATE_RESOLVING_BACKLOG
            else:
                self.log_event(f"Chưa tới được ô ({self.active_target[0]}, {self.active_target[1]}), đổi ô khác.")
                if self.active_target not in self.visited_cells:
                    self.missed_cells.add(self.active_target)
                self.active_path = []
                self.active_target = None
                self.state = self.STATE_RESOLVING_BACKLOG

        # 4.Đang quét chính mà bị chặn quá lâu -> bỏ qua ô này và đi vòng
        else:
            self.log_event(f"Vật cản chặn quá lâu. Bỏ qua ô ({target_cell[0]}, {target_cell[1]}) và đi vòng.")
            if target_cell not in self.visited_cells:
                self.missed_cells.add(target_cell)

            found_reroute = False
            for offset in range(1, min(25, len(self.coverage_path) - self.path_index)):
                future_idx = self.path_index + offset
                future_cell = self.coverage_path[future_idx]
                if future_cell not in obstacles_pos:
                    reroute = a_star_search(self.grid, (self.r, self.c), future_cell, obstacles_pos)
                    if reroute and len(reroute) > 1:
                        for skipped_idx in range(self.path_index, future_idx):
                            skipped_cell = self.coverage_path[skipped_idx]
                            if skipped_cell not in self.visited_cells:
                                self.missed_cells.add(skipped_cell)
                        self.active_path = reroute[1:]
                        self.active_target = future_cell
                        self.path_index = future_idx
                        self.state = self.STATE_PATROLLING
                        found_reroute = True
                        self.log_event(f"Đi vòng né vật cản tới ({future_cell[0]}, {future_cell[1]}).")
                        break
            if not found_reroute:
                self.state = self.STATE_WAITING

    def check_and_start_backlog(self, obstacles_pos):
        """Khởi động quét bù các ô bỏ sót sau khi quét xong lượt chính"""
        if self.missed_cells:
            unresolved = set(self.missed_cells)
            curr = (self.r, self.c)
            sorted_backlog = []
            
            while unresolved:
                best_point, _ = get_nearest_missed_cell(curr, self.direction, unresolved)
                if best_point is None:
                    break
                sorted_backlog.append(best_point)
                unresolved.remove(best_point)
                curr = best_point

            self.backlog_targets = deque(sorted_backlog)
            self.state = self.STATE_RESOLVING_BACKLOG
            self.log_event(f"Hoàn thành lượt quét chính. Đang quét bù {len(self.backlog_targets)} ô còn sót!")
            
            first_target = self.backlog_targets.popleft()
            p = a_star_search(self.grid, (self.r, self.c), first_target, obstacles_pos)
            if p and len(p) > 1:
                self.active_path = p[1:]
                self.active_target = first_target
        else:
            self.start_new_patrol_cycle(obstacles_pos)

    def start_new_patrol_cycle(self, obstacles_pos):
        """Hoàn tất chu kỳ hiện tại, reset thông số và bắt đầu chu kỳ quét mới"""
        old_cycle = self.cycle_count
        self.cycle_count += 1
        
        self.visited_cells.clear()
        self.visited_cells.add((self.r, self.c))
        self.missed_cells.clear()
        self.backlog_targets.clear()
        self.path_index = 0
        self.wait_count = 0
        
        cycle_start_pos = self.coverage_path[0]
        
        if self.strategy_mode == "zonal":
            self.coverage_path = generate_zonal_coverage_path(self.grid, cycle_start_pos)
        else:
            self.coverage_path = generate_coverage_path(self.grid, cycle_start_pos)
        
        self.log_event(f"Hoàn tất chu kỳ {old_cycle}. Bắt đầu chu kỳ {self.cycle_count}")

        if (self.r, self.c) != cycle_start_pos:
            return_start = a_star_search(self.grid, (self.r, self.c), cycle_start_pos, obstacles_pos)
            if return_start and len(return_start) > 1:
                self.active_path = return_start[1:]
                self.active_target = cycle_start_pos
                self.state = self.STATE_PATROLLING
            else:
                self.state = self.STATE_PATROLLING
        else:
            self.active_path = []
            self.active_target = None
            self.state = self.STATE_PATROLLING

    def toggle_strategy(self, obstacles_pos=None):
        """Chuyển đổi giữa 2 thuật toán: Quét phân vùng <-> Luống cày"""
        if obstacles_pos is None:
            obstacles_pos = set()
        if self.strategy_mode == "zonal":
            self.strategy_mode = "classic"
            self.coverage_path = generate_coverage_path(self.grid, (self.r, self.c))
            self.log_event("Đổi chiến lược: QUÉT LUỐNG CÀY (Boustrophedon)")
        else:
            self.strategy_mode = "zonal"
            self.coverage_path = generate_zonal_coverage_path(self.grid, (self.r, self.c))
            self.log_event("Đổi chiến lược: QUÉT PHÂN VÙNG KHUÔN VIÊN")
        self.path_index = 0
        self.active_path = []
        self.active_target = None
        self.state = self.STATE_PATROLLING

    def kich_hoat_pin_yeu(self, ds_can_dong=None):
        """Giả lập pin yếu để xe tự động chạy về Trạm sạc Tòa D (Phím B)"""
        if ds_can_dong is None:
            ds_can_dong = set()
        if self.state not in (self.STATE_RETURNING_TO_CHARGE, self.STATE_CHARGING):
            self.phan_tram_pin = min(self.phan_tram_pin, NGUONG_PIN_YEU - 2.0)
            self.resume_path_index = self.path_index
            path_charge = a_star_search(self.grid, (self.r, self.c), self.vi_tri_tram_sac, ds_can_dong)
            if path_charge and len(path_charge) > 1:
                self.active_path = path_charge[1:]
                self.active_target = self.vi_tri_tram_sac
                self.state = self.STATE_RETURNING_TO_CHARGE
                self.log_event(f"[KÍCH HOẠT] Pin yếu ({self.phan_tram_pin:.1f}%). Về trạm sạc Tòa D!")
            else:
                self.log_event("Không thể tìm đường về Trạm sạc Tòa D lúc này!")

    trigger_low_battery = kich_hoat_pin_yeu
