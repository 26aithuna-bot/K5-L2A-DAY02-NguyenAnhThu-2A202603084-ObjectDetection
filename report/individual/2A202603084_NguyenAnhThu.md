# Báo cáo cá nhân — Ngày 2 Object Detection

<!-- KHUNG BÁO CÁO: mọi chỗ ghi **TODO** phải tự điền bằng kết quả thật, rồi xóa chữ TODO và comment này trước khi nộp. -->

## 1. Thông tin học viên

- Họ tên: Nguyen Anh Thu **TODO: ghi đúng họ tên có dấu**
- MSSV: 2A202603084
- Email: 26ai.thuna@vinuni.edu.vn
- Lớp: K5-L2A
- Link repo bài làm: https://github.com/26aithuna-bot/K5-L2A-DAY02-NguyenAnhThu-2A202603084-ObjectDetection
- Link Colab đã chạy: **TODO**

## 2. Schema và mini guideline

Xem [GUIDELINE_MINI.md](../../GUIDELINE_MINI.md).

Tóm tắt các ca mơ hồ đã quyết định:

| Ảnh | Ca | Quyết định |
|---|---|---|
| `drive_019` | Minivan/MPV chở người, thân hộp, nóc cao | `van` |
| `drive_003` | Xe bị cắt bởi rìa phải, chỉ còn đầu xe | `truck`, box chạm rìa ảnh |
| `drive_007`, `drive_011`, `drive_012`, `drive_014`, `drive_030`, `drive_031` | Xe rất nhỏ ở xa, vùng tối, không chắc lớp | Không gán |

**TODO:** cách áp dụng schema (đặc biệt ranh giới `car`/`van` và `truck`/`van`/pickup) và phần cần giảng viên làm rõ.

## 3. Annotation và self-QC

- Số file nhãn train: 50 (`dataset/labels/train/`), 1177 box: car 1005, truck 40, bus 105, van 27.
- Quy trình tạo nhãn:
  1. Tạo nhãn nháp bằng YOLO pretrained trên COCO ([tools/prelabel_yolo.py](../../tools/prelabel_yolo.py)), map COCO car/truck/bus → car/truck/bus; COCO không có `van`. **TODO: ghi checkpoint đã dùng (vd. `yolo26x.pt`) và nơi chạy.**
  2. Import nhãn nháp vào CVAT (job 2, 50 ảnh), rà và sửa tay, export "CVAT for images 1.1" lúc 2026-11-10 04:00 UTC.
  3. Chuyển XML sang YOLO bằng [tools/cvat_xml_to_yolo.ps1](../../tools/cvat_xml_to_yolo.ps1).
- Mức chỉnh sửa so với nhãn nháp (so khớp cùng ảnh, IoU ≥ 0.5): 1090 box giữ gần như nguyên (IoU > 0.95), 55 box chỉnh kích thước/vị trí, 30 box đổi lớp, thêm 2 box, xóa 3 box.
- Kết quả checker (`python -X utf8 tools/check_yolo_labels.py`, Python 3.13 Miniconda): `ĐẠT cấu trúc: 50/50 file nhãn hợp lệ.`
- Danh sách ít nhất 10 ảnh đã rà bằng mắt: **TODO** (preview có đánh số box: `outputs/self_qc/previews/`, danh sách box ưu tiên: `outputs/self_qc/review_list.csv`, tạo bằng [tools/review_labels.ps1](../../tools/review_labels.ps1)).
- Lỗi bỏ sót/box/class phát hiện khi rà và cách sửa: **TODO**
- Commit khóa nhãn ban đầu: `7b1b38d` **TODO: ghi link commit sau khi push**

## 4. Gold QC và rework

| Chỉ số | Trước sửa | Sau sửa nếu có |
|---|---:|---:|
| TP | 486 | 485 |
| FP | 691 | 685 |
| FN | 167 | 168 |
| Precision | 0.4129 | 0.4145 |
| Recall | 0.7443 | 0.7427 |
| F1 | 0.5311 | 0.5321 |
| mean_iou_of_matches | 0.8484 | 0.8482 |
| passed | false | false |

