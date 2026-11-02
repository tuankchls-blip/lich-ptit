# Đặc tả chương trình Lịch PTIT – theo dõi lịch học, lịch thi và việc cần làm

Oct 30, 2026 · @Tuân

Chương trình **Lịch PTIT** gom lịch học, lịch thi và việc cần làm của hệ từ xa vào một kho dữ liệu duy nhất, rồi đẩy ra điện thoại theo ba đường: lịch iPhone có báo thức đúng giờ, thông báo tóm tắt sáng và tối bằng Phím tắt iPhone, và một trang web xem nhanh.

## 1. Mục tiêu và phạm vi

**Bài toán.** Thông tin học tập nằm rải rác: lịch học và điểm ở hệ thống Quản lý đào tạo, bài tập và hạn nộp ở LMS (Moodle), lịch thi qua thông báo của trung tâm, còn việc cá nhân thì ghi tay. Dễ quên hạn nộp hoặc ngày thi.

**Mục tiêu đo được:**

- Không bỏ lỡ hạn nộp hay buổi thi nào: mỗi mục có ít nhất 2 lần nhắc trước hạn.
- Mở điện thoại là thấy ngay "hôm nay và 7 ngày tới" trong dưới 5 giây.
- Thêm một việc mới mất dưới 30 giây (sửa 1 file YAML).
- Chạy miễn phí, không cần máy chủ riêng.

**Trong phạm vi:** lịch học (buổi học trực tuyến, buổi tập trung), lịch thi kết thúc học phần, hạn nộp bài tập/kiểm tra trên LMS, việc cá nhân liên quan đến học (đăng ký tín chỉ, đóng học phí, nộp hồ sơ), nhắc nhở trên điện thoại.

**Ngoài phạm vi (bản đầu):** tính điểm, xếp lịch đăng ký tín chỉ, ứng dụng iOS gốc (native app), tự động đăng nhập lấy dữ liệu khi chưa kiểm tra được cổng trường cho phép.

**Người dùng:** một người (bạn). Thiết bị chính: iPhone; máy tính để sửa dữ liệu và code bằng Claude Code.

## 2. Nguồn dữ liệu

Lịch học hằng tuần lấy từ trang Thời khóa biểu tuần của hệ thống Quản lý đào tạo; bài tự học và hạn nộp lấy từ LMS; lịch thi chưa công bố nên nhập tay khi có thông báo.

