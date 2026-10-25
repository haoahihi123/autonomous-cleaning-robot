# -*- coding: utf-8 -*-
"""
Bộ vẽ giao diện đồ họa Pygame cho mô phỏng xe dọn rác
- Vẽ bản đồ trường, các khối nhà, cây xanh, đường đi
- Hiển thị vị trí xe, tầm nhìn cảm biến, rác và sinh viên di chuyển
- Thanh điều khiển bên phải (thông số pin, trạng thái, phím tắt, nhật ký)
"""

import time
import pygame
from config import (
    GRID_ROWS, GRID_COLS, CELL_SIZE, MAP_WIDTH, MAP_HEIGHT,
    SIDEBAR_WIDTH, TOPBAR_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT,
    CELL_EMPTY_ROAD, CELL_BUILDING, CELL_GARDEN, CELL_WATER, CELL_OUTSIDE,
    MAU_NEN_APP, MAU_THE_TRANG, MAU_THE_PHU, MAU_VIEN_THE, MAU_VIEN_PHU,
    MAU_CHU_CHINH, MAU_CHU_PHU, MAU_CHU_MO,
    MAU_XANH_GOOGLE, MAU_XANH_NHAT, MAU_XANH_DAM,
    MAU_XANH_LA, MAU_XANH_LA_NHAT,
    MAU_CAM, MAU_CAM_NHAT,
    MAU_DO,
    MAU_MAP_NGOAI, MAU_MAP_DAT, MAU_MAP_DUONG, MAU_MAP_VIEN_DUONG,
    MAU_MAP_CO, MAU_MAP_NUOC,
    MAU_KHOI_HOC, VIEN_KHOI_HOC,
    MAU_KHOI_TRUNGTAM, VIEN_KHOI_TRUNGTAM,
    MAU_KHOI_XUONG, VIEN_KHOI_XUONG,
    MAU_KHOI_DICHVU, VIEN_KHOI_DICHVU,
    FontManager
)

