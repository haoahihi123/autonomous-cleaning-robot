"""
Cấu hình hệ thống, thông số mô phỏng và bảng màu giao diện
Đồ án xe dọn rác tự hành - ĐH Công nghệ Kỹ thuật TP.HCM
"""

import sys
import pygame

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Kích thước lưới bản đồ và cửa sổ hiển thị
GRID_COLS = 48          # Số cột lưới bản đồ
GRID_ROWS = 36          # Số hàng lưới bản đồ
CELL_SIZE = 15          # Kích thước mỗi ô (pixel)

MAP_WIDTH = GRID_COLS * CELL_SIZE   # Chiều rộng phần bản đồ
MAP_HEIGHT = GRID_ROWS * CELL_SIZE  # Chiều cao phần bản đồ
SIDEBAR_WIDTH = 300                 # Chiều rộng thanh điều khiển bên phải
TOPBAR_HEIGHT = 44                  # Chiều cao thanh tiêu đề

WINDOW_WIDTH = MAP_WIDTH + SIDEBAR_WIDTH
WINDOW_HEIGHT = TOPBAR_HEIGHT + MAP_HEIGHT

# Cấu hình xe và cảm biến
SENSOR_RADIUS = 3.0        # Bán kính cảm biến quét của xe (ô)
ROBOT_SPEED_DELAY = 85     # Tốc độ xe (ms/bước)
MAX_WAIT_STEPS = 3         # Số bước chờ tối đa khi gặp vật cản trước khi tìm đường khác
TRASH_SPAWN_INTERVAL = 3.0 # Chu kỳ tự sinh thêm rác (giây)

# Cấu hình trạm sạc và pin
TOA_DO_TRAM_SAC = (8, 18)        # Tọa độ trạm sạc trước Tòa D
PIN_TOI_DA = 100.0               # Mức pin tối đa (%)
PIN_TIEU_HAO_MOI_BUOC = 0.25     # Pin tiêu hao mỗi bước (%)
NGUONG_PIN_YEU = 20.0            # Ngưỡng pin yếu cần về sạc (%)
SO_BUOC_SAC_PIN = 45             # Số nhịp sạc đầy tại trạm

CHARGING_STATION_POS = TOA_DO_TRAM_SAC
BATTERY_MAX = PIN_TOI_DA
BATTERY_DRAIN_PER_STEP = PIN_TIEU_HAO_MOI_BUOC
BATTERY_LOW_THRESHOLD = NGUONG_PIN_YEU
CHARGE_DURATION_STEPS = SO_BUOC_SAC_PIN

# Phân loại ô trên bản đồ
CELL_EMPTY_ROAD = 0   # Đường đi
CELL_BUILDING   = 1   # Tòa nhà (vật cản, chắn tầm nhìn)
CELL_GARDEN     = 2   # Cây xanh / bồn hoa
CELL_WATER      = 3   # Hồ nước
CELL_SPORTS     = 4   # Sân bóng
CELL_OUTSIDE    = 5   # Ngoài ranh giới trường

# Bảng màu giao diện
MAU_NEN_APP        = (242, 244, 247)
MAU_THE_TRANG      = (255, 255, 255)
MAU_THE_PHU        = (246, 248, 250)
MAU_VIEN_THE       = (225, 228, 233)
MAU_VIEN_PHU       = (214, 218, 224)

# Màu chữ
MAU_CHU_CHINH      = (33, 37, 41)
MAU_CHU_PHU        = (108, 117, 125)
MAU_CHU_MO         = (148, 155, 164)

# Màu điểm nhấn và trạng thái
MAU_XANH_GOOGLE    = (26, 115, 232)
MAU_XANH_NHAT      = (232, 240, 254)
MAU_XANH_DAM       = (21, 87, 176)

MAU_XANH_LA        = (40, 167, 69)
MAU_XANH_LA_NHAT   = (232, 245, 233)

MAU_CAM            = (224, 112, 10)
MAU_CAM_NHAT       = (255, 243, 205)

MAU_DO             = (220, 53, 69)
MAU_DO_NHAT        = (248, 215, 218)

# Màu nền bản đồ và địa hình
MAU_MAP_NGOAI      = (244, 246, 248)
MAU_MAP_DAT        = (238, 241, 238)
MAU_MAP_DUONG      = (252, 252, 253)
MAU_MAP_VIEN_DUONG = (230, 233, 236)
MAU_MAP_CO         = (202, 226, 208)
MAU_MAP_NUOC       = (202, 226, 242)
MAU_MAP_SAN_BONG   = (245, 242, 230)

# Nhóm màu các khu công trình theo sơ đồ trường
# 1.Khối phòng học
MAU_KHOI_HOC       = (245, 210, 185)
VIEN_KHOI_HOC      = (218, 172, 138)
CHU_KHOI_HOC       = (85, 48, 22)

# 2.Khối văn phòng, hội trường, thư viện
MAU_KHOI_TRUNGTAM  = (242, 206, 214)
VIEN_KHOI_TRUNGTAM = (214, 168, 178)
CHU_KHOI_TRUNGTAM  = (92, 38, 50)

# 3.Khối xưởng thực hành
MAU_KHOI_XUONG     = (198, 224, 238)
VIEN_KHOI_XUONG    = (154, 188, 208)
CHU_KHOI_XUONG     = (28, 62, 85)

# 4.Khối dịch vụ, căn tin
MAU_KHOI_DICHVU    = (226, 212, 238)
VIEN_KHOI_DICHVU   = (188, 168, 204)
CHU_KHOI_DICHVU    = (70, 42, 92)

MAU_TRANG     = MAU_THE_TRANG
MAU_NEN       = MAU_NEN_APP
MAU_VIEN      = MAU_VIEN_THE
MAU_CHU       = MAU_CHU_CHINH
MAU_XANH      = MAU_XANH_GOOGLE
MAU_DAT       = MAU_MAP_DAT
MAU_DUONG     = MAU_MAP_DUONG
MAU_CO        = MAU_MAP_CO
MAU_NUOC      = MAU_MAP_NUOC
MAU_NHA       = MAU_KHOI_HOC
MAU_NHA_VIEN  = VIEN_KHOI_HOC

# Quản lý font chữ hiển thị
class FontManager:
    _instance = None

    def __init__(self):
        if not pygame.font.get_init():
            pygame.font.init()
        self.title = pygame.font.SysFont("segoeui", 13, bold=True)
        self.heading = pygame.font.SysFont("segoeui", 11, bold=True)
        self.normal = pygame.font.SysFont("segoeui", 10)
        self.small = pygame.font.SysFont("segoeui", 9)
        self.tiny = pygame.font.SysFont("segoeui", 9)
        self.big = pygame.font.SysFont("segoeui", 18, bold=True)
        self.stat = pygame.font.SysFont("segoeui", 15, bold=True)
        self.map_label = pygame.font.SysFont("segoeui", 10, bold=True)
        self.map_sub = pygame.font.SysFont("segoeui", 9)

    @classmethod
    def get_fonts(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