| Nguồn | Địa chỉ | Có gì | Cách lấy | Giai đoạn |
| --- | --- | --- | --- | --- |
| Quản lý đào tạo – TKB tuần | [qldttx.pttc1.edu.vn/#/tkb-tuan](https://qldttx.pttc1.edu.vn/#/tkb-tuan) | Lịch học hằng tuần | Giai đoạn 1: bấm In, chép vào `classes.yaml`. Giai đoạn 3: tự đăng nhập bằng tài khoản của bạn, lấy JSON TKB mỗi 6 giờ | 1 → 3 |
| LMS (Moodle) | [lms.pttc1.edu.vn](https://lms.pttc1.edu.vn/login/index.php) | Bài tự học, hạn nộp, bài kiểm tra | Link iCal nếu LMS bật "Xuất lịch"; nếu không, nhập tay | 2 |
| Nhập tay (YAML) | thư mục `data/` trong repo | Lịch thi, việc cá nhân, phần bổ sung | Sửa file, commit | 1 |
| Thông báo trung tâm | [dec.ptit.edu.vn](https://dec.ptit.edu.vn/), email, nhóm lớp | Lịch thi, địa điểm thi, đợt đăng ký, hạn học phí | Chép vào `exams.yaml` / `tasks.yaml` khi có | 1 |

### Đã xác định từ trang TKB tuần (30/10/2026)

Trang tải mỗi loại dữ liệu bằng một request riêng, tên dạng `w-locds…` (chân trang ghi "Design by aqtech.vn"). Request chính là `w-locdstkbtuanusertheohocky` (3,1 kB); theo tên, nó trả TKB của bạn theo cả học kỳ, nên có thể một lần gọi là đủ mọi tuần.

| Request (tên trong Network) | Chức năng (đoán theo tên) | Dùng cho |
| --- | --- | --- |
| `w-locdstkbtuanusertheohocky` | TKB của người dùng theo học kỳ | Sinh `classes.yaml` |
| `w-locdshockytkbuser` | Danh sách học kỳ có TKB | Chọn học kỳ hiện tại |
| `w-locdsdoituongthoikhoabieu` | Loại TKB (cá nhân, …) | Tham số khi gọi TKB |
| `w-checkvalidallchucnang` | Kiểm tra quyền / phiên | Phát hiện hết phiên |
| Chưa bắt được: request đăng nhập | Nhận token | Bước đầu của `importers/qldt.py` |
| Chưa bắt được: request của mục "Xem lịch thi" | Lịch thi | Sinh `exams.yaml` tự động |

**Lịch học kỳ 1 năm học 2026–2027, tuần 11 (26/10–01/11/2026):**

| Ngày | Môn | Mã | Nhóm | Giờ | Giảng viên |
| --- | --- | --- | --- | --- | --- |
| Thứ Năm | Kỹ thuật số | ELE1433 | 03 | 19:00–21:50 (tiết 13–15) | Vũ Anh Đào |
| Thứ Sáu | Ngôn ngữ lập trình C++ | INT1339 | 08 | 19:00–21:50 (tiết 13–15) | Nguyễn Đình Hiến |
| Chủ nhật | Toán rời rạc 1 | INT1358 | 09 | 19:00–21:50 (tiết 13–15) | Nguyễn Kiều Linh |

Cả ba buổi học online buổi tối, mỗi buổi có ID, mật khẩu phòng và "Link học online". Trang còn đánh dấu **Dạy bù** và **Trùng lịch**; chương trình đọc hai cờ này và báo riêng. Giờ lấy thẳng từ dữ liệu (19:00 → 21:50), không tự tính từ số tiết.

**Ghi chú về từng nguồn:**

- **Việc cần làm tiếp trong DevTools** (che mật khẩu, token và mật khẩu phòng học trước khi gửi):
  1. Bấm `w-locdstkbtuanusertheohocky` → tab Headers: chép Request URL, Request Method, và xem có header `Authorization` không (chỉ ghi "có, dạng Bearer …"). Tab Payload: chép nội dung gửi đi. Tab Response: chép JSON của một buổi học.
  2. Tích "Keep log", đăng xuất rồi đăng nhập lại; tìm request mới xuất hiện lúc bấm Đăng nhập. Chép URL, Method, tên các trường gửi đi, và trường nào trong phản hồi chứa token.
  3. Mở mục "Xem lịch thi", chép request mới xuất hiện theo cách như bước 1.
- **Nút In** là phương án dự phòng và cách làm của giai đoạn 1: in ra hoặc lưu PDF rồi chép vào YAML.
- **LMS dùng để tự học**, chạy Moodle. Có hai cách lấy hạn nộp: link iCal (Lịch → Nhập hoặc xuất lịch → Xuất lịch → "Get calendar URL"), hoặc đăng nhập qua API của Moodle (mục bên dưới).
- **Lịch thi:** trang Quản lý đào tạo có mục "Xem lịch thi", nên chương trình lấy tự động theo cùng cách đăng nhập khi trường công bố. Theo trang tuyển sinh hệ từ xa, thi kết thúc học phần tập trung 2 ngày (thứ Bảy, Chủ nhật) mỗi kỳ. Khi mục này còn trống, bản tóm tắt Chủ nhật liệt kê môn chưa có lịch thi; khi có lịch mới, ntfy (nếu bật) báo ngay và tin sáng/tối tự động có lịch thi.

### Đăng nhập tự động vào tài khoản

Chương trình dùng tài khoản của bạn để đăng nhập Quản lý đào tạo và LMS mỗi 6 giờ, lấy TKB tuần và hạn nộp, rồi trả kết quả về Lịch iPhone, Phím tắt và trang web. Chỉ phục vụ một tài khoản: của chính bạn.

| Hệ thống | Cách đăng nhập | Lấy gì | Dự phòng |
| --- | --- | --- | --- |
| Quản lý đào tạo | Gửi lại đúng 2 request mà trang tự gửi: đăng nhập (nhận token/cookie) → lấy TKB tuần, bằng `httpx` | JSON các buổi học trong tuần; lặp cho 4 tuần tới | Playwright: trình duyệt không giao diện điền form đăng nhập, mở `#/tkb-tuan`, bắt JSON phản hồi |
| LMS (Moodle) | `login/token.php` với `service=moodle_mobile_app` → nhận token → gọi `core_calendar_get_action_events_by_timesort` | Hạn nộp, bài kiểm tra sắp tới | Link iCal; hoặc Playwright nếu trường tắt dịch vụ di động |

**Nơi chạy và nơi giữ mật khẩu:**

| Cách | Mật khẩu nằm ở | Ưu điểm | Nhược điểm |
| --- | --- | --- | --- |
| GitHub Actions (đề xuất thử trước) | GitHub Secrets của repo riêng tư: mã hóa, tự che trong log | Chạy cả khi máy tắt; cùng chỗ với phần build | Máy chạy ở nước ngoài: trang trường có thể chặn IP lạ hoặc bắt captcha |
| Máy tính của bạn (Task Scheduler hoặc self-hosted runner) | Windows Credential Manager, đọc qua thư viện `keyring` | Mật khẩu không rời máy; IP Việt Nam | Máy phải bật lúc chạy |

Nếu GitHub Actions bị chặn, chuyển bước lấy dữ liệu sang máy bạn; phần build và báo ntfy vẫn ở GitHub.

**Quy tắc khi đăng nhập:**

1. Tối đa 4 lần mỗi ngày; mỗi lần đăng nhập một lần, dùng lại token trong lượt chạy đó.
2. Sai đăng nhập 2 lần liên tiếp thì dừng và báo qua ntfy, tránh bị khóa tài khoản.
3. Gặp captcha hoặc mã OTP thì không tìm cách vượt; báo qua ntfy để bạn tự cập nhật lần đó.
4. Không ghi mật khẩu, token, cookie ra log, file hay commit; chỉ giữ các trường lịch cần dùng, bỏ phần thông tin cá nhân khác trong JSON.
5. So với dữ liệu lần trước; chỉ khi khác mới commit và báo qua ntfy "Lịch học thay đổi" kèm buổi bị đổi.
6. Đổi mật khẩu trường thì cập nhật Secret; lần đăng nhập lỗi đầu tiên sẽ nhắc bạn qua ntfy.

Tần suất này tương đương bạn tự mở trang vài lần mỗi ngày; vẫn nên xem quy định sử dụng hệ thống của trường.

## 3. Chức năng chi tiết

Bảy chức năng, đánh số theo mã để nhắc tới khi giao việc cho Claude Code. Mức ưu tiên P1 là bắt buộc cho bản đầu tiên chạy được.

| Mã | Chức năng | Mô tả | Ưu tiên |
| --- | --- | --- | --- |
| F1 | Quản lý lịch học | Buổi học lặp theo tuần (thứ, giờ, từ ngày đến ngày), có link lớp học ảo; hỗ trợ ngày nghỉ bù, dời buổi | P1 |
| F2 | Quản lý lịch thi | Môn, ngày, ca/giờ, địa điểm (trạm đào tạo), số báo danh, hình thức thi, giấy tờ cần mang | P1 |
| F3 | Việc cần làm | Việc có hạn chót, mức ưu tiên, trạng thái (chưa làm / đang làm / xong), gắn môn học nếu có | P1 |
| F4 | Nhập hạn nộp từ LMS | Đọc link iCal Moodle, chuyển thành việc cần làm, không tạo trùng khi chạy lại (dựa vào UID) | P1 |
| F5 | Nhắc nhở | Lịch iPhone báo đúng giờ; Phím tắt iOS hiện bản tóm tắt sáng và tối; ntfy (tùy chọn) báo khi lịch đổi hoặc chương trình lỗi | P1 |
| F6 | Xem trên điện thoại | Trang web: Hôm nay, Tuần này, Sắp thi, Việc còn tồn; thêm ra màn hình chính như một app | P2 |
| F7 | Thêm việc từ điện thoại | Biểu mẫu hoặc Phím tắt iOS gửi việc mới vào repo (tùy chọn, làm sau) | P3 |

**Quy tắc nghiệp vụ cần giữ đúng:**

1. Mọi thời gian lưu và hiển thị theo múi `Asia/Ho_Chi_Minh` (UTC+7).
2. Việc đã đánh dấu xong thì không nhắc nữa và biến khỏi lịch nhắc.
3. Nếu một hạn nộp từ LMS đã được bạn sửa tay (ví dụ ghi chú, trạng thái), lần nhập sau chỉ cập nhật ngày giờ, không ghi đè phần bạn sửa.
4. Phát hiện trùng giờ: buổi học hoặc buổi thi chồng nhau thì báo trong bản tóm tắt.
5. Dữ liệu sai định dạng (thiếu ngày, giờ sai) thì chương trình dừng và báo dòng lỗi, không đẩy lịch hỏng lên điện thoại.

## 4. Kiến trúc đề xuất

Chọn phương án D: dữ liệu là file YAML trong GitHub, GitHub Actions dựng ra lịch ICS, trang web và hai file tin tóm tắt cho Phím tắt iOS. Miễn phí, không cần máy chủ, và việc nhắc đúng giờ do chính iPhone làm nên không phụ thuộc mạng hay độ trễ của máy chủ.

| Phương án | Ưu điểm | Nhược điểm | Kết luận |
| --- | --- | --- | --- |
| A. Nhập tay vào Lịch iPhone | Không cần code | Không tự lấy hạn nộp LMS, không có tóm tắt, khó sửa hàng loạt | Không đủ |
| B. App di động riêng (Flutter, Swift) | Thông báo đẩy, giao diện tùy ý | Cài lâu dài lên iPhone cần tài khoản Apple Developer trả phí; nhiều việc nhất | Để sau |
| C. Web app + máy chủ + cơ sở dữ liệu | Linh hoạt, thêm việc ngay trên web | Cần máy chủ chạy liên tục; thông báo đẩy từ web trên iPhone kém ổn định | Quá nặng cho 1 người |
| **D. File tĩnh: YAML → GitHub Actions → ICS + Phím tắt + web** | Miễn phí; iPhone tự nhắc đúng giờ; dữ liệu là file đọc được, có lịch sử | Thêm việc phải sửa file hoặc dùng biểu mẫu (giai đoạn 4) | **Chọn** |

&#91;embedded content: kiến trúc Lịch PTIT · 3 nguồn, 3 bước, 3 đầu ra\]

Đường nét đứt là nguồn chưa tự động ở giai đoạn đầu (giai đoạn 1 chép tay từ bản In); chỉ Lịch iPhone đảm nhận báo thức đúng giờ, hai đầu ra còn lại chịu được độ trễ của lịch chạy GitHub Actions.

## 5. Mô hình dữ liệu

Dữ liệu nằm trong 4 file YAML dễ đọc, sửa được bằng tay; không cần cơ sở dữ liệu. Mỗi mục có `id` cố định để lịch iPhone nhận ra là cùng một sự kiện khi cập nhật.

| File | Chứa | Trường chính |
| --- | --- | --- |
| `data/courses.yaml` | Danh sách môn học kỳ này | `code`, `name`, `credits`, `teacher`, `lms_url`, `color` |
| `data/classes.yaml` | Buổi học lặp lại | `id`, `course`, `weekday`, `start`, `end`, `from`, `to`, `link`, `skip_dates`, `extra_dates` |
| `data/exams.yaml` | Lịch thi | `id`, `course`, `date`, `start`, `duration_min`, `place`, `seat_no`, `form`, `bring` |
| `data/tasks.yaml` | Việc cần làm (tay + từ LMS) | `id`, `title`, `course`, `due`, `priority`, `status`, `source`, `note`, `remind` |

**Ví dụ (giá trị minh họa, không phải lịch thật):**

```yaml
# data/courses.yaml  (học kỳ 1, 2026–2027)
- code: ELE1433
  name: Kỹ thuật số
  group: "03"
  teacher: Vũ Anh Đào
- code: INT1339
  name: Ngôn ngữ lập trình C++
  group: "08"
  teacher: Nguyễn Đình Hiến
- code: INT1358
  name: Toán rời rạc 1
  group: "09"
  teacher: Nguyễn Kiều Linh

# data/classes.yaml  (importer sinh từ dữ liệu trang; mỗi buổi một dòng)
- id: ELE1433-2026-10-29
  course: ELE1433
  date: 2026-10-29
  start: "19:00"
  end: "21:50"
  periods: [13, 15]
  online: true
  link: <Link học online>
  room_secret: true     # ID/mật khẩu phòng chỉ đưa vào ICS
  flags: []             # day_bu | trung_lich

# data/exams.yaml  (chờ trường công bố)
- id: exam-INT1358
  course: INT1358
  date: null
  start: null
  place: null
  bring: [CCCD, thẻ sinh viên]

# data/tasks.yaml
- id: task-dang-ky-tin-chi
  title: Đăng ký tín chỉ kỳ sau
  due: 2026-12-05T23:59   # ví dụ
  priority: high          # high | normal | low
  status: todo            # todo | doing | done
  source: manual          # manual | lms | qldt
  remind: [3d, 1d, 2h]
```

**Mặc định khi không ghi `remind`:** buổi học nhắc trước 30 phút; việc cần làm nhắc trước 1 ngày và 3 giờ; buổi thi nhắc trước 14 ngày, 3 ngày và tối hôm trước (20:00).

Bản kiểm tra cấu trúc (schema) viết bằng Pydantic, chạy mỗi lần build để bắt lỗi nhập liệu trước khi đẩy lên điện thoại.

## 6. Thông báo trên điện thoại

Nhắc đúng giờ từng buổi học, hạn nộp và buổi thi do chính iPhone làm qua Lịch đăng ký (ICS có báo thức). Tin tóm tắt sáng và tối hiện bằng Phím tắt iOS tải một file chữ từ trang của bạn. ntfy là phần tùy chọn, chỉ để báo khi lịch đổi hoặc chương trình lỗi. Không cần tài khoản bên thứ ba nào cho phần bắt buộc.

| Kênh | Dùng cho | Độ chính xác giờ | Ghi chú |
| --- | --- | --- | --- |
| Lịch iPhone (đăng ký `calendar.ics`) | Nhắc từng buổi học, hạn nộp, buổi thi | Đúng phút, chạy cả khi không có mạng | Phải tắt "Xóa cảnh báo" (Remove Alerts) của lịch đăng ký; iPhone làm mới theo chu kỳ cài đặt |
| Phím tắt iOS | Tin sáng 06:47, tin tối 22:13 | iPhone tự chạy đúng giờ; cần có mạng | Tự tạo một lần (\~5 phút), hướng dẫn trong `docs/shortcuts.md` |
| ntfy (tùy chọn) | Báo khi lịch học/thi/hạn nộp trong 14 ngày tới đổi, khi dữ liệu sai hoặc build lỗi | Trễ vài phút | Cài app ntfy; tên kênh là chuỗi ngẫu nhiên dài, ai biết tên là đọc được tin |
| Trang web (PWA) | Xem tổng quan khi cần | Không nhắc | Thêm ra màn hình chính từ Safari |

**Cài đặt trên iPhone (một lần):**

1. Lịch: Cài đặt → Lịch → Tài khoản → Thêm tài khoản → Khác → Thêm lịch đã đăng ký → dán link `.ics`. Tắt **Xóa cảnh báo**, chọn lấy dữ liệu mới mỗi 15 phút hoặc hàng giờ.
2. Phím tắt "Tin sáng": tác vụ *Lấy nội dung của URL* (`.../morning.txt`) → *Hiển thị thông báo*. Tự động hóa: Giờ trong ngày 06:47, hằng ngày, **Chạy ngay**.
3. Phím tắt "Tin tối": làm tương tự với `.../evening.txt`, lúc 22:13.
4. (Tùy chọn) ntfy: cài app, đăng ký tên kênh, thêm Secret `NTFY_TOPIC` vào repo.

**Cách các file tin được làm mới:** mỗi lần build, chương trình ghi `morning.txt` và `evening.txt` cạnh `calendar.ics`; mỗi file được tính cho lần hiện kế tiếp (06:47 hoặc 22:13) nên đúng ngày dù workflow chạy lúc nào. Workflow chạy 4 lần mỗi ngày (05:17, 11:17, 17:17, 21:17 giờ Việt Nam), trong đó lần 05:17 và 21:17 làm mới tin sáng và tin tối. Nếu GitHub trễ, iPhone hiện bản của lần chạy trước đó. Thông báo của Phím tắt có thể bị cắt nếu tin dài; dùng tác vụ *Hiển thị kết quả* để xem đủ.

**Nội dung hai tin:**

| Tin | Giờ (VN) | Nội dung |
| --- | --- | --- |
| Sáng | 06:47 | Hôm nay: buổi học, hạn nộp; 7 ngày tới: hạn và thi; việc quá hạn; môn chưa có lịch thi |
| Tối | 22:13 | Ngày mai có gì; việc hạn trong 48 giờ chưa xong; việc quá hạn |
| Tối Chủ nhật | 22:13 | Như tin tối, thêm tổng kết tuần tới, lịch thi đã có, môn chưa có lịch thi |
| ntfy khi lỗi | Ngay lúc build | Dữ liệu sai, build lỗi |
| ntfy khi lịch đổi | Ngay lúc build | Buổi bị bỏ (➖) và buổi mới (➕) trong 14 ngày tới |

Giờ lẻ phút (05:17 thay vì 05:00) để tránh giờ cao điểm đầu giờ của GitHub Actions. Nếu sau này dùng Android, thay Phím tắt bằng Tasker/Automate hoặc để ntfy gửi luôn cả tin sáng, tối.

**Mẫu tin sáng:**

```text
📅 Thứ Năm 29/10/2026

HÔM NAY
• 19:00–21:50  Kỹ thuật số (ELE1433)

7 NGÀY TỚI
• T6 30/10  19:00–21:50  Ngôn ngữ lập trình C++ (INT1339)
• CN 01/11  19:00–21:50  Toán rời rạc 1 (INT1358)

📝 Chưa có lịch thi: 3 môn (Kỹ thuật số, Ngôn ngữ lập trình C++, Toán rời rạc 1)
```

## 7. Cấu trúc thư mục và công nghệ

Viết bằng Python 3.12+, chạy trên GitHub Actions, xuất ra file tĩnh; không cần máy chủ hay cơ sở dữ liệu.

```text
lich-ptit/
├── data/                    # nguồn sự thật, sửa tay
│   ├── courses.yaml
│   ├── classes.yaml
│   ├── exams.yaml
│   └── tasks.yaml
├── src/lichptit/
│   ├── models.py            # Pydantic: Course, ClassSession, Exam, Task
│   ├── load.py              # đọc + kiểm tra YAML
│   ├── expand.py            # buổi học lặp → danh sách buổi cụ thể
│   ├── importers/
│   │   └── moodle_ical.py   # đọc link iCal LMS → Task
│   │   ├── moodle_api.py    # đăng nhập token.php, lấy hạn nộp
│   │   └── qldt.py          # đăng nhập QLĐT, lấy TKB tuần (httpx; dự phòng Playwright)
│   ├── secrets.py           # đọc tài khoản từ biến môi trường hoặc keyring
│   ├── export_ics.py        # xuất calendar.ics có VALARM
│   ├── export_web.py        # xuất site/data.json cho trang web
│   ├── digest.py            # soạn tin sáng / tối / tuần
│   ├── notify.py          # thông báo ntfy (tùy chọn)
│   └── cli.py               # lệnh: check | build | digest | notify
├── site/                    # trang web tĩnh (HTML + JS), PWA manifest
├── tests/                   # pytest
├── .github/workflows/
│   ├── build.yml            # khi push data/ + 4 lần/ngày: import LMS, build, deploy
│   └── (không còn digest.yml)           # tin sáng/tối do build.yml tạo
├── pyproject.toml
└── README.md
```

| Thành phần | Lựa chọn | Lý do |
| --- | --- | --- |
| Ngôn ngữ | Python | Đang học Python; thư viện lịch đầy đủ |
| Đọc/kiểm tra dữ liệu | `PyYAML` + `pydantic` | Báo lỗi rõ dòng nào sai |
| Lịch | `icalendar` (đọc và ghi ICS), `zoneinfo` | Chuẩn RFC 5545, hỗ trợ VALARM |
| Gọi mạng | `httpx` | Tải link iCal LMS, gửi thông báo ntfy |
| Trang web | HTML + JS thuần, đọc `data.json` | Không cần build front-end |
| Chạy tự động | GitHub Actions (`schedule` + `workflow_dispatch`) | Miễn phí, sẵn tài khoản GitHub |
| Hosting | Cloudflare Pages hoặc GitHub Pages | Miễn phí, HTTPS |
| Kiểm thử | `pytest` | Chạy trong workflow trước khi deploy |

Bí mật lưu trong GitHub Secrets: `NTFY_TOPIC`, `SITE_BASE_URL (chỉ khi dùng Cloudflare Pages)`, `MOODLE_ICAL_URL`, `SITE_TOKEN` (chuỗi ngẫu nhiên dùng làm tên đường dẫn), QLDT\_USERNAME, QLDT\_PASSWORD, LMS\_USERNAME, LMS\_PASSWORD.

## 8. Lộ trình theo giai đoạn

Bốn giai đoạn; mỗi giai đoạn kết thúc bằng một thứ dùng được ngay trên điện thoại. Giai đoạn 1 là bản tối thiểu (MVP), đủ để hết quên lịch.

**Giai đoạn 1 – Lịch trên iPhone (MVP)**

- [ ] Tạo repo `lich-ptit`, `pyproject.toml`, cấu trúc thư mục ở mục 7
- [ ] Viết `models.py` + `load.py`, kiểm tra 4 file YAML
- [ ] `expand.py`: bung buổi học lặp, tôn trọng `skip_dates` / `extra_dates`
- [ ] `export_ics.py`: xuất `calendar.ics` có VALARM theo quy tắc mục 5
- [ ] Nhập lịch học từ trang TKB tuần (nút In) vào classes.yaml; mở thử file `.ics` trên iPhone
- [ ] Workflow `build.yml` deploy lên Pages; đăng ký lịch trên iPhone

**Giai đoạn 2 – Tự lấy hạn nộp LMS + tin sáng/tối**

- [ ] Lấy hạn nộp LMS: thử đăng nhập qua token.php + API lịch Moodle; nếu bị tắt, dùng link iCal
- [ ] `importers/moodle_ical.py`, gộp vào `tasks.yaml` không trùng
- [ ] Tạo hai Phím tắt "Tin sáng" (06:47) và "Tin tối" (22:13) theo `docs/shortcuts.md`; `digest.py` ghi `morning.txt` / `evening.txt` mỗi lần build
- [ ] Workflow `build.yml` chạy 4 lần/ngày, tạo tin sáng/tối; thêm ntfy (tùy chọn) báo khi lịch đổi hoặc lỗi

**Giai đoạn 3 – Trang web xem nhanh**

- [ ] `export_web.py` xuất `data.json`
- [ ] Trang `site/` 4 tab: Hôm nay, Tuần, Sắp thi, Việc tồn; PWA manifest
- [ ] Tìm request JSON của trang TKB tuần (DevTools → Network), ghi lại request đăng nhập và request lấy TKB; viết importers/qldt.py tự đăng nhập bằng Secrets, lấy TKB 4 tuần tới mỗi 6 giờ, báo ntfy khi lịch đổi; thử chạy trên GitHub Actions trước, bị chặn thì chuyển về máy

**Giai đoạn 4 – Thêm việc từ điện thoại (tùy chọn)**

- [ ] Phím tắt iOS hoặc biểu mẫu web để thêm việc mới từ điện thoại
- [ ] Ghi việc vào repo qua GitHub API (cần một chỗ nhận yêu cầu, ví dụ Cloudflare Workers)

## 9. Bảo mật, kiểm thử và câu hỏi còn mở

**Bảo mật.** Lịch học gắn với tên và mã sinh viên nên không để công khai dễ tìm.

- Repo để chế độ **riêng tư**. Trang Pages vẫn truy cập được từ Internet, nên đặt file dưới đường dẫn ngẫu nhiên dài: `/<SITE_TOKEN>/calendar.ics`, không liệt kê thư mục.
- Không đưa lên trang: mật khẩu, điểm số, số CCCD, link iCal LMS (link này chứa token đăng nhập).
- Tài khoản và mật khẩu Quản lý đào tạo, LMS, link iCal và tên kênh ntfy chỉ nằm trong GitHub Secrets (hoặc Credential Manager nếu chạy trên máy); không in ra log. Bật xác thực 2 bước cho tài khoản GitHub, vì ai vào được repo là dùng được các Secret này.
- Bị lộ link: đổi `SITE_TOKEN`, build lại, đăng ký lại lịch trên iPhone.

**Kiểm thử (pytest):**

1. Bung buổi học lặp: đúng số buổi, bỏ đúng ngày nghỉ, giờ đúng múi +07.
2. ICS hợp lệ: mở lại bằng `icalendar` được, mỗi sự kiện có UID cố định qua các lần build, số VALARM đúng.
3. Nhập LMS hai lần liên tiếp không sinh việc trùng; không ghi đè trường `status`/`note` bạn đã sửa.
4. Bản tóm tắt: với ngày giả định cố định, nội dung tin khớp mẫu.
5. YAML sai (thiếu `due`, giờ "25:00") thì build thất bại và báo đúng dòng.

Kiểm tra thủ trên iPhone sau giai đoạn 1: tạo một việc hạn 10 phút sau, xác nhận điện thoại báo đúng giờ.

**Câu hỏi đã trả lời và còn mở:**

- [x] Thời khóa biểu: trang [TKB tuần](https://qldttx.pttc1.edu.vn/#/tkb-tuan), dữ liệu từ request `w-locdstkbtuanusertheohocky`; có nút In.
- [x] Lịch học hằng tuần ở Quản lý đào tạo (3 môn, 19:00–21:50); LMS dùng để tự học.
- [x] Kênh nhắc: Phím tắt iOS cho tin sáng/tối, ntfy (tùy chọn) cho cảnh báo, cùng Lịch iPhone (không dùng Telegram).
- [x] Lịch thi: có mục "Xem lịch thi" trong Quản lý đào tạo; trường chưa công bố.
- [ ] URL, Method, Payload, header và mẫu JSON của `w-locdstkbtuanusertheohocky`.
- [ ] Request đăng nhập (bắt bằng Keep log khi đăng nhập lại).
- [ ] Request của mục "Xem lịch thi".
- [ ] LMS có bật "Xuất lịch" (link iCal) hoặc API di động không?

**Prompt cho Claude Code: xem mục 11 (một prompt cho mỗi giai đoạn).**

## 10. Checklist việc cần làm

Mã nguồn giai đoạn 1 và 2 (trừ phần đăng nhập Quản lý đào tạo) đã viết xong và qua 16 bài kiểm thử, nằm trong gói `lich-ptit.zip`. Phần còn lại cần tài khoản của bạn nên phải tự làm.

**Đã xong (Claude làm):**

- [x] Cấu trúc dự án, `models.py`, `load.py`, `expand.py`, `export_ics.py`, `export_web.py`, `digest.py`, `notify.py`, `changes.py`, `cli.py`
- [x] Bộ đọc link iCal LMS và gộp với việc nhập tay
- [x] Trang web 4 tab (Hôm nay, Tuần này, Sắp thi, Việc tồn)
- [x] Workflow `build.yml` (4 lần/ngày) tạo luôn tin sáng, tin tối và báo thay đổi qua ntfy
- [x] Hướng dẫn Phím tắt iOS (`docs/shortcuts.md`)
- [x] Dữ liệu 3 môn thật, 16 bài pytest
- [x] Khung `importers/qldt.py`, chờ thông tin request

**Bạn cần làm:**

- [ ] 1\. DevTools: chụp request `w-locdstkbtuanusertheohocky` (URL, Method, Payload, mẫu JSON)
- [ ] 2\. DevTools: bật Keep log, đăng nhập lại, chụp request đăng nhập
- [ ] 3\. DevTools: mở "Xem lịch thi", chụp request
- [ ] 4\. LMS: kiểm tra nút "Lấy URL lịch"; thử app Moodle đăng nhập lms.pttc1.edu.vn
- [ ] 5\. GitHub: tạo repo riêng tư `lich-ptit`, bật xác thực 2 bước
- [ ] 6\. ntfy (tùy chọn): cài app ntfy, tạo tên kênh ngẫu nhiên dài (xem `docs/shortcuts.md`)
- [ ] 7\. Thêm Secrets: `SITE_TOKEN`, `MOODLE_ICAL_URL` (nếu có), `NTFY_TOPIC` (nếu dùng ntfy)
- [ ] 8\. Cài Python 3.12+, Git, VS Code; giải nén zip vào repo, chạy `pip install -e ".[dev]"` và `pytest`
- [ ] 9\. Sửa `from` / `to` trong `data/classes.yaml` theo TKB dạng học kỳ; dán link học online
- [ ] 10\. Bật Pages (Settings → Pages → Source: GitHub Actions) hoặc nối Cloudflare Pages; push lên `main`
- [ ] 11\. iPhone: đăng ký `https://<trang>/<SITE_TOKEN>/calendar.ics`, tắt "Xóa cảnh báo"
- [ ] 12\. Phím tắt iOS: tạo "Tin sáng" (06:47) và "Tin tối" (22:13) theo `docs/shortcuts.md`
- [ ] 13\. Chạy thử: Actions → build → Run workflow, rồi mở `.../<SITE_TOKEN>/morning.txt` trên iPhone

## 11. Prompt cho Claude Code theo giai đoạn

Mỗi giai đoạn một prompt, dán vào Claude Code theo thứ tự. Prompt nào cũng tự đủ: nêu mục tiêu, việc phải làm, và tiêu chí nghiệm thu để biết khi nào xong. Chỉ sang giai đoạn sau khi giai đoạn trước qua hết tiêu chí. Trước khi bắt đầu: xuất tài liệu này ra Markdown (Export → Markdown), lưu vào repo là `docs/spec.md`. Tài liệu này là "đặc tả"; các prompt dưới đây gọi nó như vậy.

Bộ mã mẫu `lich-ptit.zip` (nếu bạn đang giữ) chỉ là bản tham khảo. Claude Code có thể viết lại từ đầu hoặc sửa trên bản đó; prompt nào cũng đúng trong cả hai trường hợp.

| Giai đoạn | Kết quả dùng được ngay | Cần từ bạn trước khi chạy |
| --- | --- | --- |
| 0. Khởi tạo dự án | Repo có khung, quy tắc làm việc (`CLAUDE.md`) | Repo GitHub, `docs/spec.md` |
| 1. Lịch iPhone | `calendar.ics` có báo thức cho 3 môn | Ngày bắt đầu/kết thúc từng môn |
| 2. Tin sáng/tối, trang web, tự động hóa | `morning.txt`, `evening.txt`, trang 4 tab, workflow chạy trên GitHub | Secret `SITE_TOKEN`, bật Pages |
| 3. LMS và ntfy | Hạn nộp từ LMS vào lịch; báo khi lịch đổi | Link iCal LMS (nếu có), tên kênh ntfy |
| 4. Tự đăng nhập Quản lý đào tạo | TKB và lịch thi tự cập nhật | 3 request từ DevTools, mật khẩu trong Secrets |
| 5. Thêm việc từ điện thoại (tùy chọn) | Thêm việc mới không cần mở máy tính | Quyết định có làm hay không |

### Giai đoạn 0 – Khởi tạo dự án

```text
Bối cảnh: tôi là sinh viên hệ từ xa PTIT. Tôi xây dựng chương trình "Lịch PTIT" để theo dõi
lịch học, lịch thi và việc cần làm, nhắc trên iPhone. Đặc tả đầy đủ nằm ở docs/spec.md
(đọc toàn bộ trước khi làm). Chưa viết tính năng; việc là dựng khung.

Làm:
1. Tạo cấu trúc thư mục như mục 7 của đặc tả: data/, src/lichptit/, site/, tests/, docs/,
   .github/workflows/. Python 3.12+, pyproject.toml (pydantic, PyYAML, icalendar, tzdata;
   pytest cho dev; lệnh console "lichptit").
2. Tạo .gitignore (bỏ .venv, __pycache__, _site, .env, *.egg-info).
3. Tạo CLAUDE.md ghi quy tắc làm việc: trả lời và viết ghi chú bằng tiếng Việt; mọi giờ dùng
   múi Asia/Ho_Chi_Minh; KHÔNG BAO GIỜ ghi mật khẩu, token, cookie, link iCal có authtoken,
   ID/mật khẩu phòng học ra log, file, commit hay trang web; chạy pytest trước mỗi commit; commit
   nhỏ, thông điệp tiếng Việt; không đổi cấu trúc dữ liệu (mục 5) mà không hỏi tôi.
4. Tạo README.md ngắn: cách cài và chạy trên Windows (PowerShell, venv).

Nghiệm thu: pip install -e ".[dev]" chạy được; "lichptit --help" in ra trợ giúp; pytest chạy
(chưa có test cũng không lỗi). Commit "Khởi tạo dự án".
```

### Giai đoạn 1 – Lịch trên iPhone (bản tối thiểu)

```text
Làm GIAI ĐOẠN 1 theo docs/spec.md mục 3, 5, 6 và 8. Đã có khung từ giai đoạn 0.

Dữ liệu thật (học kỳ 1, 2026-2027), đặt trong data/courses.yaml:
  ELE1433 Kỹ thuật số, nhóm 03, GV Vũ Anh Đào        - học thứ Năm
  INT1339 Ngôn ngữ lập trình C++, nhóm 08, GV Nguyễn Đình Hiến - học thứ Sáu
  INT1358 Toán rời rạc 1, nhóm 09, GV Nguyễn Kiều Linh     - học Chủ nhật
Cả ba học online 19:00-21:50 (tiết 13-15). Ngày bắt đầu/kết thúc từng môn: [TÔI SẼ ĐIỀN Ở
data/classes.yaml; đặt tạm 2026-10-26 đến 2026-12-27 và ghi chú "CẦN SỬA"].

Viết:
1. models.py (Pydantic, extra=forbid): Course, ClassRule (một buổi lẻ có date, hoặc lặp
   hằng tuần có weekday+from+to; skip_dates, extra_dates, periods, online, link, room, flags
   day_bu/trung_lich, remind), Exam (date/start có thể null = trường chưa công bố), Task (due,
   priority high|normal|low, status todo|doing|done, source manual|lms|qldt, remind). Remind
   dạng 30m / 2h / 3d.
2. load.py: đọc 4 file YAML trong data/, kiểm tra schema, báo lỗi "tên file + mục số + id +
   trường"; phát hiện id trùng và môn không tồn tại.
3. expand.py: bung buổi lặp thành buổi cụ thể (tôn trọng skip_dates/extra_dates); lời nhắc
   mặc định: buổi học trước 30 phút; việc trước 1 ngày và 3 giờ; thi trước 14 ngày, 3 ngày
   và 20:00 tối hôm trước; bỏ việc done và kỳ thi chưa có ngày; đánh dấu trung lịch.
4. export_ics.py: xuất calendar.ics (RFC 5545, VALARM, UID cố định dạng "<id>-<ngày>@lich-ptit",
   múi +07 đổi sang UTC, REFRESH-INTERVAL 1 giờ). ID/mật khẩu phòng (trường room) chỉ đưa
   vào DESCRIPTION của ICS.
5. cli.py: lệnh "lichptit check" và "lichptit build --out _site --token <tên-thư-mục>" (ghi
   _site/<token>/calendar.ics).
6. 4 file YAML mẫu với dữ liệu thật ở trên; classes.yaml dùng lặp hằng tuần.
7. Test pytest: bung buổi đúng số buổi và bỏ đúng ngày nghỉ; giờ 19:00 ra "+07:00"; ICS mở lại
   bằng thư viện icalendar được, UID ổn định qua 2 lần build, số VALARM đúng; YAML sai (giờ
   25:00, thiếu due, môn không tồn tại) báo đúng dòng; room không lọt ra ngoài ICS.

Nghiệm thu: pytest qua hết; "lichptit check" báo "3 môn"; "lichptit build" tạo
calendar.ics mà tôi kéo thả vào app Lịch trên máy thấy 3 môn đúng thứ, đúng 19:00-21:50.
Commit theo từng bước nhỏ.
```

### Giai đoạn 2 – Tin sáng/tối, trang web và tự động hóa trên GitHub

```text
Làm GIAI ĐOẠN 2 theo docs/spec.md mục 4, 6, 7. Giai đoạn 1 đã xong.

Viết:
1. digest.py: soạn tin chữ tiếng Việt. Tin sáng: hôm nay (buổi học, hạn nộp), 7 ngày tới,
   việc quá hạn, các môn chưa có lịch thi. Tin tối: ngày mai, việc hạn trong 48 giờ, quá
   hạn. Tối Chủ nhật thêm tổng kết tuần tới và lịch thi đã có. Dùng mẫu ở mục 6.
2. Lệnh build ghi thêm morning.txt và evening.txt cạnh calendar.ics. Mỗi file tính cho
   lần hiện kế tiếp (06:47 hoặc 22:13 giờ Việt Nam) để đúng ngày dù build lúc nào.
3. export_web.py + site/index.html + site/manifest.json: data.json (KHÔNG chứa link lớp, ID/mật
   khẩu phòng) và trang web một file HTML+JS thuần, 4 tab: Hôm nay, Tuần này, Sắp thi, Việc
   tồn; đẹp trên iPhone, hỗ trợ chế độ tối, thêm được vào màn hình chính, meta noindex.
4. .github/workflows/build.yml: chạy khi push vào data/, src/, site/ và theo cron 4 lần/ngày
   (05:17, 11:17, 17:17, 21:17 giờ VN = 22:17, 04:17, 10:17, 14:17 UTC); bước test (pytest)
   → build (SITE_TOKEN lấy từ secret, thiếu thì dừng) → deploy GitHub Pages bằng
   actions/deploy-pages. Thư mục gốc _site chỉ có index.html trống; mọi thứ nằm dưới
   /<SITE_TOKEN>/.
5. docs/shortcuts.md: hướng dẫn từng bước tạo 2 Phím tắt iOS "Tin sáng" (06:47) và "Tin
   tối" (22:13): Lấy nội dung của URL → Hiển thị thông báo, tự động hóa Giờ trong ngày,
   Chạy ngay; cách đăng ký calendar.ics và tắt "Xóa cảnh báo" trên iPhone.
6. Test: tin sáng khớp mẫu với ngày giả định; build lúc 21:17 thứ Sáu cho tin sáng của thứ Bảy;
   tin tối Chủ nhật có "TUẦN TỚI"; data.json không chứa mật khẩu phòng.

Kiểm tra workflow bằng cách parse YAML trước khi commit (cẩn thận dấu hai chấm trong chuỗi,
 dùng run: | cho lệnh dài).

Nghiệm thu: pytest qua hết; "lichptit build" tạo đủ calendar.ics, data.json, morning.txt,
evening.txt, index.html; mở trang bằng "python -m http.server" thấy 4 tab hoạt động
trên màn hình điện thoại (thu nhỏ cửa sổ trình duyệt).
```

Sau prompt này, **bạn tự làm** (Claude Code không làm hộ được): thêm Secret `SITE_TOKEN`; bật Pages (Settings → Pages → Source: GitHub Actions); `git push`; đăng ký lịch trên iPhone; tạo hai Phím tắt theo `docs/shortcuts.md`.

### Giai đoạn 3 – Hạn nộp từ LMS và thông báo ntfy

```text
Làm GIAI ĐOẠN 3 theo docs/spec.md mục 2, 6, 9. Giai đoạn 2 đã xong và đang chạy trên GitHub.

A. LMS (Moodle, lms.pttc1.edu.vn):
1. importers/moodle_ical.py: tải link iCal từ biến môi trường MOODLE_ICAL_URL, chuyển mỗi
   VEVENT thành Task (source=lms). id ổn định = "lms-" + 10 ký tự đầu của SHA1(UID). Ánh xạ tên
   môn trong CATEGORIES sang mã môn bằng một bảng ánh xạ cấu hình được. TUYỆT ĐỐI không in
   URL (có authtoken) ra log hay thông báo lỗi.
2. load.py thêm merge_tasks: việc nhập tay trùng id thì giữ status/note/remind của tôi nhưng
   lấy hạn mới từ LMS; không tạo trùng khi chạy lại.
3. Nếu MOODLE_ICAL_URL không có thì bỏ qua bước này, không lỗi.

B. ntfy (tùy chọn, chỉ chạy khi có biến NTFY_TOPIC):
4. notify.py: gửi thông báo JSON tới https://ntfy.sh (title, message, priority); lỗi mạng chỉ
   in cảnh báo, không làm hỏng build; không in tên kênh ra log.
5. changes.py: lấy data.json của lần build trước (biến PREV_DATA_URL, lỗi thì coi như chưa có),
   so với sự kiện mới trong 14 ngày tới; liệt kê buổi bị bỏ và buổi mới; có thay đổi thì
   báo ntfy ưu tiên 4.
6. cli.py: thêm lệnh "lichptit notify"; khi dữ liệu YAML sai trong GitHub Actions thì báo
   ntfy; build.yml thêm bước "if: failure()" báo ntfy "build lỗi"; thêm secret NTFY_TOPIC và
   MOODLE_ICAL_URL, SITE_BASE_URL (tùy chọn) vào workflow.
7. docs/shortcuts.md thêm phần cài ntfy.

Test: parse file iCal mẫu (đặt trong tests/fixtures); id ổn định; merge giữ status của tôi; lịch
bị dời giờ thì diff báo đúng "➖ bỏ" và "➕ mới"; không có bản trước thì không báo.

Nghiệm thu: pytest qua hết; chạy build có và không có MOODLE_ICAL_URL đều không lỗi.
```

Trước prompt này, **bạn tự làm**: lấy link iCal từ LMS (Lịch → Nhập hoặc xuất lịch → Xuất lịch → Lấy URL lịch) và thêm Secret `MOODLE_ICAL_URL`; cài app ntfy, tạo tên kênh ngẫu nhiên dài, thêm Secret `NTFY_TOPIC`. Nếu LMS không có nút lấy link iCal, bỏ phần A và dùng giai đoạn 4 cho cả LMS.

### Giai đoạn 4 – Tự đăng nhập Quản lý đào tạo

Bạn phải điền thông tin vào các chỗ trong ngoặc vuông trước khi dán. Lấy thông tin theo mục 2, phần "Đã xác định từ trang TKB tuần". **Không dán mật khẩu hay token thật vào prompt**; chỉ ghi tên trường.

```text
Làm GIAI ĐOẠN 4 theo docs/spec.md mục 2 ("Đăng nhập tự động vào tài khoản") và mục 9.
Chỉ dùng cho TÀI KHOẢN CỦA TÔI, mục đích cá nhân.

Thông tin hệ thống Quản lý đào tạo (https://qldttx.pttc1.edu.vn, ứng dụng một trang, API tên
dạng w-locds...):
- Request đăng nhập: [URL đầy đủ], phương thức [POST/GET], các trường gửi đi [tên trường,
  ví dụ username, password, ...], cách mật khẩu được mã hóa nếu có [không/md5/...], token
  trả về ở trường [tên trường] hoặc cookie [tên cookie].
- Request lấy TKB: w-locdstkbtuanusertheohocky, URL [URL], phương thức [..], payload [..],
  header xác thực [Authorization: Bearer ... có/không].
- Mẫu JSON trả về của một buổi học (đã che ID/mật khẩu phòng): [dán JSON đã làm sạch vào
  tests/fixtures/qldt_tkb.json].
- Request "Xem lịch thi": [URL, phương thức, payload]; mẫu JSON: [tests/fixtures/qldt_exam.json,
  có thể rỗng nếu trường chưa công bố].

Viết:
1. importers/qldt.py: đăng nhập bằng httpx (gửi lại đúng request trang tự gửi), lấy TKB cả học kỳ,
   chuyển thành danh sách buổi học (ClassRule có date), lấy lịch thi (Exam). Tài khoản đọc từ
   QLDT_USERNAME/QLDT_PASSWORD (biến môi trường) hoặc keyring khi chạy trên máy.
2. Parser tách riêng hàm thuần parse_tkb(json) và parse_exam(json) để test bằng fixture, không
   cần mạng. Lấy giờ trực tiếp từ dữ liệu (không tự tính từ số tiết); đọc cờ Dạy bù và
   Trùng lịch; link học online và ID/mật khẩu phòng vào trường link/room.
3. Quy tắc an toàn (bắt buộc, có test): đăng nhập 1 lần mỗi lượt chạy, tối đa 4 lần/ngày;
   sai đăng nhập 2 lần liên tiếp thì DỪNG và báo ntfy, không thử lại; gặp captcha/OTP/mã lỗi
   lạ thì dừng và báo, không tìm cách vượt; không ghi mật khẩu/token/cookie ra log, file hay
   commit; chỉ giữ các trường lịch cần dùng.
4. Lịch học lấy từ trang ghi đè data/classes.yaml (hoặc file classes_qldt.yaml gộp vào);
   khi khác bản trước thì commit và báo ntfy "Lịch học thay đổi" kèm buổi bị đổi.
5. Thử chạy trên GitHub Actions trước. Nếu bị chặn (403, captcha, IP nước ngoài), chuyển bước
   lấy dữ liệu sang máy tôi: Task Scheduler chạy "lichptit sync" (mật khẩu trong Windows
   Credential Manager bằng keyring), rồi git push file YAML; phần build và báo ntfy vẫn ở
   GitHub. Viết hướng dẫn cài Task Scheduler cho cách này.

Nghiệm thu: pytest qua hết với fixture; không có chuỗi nào giống mật khẩu/token trong log khi chạy
"lichptit sync --dry-run"; thử sai mật khẩu (test giả lập) thì dừng sau 2 lần.
```

Sau prompt này, **bạn tự làm**: thêm Secrets `QLDT_USERNAME`, `QLDT_PASSWORD` vào repo (hoặc lưu bằng `keyring` nếu chạy trên máy); chạy thử workflow bằng nút Run workflow; kiểm tra 3 buổi học khớp với trang trường.

### Giai đoạn 5 – Thêm việc từ điện thoại (tùy chọn)

Chỉ làm nếu bạn thấy sửa `tasks.yaml` trên máy tính là bất tiện. Đây là giai đoạn duy nhất cần một dịch vụ chạy liên tục, nên phức tạp hơn.

```text
Làm GIAI ĐOẠN 5 theo docs/spec.md mục 3 (F7) và mục 8.
Mục tiêu: thêm và đánh dấu xong việc cần làm từ iPhone mà không mở máy tính.
Thiết kế: Cloudflare Worker nhận yêu cầu POST có token, gọi GitHub API để sửa data/tasks.yaml
(commit), việc commit sẽ kích hoạt workflow build. Phím tắt iOS gọi Worker đó (hỏi tên việc,
hạn, ưu tiên). Token GitHub chỉ có quyền ghi đúng một file, lưu trong secret của Worker.
Trước khi viết, hãy nêu 2 phương án (Worker và biểu mẫu GitHub Issues) kèm ưu nhược điểm để
tôi chọn. Test: thêm, đánh dấu xong, chống gửi trùng, từ chối yêu cầu sai token.
```

**Cách dùng những prompt này:** dán mỗi lần một prompt, đợi Claude Code làm xong và báo đã qua tiêu chí nghiệm thu, rồi tự kiểm tra bằng mắt (mở file ICS, xem trang web) trước khi sang giai đoạn kế. Nếu Claude Code hỏi lại ở đâu, trả lời theo đặc tả; nếu đặc tả chưa nói rõ, hỏi lại tôi để cập nhật tài liệu.

## Nguồn

- [Cổng hệ Đại học từ xa PTIT](https://dec.ptit.edu.vn/) – liên kết hệ thống Quản lý đào tạo, Elearning, Thư viện số
- [LMS hệ từ xa (Moodle)](https://lms.pttc1.edu.vn/login/index.php)
- [Trang tuyển sinh Đại học từ xa PTIT](https://daihoctuxa.ptit.edu.vn/) – thi kết thúc học phần tập trung 2 ngày mỗi kỳ
- [Moodle Docs – Calendar export](https://docs.moodle.org/23/en/Calendar_export) và [kiểm thử xuất lịch trong mã nguồn Moodle](https://github.com/moodle/moodle/blob/9eed82a7f541e96502230260910e759329617b07/calendar/tests/behat/export.feature)
- [GitHub Community – độ trễ của lịch chạy schedule](https://github.com/orgs/community/discussions/204544)
- [Hebcal – tùy chọn Xóa cảnh báo của lịch đăng ký trên iPhone](https://hebcal.com/home/?p=563)
