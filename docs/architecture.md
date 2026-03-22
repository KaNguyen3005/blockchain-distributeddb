# Kiến trúc giải pháp

## 1. Mục tiêu nghiệp vụ

Hệ thống phục vụ các tác vụ sau:

- Phát hành văn bằng/chứng chỉ số cho người học.
- Đồng bộ bản ghi lên nhiều node lưu trữ để giảm rủi ro mất dữ liệu.
- Tạo dấu vết bất biến trên blockchain để chống làm giả.
- Cho phép bên thứ ba xác thực tình trạng hợp lệ của văn bằng.
- Hỗ trợ thu hồi nếu phát hiện sai phạm hoặc cần cập nhật.

## 2. Luồng xử lý

### Phát hành
1. Trường học tạo bản ghi văn bằng.
2. Hệ thống chuẩn hoá dữ liệu và sinh `credential_hash` bằng SHA-256.
3. Bản ghi được sao chép lên các node dữ liệu phân tán.
4. Blockchain ghi block mới với hành động `ISSUE`.
5. Hệ thống trả về mã văn bằng, hash và thông tin block để làm chứng thực.

### Xác thực
1. Bên xác minh nhập `credential_id` hoặc quét QR.
2. Hệ thống đọc bản ghi từ cụm lưu trữ phân tán.
3. Hệ thống tính lại fingerprint của văn bằng.
4. Blockchain được kiểm tra toàn vẹn chuỗi (`previous_hash` + `block_hash`).
5. Nếu hash trùng khớp và văn bằng chưa bị thu hồi, kết quả là hợp lệ.

### Thu hồi
1. Đơn vị phát hành chuyển trạng thái `revoked=true`.
2. Dữ liệu mới được cập nhật tới toàn bộ node.
3. Blockchain thêm block `REVOKE`.
4. Các truy vấn xác thực sau đó sẽ trả về trạng thái không hợp lệ.

## 3. Thành phần kỹ thuật trong prototype

- `src/credential_chain/models.py`: định nghĩa `Credential` và `Block`.
- `src/credential_chain/storage.py`: mô phỏng cơ sở dữ liệu phân tán bằng cơ chế replicated file store.
- `src/credential_chain/blockchain.py`: quản lý blockchain ledger dạng JSON và logic kiểm tra toàn vẹn.
- `src/credential_chain/service.py`: orchestration cho issue/verify/revoke.
- `src/credential_chain/cli.py`: giao diện dòng lệnh để demo.
- `tests/test_service.py`: kiểm thử các kịch bản cốt lõi.

## 4. Đề xuất triển khai production

### Tầng dữ liệu phân tán
- Dùng CockroachDB hoặc Cassandra để đạt replication, partition tolerance, failover.
- Thiết kế index theo `credential_id`, `issuer_id`, `recipient_name`.
- Bổ sung audit log và cơ chế backup theo vùng địa lý.

### Tầng blockchain
- Dùng permissioned blockchain để chỉ các đơn vị được cấp phép mới có quyền ghi.
- Mỗi cơ sở đào tạo sở hữu certificate/signing key riêng.
- Chỉ lưu hash và metadata tối thiểu lên chain để bảo vệ dữ liệu cá nhân.

### Tầng ứng dụng
- Cung cấp REST/gRPC API.
- Phân quyền RBAC cho trường học, sinh viên, đơn vị tuyển dụng, cơ quan quản lý.
- Tích hợp QR code chứa `credential_id` và checksum.
- Ký số PDF văn bằng để đối chiếu offline.

## 5. Bảo mật và tuân thủ

- Không lưu dữ liệu nhạy cảm không cần thiết lên blockchain.
- Mã hóa dữ liệu cá nhân ở tầng database và backup.
- Ghi nhận đầy đủ lịch sử truy cập/xác thực.
- Hỗ trợ yêu cầu tuân thủ nội bộ, quy định bảo vệ dữ liệu và quy trình cấp phát khóa.
