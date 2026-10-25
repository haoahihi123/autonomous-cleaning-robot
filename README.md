# HỆ THỐNG TỰ ĐỘNG CHO XE DỌN RÁC DI CHUYỂN VÀ THU GOM RÁC
## MÔ HÌNH TUẦN TRA LIÊN TỤC TRONG KHUÔN VIÊN ĐH SƯ PHẠM KỸ THUẬT (HCMUTE)
### Môi trường có vật cản động & Tầm nhìn giới hạn

> **Đề tài Milestone 3:** Hệ thống tự động cho một xe dọn rác di chuyển và thu gom rác trong môi trường có vật cản động, tầm nhìn giới hạn (mô phỏng tại khuôn viên Trường Đại học Sư phạm Kỹ thuật TP.HCM / ĐH Công nghệ Kỹ thuật).

---

## 👥 THÀNH VIÊN THỰC HIỆN
1. **Nguyễn Ngọc Hải Yến** — MSSV: **25139062**
   - Nghiên cứu mô hình biểu diễn bản đồ dạng lưới / đồ thị.
   - Thuật toán tìm đường ngắn nhất **A\*** (A-Star) và cập nhật đường đi khi môi trường thay đổi.
   - Thiết kế chiến lược di chuyển quét bao phủ khu vực (**Boustrophedon Sweep Planner**).
2. **Trương Cảnh Hào** — MSSV: **25139011**
   - Xử lý vật cản động (sinh viên di chuyển tịnh tiến, đổi hướng khi gặp vật cản, dự đoán xung đột ngã rẽ).
   - Cơ chế phát hiện, thu gom rác thời gian thực và quản lý ô bị bỏ sót (**Missed Cells Backlog**).
   - Xây dựng giao diện đồ họa trực quan hóa độ phân giải cao (**Pygame High-DPI Sharp Renderer**).

---

## 📁 CẤU TRÚC MÃ NGUỒN MODULAR (TÁCH BIỆT TỪNG MODULE)

Hệ thống được bóc tách thành các module độc lập, chuyên biệt rõ ràng, dễ bảo trì và mở rộng:

```
d:\xe tự hành\
│
├── config.py             # Cấu hình hằng số, kích thước lưới, thông số vận tốc, bảng màu sắc & phông chữ
├── campus_map.py         # [PHẦN MAP] Bản đồ khuôn viên HCMUTE, các khối tòa nhà, hoa viên, hồ nước, cổng trường
├── hcmute_real_map.png   # [ẢNH HIỆN TRẠNG 1/500] Bản vẽ quy hoạch mặt bằng thực tế Trường ĐH Sư phạm Kỹ thuật TP.HCM
├── algorithms.py         # [PHẦN THUẬT TOÁN] Thuật toán A*, Heuristic Manhattan, Boustrophedon Sweep, chọn ô bỏ sót thông minh
├── entities.py           # [PHẦN THỰC THỂ] Xe dọn rác thông minh (CleaningRobot), Sinh viên (DynamicObstacle), Rác (TrashItem)
├── renderer.py           # [PHẦN ĐỒ HỌA] Vẽ nền thực tế 1/500 hoặc 3D vector, xe rác chổi xoay, sóng radar, HUD Dashboard
├── main.py               # [ENTRYPOINT] File thực thi chính kết hợp tất cả các module và điều phối vòng lặp game
└── README.md             # Tài liệu thuyết minh hướng dẫn sử dụng
```

---

## 🏫 CHI TIẾT CÁC MODULE CHÍNH

### 1. `campus_map.py` — Bản đồ khuôn viên HCMUTE
Xây dựng sơ đồ mặt bằng trường ĐH Sư phạm Kỹ thuật TP.HCM (Số 1 Võ Văn Ngân, Thủ Đức):
- **Tòa nhà Trung tâm Điều hành 12 tầng**: Khối kính xanh phản quang hiện đại (biểu tượng HCMUTE).
- **Khu Giảng đường A, B, C**: Các tòa nhà giảng đường lớn của các khoa.
- **Khu Xưởng Công nghệ E**: Khoa Cơ khí Chế tạo máy & Động lực (Ô tô).
- **Thư viện số (Digital Library)**, **Hội trường lớn** & **Căn tin dịch vụ sinh viên**.
- **Sân vận động cỏ nhân tạo HCMUTE** & **Nhà thi đấu thể thao đa năng**.
- **Đài phun nước cảnh quan & Bồn hoa hoa viên**.
- **Cổng 1 (Đường Võ Văn Ngân)** & **Cổng 2 (Đường Lê Văn Chí)** với trụ gạch và biển vòm chữ vàng.

