"""
Chương trình chính mô phỏng xe dọn rác tự động - HCMUTE
Sinh viên thực hiện:
- Nguyễn Ngọc Hải Yến - MSSV: 25139062
- Trương Cảnh Hào     - MSSV: 25139011
"""

import sys
import os
import random
import time
import pygame

# Import các module trong project
from config import (
    GRID_ROWS, GRID_COLS, CELL_SIZE, MAP_WIDTH, TOPBAR_HEIGHT,
    WINDOW_WIDTH, WINDOW_HEIGHT, CELL_EMPTY_ROAD,
    ROBOT_SPEED_DELAY, TRASH_SPAWN_INTERVAL
)
from campus_map import create_hcmute_campus
from algorithms import generate_coverage_path, generate_zonal_coverage_path
from entities import CleaningRobot, DynamicObstacle, TrashItem, CampusTrashManager
from renderer import SharpRenderer

def main():
    """Hàm khởi chạy chính của chương trình mô phỏng"""
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    # Kích thước cửa sổ ban đầu và cờ RESIZABLE để người dùng tùy ý kéo giãn/phóng to thu nhỏ
    window_width = WINDOW_WIDTH
    window_height = WINDOW_HEIGHT
    screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
    pygame.display.set_caption(
        "HCMUTE - Mô phỏng xe dọn rác tự động (Vật cản động & Tầm nhìn giới hạn)"
    )
    
    # Tạo canvas ảo (virtual screen) cố định tỉ lệ chuẩn để giao diện luôn sắc nét và không bị méo chữ
    virtual_screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    clock = pygame.time.Clock()

    # 1.Khởi tạo bản đồ trường
    grid, buildings = create_hcmute_campus()

    # 2.Vị trí xuất phát từ cổng chính Võ Văn Ngân
    start_pos = (GRID_ROWS - 2, 24)

    # 3.Tạo lộ trình quét bao phủ theo phân vùng
    coverage_path = generate_zonal_coverage_path(grid, start_pos)
    robot = CleaningRobot(start_pos, grid, coverage_path)

    # 4.Lấy danh sách các ô đường có thể đi
    walkable_coords = [
        (r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS)
        if grid[r][c] == CELL_EMPTY_ROAD and (r, c) != start_pos
    ]

    # 5.Rải rác ban đầu tại các khu vực thường có rác
    trash_list = []
    existing_t_positions = set()
    for _ in range(12):
        t = CampusTrashManager.spawn_random(grid, walkable_coords, existing_t_positions)
        if t:
            trash_list.append(t)
            existing_t_positions.add(t.pos)

    # 6.Tạo các sinh viên đi lại trên sân trường (vật cản động)
    dynamic_obstacles = []
    for _ in range(6):
        if walkable_coords:
            p = random.choice(walkable_coords)
            dynamic_obstacles.append(DynamicObstacle(p, grid))
            
    if walkable_coords:
        lead_p = random.choice(walkable_coords)
        leader = DynamicObstacle(lead_p, grid)
        dynamic_obstacles.append(leader)
        follower = DynamicObstacle(lead_p, grid, is_follower=True, leader=leader)
        dynamic_obstacles.append(follower)

    # 7.Khởi tạo bộ vẽ giao diện pygame vẽ lên canvas ảo
    renderer = SharpRenderer(virtual_screen, grid, buildings)

    # Biến quản lý thời gian và vòng lặp
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

        # Xử lý sự kiện bàn phím và chuột
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                # Cập nhật kích thước khi người dùng kéo thay đổi kích thước cửa sổ
                window_width = max(600, event.w)
                window_height = max(400, event.h)
                screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)

            elif event.key_down if hasattr(event, 'key_down') else False:
                pass
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    is_paused = not is_paused
                    robot.log_event("ĐÃ TẠM DỪNG MÔ PHỎNG" if is_paused else "TIẾP TỤC MÔ PHỎNG")

                elif event.key == pygame.K_z:
                    # Đổi giữa 2 thuật toán quét (Phân vùng <-> Luống cày)
                    obs_pos = {obs.get_pos() for obs in dynamic_obstacles}
                    robot.toggle_strategy(obs_pos)

                elif event.key == pygame.K_b:
                    # Giả lập pin yếu -> Xe chạy về trạm sạc Tòa D
                    obs_pos = {obs.get_pos() for obs in dynamic_obstacles}
                    robot.kich_hoat_pin_yeu(obs_pos)

                elif event.key == pygame.K_c:
                    # Sinh rác tập trung (giờ nghỉ căn tin, sân bóng)
                    burst_name = random.choice(["CĂN TIN & HỘI TRƯỜNG", "SÂN BÓNG & THỂ THAO", "ĐÀI PHUN NƯỚC & HOA VIÊN"])
                    existing_t = {t.pos for t in trash_list}
                    new_burst = CampusTrashManager.spawn_burst(grid, walkable_coords, existing_t, hotspot_name=burst_name, count=5)
                    if new_burst:
                        trash_list.extend(new_burst)
                        robot.log_event(f"Giờ nghỉ: xuất hiện {len(new_burst)} rác tại {burst_name.title()}")
                    
                elif event.key == pygame.K_f:
                    renderer.fog_enabled = not renderer.fog_enabled
                    robot.log_event(
                        f"Sương mù tầm nhìn: {'BẬT' if renderer.fog_enabled else 'TẮT'}"
                    )
                    
                elif event.key == pygame.K_r:
                    existing_t = {t.pos for t in trash_list}
                    new_item = CampusTrashManager.spawn_random(grid, walkable_coords, existing_t)
                    if new_item:
                        trash_list.append(new_item)
                        robot.log_event(f"Thêm rác tại ({new_item.pos[0]}, {new_item.pos[1]}): {new_item.trash_type}")
                        
                elif event.key == pygame.K_o:
                    if walkable_coords:
                        p = random.choice(walkable_coords)
                        dynamic_obstacles.append(DynamicObstacle(p, grid))
                        robot.log_event(f"Thêm sinh viên tại ({p[0]}, {p[1]})")
                        
                elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    robot_delay = max(30, robot_delay - 20)
                    robot.log_event(f"Tốc độ xe: {robot_delay}ms/bước")
                    
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    robot_delay = min(400, robot_delay + 20)
                    robot.log_event(f"Tốc độ xe: {robot_delay}ms/bước")

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                # Tính tỉ lệ co dãn hiện tại để quy đổi tọa độ click chuột về canvas chuẩn
                cur_scale = min(window_width / WINDOW_WIDTH, window_height / WINDOW_HEIGHT)
                cur_scaled_w = int(WINDOW_WIDTH * cur_scale)
                cur_scaled_h = int(WINDOW_HEIGHT * cur_scale)
                cur_offset_x = (window_width - cur_scaled_w) // 2
                cur_offset_y = (window_height - cur_scaled_h) // 2

                if cur_scale > 0:
                    vx = int((mx - cur_offset_x) / cur_scale)
                    vy = int((my - cur_offset_y) / cur_scale)
                else:
                    vx, vy = mx, my

                if 0 <= vx < MAP_WIDTH and TOPBAR_HEIGHT <= vy < WINDOW_HEIGHT:
                    col = vx // CELL_SIZE
                    row = (vy - TOPBAR_HEIGHT) // CELL_SIZE
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
            # 1.Tự động sinh thêm rác theo chu kỳ
            if time.time() - last_trash_spawn_time > TRASH_SPAWN_INTERVAL:
                last_trash_spawn_time = time.time()
                if len(trash_list) < 25 and walkable_coords:
                    existing_t = {t.pos for t in trash_list}
                    new_item = CampusTrashManager.spawn_random(grid, walkable_coords, existing_t)
                    if new_item:
                        trash_list.append(new_item)

            # 2.Cập nhật vị trí sinh viên di chuyển
            if current_ticks - last_obstacle_step_time >= 260:
                last_obstacle_step_time = current_ticks
                all_obs_pos = {obs.get_pos() for obs in dynamic_obstacles}
                for obs in dynamic_obstacles:
                    obs.update(all_obs_pos, robot.get_pos())

            # 3.Cập nhật bước đi của xe
            if current_ticks - last_robot_step_time >= robot_delay:
                last_robot_step_time = current_ticks
                robot.step(trash_list, dynamic_obstacles)

        # 1.Vẽ giao diện đầy đủ lên canvas ảo
        renderer.draw(robot, trash_list, dynamic_obstacles, fps, elapsed, is_paused)

        # 2.Tính toán tỉ lệ và tọa độ căn giữa cửa sổ
        scale = min(window_width / WINDOW_WIDTH, window_height / WINDOW_HEIGHT)
        scaled_w = int(WINDOW_WIDTH * scale)
        scaled_h = int(WINDOW_HEIGHT * scale)
        offset_x = (window_width - scaled_w) // 2
        offset_y = (window_height - scaled_h) // 2

        # 3.Đổ màu nền viền cho cửa sổ (màu tối đồng bộ khi kéo rộng hơn tỉ lệ chuẩn)
        screen.fill((18, 22, 32))

        # 4.Phóng to / thu nhỏ canvas ảo đưa lên màn hình
        if scaled_w == WINDOW_WIDTH and scaled_h == WINDOW_HEIGHT:
            screen.blit(virtual_screen, (offset_x, offset_y))
        else:
            scaled_surf = pygame.transform.smoothscale(virtual_screen, (scaled_w, scaled_h))
            screen.blit(scaled_surf, (offset_x, offset_y))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
