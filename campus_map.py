# -*- coding: utf-8 -*-
"""
MODULE BẢN ĐỒ HIỆN TRẠNG 1/500 TRƯỜNG ĐH CÔNG NGHỆ KỸ THUẬT TP.HCM (48x36 Ô LƯỚI)
Mô phỏng chính xác bố cục không gian và 4 nhóm màu khối công trình theo Bản đồ hiện trạng tỉ lệ 1/500:
- Đầy đủ các khối công trình: Toyota, Maker Space, Sân Việt Đức, Khối A10, Khối G, TH Khoa XD...
"""

from config import (
    GRID_COLS, GRID_ROWS,
    CELL_EMPTY_ROAD, CELL_BUILDING, CELL_GARDEN, CELL_WATER, CELL_SPORTS, CELL_OUTSIDE,
    MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC,
    MAU_KHOI_TRUNGTAM, VIEN_KHOI_TRUNGTAM, CHU_KHOI_TRUNGTAM,
    MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG,
    MAU_KHOI_DICHVU, VIEN_KHOI_DICHVU, CHU_KHOI_DICHVU,
    MAU_MAP_SAN_BONG
)


class BuildingInfo:
    """Đại diện cho một khối công trình kiến trúc trên bản đồ quy hoạch 1/500"""
    def __init__(self, name, rect, code, category, color, border_color, text_color):
        self.name = name
        self.rect = rect               # (col, row, width, height)
        self.code = code               # Nhãn hiển thị trên khối nhà
        self.category = category       # Nhóm công trình theo chú thích 1/500
        self.color = color
        self.border_color = border_color
        self.text_color = text_color


