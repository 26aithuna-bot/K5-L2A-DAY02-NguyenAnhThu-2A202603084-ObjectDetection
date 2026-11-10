#!/usr/bin/env python3
"""
Pre-label (gán nhãn nháp) cho 50 ảnh train bằng YOLO pretrained trên COCO,
xuất đúng định dạng YOLO detection của lab Day 2 (car=0, truck=1, bus=2, van=3).

QUAN TRỌNG: đây chỉ là NHÃN NHÁP. Mọi box phải được mở lại và sửa tay trong
CVAT / Label Studio / Roboflow trước khi khóa nhãn. COCO không có lớp "van",
và COCO "truck" gộp cả xe tải, van và xe bán tải, nên các box truck đều bị
đánh dấu cần rà lại.

Chạy từ thư mục gốc repo lab:
    python3 tools/prelabel_yolo.py
    python3 tools/prelabel_yolo.py --model yolo11x.pt --conf 0.25 --device 0

Đầu ra:
    outputs/prelabel_review/labels/<basename>.txt  nhãn nháp, 5 cột, normalized
    outputs/prelabel_review/review_boxes.csv   từng box + cờ cần rà
    outputs/prelabel_review/review_images.csv  số box mỗi ảnh + số cờ
    outputs/prelabel_review/previews/*.jpg     ảnh vẽ box để rà nhanh
    outputs/prelabel_review/cvat_yolo11.zip    import vào CVAT (YOLO 1.1)
(`outputs/` đã nằm trong .gitignore của lab nên không bị commit.)
"""
from __future__ import annotations

import argparse
import csv
import shutil
import sys
import zipfile
from pathlib import Path

# Schema bắt buộc của lab (data.yaml). Không đổi thứ tự.
SCHEMA = {0: "car", 1: "truck", 2: "bus", 3: "van"}

# COCO id -> schema id. Chỉ giữ 3 lớp xe bốn bánh có trong COCO.
# COCO 3 (motorcycle), 1 (bicycle), 0 (person)... bị bỏ qua theo GUIDE.md.
COCO_TO_SCHEMA = {2: 0, 7: 1, 5: 2}  # car->car, truck->truck, bus->bus

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
COLORS = {0: (0, 200, 0), 1: (0, 120, 255), 2: (255, 60, 60), 3: (200, 0, 200)}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--images", default="dataset/images/train", help="thư mục 50 ảnh train")
    p.add_argument("--labels", default="outputs/prelabel_review/labels", help="nơi ghi nhãn nháp (KHÔNG ghi thẳng vào dataset/labels/train)")
    p.add_argument("--review-dir", default="outputs/prelabel_review", help="nơi ghi CSV/preview/zip CVAT")
    p.add_argument("--model", default="yolo26x.pt", help="checkpoint COCO (yolo26x.pt, yolo11x.pt, ...)")
    p.add_argument("--conf", type=float, default=0.25, help="ngưỡng confidence giữ box")
    p.add_argument("--review-conf", type=float, default=0.50, help="box dưới ngưỡng này bị gắn cờ low_conf")
    p.add_argument("--iou", type=float, default=0.60, help="ngưỡng IoU cho NMS")
    p.add_argument("--imgsz", type=int, default=1280, help="kích thước suy luận; ảnh CCTV có nhiều xe nhỏ nên để lớn")
    p.add_argument("--min-px", type=float, default=8.0, help="bỏ box có cạnh ngắn hơn số pixel này")
    p.add_argument("--device", default=None, help="'0' cho GPU, 'cpu', hoặc để trống tự chọn")
    p.add_argument("--overwrite", action="store_true", help="cho phép ghi đè file nhãn đã có")
    p.add_argument("--no-preview", action="store_true", help="không vẽ ảnh preview")
    p.add_argument("--no-cvat", action="store_true", help="không tạo zip import CVAT")
    return p.parse_args()


def clamp01(v: float) -> float:
    return min(1.0, max(0.0, v))