### 2. `algorithms.py` — Các thuật toán cốt lõi
- **Thuật toán A\*** (`a_star_search`): Tìm đường đi ngắn nhất tối ưu với hàm Heuristic Manhattan $h(a, b) = |a.r - b.r| + |a.c - b.c|$. Có cơ chế fallback: ưu tiên né hoàn toàn vật cản động, nếu bị bao vây kín sẽ dùng bản đồ tĩnh để tìm đường thoát.
- **Chiến lược quét bao phủ Boustrophedon** (`generate_coverage_path`): Lập lộ trình luống cày zigzag phủ kín toàn bộ lối đi trong trường, kết hợp **A\* Connector** nối mượt mà qua các đoạn bị công trình che chắn.
- **Dự đoán xung đột ngã rẽ** (`check_collision_conflict`): Dự báo trước 1 bước vị trí của sinh viên ($\text{pos}_{next}$), phát hiện xung đột ô (Cell Conflict) và xung đột hoán đổi trực diện (Head-on Swap).
- **Thuật toán chọn ô bỏ sót thông minh** (`get_nearest_missed_cell`): Được tinh chỉnh và tích hợp từ sườn thuật toán đề xuất của nhóm sinh viên, lựa chọn mục tiêu bù sót dựa trên hàm chi phí phạt 3 bậc `(khoảng_cách, lệch_hàng * 2, ngược_hướng_di_chuyển * 3)` giúp xe hạn chế tối đa việc đảo chiều hay cua gấp khi quay lại dọn các điểm bị sinh viên che trước đó.

### 3. `entities.py` — Cơ chế tuần tra liên tục qua nhiều chu kỳ (Continuous Patrol)
- **Tự động bắt đầu chu kỳ mới**: Khi hoàn thành 1 lượt quét (100% diện tích và vét sạch ô bỏ sót), hệ thống không dừng lại mà tự động:
  1. Ghi nhận hoàn thành Chu kỳ (`Chu kỳ: #1`).
  2. Tăng số chu kỳ: `cycle_count += 1`.
  3. Reset vệt đường sạch (`visited_cells`) về 0% để người dùng theo dõi chu kỳ mới.
  4. Reset chỉ số quét chính và dùng A* dẫn đường xe quay lại điểm đầu tiếp tục chu kỳ mới liên tục.
- **Thu gom rác gián đoạn (Dynamic Trash Interrupt & Return)**: Tạm dừng lộ trình quét khi phát hiện rác trong bán kính $R = 3.8$ ô, dùng A* chạy đến nhặt rác rồi quay lại điểm đã ngắt tiếp tục tuần tra.
- **Xử lý ô bỏ sót (Missed Cells Backlog)**: Ghi nhận các ô bị chặn khi né sinh viên, sau đó kết hợp thuật toán chọn ô thông minh và A* để dọn sạch sẽ.
- **Chống kẹt (Deadlock Prevention)**: Chờ nhường đường tối đa 3 nhịp; nếu vật cản đứng lâu, tự động tính đường vòng (local rerouting).

### 4. `renderer.py` — Đồ họa siêu sắc nét & Tích hợp bản đồ hiện trạng 1/500
- **Chế độ hiển thị kép (Dual-Mode View)**: Hỗ trợ chuyển đổi mượt mà giữa:
  1. **Bản đồ hiện trạng 1/500 thực tế**: Hiển thị chính xác bản vẽ quy hoạch mặt bằng Trường ĐH Sư phạm Kỹ thuật TP.HCM với đầy đủ tên khối công trình, vệt sạch bán trong suốt giúp người xem dễ dàng quan sát xe rác chạy trên từng tuyến đường thực tế.
  2. **Bản đồ vector 3D sắc nét**: Vẽ chi tiết đổ bóng khối 3D, mặt kính xanh tòa Trung tâm, bồn hoa, đài phun nước, vệt xanh ngọc lấp lánh.
- **Hiệu ứng đồ họa sống động**: Xe dọn rác có chổi xoay liên tục, đèn cảnh báo nhấp nháy, nón quét radar phát hiện vật cản.
- **Bảng điều khiển HUD bên phải**: Hiển thị rõ số chu kỳ hiện tại, thanh tiến độ bao phủ %, số rác đã dọn, rác tồn, số ô bỏ sót cần bù và bảng log sự kiện thời gian thực.

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT & CHẠY ỨNG DỤNG

### 1. Cài đặt thư viện
```bash
pip install pygame
```

### 2. Khởi chạy chương trình
Chạy file chính `main.py`:
```bash
python main.py
```

### 🎮 Bảng phím điều khiển tương tác
| Phím / Thao tác | Chức năng |
| :--- | :--- |
| **`[M]`** | **Chuyển đổi chế độ Bản đồ: Bản đồ vector (mặc định) ⟷ Bản đồ hiện trạng 1/500 thực tế** |
| **`[Z]`** | **Chuyển đổi Thuật toán quét: Quét Phân vùng khuôn viên (Zonal) ⟷ Quét luống cày (Classic)** |
| **`[B]`** | **Kích hoạt Pin yếu: Xe lập tức rẽ nhánh tự động chạy về Trạm sạc Tòa D** |
| **`[C]`** | **Kích hoạt sự kiện Bãi rác Điểm nóng (Giờ ra chơi Căn tin & Sân bóng đá)** |
| **`[SPACE]`** | Tạm dừng (Pause) / Tiếp tục (Resume) mô phỏng |
| **`[F]`** | Bật / Tắt hiệu ứng Sương mù tầm nhìn giới hạn (**Fog of War**) |
| **`[R]`** | Thả thêm rác ngẫu nhiên theo điểm nóng |
| **`[O]`** | Thêm sinh viên (vật cản động) di chuyển có mục tiêu |
| **`[+]` / `[-]`** | Tăng / Giảm tốc độ di chuyển của xe rác |
| **`Click Chuột Trái`** | Thả rác trực tiếp tại ô đường bất kỳ được click |
| **`Click Chuột Phải`** | Thả sinh viên di chuyển trực tiếp tại ô được click |
