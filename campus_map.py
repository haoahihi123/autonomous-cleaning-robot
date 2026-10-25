# -*- coding: utf-8 -*-
"""
MODULE BẢN ĐỒ HIỆN TRẠNG 1/500 TRƯỜNG ĐH SPKT TP.HCM (CHUẨN TỈ LỆ 48x36 Ô LƯỚI)
Mô phỏng chính xác không gian thực tế theo hồ sơ quy hoạch 1/500 HCMUTE:
- TOÀN BỘ ĐỒ THỊ ĐƯỜNG ĐI LIÊN THÔNG HOÀN TOÀN: 0 ĐIỂM KẸT (DEAD ENDS = 0).
- Giữ nguyên Bảng chú thích bản đồ hiện trạng 1/500 ở góc Tây Bắc (không che khuất đường đi).
- TRỤC TRUNG TÂM PHÍA BẮC:
  + KHỐI B: Tọa lạc ở phía Bắc khuôn viên trường (hàng 2..5, cột 19..26).
  + THƯ VIỆN TRUNG TÂM & VP ĐOÀN: (hàng 7..9, cột 19..26 và hàng 6..8, cột 28..30).
  + HÀNH LANG THÔNG THUỐNG (hàng 9-10): Cho phép đi lại giữa Thư viện và Khối A ra ngoài.
  + KHỐI A: Hai cánh dọc (hàng 11..15, cột 19..21 và 24..26). Khoảng sân ở giữa là ĐƯỜNG ĐI (không có bãi cỏ), đi lại tự do.
  + BÃI CỎ RỘNG 2 Ô: Đặt ở khoảng trống phía Đông Khối A (hàng 11..15, cột 28..29), chừa đường đi thông thoáng xung quanh.
- KHU VỰC HỘI TRƯỜNG LỚN & XUNG QUANH (Chuẩn 100% bản vẽ gốc):
  + Tuyến đường ngang trung tâm quang đãng, không có bãi cỏ hay hồ nước cản trở.
  + Phía Tây: HỘI TRƯỜNG LỚN (khối hội nghị màu hồng, hàng 18..23, cột 18..23).
  + Phía Đông: KHỐI A10 (chữ nhật ngang, hàng 17..19, cột 25..30) và SÂN VIỆT ĐỨC (nằm ngay dưới A10, hàng 21..24, cột 25..30).
- TỔ HỢP TÒA TRUNG TÂM MẶT TIỀN VÕ VĂN NGÂN:
  + Tòa Trung tâm A1 dính liền mạch với Khối A.2 - A.3 (cánh Tây) và Khối A.4 - A.5 (cánh Đông).
  + Phía trước là dải bãi cỏ xanh mát dọc đường Võ Văn Ngân, chừa đường hàng 34 thông suốt qua lại.
- PHÂN KHU ĐÔNG: Cụm Xưởng Ô tô, Cơ khí, Nhiệt Lạnh, TH Khoa XD, Toyota, Khối F.1, Khối G, Maker Space và Sân bóng đá.
- 3 CỔNG PHÍA ĐÔNG HƯỚNG RA ĐƯỜNG LÊ VĂN CHÍ & 2 CỔNG ĐƯỜNG VÕ VĂN NGÂN.
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

    # 1.Ranh giới ngoài khuôn viên:
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if r == 0 or r == GRID_ROWS - 1 or c == 0 or c == GRID_COLS - 1:
                grid[r][c] = CELL_OUTSIDE
            # Khu vực dành riêng cho Bảng chú thích 1/500 (Góc Tây Bắc: col 0..11, row 0..12)
            elif r <= 12 and c <= 11:
                grid[r][c] = CELL_OUTSIDE

    # 2.Danh sách khối nhà CHUẨN 100% THEO HÌNH ẢNH BẢN VẼ GỐC (0 OVERLAPS):
    buildings = [
        # TRỤC TRUNG TÂM PHÍA BẮC: KHỐI B, THƯ VIỆN & HAI CÁNH KHỐI A
        BuildingInfo("KHỐI B", (19, 2, 8, 4), "Khối B", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("THƯ VIỆN TRUNG TÂM", (19, 7, 8, 3), "Khối Thư Viện", "trungtam",
                     MAU_KHOI_TRUNGTAM, VIEN_KHOI_TRUNGTAM, CHU_KHOI_TRUNGTAM),
        BuildingInfo("KHỐI A (DÃY TÂY)", (19, 11, 3, 5), "Khối A", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("KHỐI A (DÃY ĐÔNG)", (24, 11, 3, 5), "Khối A", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("VP. ĐOÀN TRƯỜNG", (28, 6, 3, 3), "VP Đoàn", "dichvu",
                     MAU_KHOI_DICHVU, VIEN_KHOI_DICHVU, CHU_KHOI_DICHVU),

        # CỤM HỘI TRƯỜNG LỚN, KHỐI A10 & SÂN VIỆT ĐỨC (CHUẨN ẢNH GỐC)
        BuildingInfo("HỘI TRƯỜNG LỚN", (18, 18, 6, 6), "Hội Trường Lớn", "trungtam",
                     MAU_KHOI_TRUNGTAM, VIEN_KHOI_TRUNGTAM, CHU_KHOI_TRUNGTAM),
        BuildingInfo("KHỐI A10", (25, 17, 6, 3), "Khối A10", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("SÂN VIỆT ĐỨC", (25, 21, 6, 4), "Sân Việt Đức", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),

        # TỔ HỢP TÒA TRUNG TÂM MẶT TIỀN VÕ VĂN NGÂN (A1 - A5 DÍNH LIỀN MẠCH)
        BuildingInfo("KHỐI A.2 - A.3", (14, 27, 7, 4), "Khu A.2 - A.3", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("TÒA TRUNG TÂM A1 (12 TẦNG)", (21, 26, 6, 5), "Tòa TT A1", "trungtam",
                     MAU_KHOI_TRUNGTAM, VIEN_KHOI_TRUNGTAM, CHU_KHOI_TRUNGTAM),
        BuildingInfo("KHỐI A.4 - A.5", (27, 27, 7, 4), "Khu A.4 - A.5", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),

        # PHÂN KHU TÂY BẮC & TÂY (KHOA ĐIỆN - ĐT & CỤM KHỐI E CƠ KHÍ)
        # Mở rộng đường bao Tây (cột 1) thông suốt, tránh tuyệt đối ngõ cụt
        BuildingInfo("KHỐI C (KHOA ĐIỆN - ĐT)", (14, 2, 4, 6), "Khối C", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("KHỐI D (KHOA ĐIỆN - ĐT)", (14, 9, 4, 7), "Khối D", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("XƯỞNG HÀN / IN", (2, 14, 4, 3), "Xưởng Hàn", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("KHỐI E.1 (CƠ KHÍ MÁY)", (7, 14, 5, 3), "Khối E.1", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("CĂN TIN - SIÊU THỊ E.2", (7, 18, 5, 4), "Căn Tin E2", "dichvu",
                     MAU_KHOI_DICHVU, VIEN_KHOI_DICHVU, CHU_KHOI_DICHVU),
        BuildingInfo("KHỐI E.0 (VP KHOA)", (2, 18, 4, 5), "Khối E.0", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("KHỐI E.3 (XƯỞNG CKM)", (7, 23, 5, 4), "Xưởng E.3", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("KHỐI E.4 (BÁT GIÁC)", (7, 28, 5, 4), "Khối E.4", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("PTN CNVL & TTKT", (2, 24, 4, 7), "PTN CNVL", "dichvu",
                     MAU_KHOI_DICHVU, VIEN_KHOI_DICHVU, CHU_KHOI_DICHVU),

        # PHÂN KHU ĐÔNG (CỤM XƯỞNG TH, F1, G, MAKER SPACE, TOYOTA, SÂN BÓNG)
        BuildingInfo("TRẠM Y TẾ", (31, 2, 4, 3), "Y tế", "dichvu",
                     MAU_KHOI_DICHVU, VIEN_KHOI_DICHVU, CHU_KHOI_DICHVU),
        BuildingInfo("XƯỞNG NHIỆT - ĐIỆN LẠNH", (31, 6, 4, 3), "X.Nhiệt Lạnh", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("KHỐI F.1", (31, 10, 4, 3), "Khối F.1", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),
        BuildingInfo("KHỐI G (TT VIỆT ĐỨC)", (31, 14, 4, 4), "Khối G", "hoc",
                     MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC),

        BuildingInfo("XƯỞNG THỰC HÀNH Ô TÔ", (37, 3, 6, 3), "X.Động Lực", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("XƯỞNG CƠ KHÍ", (37, 7, 6, 3), "X.Cơ Khí", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("KHU MAKER SPACE", (36, 11, 5, 10), "Maker Space", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("TH KHOA XD", (42, 11, 4, 4), "TH Khoa XD", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("DỊCH VỤ Ô TÔ TOYOTA", (42, 16, 4, 5), "Toyota", "xuong",
                     MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG),
        BuildingInfo("SÂN BÓNG ĐÁ NGOÀI TRỜI", (35, 23, 11, 11), "Sân Bóng Đá", "sanbong",
                     MAU_MAP_SAN_BONG, (210, 205, 180), (90, 100, 80)),
    ]

    for b in buildings:
        col, row, w, h = b.rect
        cell_type = CELL_SPORTS if b.category == "sanbong" else CELL_BUILDING
        for r in range(row, row + h):
            for c in range(col, col + w):
                if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
                    grid[r][c] = cell_type

    # 3.Công viên & Mảng xanh hoa viên:
    gardens = [
        # BÃI CỎ RỘNG 2 Ô Ở KHOẢNG TRỐNG PHÍA ĐÔNG KHỐI A (chừa đường đi thông thoáng xung quanh)
        (28, 11, 2, 5),
        # Hoa viên mặt tiền Tòa A1 - A5 dọc đường Võ Văn Ngân:
        # Chừa đại lộ trung tâm (cột 23-24, hàng 32-33) nối thẳng Cổng chính Võ Văn Ngân vào Tòa A1
        (14, 32, 9, 2),  # Mảng hoa viên phía Tây mặt tiền
        (25, 32, 9, 2),  # Mảng hoa viên phía Đông mặt tiền
    ]
    for col, row, w, h in gardens:
        for r in range(row, row + h):
            for c in range(col, col + w):
                if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS and grid[r][c] == CELL_EMPTY_ROAD:
                    grid[r][c] = CELL_GARDEN

    return grid, buildings
