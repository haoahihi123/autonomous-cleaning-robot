# -*- coding: utf-8 -*-
"""
Các thuật toán tìm đường và quét bao phủ bản đồ
- Thuật toán A* có tính hướng đi (giảm rẽ ngoằn ngoèo)
- Thuật toán quét bao phủ luống cày và quét theo phân khu
- Kiểm tra tầm nhìn và dự đoán va chạm vật cản động
"""

import heapq
from collections import deque
from config import GRID_ROWS, GRID_COLS, CELL_EMPTY_ROAD, CELL_BUILDING

# Khoảng cách Manhattan giữa 2 ô trên lưới
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Chi phí phạt chuyển hướng (Turn Penalty) giúp xe giữ quán tính đi thẳng dọc hành lang
def compute_turn_penalty(huong_ht, huong_moi, turn_penalty=0.35, u_turn_penalty=1.0):
    """
    Tính toán chi phí phạt chuyển hướng:
    - Đi thẳng: phạt 0.0 (giữ nguyên quán tính)
    - Rẽ góc vuông 90 độ: phạt +0.35 (ưu tiên đi thẳng nếu khoảng cách bằng nhau)
    - Quay đầu ngược lại 180 độ: phạt +1.0 (tránh xe đổi chiều đột ngột)
    """
    if huong_ht is None or huong_moi == huong_ht:
        return 0.0
    if huong_moi[0] == -huong_ht[0] and huong_moi[1] == -huong_ht[1]:
        return u_turn_penalty
    return turn_penalty

# Kiểm tra đường nối 2 điểm có bị tòa nhà che không (để xe không nhìn xuyên tường)
def has_line_of_sight(grid, p1, p2):
    r1, c1 = p1
    r2, c2 = p2
    steps = max(abs(r2 - r1), abs(c2 - c1)) * 3
    if steps == 0:
        return True
    for i in range(1, steps):
        t = i / steps
        r = int(round(r1 + (r2 - r1) * t))
        c = int(round(c1 + (c2 - c1) * t))
        if (r, c) != p1 and (r, c) != p2:
            if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
                if grid[r][c] == CELL_BUILDING:
                    return False
    return True

# Tính điểm ưu tiên khi chọn ô tiếp theo (ưu tiên ô gần, cùng hàng và thuận chiều đi)
def tinh_diem_uu_tien_o(vi_tri_ht, huong_ngang, o_muc_tieu):
    r1, c1 = vi_tri_ht
    r2, c2 = o_muc_tieu
    khoang_cach = abs(r1 - r2) + abs(c1 - c2)
    khac_hang = 0 if r1 == r2 else 1

    if huong_ngang >= 0:
        nguoc_huong = 0 if c2 >= c1 else 1
    else:
        nguoc_huong = 0 if c2 <= c1 else 1

    return (khoang_cach, khac_hang, nguoc_huong)

# Lấy ô bỏ sót gần và thuận hướng xe nhất
def get_nearest_missed_cell(vi_tri_ht, huong_ht, ds_o_sot):
    if not ds_o_sot:
        return None, float('inf')

    o_tot_nhat = min(ds_o_sot, key=lambda o: tinh_diem_uu_tien_o(vi_tri_ht, huong_ht, o))
    kc = heuristic(vi_tri_ht, o_tot_nhat)
    return o_tot_nhat, kc

# Lấy các ô kề bên hợp lệ có thể đi được (4 hướng)
def get_neighbors(pos, grid, dynamic_obstacles_pos=None):
    r, c = pos
    neighbors = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
            if grid[nr][nc] == CELL_EMPTY_ROAD:
                if dynamic_obstacles_pos and (nr, nc) in dynamic_obstacles_pos:
                    continue
                neighbors.append((nr, nc))
    return neighbors

# Thuật toán A* tìm đường ngắn nhất, có cộng thêm chi phí khi rẽ/quay đầu để xe đi thẳng mượt hơn
def a_star_search(grid, xp, dich, ds_can_dong=None, huong_ht=None, turn_penalty=0.35, u_turn_penalty=1.0):
    if xp == dich:
        return [xp]

    def tim_duong(tap_can):
        hang_doi = []
        heapq.heappush(hang_doi, (0.0, 0, xp, huong_ht))
        vet_duong = {xp: None}
        cp_thuc = {xp: 0.0}
        stt = 1

        while hang_doi:
            _, _, o_ht, h_ht = heapq.heappop(hang_doi)

            if o_ht == dich:
                break

            r_ht, c_ht = o_ht
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                r_moi, c_moi = r_ht + dr, c_ht + dc
                if not (0 <= r_moi < GRID_ROWS and 0 <= c_moi < GRID_COLS):
                    continue
                if grid[r_moi][c_moi] != CELL_EMPTY_ROAD:
                    continue
                if tap_can and (r_moi, c_moi) in tap_can:
                    continue

                o_moi = (r_moi, c_moi)
                huong_di = (dr, dc)

                # Thêm chi phí phạt đổi hướng (Turn Penalty)
                cp_buoc = 1.0 + compute_turn_penalty(h_ht, huong_di, turn_penalty, u_turn_penalty)

                cp_moi = cp_thuc[o_ht] + cp_buoc

                if o_moi not in cp_thuc or cp_moi < cp_thuc[o_moi] - 1e-5:
                    cp_thuc[o_moi] = cp_moi
                    h = heuristic(o_moi, dich) * 1.001
                    heapq.heappush(hang_doi, (cp_moi + h, stt, o_moi, huong_di))
                    vet_duong[o_moi] = o_ht
                    stt += 1

        if dich not in vet_duong:
            return None

        duong_di = []
        nut = dich
        while nut is not None:
            duong_di.append(nut)
            nut = vet_duong[nut]
        duong_di.reverse()
        return duong_di

    # Bước 1: Thử tìm đường né toàn bộ vật cản động
    ket_qua = tim_duong(ds_can_dong)
    if ket_qua is not None:
        return ket_qua

    # Bước 2: Nếu bị kẹt tạm thời, tìm theo bản đồ tĩnh để xe tiến lại gần rồi đợi
    return tim_duong(None)