"Sau sửa" = rework vòng 1 (export CVAT 2026-11-10 06:02 UTC): đổi lớp 11 box (vd. `drive_011` #14 truck→car, `drive_016` #5/#10 truck→van), xóa 7 box không phải xe/không nhận ra lớp/trùng (vd. `drive_020` box trùng trên SUV đen, `drive_041` #25 khối công trình mép phải, `drive_021` #2 phản chiếu trong nhà chờ), chỉnh cạnh ~100 box. Tổng 1170 box: car 1004, truck 28, bus 105, van 33.

"Trước sửa" = commit khóa nhãn `7b1b38d`, chạy `tools/evaluate_annotations.py` (IoU 0.50) với `gold_train_labels/` do giảng viên phát. Kết quả: `outputs/annotation_evaluation.json`.

**TODO:** thời điểm nhận gold so với thời điểm khóa nhãn; danh sách ảnh/box đã rework và lý do.

## 5. Kết quả YOLO

- Runtime, GPU/CPU, phiên bản Ultralytics và Torch: **TODO**
- Các tham số thay đổi so với notebook nếu có và lý do: **TODO**
- Đường dẫn best checkpoint trong phiên chạy: **TODO**

| Chỉ số trên 10 ảnh eval | Giá trị |
|---|---:|
| Precision | **TODO** |
| Recall | **TODO** |
| mAP50 | **TODO** |
| mAP50–95 | **TODO** |

Ảnh prediction: `assets/eval_predictions/visuals/`; log train và ảnh chỉ số: `assets/yolo26_runs/`. **TODO:** dẫn link tới ít nhất một ảnh và vật thể cụ thể.

Trả lời bốn câu hỏi cuối notebook:

1. Lớp nào recall thấp nhất? Ảnh nào minh họa? **TODO**
2. Nếu mAP50 cao nhưng mAP50–95 thấp, cần kiểm điều gì trên box? **TODO**
3. Lỗi class nào có thể liên quan guideline? Dữ kiện nào hỗ trợ nhận xét? **TODO**
4. Vì sao không dùng 10 ảnh eval để train? Vai trò validation của chúng trong notebook là gì? **TODO**

## 6. Khó khăn và cách xử lý

| Bước/thời điểm | Lỗi quan sát | Cách đã thử | Kết quả/còn thiếu |
|---|---|---|---|
| CP2 | COCO không có lớp `van`; COCO `truck` gộp xe tải, van, pickup | Đánh dấu box truck/bus/car nghi ngờ để rà tay trong CVAT | 27 box đổi sang `van` |
| CP3 | `python` trong PATH trỏ tới alias Microsoft Store; checker lỗi `UnicodeEncodeError` khi in tiếng Việt ra console cp1252 | Dùng Python Miniconda (`C:\ProgramData\miniconda3\python.exe`) với `-X utf8` | Checker đạt 50/50 |
| **TODO** | | | |

## 7. Tự đánh giá theo rubric

**TODO:** đối chiếu [RUBRIC.md](../../RUBRIC.md); phần nào đã có kết quả, phần nào còn thiếu hoặc chưa kiểm được.

## 8. Công cụ AI và tài liệu tham khảo

- YOLO pretrained trên COCO (Ultralytics): tạo nhãn nháp cho 50 ảnh train; toàn bộ nhãn được import vào CVAT để rà/sửa tay (mức chỉnh sửa ghi ở mục 3).
- Claude Code: dọn cấu trúc repo, viết `tools/cvat_xml_to_yolo.ps1` (chuyển định dạng) và `tools/review_labels.ps1` (preview + danh sách box cần rà), dựng khung báo cáo này. Không dùng để vẽ/sửa nhãn hay viết phần phân tích.
- **TODO:** công cụ đã dùng để viết `tools/prelabel_yolo.py`, các công cụ khác, và phần đã tự kiểm tra.
- Nguồn ngoài repo: tài liệu Ultralytics, CVAT. **TODO: bổ sung nếu có.**