def to_yolo_line(cls: int, x1: float, y1: float, x2: float, y2: float, w: int, h: int) -> str | None:
    """Pixel xyxy -> dòng YOLO normalized, đã kẹp trong ảnh (box chạm rìa khi bị cắt khung)."""
    x1, x2 = clamp01(x1 / w), clamp01(x2 / w)
    y1, y2 = clamp01(y1 / h), clamp01(y2 / h)
    bw, bh = x2 - x1, y2 - y1
    if bw <= 0 or bh <= 0:
        return None
    xc, yc = x1 + bw / 2, y1 + bh / 2
    return f"{cls} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}"


def flags_for(cls: int, conf: float, x1, y1, x2, y2, w, h, review_conf: float) -> list[str]:
    f = []
    if cls == 1:
        # COCO truck gộp xe tải, van, xe bán tải: phải tự quyết truck / van / car.
        f.append("check_truck_vs_van_or_pickup")
    if cls == 0 and conf < 0.80:
        # Minivan thường bị COCO gọi là car: rà xem có phải van không.
        f.append("check_car_vs_van")
    if cls == 2 and conf < 0.80:
        # Minibus/van chở khách dễ lẫn với bus.
        f.append("check_bus_vs_van_minibus")
    if conf < review_conf:
        f.append("low_conf")
    edge = 2  # px
    if x1 <= edge or y1 <= edge or x2 >= w - edge or y2 >= h - edge:
        f.append("touches_edge")
    if min(x2 - x1, y2 - y1) < 20:
        f.append("small")
    return f


def write_cvat_zip(img_paths: list[Path], labels_dir: Path, out_zip: Path) -> None:
    """Zip theo định dạng CVAT 'YOLO 1.1' để import nhãn nháp vào task CVAT."""
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("obj.names", "\n".join(SCHEMA[i] for i in range(4)) + "\n")
        z.writestr(
            "obj.data",
            "classes = 4\ntrain = data/train.txt\nnames = data/obj.names\nbackup = backup/\n",
        )
        z.writestr("train.txt", "\n".join(f"data/obj_train_data/{p.name}" for p in img_paths) + "\n")
        for p in img_paths:
            z.write(labels_dir / f"{p.stem}.txt", f"obj_train_data/{p.stem}.txt")


