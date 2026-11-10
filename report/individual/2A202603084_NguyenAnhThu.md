# Báo cáo cá nhân — Ngày 2 Object Detection

## 1. Thông tin học viên

- Họ tên:
- MSSV: 2A202603084
- Email: 26ai.thuna@vinuni.edu.vn
- Lớp: K5-L2A
- Link repo bài làm: https://github.com/26aithuna-bot/K5-L2A-DAY02-NguyenAnhThu-2A202603084-ObjectDetection
- Link Colab đã chạy:

## 2. Schema và mini guideline

Chi tiết trong [GUIDELINE_MINI.md](../../GUIDELINE_MINI.md).

| Ảnh | Tình huống | Quyết định |
|---|---|---|
| `drive_019` | Minivan/MPV chở người, thân hộp, nóc cao | `van` |
| `drive_003` | Xe bị cắt ở rìa phải, chỉ còn đầu xe | `truck`, box chạm rìa ảnh |
| `drive_007`, `drive_011`, `drive_012`, `drive_014`, `drive_030`, `drive_031` | Xe rất nhỏ ở xa, vùng tối, không chắc lớp | Không gán |

Cách áp dụng schema và phần cần giảng viên làm rõ:

## 3. Annotation và self-QC

- Số file nhãn train: 50.
- Cách làm: chạy YOLO pretrained COCO ([tools/prelabel_yolo.py](../../tools/prelabel_yolo.py)) để có nhãn nháp, import vào CVAT rồi rà và sửa tay từng ảnh, export "CVAT for images 1.1" và chuyển sang YOLO bằng [tools/cvat_xml_to_yolo.ps1](../../tools/cvat_xml_to_yolo.ps1).
- Model dùng để tạo nhãn nháp:
- Bản khóa so với nhãn nháp: 1090 box gần như giữ nguyên, 55 box chỉnh vị trí/kích thước, 30 box đổi lớp, thêm 2 box, xóa 3 box. Tổng 1177 box (car 1005, truck 40, bus 105, van 27).
- Checker: `ĐẠT cấu trúc: 50/50 file nhãn hợp lệ.`
- Ảnh đã rà bằng mắt:
- Lỗi phát hiện khi rà và cách sửa:
- Commit khóa nhãn: [`7b1b38d`](https://github.com/26aithuna-bot/K5-L2A-DAY02-NguyenAnhThu-2A202603084-ObjectDetection/commit/7b1b38d)

## 4. Gold QC và rework

| Chỉ số | Trước sửa | Sau sửa |
|---|---:|---:|
| TP | 486 | 485 |
| FP | 691 | 685 |
| FN | 167 | 168 |
| Precision | 0.4129 | 0.4145 |
| Recall | 0.7443 | 0.7427 |
| F1 | 0.5311 | 0.5321 |
| mean_iou_of_matches | 0.8484 | 0.8482 |
| passed | false | false |

Trước sửa: commit `7b1b38d`. Sau sửa: commit [`1b30601`](https://github.com/26aithuna-bot/K5-L2A-DAY02-NguyenAnhThu-2A202603084-ObjectDetection/commit/1b30601), kết quả trong `outputs/annotation_evaluation.json`.

Rework: đổi lớp 11 box (vd. `drive_011` #14 truck → car, `drive_016` #5 và #10 truck → van), xóa 7 box (vd. box trùng trên SUV đen ở `drive_020`, khối công trình ở mép phải `drive_041`, hình phản chiếu trong nhà chờ ở `drive_021`), chỉnh lại khoảng 100 box. Còn 1170 box: car 1004, truck 28, bus 105, van 33.

Thời điểm nhận gold:

## 5. Kết quả YOLO

- Runtime: Google Colab, GPU (`device: 0`). Phiên bản Ultralytics và Torch:
- Tham số: giữ nguyên notebook (`yolo26n.pt`, 50 epoch, `imgsz=640`, `batch=-1`, `seed=20260909`).
- Best checkpoint: `/content/Day2-Lab/outputs/yolo26_runs/vehicle_annotation/weights/best.pt`

| Chỉ số trên 10 ảnh eval | Giá trị |
|---|---:|
| Precision | 0.4105 |
| Recall | 0.2303 |
| mAP50 | 0.2723 |
| mAP50–95 | 0.2017 |

- Ảnh prediction trên 10 ảnh eval: [assets/eval_predictions/visuals/](assets/eval_predictions/visuals/), ví dụ [drive_053](assets/eval_predictions/visuals/drive_053.jpg).
- Log train: [results.csv](assets/yolo26_runs/vehicle_annotation/results.csv), [results.png](assets/yolo26_runs/vehicle_annotation/results.png).
- Đánh giá best.pt: [confusion matrix](assets/yolo26_runs/vehicle_eval/confusion_matrix.png), [PR curve](assets/yolo26_runs/vehicle_eval/BoxPR_curve.png).

1. Lớp nào recall thấp nhất? Ảnh nào minh họa?
2. Nếu mAP50 cao nhưng mAP50–95 thấp, cần kiểm điều gì trên box?
3. Lỗi class nào có thể liên quan guideline? Dữ kiện nào hỗ trợ nhận xét?
4. Vì sao không dùng 10 ảnh eval để train? Vai trò validation của chúng trong notebook là gì?

## 6. Khó khăn và cách xử lý

| Bước | Lỗi quan sát | Cách đã thử | Kết quả |
|---|---|---|---|
| CP2 | COCO không có lớp `van`, lớp `truck` của COCO gộp cả xe tải, van, pickup | Rà riêng các box truck/bus/car nghi ngờ trong CVAT | Đổi 27 box sang `van` |
| CP3 | `python` mở alias Microsoft Store; checker lỗi `UnicodeEncodeError` khi in tiếng Việt | Dùng Python của Miniconda với `-X utf8` | Checker đạt 50/50 |
| | | | |

## 7. Tự đánh giá theo rubric

## 8. Công cụ AI và tài liệu tham khảo

- YOLO pretrained COCO (Ultralytics): tạo nhãn nháp, sau đó rà và sửa tay trong CVAT.
- Claude Code: sắp xếp repo, viết script chuyển CVAT XML sang YOLO và script vẽ preview để rà nhãn.
- Tài liệu: Ultralytics, CVAT.