class SharpRenderer:
    """Quản lý vẽ giao diện và bản đồ mô phỏng"""

    def __init__(self, screen, grid, buildings):
        self.screen = screen
        self.grid = grid
        self.buildings = buildings
        self.fonts = FontManager.get_fonts()
        self.fog_enabled = False   # Phím F: bật/tắt sương mù tầm nhìn

        # Surface bán trong suốt cho ô đã đi qua và ô bỏ sót
        self.o_sach = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        self.o_sach.fill((26, 115, 232, 30))

        self.o_sot = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        self.o_sot.fill((217, 48, 37, 48))

        self.static_map_surf = pygame.Surface((MAP_WIDTH, MAP_HEIGHT))
        self.render_static_map()

    def render_static_map(self):
        """Vẽ sẵn nền bản đồ tĩnh để tối ưu FPS khi chạy"""
        surf = self.static_map_surf
        surf.fill(MAU_MAP_NGOAI)

        # 1.Vẽ nền khuôn viên, đường nội bộ, mảng cây xanh và hồ nước
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                cell = self.grid[r][c]
                if cell == CELL_OUTSIDE:
                    continue
                rect = (c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if cell == CELL_EMPTY_ROAD:
                    pygame.draw.rect(surf, MAU_MAP_DUONG, rect)
                    pygame.draw.rect(surf, MAU_MAP_VIEN_DUONG, rect, 1)
                elif cell == CELL_GARDEN:
                    pygame.draw.rect(surf, MAU_MAP_CO, rect)
                    pygame.draw.rect(surf, (162, 214, 176), rect, 1)
                elif cell == CELL_WATER:
                    pygame.draw.rect(surf, MAU_MAP_NUOC, rect)
                    pygame.draw.rect(surf, (145, 198, 238), rect, 1)
                else:
                    pygame.draw.rect(surf, MAU_MAP_DAT, rect)

        # 2.Vẽ đường viền ranh giới bao quanh khuôn viên trường (như bản vẽ 1/500)
        mau_ranh_gioi = (130, 140, 150)
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.grid[r][c] != CELL_OUTSIDE:
                    x, y = c * CELL_SIZE, r * CELL_SIZE
                    if r == 0 or self.grid[r - 1][c] == CELL_OUTSIDE:
                        pygame.draw.line(surf, mau_ranh_gioi, (x, y), (x + CELL_SIZE, y), 2)
                    if r == GRID_ROWS - 1 or self.grid[r + 1][c] == CELL_OUTSIDE:
                        pygame.draw.line(surf, mau_ranh_gioi, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 2)
                    if c == 0 or self.grid[r][c - 1] == CELL_OUTSIDE:
                        pygame.draw.line(surf, mau_ranh_gioi, (x, y), (x, y + CELL_SIZE), 2)
                    if c == GRID_COLS - 1 or self.grid[r][c + 1] == CELL_OUTSIDE:
                        pygame.draw.line(surf, mau_ranh_gioi, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)

        # 3.Vẽ các khối công trình kiến trúc theo đúng 4 nhóm màu quy hoạch 1/500
        for b in self.buildings:
            col, row, w, h = b.rect
            rect = pygame.Rect(
                col * CELL_SIZE + 1,
                row * CELL_SIZE + 1,
                w * CELL_SIZE - 2,
                h * CELL_SIZE - 2
            )

            if b.category == "sanbong":
                # Sân bóng đá ngoài trời ở góc Đông Nam (Nền kem vàng nhạt + vạch sân cỏ)
                pygame.draw.rect(surf, b.color, rect, border_radius=3)
                pygame.draw.rect(surf, b.border_color, rect, 1, border_radius=3)
                inner_pitch = rect.inflate(-10, -10)
                pygame.draw.rect(surf, (218, 240, 222), inner_pitch, border_radius=2)
                pygame.draw.rect(surf, (165, 205, 172), inner_pitch, 1, border_radius=2)
                pygame.draw.line(surf, (165, 205, 172), (inner_pitch.centerx, inner_pitch.top), (inner_pitch.centerx, inner_pitch.bottom), 1)
                pygame.draw.circle(surf, (165, 205, 172), inner_pitch.center, 10, 1)
            else:
                pygame.draw.rect(surf, b.color, rect, border_radius=3)
                pygame.draw.rect(surf, b.border_color, rect, 1, border_radius=3)
                # Viền sáng nhẹ mô phỏng ánh sáng kiến trúc 2D trên nóc tòa nhà
                pygame.draw.line(surf, (255, 255, 255, 120), (rect.left + 2, rect.top + 1), (rect.right - 2, rect.top + 1), 1)

            nhan = self.fonts.map_label.render(b.code, True, b.text_color)
            surf.blit(nhan, nhan.get_rect(center=rect.center))

        # 4.Vẽ Bảng Chú Thích Bản Đồ Hiện Trạng 1/500 ở góc Tây Bắc (đúng vị trí bản vẽ thật)
        self.ve_bang_chu_thich_1500(surf)

        # 5.Vẽ các Cổng trường theo đúng hồ sơ thực tế (Võ Văn Ngân & 3 cổng đường Lê Văn Chí)
        self.ve_nhan_cong(surf, "Cổng chính Võ Văn Ngân", int(24 * CELL_SIZE), (GRID_ROWS - 1) * CELL_SIZE - 2, "south")
        self.ve_nhan_cong(surf, "Cổng phụ", int(9 * CELL_SIZE), (GRID_ROWS - 1) * CELL_SIZE - 2, "south")

        # 3 Cổng hướng ra đường Lê Văn Chí (đúng vị trí hành lang giao thông thông suốt):
        self.ve_nhan_cong(surf, "Cổng KTX Lê Văn Chí", (GRID_COLS - 1) * CELL_SIZE, int(1.5 * CELL_SIZE), "east")
        self.ve_nhan_cong(surf, "Cổng phụ Lê Văn Chí", (GRID_COLS - 1) * CELL_SIZE, int(9.5 * CELL_SIZE), "east")
        self.ve_nhan_cong(surf, "Cổng phụ Lê Văn Chí", (GRID_COLS - 1) * CELL_SIZE, int(21.5 * CELL_SIZE), "east")

    def ve_bang_chu_thich_1500(self, surf):
        """Vẽ thẻ Chú thích bản đồ hiện trạng 1/500 gọn gàng ở góc Tây Bắc, không che khuất bất kỳ khối nhà hay đường đi nào"""
        box = pygame.Rect(8, 8, 184, 194)
        pygame.draw.rect(surf, (226, 230, 236), box.move(1, 1), border_radius=6)
        pygame.draw.rect(surf, MAU_THE_TRANG, box, border_radius=6)
        pygame.draw.rect(surf, MAU_VIEN_THE, box, 1, border_radius=6)

        x = box.left + 8
        y = box.top + 6
        t1 = self.fonts.heading.render("BẢN ĐỒ HIỆN TRẠNG 1/500", True, MAU_CHU_CHINH)
        surf.blit(t1, (x, y))
        y += 15
        t2 = self.fonts.tiny.render("ĐH Công nghệ Kỹ thuật TP.HCM", True, MAU_CHU_PHU)
        surf.blit(t2, (x, y))
        y += 14
        pygame.draw.line(surf, MAU_VIEN_THE, (x, y), (box.right - 8, y), 1)
        y += 5

        nhom_mau = [
            (MAU_KHOI_HOC, VIEN_KHOI_HOC, "Khối phòng học (A, B, C, D, E, F)"),
            (MAU_KHOI_TRUNGTAM, VIEN_KHOI_TRUNGTAM, "Tòa Trung tâm - Hội trường - TV"),
            (MAU_KHOI_XUONG, VIEN_KHOI_XUONG, "Xưởng TH - Maker Space - PTN"),
            (MAU_KHOI_DICHVU, VIEN_KHOI_DICHVU, "Văn phòng dịch vụ - Căn tin"),
            (MAU_MAP_CO, (140, 195, 155), "Mảng cây xanh - Hoa viên"),
        ]
        for mau_nen, mau_vien, mo_ta in nhom_mau:
            o_mau = pygame.Rect(x, y + 1, 12, 8)
            pygame.draw.rect(surf, mau_nen, o_mau, border_radius=2)
            pygame.draw.rect(surf, mau_vien, o_mau, 1, border_radius=2)
            txt = self.fonts.tiny.render(mo_ta, True, MAU_CHU_CHINH)
            surf.blit(txt, (x + 18, y))
            y += 13

        y += 3
        pygame.draw.line(surf, MAU_VIEN_THE, (x, y), (box.right - 8, y), 1)
        y += 5

        ky_hieu = [
            "• A1 - A5: Tòa Trung tâm & Giảng đường",
            "• Khối B, Thư viện & Cánh Khối A",
            "• Hội trường lớn, Khối A10, Sân V.Đức",
            "• Khu C, D: Khoa Điện - Điện tử",
            "• Maker Space, Toyota & Cụm xưởng",
        ]
        for dong in ky_hieu:
            txt = self.fonts.map_sub.render(dong, True, MAU_CHU_PHU)
            surf.blit(txt, (x, y))
            y += 11

    def ve_nhan_cong(self, surf, chu, tam_x, tam_y, huong="south"):
        """Vẽ thẻ định vị cổng trường gọn đẹp, không che khuất công trình"""
        nhan = self.fonts.map_sub.render(chu, True, MAU_CHU_CHINH)
        if huong == "east":
            khung = nhan.get_rect(midright=(tam_x - 4, tam_y)).inflate(12, 4)
        else:
            khung = nhan.get_rect(center=(tam_x, tam_y)).inflate(14, 4)

        khung.clamp_ip(pygame.Rect(4, 4, MAP_WIDTH - 6, MAP_HEIGHT - 4))
        pygame.draw.rect(surf, (222, 226, 232), khung.move(0, 1), border_radius=khung.height // 2)
        pygame.draw.rect(surf, MAU_THE_TRANG, khung, border_radius=khung.height // 2)
        pygame.draw.rect(surf, MAU_VIEN_PHU, khung, 1, border_radius=khung.height // 2)
        pygame.draw.circle(surf, MAU_XANH_GOOGLE, (khung.left + 6, khung.centery), 2.5)
        surf.blit(nhan, nhan.get_rect(midleft=(khung.left + 11, khung.centery)))

    # 2.VẼ TỔNG THỂ MỖI KHUNG HÌNH (MAIN DRAW LOOP)
    def draw(self, robot, trash_list, dynamic_obstacles, fps, elapsed_time, is_paused=False):
        """Vẽ toàn bộ giao diện: Bản đồ Vector 1/500 + Topbar + Sidebar Card"""
        self.screen.fill(MAU_NEN_APP)

        # 1.Nền bản đồ Vector 1/500
        self.screen.blit(self.static_map_surf, (0, TOPBAR_HEIGHT))
        pygame.draw.line(self.screen, MAU_VIEN_THE, (MAP_WIDTH, TOPBAR_HEIGHT), (MAP_WIDTH, WINDOW_HEIGHT), 1)

        # 2.Ô đã quét (phủ xanh dịu) và ô bỏ sót (đỏ dịu)
        for (r, c) in robot.visited_cells:
            self.screen.blit(self.o_sach, (c * CELL_SIZE, TOPBAR_HEIGHT + r * CELL_SIZE))

        for (r, c) in robot.missed_cells:
            x, y = c * CELL_SIZE, TOPBAR_HEIGHT + r * CELL_SIZE
            self.screen.blit(self.o_sot, (x, y))
            pygame.draw.rect(self.screen, MAU_DO, (x, y, CELL_SIZE, CELL_SIZE), 1)

        # 2.5. Trạm sạc pin Tòa D (Charging Station)
        cs_pos = getattr(robot, "vi_tri_tram_sac", getattr(robot, "charging_station_pos", (8, 18)))
        cs_x = cs_pos[1] * CELL_SIZE
        cs_y = TOPBAR_HEIGHT + cs_pos[0] * CELL_SIZE
        cs_rect = pygame.Rect(cs_x, cs_y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, (254, 243, 199), cs_rect, border_radius=3)
        pygame.draw.rect(self.screen, (245, 158, 11), cs_rect, 1, border_radius=3)
        bolt_surf = self.fonts.tiny.render("⚡", True, (217, 119, 6))
        self.screen.blit(bolt_surf, bolt_surf.get_rect(center=cs_rect.center))

        if getattr(robot, "state", "") == getattr(robot, "STATE_CHARGING", ""):
            pulse = int((time.time() * 5) % 3) * 2
            pygame.draw.circle(self.screen, (245, 158, 11), cs_rect.center, CELL_SIZE // 2 + pulse + 2, 1)

        # 3.Lộ trình xe dự kiến (Đường chỉ dẫn Google Maps)
        if robot.active_path:
            diem = [self.tam_o(robot.r, robot.c)] + [self.tam_o(r, c) for r, c in robot.active_path]
            if len(diem) >= 2:
                pygame.draw.lines(self.screen, MAU_XANH_GOOGLE, False, diem, 2)

        # 4.Các điểm rác
        for t in trash_list:
            if not self.fog_enabled or robot.is_in_sensor_range(t.pos):
                tam = self.tam_o(*t.pos)
                pygame.draw.circle(self.screen, t.color, tam, 4)
                pygame.draw.circle(self.screen, (90, 100, 115), tam, 4, 1)

        # 5.Sinh viên di chuyển
        for obs in dynamic_obstacles:
            if not self.fog_enabled or robot.is_in_sensor_range(obs.get_pos()):
                tam = self.tam_o(obs.r, obs.c)
                pygame.draw.circle(self.screen, MAU_THE_TRANG, tam, 6)
                pygame.draw.circle(self.screen, (75, 85, 99), tam, 4)

        # 6.Xe dọn rác: Định vị GPS Google Maps (Chặn tia cảm biến khi gặp tường tòa nhà)
        rx, ry = self.tam_o(robot.r, robot.c)
        ban_kinh = int(robot.sensor_radius * CELL_SIZE)
        top_left_x = rx - ban_kinh
        top_left_y = ry - ban_kinh

        vung = pygame.Surface((ban_kinh * 2, ban_kinh * 2), pygame.SRCALPHA)
        pygame.draw.circle(vung, (26, 115, 232, 22), (ban_kinh, ban_kinh), ban_kinh)
        pygame.draw.circle(vung, (26, 115, 232, 95), (ban_kinh, ban_kinh), ban_kinh, 1)

        song = int(robot.pulse_radius * CELL_SIZE)
        if song > 0:
            pygame.draw.circle(vung, (26, 115, 232, 55), (ban_kinh, ban_kinh), song, 1)

        # Cắt bỏ vùng sóng cảm biến tại các ô tòa nhà hoặc ô bị tường chắn tầm nhìn
        r_span = int(robot.sensor_radius) + 2
        for nr in range(max(0, robot.r - r_span), min(GRID_ROWS, robot.r + r_span + 1)):
            for nc in range(max(0, robot.c - r_span), min(GRID_COLS, robot.c + r_span + 1)):
                if self.grid[nr][nc] == CELL_BUILDING or not robot.is_in_sensor_range((nr, nc)):
                    local_x = nc * CELL_SIZE - top_left_x
                    local_y = (TOPBAR_HEIGHT + nr * CELL_SIZE) - top_left_y
                    pygame.draw.rect(vung, (0, 0, 0, 0), (local_x, local_y, CELL_SIZE, CELL_SIZE))

        self.screen.blit(vung, (top_left_x, top_left_y))

        pygame.draw.circle(self.screen, MAU_THE_TRANG, (rx, ry), 7)
        pygame.draw.circle(self.screen, MAU_XANH_GOOGLE, (rx, ry), 4.5)
        pygame.draw.circle(self.screen, MAU_THE_TRANG, (rx, ry), 1.5)

        # 7.Sương mù tầm nhìn giới hạn (Fog of War) nếu bật - Không nhìn xuyên tòa nhà
        if self.fog_enabled:
            suong = pygame.Surface((MAP_WIDTH, MAP_HEIGHT), pygame.SRCALPHA)
            suong.fill((32, 33, 36, 145))
            pygame.draw.circle(suong, (0, 0, 0, 0), (rx, ry - TOPBAR_HEIGHT), ban_kinh)
            for nr in range(max(0, robot.r - r_span), min(GRID_ROWS, robot.r + r_span + 1)):
                for nc in range(max(0, robot.c - r_span), min(GRID_COLS, robot.c + r_span + 1)):
                    if self.grid[nr][nc] == CELL_BUILDING or not robot.is_in_sensor_range((nr, nc)):
                        pygame.draw.rect(suong, (32, 33, 36, 145), (nc * CELL_SIZE, nr * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            self.screen.blit(suong, (0, TOPBAR_HEIGHT))

        # 8.Render Topbar & Sidebar
        self.draw_topbar(robot, fps, elapsed_time, is_paused)
        self.draw_sidebar(robot, len(trash_list), len(dynamic_obstacles), is_paused)

    # 3.HÀM TIỆN ÍCH VẼ GIAO DIỆN
    def tam_o(self, r, c):
        """Tọa độ pixel tâm của ô (r, c)"""
        return (c * CELL_SIZE + CELL_SIZE // 2, TOPBAR_HEIGHT + r * CELL_SIZE + CELL_SIZE // 2)

    def chu(self, font, noi_dung, mau, x, y):
        """Vẽ chuỗi chữ và trả về chiều rộng"""
        anh = font.render(noi_dung, True, mau)
        self.screen.blit(anh, (x, y))
        return anh.get_width()

    def cat_chu(self, font, noi_dung, rong_toi_da):
        """Cắt bớt chuỗi nếu quá dài kèm dấu ..."""
        if font.size(noi_dung)[0] <= rong_toi_da:
            return noi_dung
        while noi_dung and font.size(noi_dung + "...")[0] > rong_toi_da:
            noi_dung = noi_dung[:-1]
        return noi_dung + "..."

    def ve_pill(self, noi_dung, x_phai, y, mau_nen=MAU_THE_PHU, mau_vien=MAU_VIEN_PHU, mau_chu=MAU_CHU_PHU):
        """Vẽ viên badge căn phải, trả về tọa độ x bên trái"""
        anh = self.fonts.small.render(noi_dung, True, mau_chu)
        w = anh.get_width() + 16
        h = 24
        khung = pygame.Rect(x_phai - w, y, w, h)
        pygame.draw.rect(self.screen, mau_nen, khung, border_radius=12)
        pygame.draw.rect(self.screen, mau_vien, khung, 1, border_radius=12)
        self.screen.blit(anh, anh.get_rect(center=khung.center))
        return khung.left

    def ve_status_pill(self, is_paused, x_phai, y):
        """Vẽ badge trạng thái có chấm màu chuẩn Google Cloud"""
        text = "Tạm dừng" if is_paused else "Đang chạy"
        mau_nen = (254, 243, 199) if is_paused else (230, 244, 234)
        mau_vien = (251, 211, 141) if is_paused else (168, 218, 181)
        mau_cham = (217, 119, 6) if is_paused else (24, 128, 56)
        mau_chu = (180, 83, 9) if is_paused else (24, 128, 56)

        anh = self.fonts.small.render(text, True, mau_chu)
        w = anh.get_width() + 24
        h = 24
        khung = pygame.Rect(x_phai - w, y, w, h)
        pygame.draw.rect(self.screen, mau_nen, khung, border_radius=12)
        pygame.draw.rect(self.screen, mau_vien, khung, 1, border_radius=12)
        pygame.draw.circle(self.screen, mau_cham, (khung.left + 9, khung.centery), 3.5)
        self.screen.blit(anh, (khung.left + 16, khung.centery - anh.get_height() // 2))
        return khung.left

    # 4.THANH TIÊU ĐỀ PHẲNG CHUẨN GOOGLE / FACEBOOK
    def draw_topbar(self, robot, fps, elapsed_time, is_paused):
        """Thanh điều hướng trên cùng phong cách Google Workspace"""
        pygame.draw.rect(self.screen, MAU_THE_TRANG, (0, 0, WINDOW_WIDTH, TOPBAR_HEIGHT))
        pygame.draw.line(self.screen, MAU_VIEN_THE, (0, TOPBAR_HEIGHT - 1), (WINDOW_WIDTH, TOPBAR_HEIGHT - 1), 1)

        icon_rect = pygame.Rect(12, 9, 26, 26)
        pygame.draw.rect(self.screen, MAU_XANH_NHAT, icon_rect, border_radius=6)
        pygame.draw.rect(self.screen, (200, 220, 248), icon_rect, 1, border_radius=6)
        pygame.draw.circle(self.screen, MAU_XANH_GOOGLE, icon_rect.center, 5)
        pygame.draw.circle(self.screen, MAU_THE_TRANG, icon_rect.center, 2)

        tx = 46
        self.chu(self.fonts.title, "Hệ Thống Xe Dọn Rác Tự Hành", MAU_CHU_CHINH, tx, 6)
        self.chu(self.fonts.small,
                 "Bản đồ quy hoạch 1/500 ĐH Công nghệ Kỹ thuật TP.HCM · Hải Yến & Cảnh Hào",
                 MAU_CHU_PHU, tx, 24)

        x = WINDOW_WIDTH - 12
        y_badge = 10

        x = self.ve_status_pill(is_paused, x, y_badge) - 6

        phut, giay = int(elapsed_time // 60), int(elapsed_time % 60)
        x = self.ve_pill(f"⏱ {phut:02d}:{giay:02d}", x, y_badge) - 6

        self.ve_pill(f"⚡ {fps:.0f} FPS", x, y_badge)

    # Vẽ thanh thông tin điều khiển bên phải
    def draw_sidebar(self, robot, trash_count, obstacle_count, is_paused):
        card_x = MAP_WIDTH + 8
        card_w = SIDEBAR_WIDTH - 16

        # Thẻ 1: Trạng thái và tiến độ
        c1_y = TOPBAR_HEIGHT + 6
        c1_h = 92
        c1_rect = pygame.Rect(card_x, c1_y, card_w, c1_h)
        pygame.draw.rect(self.screen, (226, 230, 236), c1_rect.move(0, 1), border_radius=8)
        pygame.draw.rect(self.screen, MAU_THE_TRANG, c1_rect, border_radius=8)
        pygame.draw.rect(self.screen, MAU_VIEN_THE, c1_rect, 1, border_radius=8)

        self.chu(self.fonts.tiny, "TRẠNG THÁI & TIẾN ĐỘ", MAU_CHU_MO, card_x + 12, c1_y + 8)

        bat_pct = getattr(robot, "phan_tram_pin", getattr(robot, "battery", 100.0))
        is_charging = getattr(robot, "state", "") == getattr(robot, "STATE_CHARGING", "")
        if is_charging:
            bat_color = (217, 119, 6)
            bat_txt = f"{bat_pct:.0f}%"
        elif bat_pct > 50:
            bat_color = (22, 163, 74)
            bat_txt = f"{bat_pct:.0f}%"
        elif bat_pct > 20:
            bat_color = (217, 119, 6)
            bat_txt = f"{bat_pct:.0f}%"
        else:
            bat_color = (220, 38, 38)
            bat_txt = f"{bat_pct:.0f}%"

        bat_render = self.fonts.small.render(bat_txt, True, bat_color)
        txt_x = card_x + card_w - 12 - bat_render.get_width()
        self.screen.blit(bat_render, (txt_x, c1_y + 7))

        bx = txt_x - 22
        by = c1_y + 9
        pygame.draw.rect(self.screen, (195, 200, 208), (bx, by, 17, 9), 1, border_radius=2)
        pygame.draw.rect(self.screen, (195, 200, 208), (bx + 17, by + 2, 2, 5), border_radius=1)
        fill_w = max(0, int(15 * min(1.0, bat_pct / 100)))
        if fill_w > 0:
            pygame.draw.rect(self.screen, bat_color, (bx + 1, by + 1, fill_w, 7), border_radius=1)

        state_color_map = {
            "patrol": ("Đang tuần tra", (232, 240, 254), (187, 214, 251), (26, 115, 232)),
            "cleaning": ("Đang gom rác", (230, 244, 234), (168, 218, 181), (24, 128, 56)),
            "avoiding": ("Né vật cản", (254, 237, 237), (250, 180, 180), (217, 48, 37)),
            "re-planning": ("Tìm đường vòng", (254, 237, 237), (250, 180, 180), (217, 48, 37)),
            "về trạm sạc tòa d": ("Về sạc Tòa D", (254, 243, 199), (251, 211, 141), (217, 119, 6)),
            "đang sạc pin (tòa d)": (f"Nạp pin ⚡ ({bat_pct:.0f}%)", (254, 243, 199), (251, 211, 141), (217, 119, 6)),
        }
        st_raw = robot.state.lower()
        st_info = state_color_map.get(st_raw, (robot.state, (241, 243, 244), (218, 220, 224), MAU_CHU_CHINH))
        st_text, bg_col, brd_col, txt_col = st_info

        st_pill = self.fonts.small.render(st_text, True, txt_col)
        st_rect = pygame.Rect(card_x + 12, c1_y + 24, st_pill.get_width() + 18, 20)
        pygame.draw.rect(self.screen, bg_col, st_rect, border_radius=10)
        pygame.draw.rect(self.screen, brd_col, st_rect, 1, border_radius=10)
        pygame.draw.circle(self.screen, txt_col, (st_rect.left + 7, st_rect.centery), 2.5)
        self.screen.blit(st_pill, (st_rect.left + 13, st_rect.centery - st_pill.get_height() // 2))

        mode_name = "Quét phân vùng" if getattr(robot, "strategy_mode", "") == "zonal" else "Quét luống cày"
        self.chu(self.fonts.small, mode_name, MAU_CHU_PHU, st_rect.right + 10, c1_y + 27)

        tong_o = sum(hang.count(CELL_EMPTY_ROAD) for hang in self.grid)
        da_quet = len(robot.visited_cells)
        phan_tram = (da_quet / tong_o * 100) if tong_o else 0

        self.chu(self.fonts.big, f"{phan_tram:.0f}%", MAU_XANH_GOOGLE, card_x + 12, c1_y + 48)
        self.chu(self.fonts.small, f"Chu kỳ {robot.cycle_count}", MAU_CHU_CHINH, card_x + 60, c1_y + 51)

        detail_txt = f"{da_quet}/{tong_o} ô"
        d_render = self.fonts.small.render(detail_txt, True, MAU_CHU_MO)
        self.screen.blit(d_render, (card_x + card_w - 12 - d_render.get_width(), c1_y + 51))

        bar_x = card_x + 12
        bar_y = c1_y + 74
        bar_w = card_w - 24
        bar_h = 7
        pygame.draw.rect(self.screen, (238, 242, 246), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        pygame.draw.rect(self.screen, (226, 230, 235), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)
        if da_quet > 0:
            fill_w = max(4, int(bar_w * min(1.0, phan_tram / 100)))
            pygame.draw.rect(self.screen, MAU_XANH_GOOGLE, (bar_x, bar_y, fill_w, bar_h), border_radius=3)

        # Thẻ 2: Thông số thời gian thực
        c2_y = c1_y + c1_h + 6
        c2_h = 92
        c2_rect = pygame.Rect(card_x, c2_y, card_w, c2_h)
        pygame.draw.rect(self.screen, (226, 230, 236), c2_rect.move(0, 1), border_radius=8)
        pygame.draw.rect(self.screen, MAU_THE_TRANG, c2_rect, border_radius=8)
        pygame.draw.rect(self.screen, MAU_VIEN_THE, c2_rect, 1, border_radius=8)

        self.chu(self.fonts.tiny, "CHỈ SỐ THỜI GIAN THỰC", MAU_CHU_MO, card_x + 12, c2_y + 8)

        so_lieu = [
            ("Rác đã gom", robot.collected_trash_count, (24, 128, 56)),
            ("Rác còn lại", trash_count, (26, 115, 232)),
            ("Ô bỏ sót", len(robot.missed_cells), (217, 48, 37) if robot.missed_cells else MAU_CHU_PHU),
            ("Sinh viên", obstacle_count, (75, 85, 99)),
        ]

        tile_w = (card_w - 30) // 2
        tile_h = 28
        for i, (nhan, gia_tri, mau_so) in enumerate(so_lieu):
            tx = card_x + 12 + (i % 2) * (tile_w + 6)
            ty = c2_y + 24 + (i // 2) * (tile_h + 6)

            t_box = pygame.Rect(tx, ty, tile_w, tile_h)
            pygame.draw.rect(self.screen, MAU_THE_PHU, t_box, border_radius=5)
            pygame.draw.rect(self.screen, MAU_VIEN_THE, t_box, 1, border_radius=5)
            pygame.draw.rect(self.screen, mau_so, (t_box.left, t_box.top, 3, t_box.height), border_top_left_radius=5, border_bottom_left_radius=5)

            self.chu(self.fonts.tiny, nhan, MAU_CHU_PHU, tx + 8, ty + 7)
            val_render = self.fonts.stat.render(str(gia_tri), True, mau_so)
            self.screen.blit(val_render, (t_box.right - val_render.get_width() - 8, ty + 4))

        # Thẻ 3: Bảng phím tắt
        c3_y = c2_y + c2_h + 6
        c3_h = 130
        c3_rect = pygame.Rect(card_x, c3_y, card_w, c3_h)
        pygame.draw.rect(self.screen, (226, 230, 236), c3_rect.move(0, 1), border_radius=8)
        pygame.draw.rect(self.screen, MAU_THE_TRANG, c3_rect, border_radius=8)
        pygame.draw.rect(self.screen, MAU_VIEN_THE, c3_rect, 1, border_radius=8)

        self.chu(self.fonts.tiny, "PHÍM TẮT ĐIỀU KHIỂN", MAU_CHU_MO, card_x + 12, c3_y + 8)

        phim_tat = [
            ("Space", "Tạm dừng"),   ("Z", "Đổi thuật toán"),
            ("B", "Sạc pin Tòa D"),  ("F", "Sương mù"),
            ("C", "Rác giờ nghỉ"),   ("R", "Thêm rác"),
            ("O", "Thêm SV"),        ("+ / -", "Tốc độ xe"),
        ]

        col_w = (card_w - 24) // 2
        for i, (phim, mo_ta) in enumerate(phim_tat):
            kx = card_x + 12 + (i % 2) * col_w
            ky = c3_y + 24 + (i // 2) * 20

            k_surf = self.fonts.tiny.render(phim, True, MAU_CHU_CHINH)
            k_box = pygame.Rect(kx, ky, max(22, k_surf.get_width() + 8), 16)
            pygame.draw.rect(self.screen, (244, 245, 247), k_box, border_radius=3)
            pygame.draw.rect(self.screen, (218, 220, 224), k_box, 1, border_radius=3)
            pygame.draw.line(self.screen, (190, 194, 200), (k_box.left + 2, k_box.bottom - 1), (k_box.right - 2, k_box.bottom - 1), 1)
            self.screen.blit(k_surf, k_surf.get_rect(center=k_box.center))

            self.chu(self.fonts.tiny, mo_ta, MAU_CHU_PHU, k_box.right + 6, ky + 1)

        pygame.draw.line(self.screen, (243, 244, 246), (card_x + 12, c3_y + 107), (card_x + card_w - 12, c3_y + 107), 1)
        self.chu(self.fonts.tiny, "Chuột trái: Thả rác  ·  Chuột phải: Thêm SV", MAU_CHU_MO, card_x + 12, c3_y + 111)

        # Thẻ 4: Nhật ký hoạt động
        c4_y = c3_y + c3_h + 6
        c4_h = WINDOW_HEIGHT - c4_y - 6
        c4_rect = pygame.Rect(card_x, c4_y, card_w, c4_h)
        pygame.draw.rect(self.screen, (226, 230, 236), c4_rect.move(0, 1), border_radius=8)
        pygame.draw.rect(self.screen, MAU_THE_TRANG, c4_rect, border_radius=8)
        pygame.draw.rect(self.screen, MAU_VIEN_THE, c4_rect, 1, border_radius=8)

        self.chu(self.fonts.tiny, "NHẬT KÝ HOẠT ĐỘNG", MAU_CHU_MO, card_x + 12, c4_y + 8)

        so_dong = max(0, (c4_h - 26) // 16)
        dong_hien = robot.event_logs[-so_dong:] if so_dong else []

        if dong_hien:
            line_h = min(c4_h - 32, len(dong_hien) * 16 - 6)
            if line_h > 0:
                pygame.draw.line(self.screen, (230, 234, 240), (card_x + 16, c4_y + 30), (card_x + 16, c4_y + 30 + line_h), 1)

        for i, dong in enumerate(reversed(dong_hien)):
            ly = c4_y + 24 + i * 16
            mau = MAU_CHU_CHINH if i == 0 else MAU_CHU_PHU
            if i == 0:
                pygame.draw.circle(self.screen, (232, 240, 254), (card_x + 16, ly + 6), 4)
                pygame.draw.circle(self.screen, MAU_XANH_GOOGLE, (card_x + 16, ly + 6), 2.5)
            else:
                pygame.draw.circle(self.screen, (180, 185, 192), (card_x + 16, ly + 6), 2)

            rut_gon = self.cat_chu(self.fonts.tiny, dong, card_w - 32)
            self.chu(self.fonts.tiny, rut_gon, mau, card_x + 25, ly)