# Sinh lộ trình quét luống cày (Boustrophedon) từ cổng chính lên phía bắc
def generate_coverage_path(grid, start_pos=(GRID_ROWS - 2, 24)):
    walkable_cells = []
    for r in range(GRID_ROWS - 1, -1, -1):
        row_cells = [
            (r, c) for c in range(GRID_COLS)
            if grid[r][c] == CELL_EMPTY_ROAD
        ]
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

        for idx, pt in enumerate(remaining[:25]):
            d = heuristic(current, pt)
            if d < min_dist:
                min_dist = d
                best_idx = idx
                if d == 1:
                    break

        next_target = remaining.pop(best_idx)

        if heuristic(current, next_target) == 1:
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

# Sinh lộ trình quét theo từng phân khu trong trường
def generate_zonal_coverage_path(grid, start_pos=(GRID_ROWS - 2, 24)):
    zones_def = [
        {"name": "QUẢNG TRƯỜNG & TÒA TRUNG TÂM A1 - A5",    "rows": (25, GRID_ROWS), "cols": (13, 35)},
        {"name": "CỤM KHỐI E (CƠ KHÍ MÁY) & CĂN TIN E2",    "rows": (13, GRID_ROWS), "cols": (1, 14)},
        {"name": "HỘI TRƯỜNG, KHỐI A10 & SÂN VIỆT ĐỨC",     "rows": (16, 25),        "cols": (14, 31)},
        {"name": "KHỐI THƯ VIỆN, KHỐI A, C & D",            "rows": (1, 16),         "cols": (13, 31)},
        {"name": "CỤM XƯỞNG, MAKER SPACE, TOYOTA & SÂN BÓNG", "rows": (1, GRID_ROWS), "cols": (31, GRID_COLS)}
    ]

    all_walkable = {
        (r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS)
        if grid[r][c] == CELL_EMPTY_ROAD
    }

    full_path = [start_pos]
    current = start_pos
    visited = {start_pos}
    huong_ngang = 1

    for zone in zones_def:
        r_min, r_max = zone["rows"]
        c_min, c_max = zone["cols"]

        zone_cells = {
            (r, c) for (r, c) in all_walkable
            if r_min <= r < r_max and c_min <= c < c_max and (r, c) not in visited
        }

        while zone_cells:
            # Chọn ô gần nhất, cùng hàng và thuận chiều quét
            next_pt = min(zone_cells, key=lambda pt: tinh_diem_uu_tien_o(current, huong_ngang, pt))
            zone_cells.remove(next_pt)

            if next_pt == current:
                continue

            if next_pt[1] > current[1]:
                huong_ngang = 1
            elif next_pt[1] < current[1]:
                huong_ngang = -1

            if heuristic(current, next_pt) == 1:
                full_path.append(next_pt)
                current = next_pt
                visited.add(next_pt)
            else:
                conn = a_star_search(grid, current, next_pt)
                if conn and len(conn) > 1:
                    for step in conn[1:]:
                        full_path.append(step)
                        visited.add(step)
                        zone_cells.discard(step)
                    current = next_pt
                else:
                    full_path.append(next_pt)
                    current = next_pt
                    visited.add(next_pt)

    # Quét các ô còn sót ngoài ranh giới phân khu
    leftover = all_walkable - visited
    while leftover:
        next_pt = min(leftover, key=lambda pt: tinh_diem_uu_tien_o(current, huong_ngang, pt))
        leftover.remove(next_pt)
        conn = a_star_search(grid, current, next_pt)
        if conn and len(conn) > 1:
            for step in conn[1:]:
                full_path.append(step)
                visited.add(step)
                leftover.discard(step)
            current = next_pt
        else:
            full_path.append(next_pt)
            current = next_pt
            visited.add(next_pt)

    # Quay về vị trí xuất phát để hoàn tất chu kỳ
    back_home = a_star_search(grid, current, start_pos)
    if back_home and len(back_home) > 1:
        full_path.extend(back_home[1:])

    return full_path

# Kiểm tra ô tiếp theo có đang bị sinh viên đứng hoặc chuẩn bị bước vào không
def check_collision_conflict(target_cell, obstacles_pos, obstacles_pred):
    return (target_cell in obstacles_pos) or (target_cell in obstacles_pred)

# Thuật toán BFS tìm đường (dùng để đối chiếu với A*)
def find_path_bfs(grid, xp, dich, ds_can_dong=None):
    if xp == dich:
        return [xp]

    hang_doi = deque([xp])
    vet_duong = {xp: None}
    tap_can = set(ds_can_dong) if ds_can_dong else set()

    while hang_doi:
        o_ht = hang_doi.popleft()
        if o_ht == dich:
            break

        r_ht, c_ht = o_ht
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            r_moi, c_moi = r_ht + dr, c_ht + dc
            if 0 <= r_moi < GRID_ROWS and 0 <= c_moi < GRID_COLS:
                if grid[r_moi][c_moi] == CELL_EMPTY_ROAD and (r_moi, c_moi) not in tap_can:
                    o_moi = (r_moi, c_moi)
                    if o_moi not in vet_duong:
                        hang_doi.append(o_moi)
                        vet_duong[o_moi] = o_ht

    if dich not in vet_duong:
        return None

    duong_di = []
    nut = dich
    while nut is not None:
        duong_di.append(nut)
        nut = vet_duong[nut]
    duong_di.reverse()
    return duong_di