def create_hcmute_campus():
    grid = [[CELL_EMPTY_ROAD for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

    # 1. Ranh giới ngoài:
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if r == 0 or r == GRID_ROWS - 1 or c == 0 or c == GRID_COLS - 1:
                grid[r][c] = CELL_OUTSIDE
            # Vạt góc nhẹ ở đường Lê Văn Chí
            elif r <= 2 and c >= 44:
                grid[r][c] = CELL_OUTSIDE
            # KHU VỰC DÀNH CHO BẢNG CHÚ THÍCH BẢN ĐỒ 1/500 (Góc Tây Bắc: col 0..12, row 0..13)
            # Không có KTX, không có bãi cỏ KTX, đặt trọn vẹn Bảng Chú Thích không bị che khuất
            elif r <= 13 and c <= 12:
                grid[r][c] = CELL_OUTSIDE

    # 2. Danh sách khối nhà CHUẨN XÁC THEO MAP GỐC
    buildings = [
        # =====================================================================
        # TRỤC TRUNG TÂM PHÍA BẮC (KHỐI C, D, B, THƯ VIỆN, KHỐI A)
        # =====================================================================
        # Khối C: Cực kỳ thanh mảnh, dài dọc bên trái Khối B
        BuildingInfo("KHỐI C (KHOA ĐIỆN - ĐT)", (15, 2, 4, 6), "Khối C", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        # Khối B: Phòng học chung & PTN
        BuildingInfo("KHỐI B", (21, 2, 7, 5), "Khối B", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        # Khối Thư viện: Khối hồng nằm ngang giữa B và A
        BuildingInfo("THƯ VIỆN TRUNG TÂM", (21, 8, 7, 3), "Thư Viện", "trungtam",
                     MAU_KHOI_TRUNGTAM, VIEN_KHOI_TRUNGTAM, CHU_KHOI_TRUNGTAM),
        # Khối D: Thanh mảnh, dài dọc bên trái Khối A
        BuildingInfo("KHỐI D (KHOA ĐIỆN - ĐT)", (15, 9, 4, 7), "Khối D", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        # Khối A: Giảng đường chung
        BuildingInfo("KHỐI A", (21, 12, 7, 4), "Khối A", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),

        # =====================================================================
        # HỘI TRƯỜNG LỚN, KHỐI A10, SÂN VIỆT ĐỨC (CHUẨN HÓA VỊ TRÍ SO VỚI MAP GỐC)
        # Khối A10 nằm trên Sân Việt Đức.
        # Hội Trường Lớn và Sân Việt Đức NẰM CÙNG HÀNG NGANG (cùng row 20..23)!
        # =====================================================================
        BuildingInfo("KHỐI A10", (22, 17, 6, 2), "Khối A10", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("HỘI TRƯỜNG LỚN", (14, 20, 6, 4), "Hội Trường", "trungtam",
                     MAU_KHOI_TRUNGTAM, VIEN_KHOI_TRUNGTAM, CHU_KHOI_TRUNGTAM),
        BuildingInfo("SÂN VIỆT ĐỨC", (22, 20, 6, 4), "Sân Việt Đức", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),

        # =====================================================================
        # TÒA NHÀ TRUNG TÂM (MẶT TIỀN VÕ VĂN NGÂN)
        # =====================================================================
        BuildingInfo("CÁNH A2-A3", (14, 25, 5, 4), "Khu A2-A3", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("TÒA TRUNG TÂM A1", (21, 25, 7, 5), "Tòa TT A1", "trungtam",
                     MAU_KHOI_TRUNGTAM, VIEN_KHOI_TRUNGTAM, CHU_KHOI_TRUNGTAM),
        BuildingInfo("CÁNH A4-A5", (29, 25, 5, 4), "Khu A4-A5", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),

        # =====================================================================
        # PHÂN KHU ĐÔNG (MAKER SPACE, TOYOTA, SÂN BÓNG, CỤM XƯỞNG)
        # =====================================================================
        BuildingInfo("TRẠM Y TẾ", (30, 2, 4, 3), "Y tế", "dichvu",
                     MAU_KHOI_DICHVU, VIEN_KHOI_DICHVU, CHU_KHOI_DICHVU),
        BuildingInfo("XƯỞNG THỰC HÀNH Ô TÔ", (36, 2, 7, 3), "X.Động Lực", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("XƯỞNG NHIỆT - ĐIỆN LẠNH", (30, 6, 5, 4), "X.Nhiệt Lạnh", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("XƯỞNG CƠ KHÍ", (36, 6, 6, 4), "X.Cơ Khí", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("KHỐI F.1", (30, 11, 5, 4), "Khối F.1", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("TH KHOA XD", (36, 11, 7, 3), "TH Khoa XD", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("KHỐI G (TT VIỆT ĐỨC)", (30, 16, 5, 5), "Khối G", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("KHU MAKER SPACE", (36, 15, 6, 6), "Maker Space", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("DỊCH VỤ Ô TÔ TOYOTA", (43, 15, 3, 6), "Toyota", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("SÂN BÓNG ĐÁ NGOÀI TRỜI", (34, 23, 12, 10), "Sân Bóng Đá", "sanbong",
                     MAU_MAP_SAN_BONG, (210, 205, 180), (90, 100, 80)),

        # =====================================================================
        # PHÂN KHU TÂY & TÂY NAM (KHỐI E CƠ KHÍ MÁY & CĂN TIN - DƯỚI BẢNG CHÚ THÍCH)
        # Bảng chú thích kết thúc ở row 13.
        # Hàng 14, 15 là đường giao thông thông thoáng (CELL_EMPTY_ROAD).
        # Khối E.1 và Xưởng bắt đầu từ row 16.
        # =====================================================================
        BuildingInfo("XƯỞNG HÀN / IN", (1, 16, 4, 4), "Xưởng Hàn", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("KHỐI E.1 (CƠ KHÍ MÁY)", (6, 16, 6, 3), "Khối E.1", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("CĂN TIN - SIÊU THỊ E.2", (7, 20, 5, 3), "Căn Tin E2", "dichvu",
                     MAU_KHOI_DICHVU, VIEN_KHOI_DICHVU, CHU_KHOI_DICHVU),
        BuildingInfo("KHỐI E.0 (VP KHOA)", (1, 21, 4, 6), "Khối E.0", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("KHỐI E.3 (XƯỞNG CƠ KHÍ MÁY)", (6, 24, 6, 4), "Xưởng E.3", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("KHỐI E.4 (BÁT GIÁC)", (6, 29, 6, 4), "Khối E.4", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("PTN CNVL & TTKT", (1, 28, 4, 5), "PTN CNVL", "dichvu",
                     MAU_KHOI_DICHVU, VIEN_KHOI_DICHVU, CHU_KHOI_DICHVU),
    ]

    occupied = {}
    overlaps = []
    for b in buildings:
        col, row, w, h = b.rect
        for r in range(row, row + h):
            for c in range(col, col + w):
                if (r, c) in occupied:
                    overlaps.append((b.name, occupied[(r, c)], r, c))
                occupied[(r, c)] = b.name
                cell_type = CELL_SPORTS if b.category == "sanbong" else CELL_BUILDING
                grid[r][c] = cell_type

    if overlaps:
        print("OVERLAPS DETECTED:")
        for o in overlaps:
            print(" ", o)
    else:
        print("PERFECT: No overlaps detected! All buildings cleanly placed.")

    # 3. Hồ nước trước Tòa A1
    for r in range(31, 34):
        for c in range(21, 28):
            grid[r][c] = CELL_WATER

    # 4. Công viên & Mảng xanh
    gardens = [
        (12, 22, 2, 10), # Dải công viên xanh giữa Khối E và Tòa A1
        (14, 18, 5, 2),  # Khoảng xanh trước Hội trường (dưới Khối D)
        (29, 30, 4, 3),  # Mảng cỏ trước Sân bóng
        (37, 21, 5, 1),  # Mảng cây xanh cạnh Maker Space
    ]
    for col, row, w, h in gardens:
        for r in range(row, row + h):
            for c in range(col, col + w):
                if grid[r][c] == CELL_EMPTY_ROAD:
                    grid[r][c] = CELL_GARDEN

    return grid, buildings
