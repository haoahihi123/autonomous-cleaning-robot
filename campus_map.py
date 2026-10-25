"""
MODULE BẢN ĐỒ HIỆN TRẠNG 1/500 TRƯỜNG ĐH CNKT TP.HCM (MỞ RỘNG 48x36 Ô LƯỚI)
Mô phỏng chính xác bố cục không gian và 4 nhóm màu khối công trình theo Bản đồ hiện trạng tỉ lệ 1/500:
- Kích thước các tòa nhà dày dặn (4 - 8 ô), đảm bảo tầm nhìn cảm biến của xe không thể quét xuyên tòa nhà.
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

    #1. Đánh dấu vùng ngoài ranh giới trường (CELL_OUTSIDE) tạo hình dáng thật của khuôn viên
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if r == 0 or r == GRID_ROWS - 1 or c == 0 or c == GRID_COLS - 1:
                grid[r][c] = CELL_OUTSIDE
            elif r <= 18 and c <= 14:
                grid[r][c] = CELL_OUTSIDE
            elif r <= 3 and c >= 38:
                grid[r][c] = CELL_OUTSIDE
            elif r <= 7 and c >= 44:
                grid[r][c] = CELL_OUTSIDE

    #2. Danh sách các khối công trình tỉ lệ lớn trên lưới 48x36
    buildings = [
        BuildingInfo(
            "TÒA D", (17, 2, 4, 6), "Khu D", "hoc",
            MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC
        ),
        BuildingInfo(
            "TÒA B", (23, 2, 7, 6), "Khu B", "hoc",
            MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC
        ),
        BuildingInfo(
            "Y TẾ", (32, 2, 4, 4), "Y tế", "Y tế",
            MAU_KHOI_DICHVU, VIEN_KHOI_DICHVU, CHU_KHOI_DICHVU
        ),
        BuildingInfo(
            "XƯỞNG THỰC HÀNH Ô TÔ", (37, 5, 6, 3), "X.Động Lực", "xuong",
            MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG
        ),
        BuildingInfo(
            "TÒA C", (17, 10, 4, 7), "Khu C", "hoc",
            MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC
        ),
        BuildingInfo(
            "THƯ VIỆN TÒA A", (23, 10, 7, 3), "Thư Viện", "trungtam",
            MAU_KHOI_TRUNGTAM, VIEN_KHOI_TRUNGTAM, CHU_KHOI_TRUNGTAM
        ),
        BuildingInfo(
            "TÒA A", (23, 14, 7, 4), "Khu A", "hoc",
            MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC
        ),
        BuildingInfo(
            "XƯỞNG THỰC HÀNH", (35, 9, 7, 4), "X.Cơ Khí", "xuong",
            MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG
        ),
        BuildingInfo(
            "TÒA E1", (34, 14, 7, 4), "Khu E.1", "hoc",
            MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC
        ),
        BuildingInfo(
            "XƯỞNG THỰC HÀNH", (2, 20, 4, 4), "Xưởng TH", "xuong",
            MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG
        ),
        BuildingInfo(
            "TÒA E4", (8, 20, 5, 3), "Khu E.4", "hoc",
            MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC
        ),
        BuildingInfo(
            "TÒA E2", (15, 20, 4, 4), "Căn Tin E2", "dichvu",
            MAU_KHOI_DICHVU, VIEN_KHOI_DICHVU, CHU_KHOI_DICHVU
        ),
        BuildingInfo(
            "KHU A", (28, 19, 4, 4), "", "hoc",
            MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC
        ),
        BuildingInfo(
            "HỘI TRƯỜNG", (21, 19, 6, 4), "Hội Trường", "trungtam",
            MAU_KHOI_TRUNGTAM, VIEN_KHOI_TRUNGTAM, CHU_KHOI_TRUNGTAM
        ),
        BuildingInfo(
            "TÒA F1", (34, 19, 7, 4), "Khu F.1", "hoc",
            MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC
        ),
        BuildingInfo(
            "KHỐI XƯỞNG CƠ KHÍ MÁY E.3", (42, 14, 4, 9), "Xưởng E.3", "xuong",
            MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG
        ),
        BuildingInfo(
            "TÒA E.5", (2, 26, 5, 7), "Khu E.5", "xuong",
            MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG
        ),
        BuildingInfo(
            "PHÒNG THÍ NGHIỆM KHU G", (9, 25, 4, 3), "PTN Điện", "xuong",
            MAU_KHOI_XUONG, VIEN_KHOI_XUONG, CHU_KHOI_XUONG
        ),
        BuildingInfo(
            "TÒA E4", (9, 29, 4, 4), "KHU E4", "hoc",
            MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC
        ),
        BuildingInfo(
            "TÒA A2-A3", (17, 25, 4, 4), "Khu A2-A3", "hoc",
            MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC
        ),
        BuildingInfo(
            "TÒA A-1", (21, 25, 6, 4), "Tòa TT A1", "trungtam",
            MAU_KHOI_TRUNGTAM, VIEN_KHOI_TRUNGTAM, CHU_KHOI_TRUNGTAM
        ),
        BuildingInfo(
            "CÁNH TÒA A4-A5", (27, 25, 4, 4), "Khu A4-A5", "hoc",
            MAU_KHOI_HOC, VIEN_KHOI_HOC, CHU_KHOI_HOC
        ),
        BuildingInfo(
            "SÂN BÓNG", (34, 25, 11, 8), "Sân Bóng Đá", "sanbong",
            MAU_MAP_SAN_BONG, (210, 205, 180), (90, 100, 80)
        ),
    ]

    for b in buildings:
        col, row, w, h = b.rect
        cell_type = CELL_SPORTS if b.category == "sanbong" else CELL_BUILDING
        for r in range(row, row + h):
            for c in range(col, col + w):
                if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
                    grid[r][c] = cell_type

    # 3. Bãi cỏ trước tòa trung tâm
    for r in range(30, 33):
        for c in range(23, 25):
            grid[r][c] = CELL_WATER

    # 4. Mảng cây xanh / Hoa viên cảnh quan theo đúng bản đồ 1/500
    gardens = [
        (17, 30, 5, 3),  # Đồi cỏ bán nguyệt bên trái trước Tòa Trung tâm
        (26, 30, 5, 3),  # Đồi cỏ bán nguyệt bên phải trước Tòa Trung tâm
        (17, 18, 3, 1),  # Hoa viên nhỏ trước Hội trường
        (31, 8, 2, 4),   # Mảng cây xanh dọc trục trung tâm Bắc
        (31, 14, 2, 4),  # Hàng cây ngăn Khu D và Khu E.1
        (7, 29, 1, 4),   # Vườn hoa khu Việt Đức
    ]
    for col, row, w, h in gardens:
        for r in range(row, row + h):
            for c in range(col, col + w):
                if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS and grid[r][c] == CELL_EMPTY_ROAD:
                    grid[r][c] = CELL_GARDEN

    return grid, buildings
