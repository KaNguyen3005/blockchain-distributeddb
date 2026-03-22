# Hệ thống xác thực văn bằng, chứng chỉ dựa trên cơ sở dữ liệu phân tán và Blockchain

Đây là nguyên mẫu (prototype) cho bài toán **phát hành, lưu trữ và xác thực văn bằng/chứng chỉ** với hai lớp bảo vệ:

1. **Cơ sở dữ liệu phân tán**: mỗi văn bằng được sao chép sang nhiều node lưu trữ (`node-a`, `node-b`, `node-c`) để tăng độ sẵn sàng.
2. **Blockchain ledger**: mỗi lần phát hành hoặc thu hồi đều tạo block chứa hash của văn bằng, giúp phát hiện chỉnh sửa trái phép.

## Kiến trúc tổng thể

- **Institution / Issuer**: đơn vị phát hành văn bằng.
- **ReplicatedCredentialStore**: lưu bản ghi văn bằng lên nhiều node.
- **BlockchainLedger**: ghi nhận fingerprint SHA-256 của văn bằng và liên kết block bằng `previous_hash`.
- **CredentialService**: lớp nghiệp vụ cung cấp 3 thao tác chính:
  - `issue_credential`: phát hành văn bằng
  - `verify_credential`: xác thực văn bằng
  - `revoke_credential`: thu hồi văn bằng
- **CLI**: cho phép chạy demo nhanh từ terminal.

Chi tiết thiết kế xem tại `docs/architecture.md`.

## Cách chạy

### 1. Chạy kiểm thử

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

### 2. Phát hành văn bằng

```bash
PYTHONPATH=src python -m credential_chain.cli issue CERT-001 "Nguyen Van A" "Open Digital University" Bachelor "Computer Science" 2026-03-22 issuer-001 --metadata '{"gpa":"3.8"}'
```

### 3. Xác thực văn bằng

```bash
PYTHONPATH=src python -m credential_chain.cli verify CERT-001
```

### 4. Thu hồi văn bằng

```bash
PYTHONPATH=src python -m credential_chain.cli revoke CERT-001
```

## Thư mục dữ liệu

- `data/nodes/node-a`, `data/nodes/node-b`, `data/nodes/node-c`: nơi lưu bản sao văn bằng.
- `data/blockchain/ledger.json`: sổ cái blockchain dạng JSON.

## Hướng mở rộng thực tế

- Thay JSON file bằng **Cassandra / CockroachDB / MongoDB cluster** để có khả năng scale thực sự.
- Thay blockchain mô phỏng bằng **Hyperledger Fabric**, **Quorum** hoặc smart contract trên EVM chain.
- Bổ sung chữ ký số của đơn vị phát hành, mã QR, REST API và phân quyền theo vai trò.
- Tích hợp cổng tra cứu dành cho doanh nghiệp/tổ chức tuyển dụng.
