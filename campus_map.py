# -*- coding: utf-8 -*-
"""
MODULE BẢN ĐỒ HIỆN TRẠNG 1/500 TRƯỜNG ĐH CÔNG NGHỆ KỸ THUẬT TP.HCM (48x36 Ô LƯỚI)
Mô phỏng chính xác bố cục không gian và 4 nhóm màu khối công trình theo Bản đồ hiện trạng tỉ lệ 1/500:
- Tòa Trung tâm A1 - A5 liền khối thống nhất mặt tiền Võ Văn Ngân
- Hội trường Lớn bố trí tại trục trung tâm; Sân Việt Đức và Khối A10 đặt bên phải Hội trường
- Bãi cỏ lớn trang nghiêm trước mặt khối Tòa Trung tâm A1 - A5
- Phía Tây Hội trường lớn và hành lang Khối E hoàn toàn thông thoáng, không có góc kẹt hay đường cụt
- Khối E2 (nguyên là Khoa Thời trang) và Khối E0 (nguyên là PTN CNVL) được chuẩn hóa tên gọi
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
    """
    Khởi tạo ma trận lưới 48x36 khuôn viên Trường ĐH Công nghệ Kỹ thuật TP.HCM.
    Đảm bảo 100% đường giao thông thông thoáng, liên thông và không có bất kỳ ngõ cụt nào.
    """
    grid = [[CELL_EMPTY_ROAD for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

    # 1. Ranh giới ngoài & bảng chú thích
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if r == 0 or r == GRID_ROWS - 1 or c == 0 or c == GRID_COLS - 1:
                grid[r][c] = CELL_OUTSIDE
            # Vạt góc thông thoáng tại Cổng Lê Văn Chí
            elif r <= 2 and c >= 46:
                grid[r][c] = CELL_OUTSIDE
            # Khu vực bảng chú thích 1/500 góc Tây Bắc (col 0..12, row 0..13)
            elif r <= 13 and c <= 12:
                grid[r][c] = CELL_OUTSIDE

    # 2. Danh sách khối nhà CHUẨN XÁC THEO BẢN ĐỒ TỔNG THỂ VÀ THÔNG THOÁNG
    buildings = [
        # =====================================================================
        # TRỤC BẮC: KHỐI C, D, B, THƯ VIỆN, KHỐI A
        # =====================================================================
        BuildingInfo("KHỐI C (KHOA ĐIỆN - ĐT)", (14, 2, 4, 6), "Khối C", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("KHỐI B", (21, 2, 7, 5), "Khối B", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("THƯ VIỆN TRUNG TÂM", (21, 8, 7, 3), "Thư Viện", "trungtam",
                     MAU_KHOI_TRUNGTAM, VIEN_KHOI_TRUNGTAM, CHU_KHOI_TRUNGTAM),
        BuildingInfo("KHỐI D (KHOA ĐIỆN - ĐT)", (14, 9, 4, 5), "Khối D", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("KHỐI A", (21, 12, 7, 3), "Khối A", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),

        # =====================================================================
        # KHU VỰC TRUNG TÂM: HỘI TRƯỜNG LỚN & KHỐI A10 & SÂN VIỆT ĐỨC
        # Hội trường lớn nằm trên trục trung tâm thẳng hướng ra quảng trường
        # =====================================================================
        BuildingInfo("HỘI TRƯỜNG LỚN", (16, 17, 7, 5), "Hội Trường Lớn", "trungtam",
                     MAU_KHOI_TRUNGTAM, VIEN_KHOI_TRUNGTAM, CHU_KHOI_TRUNGTAM),
        BuildingInfo("KHỐI A10", (25, 15, 6, 2), "Khối A10", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("SÂN VIỆT ĐỨC", (25, 18, 6, 4), "Sân Việt Đức", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),

        # =====================================================================
        # TÒA TRUNG TÂM LIỀN KHỐI (A1 - A2 - A3 - A4 - A5 KHÔNG TÁCH RỜI)
        # =====================================================================
        BuildingInfo("CÁNH TRÁI A2-A3", (14, 25, 6, 5), "Khối A.2 - A.3", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("TÒA TRUNG TÂM A1", (20, 25, 7, 5), "Tòa Trung Tâm A.1", "trungtam",
                     MAU_KHOI_TRUNGTAM, VIEN_KHOI_TRUNGTAM, CHU_KHOI_TRUNGTAM),
        BuildingInfo("CÁNH PHẢI A4-A5", (27, 25, 6, 5), "Khối A.4 - A.5", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),

        # =====================================================================
        # PHÂN KHU ĐÔNG (CỤM XƯỞNG, MAKER SPACE, TOYOTA, SÂN BÓNG)
        # =====================================================================
        BuildingInfo("TRẠM Y TẾ", (34, 2, 4, 3), "Y tế", "dichvu",
                     MAU_KHOI_DICHVU, VIEN_KHOI_DICHVU, CHU_KHOI_DICHVU),
        BuildingInfo("XƯỞNG THỰC HÀNH Ô TÔ", (39, 2, 5, 3), "X.Động Lực", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("XƯỞNG NHIỆT - ĐIỆN LẠNH", (34, 6, 4, 4), "X.Nhiệt Lạnh", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("XƯỞNG CƠ KHÍ", (39, 6, 5, 4), "X.Cơ Khí", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("KHỐI F.1", (34, 11, 5, 4), "Khối F.1", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("TH KHOA XD", (40, 11, 6, 3), "TH Khoa XD", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("KHỐI G (TT VIỆT ĐỨC)", (34, 16, 5, 5), "Khối G", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("KHU MAKER SPACE", (40, 15, 4, 7), "Maker Space", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("DỊCH VỤ Ô TÔ TOYOTA", (44, 15, 3, 7), "Toyota", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("SÂN BÓNG ĐÁ NGOÀI TRỜI", (34, 24, 12, 9), "Sân Bóng Đá", "sanbong",
                     MAU_MAP_SAN_BONG, (210, 205, 180), (90, 100, 80)),

        # =====================================================================
        # PHÂN KHU TÂY & TÂY NAM (CỤM KHỐI E CƠ KHÍ MÁY & DỊCH VỤ)
        # =====================================================================
        BuildingInfo("XƯỞNG HÀN / IN", (1, 16, 4, 4), "Xưởng Hàn", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("KHỐI E.2", (6, 16, 6, 3), "Khối E.2", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("CĂN TIN - SIÊU THỊ E.2", (6, 20, 6, 3), "Căn Tin", "dichvu",
                     MAU_KHOI_DICHVU, VIEN_KHOI_DICHVU, CHU_KHOI_DICHVU),
        BuildingInfo("XƯỞNG THỰC HÀNH (VP KHOA)", (1, 20, 4, 7), "Xưởng In", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("KHỐI E.3 (XƯỞNG CƠ KHÍ MÁY)", (6, 24, 6, 4), "Xưởng E.3", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("KHỐI E.4 (BÁT GIÁC)", (6, 29, 6, 4), "Khối E.4", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("KHỐI E.0", (1, 27, 4, 6), "Khối E.0", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
    ]

    for b in buildings:
        col, row, w, h = b.rect
        for r in range(row, row + h):
            for c in range(col, col + w):
                cell_type = CELL_SPORTS if b.category == "sanbong" else CELL_BUILDING
                grid[r][c] = cell_type

    # 3. Mảng cỏ hoa viên THEO ĐÚNG BẢN ĐỒ TỔNG THỂ:
    # - Tuyệt đối không có cỏ ở phía Tây Hội trường lớn và dọc Khối A.2-A.3
    #   (Đại lộ rộng 3-4 ô nối liền thông suốt Bắc - Nam)
    # - Một bãi cỏ lớn thống nhất (cols 17..29, rows 31..33) trước mặt khối Tòa A1 - A5
    #   (Được bao bọc 4 phía bởi đường rộng rãi, tuyệt đối 0 đường cụt)
    gardens = [
        (17, 31, 13, 3), # 1 BÃI CỎ LỚN TRƯỚC TOÀN KHỐI A1 - A5
        (34, 21, 5, 2),  # Cây xanh cảnh quan trước Khối G
    ]
    for col, row, w, h in gardens:
        for r in range(row, row + h):
            for c in range(col, col + w):
                if grid[r][c] == CELL_EMPTY_ROAD:
                    grid[r][c] = CELL_GARDEN

    return grid, buildings


def create_true_campus():
    """Bí danh tương thích cho create_hcmute_campus()"""
    return create_hcmute_campus()
