param(
    [Parameter(Mandatory = $true)][string]$Xml,
    [string]$Images = "dataset/images/train",
    [string]$Out = "dataset/labels/train",
    [switch]$Overwrite
)
$ErrorActionPreference = 'Stop'
$inv = [Globalization.CultureInfo]::InvariantCulture
$schema = @{ car = 0; truck = 1; bus = 2; van = 3 }

[xml]$doc = Get-Content -LiteralPath $Xml -Raw -Encoding UTF8
$byName = @{}
foreach ($img in $doc.annotations.image) { $byName[[IO.Path]::GetFileNameWithoutExtension($img.name)] = $img }

$stems = Get-ChildItem -LiteralPath $Images -File | Where-Object { $_.Extension -match '^\.(jpe?g|png)$' } |
    ForEach-Object { $_.BaseName } | Sort-Object
if (-not $stems) { throw "Không tìm thấy ảnh trong $Images" }
$missing = $stems | Where-Object { -not $byName.ContainsKey($_) }
if ($missing) { throw "annotations.xml thiếu $($missing.Count) ảnh: $($missing -join ', ')" }
$extra = $byName.Keys | Where-Object { $stems -notcontains $_ }
if ($extra) { throw "annotations.xml có ảnh không thuộc $Images (có thể là eval?): $($extra -join ', ')" }

New-Item -ItemType Directory -Force -Path $Out | Out-Null
if (-not $Overwrite) {
    $exists = $stems | Where-Object { Test-Path -LiteralPath (Join-Path $Out "$_.txt") }
    if ($exists) { throw "$($exists.Count) file nhãn đã tồn tại trong $Out (vd. $($exists[0]).txt). Thêm -Overwrite nếu chắc chắn." }
}

$utf8 = New-Object System.Text.UTF8Encoding($false)
$counts = @{ 0 = 0; 1 = 0; 2 = 0; 3 = 0 }
$skipped = 0
foreach ($stem in $stems) {
    $img = $byName[$stem]
    $W = [double]::Parse($img.width, $inv); $H = [double]::Parse($img.height, $inv)
    $other = @($img.ChildNodes | Where-Object { $_.NodeType -eq 'Element' -and $_.Name -ne 'box' })
    if ($other) { throw "$stem có shape không phải box ($($other[0].Name)); lab chỉ dùng bounding box." }
    $lines = New-Object System.Collections.Generic.List[string]
    foreach ($b in $img.box) {
        if (-not $schema.ContainsKey($b.label)) { throw "$stem có label '$($b.label)' ngoài schema car/truck/bus/van." }
        if ($b.rotation -and [double]::Parse($b.rotation, $inv) -ne 0) { throw "$stem có box xoay; hãy bỏ rotation trong CVAT." }
        $x1 = [Math]::Min($W, [Math]::Max(0, [double]::Parse($b.xtl, $inv)))
        $y1 = [Math]::Min($H, [Math]::Max(0, [double]::Parse($b.ytl, $inv)))
        $x2 = [Math]::Min($W, [Math]::Max(0, [double]::Parse($b.xbr, $inv)))
        $y2 = [Math]::Min($H, [Math]::Max(0, [double]::Parse($b.ybr, $inv)))
        $bw = ($x2 - $x1) / $W; $bh = ($y2 - $y1) / $H
        if ($bw -le 0 -or $bh -le 0) { $skipped++; Write-Warning "$stem bỏ box rỗng sau khi kẹp biên"; continue }
        $cls = $schema[$b.label]
        $counts[$cls]++
        $lines.Add(('{0} {1} {2} {3} {4}' -f $cls,
            ((($x1 + $x2) / 2 / $W).ToString('F6', $inv)), ((($y1 + $y2) / 2 / $H).ToString('F6', $inv)),
            ($bw.ToString('F6', $inv)), ($bh.ToString('F6', $inv))))
    }
    $text = if ($lines.Count) { ($lines -join "`n") + "`n" } else { "" }
    [IO.File]::WriteAllText((Join-Path (Resolve-Path $Out) "$stem.txt"), $text, $utf8)
}
$total = ($counts.Values | Measure-Object -Sum).Sum
Write-Output ("Đã ghi {0} file vào {1} | car={2} truck={3} bus={4} van={5} | tổng={6} | bỏ={7}" -f `
    $stems.Count, $Out, $counts[0], $counts[1], $counts[2], $counts[3], $total, $skipped)
