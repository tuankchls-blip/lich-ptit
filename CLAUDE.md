# Quy tắc làm việc – Lịch PTIT

Đặc tả đầy đủ: `docs/spec.md`. Đọc trước khi làm bất kỳ giai đoạn nào.

- Trả lời, viết ghi chú, docstring và thông điệp commit bằng **tiếng Việt**.
- Mọi thời gian lưu và hiển thị theo múi **Asia/Ho_Chi_Minh** (UTC+7).
- **KHÔNG BAO GIỜ** ghi mật khẩu, token, cookie, link iCal có authtoken, ID/mật khẩu phòng học
  ra log, file, commit hay trang web. ID/mật khẩu phòng (trường `room`) chỉ được đưa vào
  DESCRIPTION của `calendar.ics`.
- Chạy `pytest` trước mỗi commit; chỉ commit khi qua hết.
- Commit nhỏ, mỗi commit một việc, thông điệp tiếng Việt.
- **Không đổi cấu trúc dữ liệu** (mục 5 của đặc tả: các trường trong `data/*.yaml`) mà không hỏi
  chủ dự án trước.
- Dữ liệu sai định dạng thì dừng và báo rõ file + mục + trường; không xuất lịch hỏng.
