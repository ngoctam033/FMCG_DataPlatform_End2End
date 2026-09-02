# Shared Simulator Concepts

Thư mục này chứa các code, cấu hình, hoặc khái niệm được chia sẻ chung giữa nhiều Data Source Simulators.

## Nguyên tắc sử dụng

- **Quy tắc số 3 (Rule of Three) hoặc số 2:** Chỉ chuyển logic vào đây khi có ít nhất hai simulator khác nhau thực sự sử dụng nó. Tránh premature abstraction.
- Không chứa logic nghiệp vụ đặc thù của một hệ thống nguồn cụ thể.
- Ví dụ về những thứ có thể nằm ở đây: thư viện sinh dữ liệu giả ngẫu nhiên có seed chung, schema validator chung, script định dạng logging.