def main() -> int:
    a = parse_args()
    images_dir, labels_dir, review_dir = Path(a.images), Path(a.labels), Path(a.review_dir)

    if not images_dir.is_dir():
        sys.exit(f"Không thấy thư mục ảnh: {images_dir}. Hãy chạy từ thư mục gốc repo lab.")
    if "eval" in images_dir.parts:
        sys.exit("Không pre-label tập eval: eval là validation, không thuộc phần bạn gán nhãn.")

    img_paths = sorted(p for p in images_dir.iterdir() if p.suffix.lower() in IMG_EXTS)
    if not img_paths:
        sys.exit(f"Không có ảnh trong {images_dir}")
    if len(img_paths) != 50:
        print(f"[cảnh báo] tìm thấy {len(img_paths)} ảnh, lab yêu cầu 50.")

    labels_dir.mkdir(parents=True, exist_ok=True)
    existing = [p for p in img_paths if (labels_dir / f"{p.stem}.txt").exists()]
    if existing and not a.overwrite:
        sys.exit(
            f"{len(existing)} file nhãn đã tồn tại trong {labels_dir} (vd. {existing[0].stem}.txt). "
            "Thêm --overwrite nếu chắc chắn muốn ghi đè."
        )

    try:
        from ultralytics import YOLO
    except ImportError:
        sys.exit("Thiếu ultralytics. Cài bằng: pip install -U ultralytics")

    model = YOLO(a.model)
    names = model.names
    for cid, expected in ((2, "car"), (5, "bus"), (7, "truck")):
        if names.get(cid) != expected:
            sys.exit(f"Model '{a.model}' không theo id COCO ({cid} = {names.get(cid)!r}). Dùng checkpoint COCO gốc.")

    preview_dir = review_dir / "previews"
    review_dir.mkdir(parents=True, exist_ok=True)
    if not a.no_preview:
        preview_dir.mkdir(parents=True, exist_ok=True)

    box_rows, img_rows = [], []
    totals = {k: 0 for k in SCHEMA}

    for i, img_path in enumerate(img_paths, 1):
        res = model.predict(
            source=str(img_path),
            conf=a.conf,
            iou=a.iou,
            imgsz=a.imgsz,
            classes=list(COCO_TO_SCHEMA),
            agnostic_nms=True,  # tránh một xe ra 2 box car+truck chồng nhau
            device=a.device,
            verbose=False,
        )[0]
        h, w = res.orig_shape
        lines, n_flag = [], 0
        draw = []

        for b in res.boxes:
            coco_id = int(b.cls.item())
            conf = float(b.conf.item())
            x1, y1, x2, y2 = (float(v) for v in b.xyxy[0].tolist())
            if min(x2 - x1, y2 - y1) < a.min_px:
                continue
            cls = COCO_TO_SCHEMA[coco_id]
            line = to_yolo_line(cls, x1, y1, x2, y2, w, h)
            if line is None:
                continue
            f = flags_for(cls, conf, x1, y1, x2, y2, w, h, a.review_conf)
            n_flag += bool(f)
            totals[cls] += 1
            lines.append(line)
            draw.append((cls, conf, x1, y1, x2, y2, bool(f)))
            box_rows.append({
                "image": img_path.name, "box_idx": len(lines) - 1, "class_id": cls,
                "class": SCHEMA[cls], "coco_class": names[coco_id], "conf": f"{conf:.3f}",
                "x1": round(x1), "y1": round(y1), "x2": round(x2), "y2": round(y2),
                "flags": ";".join(f),
            })

        # Ảnh không có xe hợp lệ vẫn phải có file .txt rỗng.
        (labels_dir / f"{img_path.stem}.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        img_rows.append({"image": img_path.name, "width": w, "height": h, "n_boxes": len(lines), "n_flagged": n_flag})

        if not a.no_preview:
            import cv2
            im = res.orig_img.copy()
            for cls, conf, x1, y1, x2, y2, flagged in draw:
                c = COLORS[cls]
                cv2.rectangle(im, (int(x1), int(y1)), (int(x2), int(y2)), c, 1)
                tag = f"{SCHEMA[cls]} {conf:.2f}{' ?' if flagged else ''}"
                cv2.putText(im, tag, (int(x1), max(10, int(y1) - 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.35, c, 1, cv2.LINE_AA)
            cv2.imwrite(str(preview_dir / f"{img_path.stem}.jpg"), im)

        print(f"[{i:02d}/{len(img_paths)}] {img_path.name}: {len(lines)} box, {n_flag} cần rà")

    with open(review_dir / "review_boxes.csv", "w", newline="", encoding="utf-8") as fh:
        cols = ["image", "box_idx", "class_id", "class", "coco_class", "conf", "x1", "y1", "x2", "y2", "flags"]
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        wr.writerows(box_rows)
    with open(review_dir / "review_images.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=["image", "width", "height", "n_boxes", "n_flagged"])
        wr.writeheader()
        wr.writerows(sorted(img_rows, key=lambda r: -r["n_flagged"]))

    if not a.no_cvat:
        write_cvat_zip(img_paths, labels_dir, review_dir / "cvat_yolo11.zip")

    n_box = sum(totals.values())
    n_flag_box = sum(1 for r in box_rows if r["flags"])
    print("\n=== Tóm tắt nhãn nháp ===")
    print(f"Ảnh: {len(img_paths)} | file nhãn: {len(img_rows)} | ảnh rỗng: {sum(r['n_boxes'] == 0 for r in img_rows)}")
    print(" | ".join(f"{SCHEMA[k]}={v}" for k, v in totals.items()) + f" | tổng={n_box}")
    print(f"Box cần rà: {n_flag_box}/{n_box}  (xem {review_dir / 'review_boxes.csv'})")
    print("van=0 là bình thường: COCO không có lớp van, bạn phải tự đổi class khi rà tay.")
    print("Bước tiếp: import vào công cụ annotation, sửa tay toàn bộ, export ra dataset/labels/train/ rồi chạy tools/check_yolo_labels.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
