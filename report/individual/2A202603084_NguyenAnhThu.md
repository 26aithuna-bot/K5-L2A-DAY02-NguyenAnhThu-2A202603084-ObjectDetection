# Báo cáo cá nhân — Ngày 2 Object Detection

## 1. Thông tin học viên

- Họ tên: Nguyễn Anh Thư
- MSSV: 2A202603084
- Email: 26ai.thuna@vinuni.edu.vn
- Lớp: K5-L2A
- Link repo bài làm: https://github.com/26aithuna-bot/K5-L2A-DAY02-NguyenAnhThu-2A202603084-ObjectDetection
- Link Colab đã chạy: https://colab.research.google.com/gist/26aithuna-bot/caa3ff5c3fb3b1e32282dbc6358366a3/day2_annotation_to_yolo.ipynb

## 2. Schema và mini guideline

Chi tiết trong [GUIDELINE_MINI.md](../../GUIDELINE_MINI.md).

| Ảnh | Tình huống | Quyết định |
|---|---|---|
| `drive_019` | Minivan/MPV chở người, thân hộp, nóc cao | `van` |
| `drive_003` | Xe bị cắt ở rìa phải, chỉ còn đầu xe | `truck`, box chạm rìa ảnh |
| `drive_007` (box #14) | Nóc xe xám bị cắt ở mép trên, nhỏ nhưng còn nhận ra là xe con | `car`, box chạm rìa trên |
| `drive_007`, `drive_011`, `drive_012`, `drive_014`, `drive_030`, `drive_031` | Xe rất nhỏ ở xa, vùng tối, không chắc lớp | Không gán |

Cách áp dụng schema:

- `car` và `van`: van có nóc cao hơn hẳn, mũi ngắn, đuôi gần thẳng đứng, thân liền một khối hộp. SUV/sedan có capo dài, nóc thấp nên là `car`.
- `truck` và `van`/pickup: `truck` có cabin tách khỏi thùng hàng, thùng cao và dài hơn cabin. Pickup có thùng hở thấp, cỡ xe con, nên là `car`. Xe có cabin và khoang sau liền một hộp là `van`.
- Xe nhỏ ở xa: vẫn gán nếu còn nhận ra lớp (vd. nóc xe ở `drive_007`), chỉ bỏ khi không xác định được lớp.

Cần giảng viên làm rõ:

- Thứ tự class ID chính thức. Nhãn eval cho thấy thứ tự `0 car, 1 van, 2 truck, 3 bus`, khác `data.yaml` đang dùng (`0 car, 1 truck, 2 bus, 3 van`). Chi tiết ở mục 5, câu 3.
- Minibus 12–16 chỗ thuộc `van` hay `bus`.
- Ngưỡng kích thước để coi là "quá nhỏ, không gán".
- Xe tải nhỏ thùng kín cỡ van thuộc lớp nào.

## 3. Annotation và self-QC

- Số file nhãn train: 50.
- Cách làm: chạy YOLO pretrained COCO ([tools/prelabel_yolo.py](../../tools/prelabel_yolo.py)) để có nhãn nháp, import vào CVAT rồi rà và sửa tay từng ảnh, export "CVAT for images 1.1" và chuyển sang YOLO bằng [tools/cvat_xml_to_yolo.ps1](../../tools/cvat_xml_to_yolo.ps1).
- Nhãn nháp: YOLO pretrained COCO (Ultralytics), chạy bằng `tools/prelabel_yolo.py`, sau đó import vào CVAT để rà và sửa tay.
- Bản khóa so với nhãn nháp: 1090 box gần như giữ nguyên, 55 box chỉnh vị trí/kích thước, 30 box đổi lớp, thêm 2 box, xóa 3 box. Tổng 1177 box (car 1005, truck 40, bus 105, van 27).
- Checker: `ĐẠT cấu trúc: 50/50 file nhãn hợp lệ.`
- Ảnh đã rà bằng mắt (13 ảnh): `drive_003`, `drive_007`, `drive_009`, `drive_011`, `drive_016`, `drive_019`, `drive_020`, `drive_021`, `drive_026`, `drive_038`, `drive_039`, `drive_041`, `drive_044`.
- Lỗi phát hiện khi rà và cách sửa:
  - Sai lớp do model COCO: COCO không có `van`, lớp `truck` của COCO gộp cả van và pickup. Đổi 30 box sang đúng lớp, đa số sang `van`. Lượt rework đổi thêm 11 box (vd. `drive_016` #5, #10 truck → van; `drive_011` #14 truck → car).
  - Box trùng hoặc vật ngoài schema: xóa box trùng trên SUV đen (`drive_020`), khối công trình ở mép phải (`drive_041`), hình phản chiếu trong nhà chờ (`drive_021`).
  - Box lỏng, lệch, chưa chạm rìa ảnh: chỉnh 55 box ở lượt đầu và khoảng 100 box ở lượt rework.
  - Bỏ sót: thêm 2 box.
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

Thời điểm nhận gold: sau khi khóa nhãn ở commit `7b1b38d` (chiều 10/11/2026).

## 5. Kết quả YOLO

- Runtime: Google Colab, GPU Tesla T4 (15 GB), Python 3.13.16, Ultralytics 8.4.208, torch 2.14.1+cu130. Train 50 epoch hết khoảng 1.4 phút.
- Tham số: giữ nguyên notebook (`yolo26n.pt`, 50 epoch, `imgsz=640`, `batch=-1` được AutoBatch chọn 44, `seed=20260909`). Dữ liệu: 50 ảnh train, 10 ảnh eval làm validation.
- Best checkpoint: `/content/Day2-Lab/outputs/yolo26_runs/vehicle_annotation/weights/best.pt`

| Chỉ số trên 10 ảnh eval | Giá trị |
|---|---:|
| Precision | 0.4105 |
| Recall | 0.2303 |
| mAP50 | 0.2723 |
| mAP50–95 | 0.2017 |

| Lớp | Số ảnh | Số box | Precision | Recall | mAP50 | mAP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| car | 10 | 94 | 0.833 | 0.638 | 0.739 | 0.523 |
| truck | 5 | 5 | 0.675 | 0.200 | 0.239 | 0.206 |
| bus | 2 | 2 | 0.000 | 0.000 | 0.008 | 0.004 |
| van | 6 | 12 | 0.134 | 0.083 | 0.103 | 0.074 |

- Ảnh prediction trên 10 ảnh eval: [assets/eval_predictions/visuals/](assets/eval_predictions/visuals/), ví dụ [drive_053](assets/eval_predictions/visuals/drive_053.jpg).
- Log train: [results.csv](assets/yolo26_runs/vehicle_annotation/results.csv), [results.png](assets/yolo26_runs/vehicle_annotation/results.png).
- Đánh giá best.pt: [confusion matrix](assets/yolo26_runs/vehicle_eval/confusion_matrix.png), [PR curve](assets/yolo26_runs/vehicle_eval/BoxPR_curve.png).

**1. Lớp nào recall thấp nhất? Ảnh nào minh họa?**

- Theo metrics, `bus` có recall thấp nhất (0.000 trên 2 box). Ví dụ [drive_058](assets/eval_predictions/visuals/drive_058.jpg): xe nhỏ màu xanh trắng ở bên phải mang nhãn "bus" nhưng model đoán `car`.
- `van` có recall 0.083 trên 12 box. Các xe buýt mang nhãn "van" ở `drive_052`, `drive_053`, `drive_056`, `drive_058` đều bị model đoán là `bus`. Ví dụ [drive_053](assets/eval_predictions/visuals/drive_053.jpg): xe buýt xanh lá (`bus 0.85`) và xe buýt đỏ trắng (`bus 0.84`).
- Thực chất model vẫn tìm thấy và khoanh đúng xe buýt. Recall thấp là do lệch class ID (câu 3), không phải do bỏ sót.

**2. Nếu mAP50 cao nhưng mAP50–95 thấp, cần kiểm điều gì trên box?**

- Độ sát của box ở các ngưỡng IoU cao: cạnh box có chạm đúng điểm ngoài cùng của xe không, có lấn bóng đổ hoặc nền không, xe bị cắt khung có kéo cạnh chạm rìa ảnh không, xe bị che có khoanh đúng phần nhìn thấy không.
- Cách vẽ có nhất quán giữa train và eval/gold không, ví dụ có lấy cả bánh xe và gương không.
- Nhãn train có hình học tốt: mean IoU 0.848 so với gold. Khoảng cách mAP50 → mAP50–95 của `car` (0.739 → 0.523) có thể đến từ box model trên xe nhỏ ở xa, nơi lệch vài pixel đã làm IoU giảm nhiều.

**3. Lỗi class nào có thể liên quan guideline? Dữ kiện nào hỗ trợ nhận xét?**

- Lỗi chính là lệch thứ tự class ID giữa `data.yaml`/guideline (`0 car, 1 truck, 2 bus, 3 van`) và nhãn eval/gold (`0 car, 1 van, 2 truck, 3 bus`). Dữ kiện:
  - Mọi xe buýt trong nhãn eval đều mang ID 3 ("van"): `drive_052`, `drive_053`, `drive_056`, `drive_058`.
  - Xe van thân hộp trong nhãn eval mang ID 1 ("truck"): xe trắng ở `drive_059`, và `drive_056`.
  - Confusion matrix: 11/12 box "van" bị đoán là `bus`, tức model đoán đúng loại xe nhưng sai ID.
  - mAP50 cao nhất ở epoch 1 (0.272) rồi giảm còn 0.232 ở epoch 50: càng học theo ID của nhãn train thì càng lệch với eval.
  - Gold QC có F1 0.53 dù mean IoU 0.848: box sát nhưng không khớp lớp.
- Ranh giới `car`/`van` trong guideline: SUV và MPV cao dễ lẫn. Confusion matrix có 3 box `car` bị đoán là `van`, và 4/5 box mang ID 1 bị đoán là `car`.
- Mất cân bằng lớp: car 1004 box so với truck 28 và van 33, nên model nghiêng về `car`.

**4. Vì sao không dùng 10 ảnh eval để train? Vai trò validation của chúng trong notebook là gì?**

- Eval phải là dữ liệu model chưa thấy để đo khả năng tổng quát hóa. Dùng eval để train sẽ làm metrics bị thổi phồng, và rubric coi đây là vi phạm.
- Trong notebook, eval vừa là validation (chấm sau mỗi epoch để chọn `best.pt`) vừa là tập báo kết quả cuối. Vì `best.pt` được chọn theo chính tập này nên kết quả cuối hơi lạc quan. Tập chỉ có 10 ảnh, 113 box, riêng `bus` chỉ 2 box, nên số liệu theo từng lớp rất nhiễu.

## 6. Khó khăn và cách xử lý

| Bước | Lỗi quan sát | Cách đã thử | Kết quả |
|---|---|---|---|
| CP2 | COCO không có lớp `van`, lớp `truck` của COCO gộp cả xe tải, van, pickup | Rà riêng các box truck/bus/car nghi ngờ trong CVAT | Đổi 27 box sang `van` |
| CP3 | `python` mở alias Microsoft Store; checker lỗi `UnicodeEncodeError` khi in tiếng Việt | Dùng Python của Miniconda với `-X utf8` | Checker đạt 50/50 |
| CP5 | F1 0.53 dù mean IoU 0.848 | Đối chiếu nhãn eval với `data.yaml` | Phát hiện lệch thứ tự class ID |
| CP6 | `best.pt` rơi vào epoch 1, mAP giảm dần sau đó | Phân tích confusion matrix và ảnh eval | Do lệch ID, cộng thêm dữ liệu ít và mất cân bằng lớp |

## 7. Tự đánh giá theo rubric

Đã đạt:

- Định dạng YOLO: 50/50 file, checker đạt.
- Hình học box: mean IoU 0.848, trên ngưỡng 0.70 và trên mức 0.80.
- Mini guideline: có định nghĩa lớp, quy tắc box và các ca mơ hồ có lý do.
- Pipeline: Colab chạy được, không dùng eval để train, có metrics, ảnh và nhận xét lỗi.

Còn thiếu:

- Gold QC: F1 0.532 < 0.80. Đã có một vòng rework và tìm ra nguyên nhân chính là lệch class ID, nhưng chưa sửa ID và chạy lại.
- Phân lớp nhất quán: bị ảnh hưởng bởi lệch ID giữa nhãn train và gold.
- Đầy đủ vật thể: recall 0.743 so với gold, vẫn còn xe bị bỏ sót.

## 8. Công cụ AI và tài liệu tham khảo

- YOLO pretrained COCO (Ultralytics): tạo nhãn nháp, sau đó rà và sửa tay trong CVAT.
- Claude Code: sắp xếp repo, viết script chuyển CVAT XML sang YOLO và script vẽ preview để rà nhãn, tổng hợp số liệu và chỉnh câu chữ khi đưa câu trả lời vào báo cáo.
- Tài liệu: Ultralytics, CVAT.
