# Lịch PTIT

Gom lịch học, lịch thi và việc cần làm (hệ từ xa PTIT) vào các file YAML trong `data/`,
rồi xuất ra `calendar.ics` có báo thức để đăng ký trên iPhone. Đặc tả: [`docs/spec.md`](docs/spec.md).

## Cài đặt trên Windows (PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
```

Nếu PowerShell chặn chạy script: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## Dùng

```powershell
lichptit --help
lichptit check                                # kiểm tra 4 file YAML trong data/
lichptit build --out _site --token <chuoi-ngau-nhien>   # tạo _site/<token>/calendar.ics
```

Mở `_site/<token>/calendar.ics` bằng app Lịch để xem thử.

## Dữ liệu

| File | Chứa |
| --- | --- |
| `data/courses.yaml` | Môn học kỳ này |
| `data/classes.yaml` | Buổi học (lặp hằng tuần hoặc buổi lẻ) |
| `data/exams.yaml` | Lịch thi (để `date: null` khi trường chưa công bố) |
| `data/tasks.yaml` | Việc cần làm |
