<#
Công cụ hỗ trợ self-QC (CP3): vẽ nhãn YOLO lên ảnh và liệt kê các box nên rà lại bằng mắt.
Không sửa nhãn - chỉ tạo tài liệu để người gán nhãn tự mở ảnh và quyết định.

Chạy từ thư mục gốc repo (PowerShell):
    powershell -ExecutionPolicy Bypass -File tools/review_labels.ps1

Đầu ra (trong outputs/, không bị commit):
    outputs/self_qc/previews/<ảnh>.png   ảnh phóng 2x, mỗi box có số thứ tự = số dòng trong file .txt
    outputs/self_qc/review_list.csv      box cần rà + lý do
    outputs/self_qc/summary.csv          số box/lớp mỗi ảnh và số box cần rà
#>
param(
    [string]$Images = "dataset/images/train",
    [string]$Labels = "dataset/labels/train",
    [string]$Out = "outputs/self_qc",
    [int]$Scale = 2,
    [double]$SmallPx = 12,      # cạnh ngắn hơn ngưỡng này (pixel ảnh gốc) -> kiểm xem có nhận ra lớp không
    [double]$DupIoU = 0.6       # hai box chồng nhau quá ngưỡng -> có thể trùng/gộp
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$inv = [Globalization.CultureInfo]::InvariantCulture
$names = @('car', 'truck', 'bus', 'van')
$colors = @([Drawing.Color]::Lime, [Drawing.Color]::Orange, [Drawing.Color]::DeepSkyBlue, [Drawing.Color]::Magenta)

function IoU($a, $b) {
    $ix = [Math]::Max(0, [Math]::Min($a.x2, $b.x2) - [Math]::Max($a.x1, $b.x1))
    $iy = [Math]::Max(0, [Math]::Min($a.y2, $b.y2) - [Math]::Max($a.y1, $b.y1))
    $i = $ix * $iy; $u = ($a.x2 - $a.x1) * ($a.y2 - $a.y1) + ($b.x2 - $b.x1) * ($b.y2 - $b.y1) - $i
    if ($u -le 0) { 0 } else { $i / $u }
}

$prevDir = Join-Path $Out 'previews'
New-Item -ItemType Directory -Force -Path $prevDir | Out-Null
$review = New-Object System.Collections.Generic.List[object]
$summary = New-Object System.Collections.Generic.List[object]

foreach ($imgFile in Get-ChildItem -LiteralPath $Images -File | Where-Object { $_.Extension -match '^\.(jpe?g|png)$' } | Sort-Object Name) {
    $stem = $imgFile.BaseName
    $src = [Drawing.Image]::FromFile($imgFile.FullName)
    $W = $src.Width; $H = $src.Height
    $boxes = @()
    $lblPath = Join-Path $Labels "$stem.txt"
    if (Test-Path -LiteralPath $lblPath) {
        $n = 0
        foreach ($line in [IO.File]::ReadAllLines((Resolve-Path -LiteralPath $lblPath))) {
            if (-not $line.Trim()) { continue }
            $n++
            $p = $line.Split((' ', "`t"), [StringSplitOptions]::RemoveEmptyEntries)
            $c = [int]$p[0]; $xc = [double]::Parse($p[1], $inv) * $W; $yc = [double]::Parse($p[2], $inv) * $H
            $bw = [double]::Parse($p[3], $inv) * $W; $bh = [double]::Parse($p[4], $inv) * $H
            $boxes += [pscustomobject]@{ idx = $n; cls = $c; x1 = $xc - $bw / 2; y1 = $yc - $bh / 2; x2 = $xc + $bw / 2; y2 = $yc + $bh / 2; w = $bw; h = $bh }
        }
    }

    $flagged = 0
    foreach ($b in $boxes) {
        $why = @()
        if ([Math]::Min($b.w, $b.h) -lt $SmallPx) { $why += 'small: phóng to xem có nhận ra lớp không' }
        if ($b.x1 -le 1 -or $b.y1 -le 1 -or $b.x2 -ge $W - 1 -or $b.y2 -ge $H - 1) { $why += 'edge: phần trong khung có đủ nhận lớp? cạnh có chạm rìa?' }
        if ($b.cls -eq 1) { $why += 'truck: xác nhận không phải van/pickup' }
        if ($b.cls -eq 2) { $why += 'bus: xác nhận không phải van/minibus nhỏ; box có ôm hết thân xe?' }
        if ($b.cls -eq 3) { $why += 'van: xác nhận theo định nghĩa van trong guideline' }
        $ar = $b.w / [Math]::Max($b.h, 1e-6)
        if ($b.cls -eq 0 -and $b.w -ge 25 -and $ar -lt 0.6) { $why += 'car cao/hẹp: kiểm xem có phải van/MPV' }
        foreach ($o in $boxes) {
            if ($o.idx -ne $b.idx -and (IoU $b $o) -ge $DupIoU) { $why += "overlap với box #$($o.idx): trùng hoặc gộp?" }
        }
        if ($why) {
            $flagged++
            $review.Add([pscustomobject]@{ image = $stem; box = $b.idx; class = $names[$b.cls]
                    x1 = [int]$b.x1; y1 = [int]$b.y1; x2 = [int]$b.x2; y2 = [int]$b.y2; reasons = ($why -join ' | ') })
        }
    }
    $summary.Add([pscustomobject]@{ image = $stem; boxes = $boxes.Count
            car = @($boxes | ? cls -eq 0).Count; truck = @($boxes | ? cls -eq 1).Count
            bus = @($boxes | ? cls -eq 2).Count; van = @($boxes | ? cls -eq 3).Count; to_review = $flagged })

    $bmp = New-Object Drawing.Bitmap ($W * $Scale), ($H * $Scale)
    $g = [Drawing.Graphics]::FromImage($bmp)
    $g.InterpolationMode = 'HighQualityBicubic'
    $g.DrawImage($src, 0, 0, $W * $Scale, $H * $Scale)
    $font = New-Object Drawing.Font 'Arial', 9, ([Drawing.FontStyle]::Bold)
    foreach ($b in $boxes) {
        $pen = New-Object Drawing.Pen $colors[$b.cls], 2
        $g.DrawRectangle($pen, [float]($b.x1 * $Scale), [float]($b.y1 * $Scale), [float]($b.w * $Scale), [float]($b.h * $Scale))
        $tag = "$($b.idx) $($names[$b.cls])"
        $sz = $g.MeasureString($tag, $font)
        $ty = [Math]::Max(0, $b.y1 * $Scale - $sz.Height)
        $g.FillRectangle((New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb(170, 0, 0, 0))), [float]($b.x1 * $Scale), [float]$ty, $sz.Width, $sz.Height)
        $g.DrawString($tag, $font, (New-Object Drawing.SolidBrush $colors[$b.cls]), [float]($b.x1 * $Scale), [float]$ty)
        $pen.Dispose()
    }
    $bmp.Save((Join-Path (Resolve-Path $prevDir) "$stem.png"), [Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose(); $src.Dispose()
}

$review | Export-Csv -LiteralPath (Join-Path $Out 'review_list.csv') -NoTypeInformation -Encoding UTF8
$summary | Sort-Object to_review -Descending | Export-Csv -LiteralPath (Join-Path $Out 'summary.csv') -NoTypeInformation -Encoding UTF8
$tot = ($summary | Measure-Object boxes -Sum).Sum
Write-Output "Ảnh: $($summary.Count) | box: $tot | box cần rà: $($review.Count) | xem $Out"
