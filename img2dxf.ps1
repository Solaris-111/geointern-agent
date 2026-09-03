# img2dxf.ps1 — 图片拖上去 -> DXF -> AutoCAD 自动打开
# 用法: 拖图片到 img2dxf.bat / 命令行: powershell -File img2dxf.ps1 "图片"
param(
    [Parameter(Mandatory=$true)][string]$ImagePath,
    [int]$Scale = 2,
    [int]$Blur = 1,
    [float]$Alpha = 0.5,
    [float]$Optimize = 0.3,
    [int]$Turdsize = 5
)

$ErrorActionPreference = "Stop"
$potrace = "D:\geointern-agent\potrace.exe"
$autocad = "C:\Program Files\Autodesk\AutoCAD 2021\acad.exe"
$tmpBmp = "$env:TEMP\potrace_tmp.bmp"
$tmpDxf = "$env:TEMP\potrace_tmp.dxf"

if (-not (Test-Path $ImagePath)) {
    Write-Host "[ERROR] File not found: $ImagePath" -ForegroundColor Red
    Read-Host "Press Enter"; exit 1
}
if (-not (Test-Path $potrace)) {
    Write-Host "[ERROR] potrace.exe not found" -ForegroundColor Red
    Read-Host "Press Enter"; exit 1
}

$dir  = Split-Path $ImagePath -Parent
$name = [IO.Path]::GetFileNameWithoutExtension($ImagePath)
$dxf  = Join-Path $dir "$name.dxf"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Image -> DXF Converter" -ForegroundColor Cyan
Write-Host "  Scale:${Scale}x  Blur:$Blur  Alpha:$Alpha  Opt:$Optimize" -ForegroundColor DarkGray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Input: $ImagePath" -ForegroundColor Yellow

# [1/4] Load and upscale
Write-Host "`n[1/4] Loading + ${Scale}x upscale..." -ForegroundColor Green
Add-Type -AssemblyName System.Drawing
$src = [System.Drawing.Image]::FromFile($ImagePath)
$sw = $src.Width; $sh = $src.Height
$w = $sw * $Scale; $h = $sh * $Scale
Write-Host "  Original: $sw x $sh -> Scaled: $w x $h"

$bmpScaled = New-Object System.Drawing.Bitmap($w, $h)
$g = [System.Drawing.Graphics]::FromImage($bmpScaled)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.DrawImage($src, 0, 0, $w, $h)
$src.Dispose(); $g.Dispose()

# [2/4] Grayscale + blur + binarize
Write-Host "`n[2/4] Grayscale + Blur($Blur) + Binarize..." -ForegroundColor Green

$bmpGray = New-Object System.Drawing.Bitmap($w, $h)
$g = [System.Drawing.Graphics]::FromImage($bmpGray)
$g.Clear([System.Drawing.Color]::White)
$cm = New-Object System.Drawing.Imaging.ColorMatrix
$cm.Matrix00 = 0.299; $cm.Matrix01 = 0.299; $cm.Matrix02 = 0.299
$cm.Matrix10 = 0.587; $cm.Matrix11 = 0.587; $cm.Matrix12 = 0.587
$cm.Matrix20 = 0.114; $cm.Matrix21 = 0.114; $cm.Matrix22 = 0.114
$cm.Matrix33 = 1; $cm.Matrix44 = 1
$attrs = New-Object System.Drawing.Imaging.ImageAttributes
$attrs.SetColorMatrix($cm)
$rect = New-Object System.Drawing.Rectangle(0, 0, $w, $h)
$g.DrawImage($bmpScaled, $rect, 0, 0, $w, $h, [System.Drawing.GraphicsUnit]::Pixel, $attrs)
$bmpScaled.Dispose(); $g.Dispose()

$bmpOut = New-Object System.Drawing.Bitmap($w, $h)

# LockBits for speed
$rect = New-Object System.Drawing.Rectangle(0, 0, $w, $h)
$srcData = $bmpGray.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, $bmpGray.PixelFormat)
$dstData = $bmpOut.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::WriteOnly, $bmpOut.PixelFormat)
$srcPtr = $srcData.Scan0; $dstPtr = $dstData.Scan0
$bpp = [System.Drawing.Image]::GetPixelFormatSize($bmpGray.PixelFormat) / 8
$stride = $srcData.Stride

$srcBytes = New-Object byte[] ($stride * $h)
$dstBytes = New-Object byte[] ($stride * $h)
[System.Runtime.InteropServices.Marshal]::Copy($srcPtr, $srcBytes, 0, $srcBytes.Length)

$r = $Blur
for ($y = 0; $y -lt $h; $y++) {
    for ($x = 0; $x -lt $w; $x++) {
        $sum = 0; $cnt = 0
        for ($dy = -$r; $dy -le $r; $dy++) {
            for ($dx = -$r; $dx -le $r; $dx++) {
                $nx = $x + $dx; $ny = $y + $dy
                if ($nx -ge 0 -and $nx -lt $w -and $ny -ge 0 -and $ny -lt $h) {
                    $pos = $ny * $stride + $nx * $bpp
                    $sum += [int]$srcBytes[$pos]
                    $cnt++
                }
            }
        }
        $avg = [int]($sum / $cnt)
        $color = if ($avg -gt 128) { 255 } else { 0 }
        $pos = $y * $stride + $x * $bpp
        $dstBytes[$pos] = $color
        $dstBytes[$pos + 1] = $color
        $dstBytes[$pos + 2] = $color
        $dstBytes[$pos + 3] = 255
    }
}
[System.Runtime.InteropServices.Marshal]::Copy($dstBytes, 0, $dstPtr, $dstBytes.Length)
$bmpGray.UnlockBits($srcData); $bmpOut.UnlockBits($dstData)
$bmpGray.Dispose()

# Save to TEMP (potrace has issues with non-ASCII paths)
if (Test-Path $tmpBmp) { Remove-Item $tmpBmp -Force }
if (Test-Path $tmpDxf) { Remove-Item $tmpDxf -Force }
$bmpOut.Save($tmpBmp, [System.Drawing.Imaging.ImageFormat]::Bmp)
$bmpOut.Dispose()
Write-Host "  BMP saved to TEMP" -ForegroundColor Gray

# [3/4] potrace vectorization
Write-Host "`n[3/4] potrace vectorization (smooth mode)..." -ForegroundColor Green
$potraceArgs = @("-b", "dxf", "-t", "$Turdsize", "-a", "$Alpha", "-O", "$Optimize", $tmpBmp, "-o", $tmpDxf)
$output = & $potrace @potraceArgs 2>&1
if ($LASTEXITCODE -ne 0 -or -not (Test-Path $tmpDxf)) {
    Write-Host "  potrace error: $output" -ForegroundColor Red
    if (Test-Path $tmpBmp) { Remove-Item $tmpBmp -Force }
    Read-Host "Press Enter"; exit 1
}
Remove-Item $tmpBmp -Force

# Try moving to target; if locked, use timestamp suffix
$finalDxf = $dxf
$moved = $false
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
foreach ($suffix in @("", "_new", "_$ts")) {
    $candidate = if ($suffix) { Join-Path $dir "$($name)$suffix.dxf" } else { $dxf }
    try {
        if (Test-Path $candidate) { Remove-Item $candidate -Force -ErrorAction Stop }
        Move-Item $tmpDxf $candidate -Force -ErrorAction Stop
        $finalDxf = $candidate
        $moved = $true
        if ($suffix) { Write-Host "  (saved as $suffix)" -ForegroundColor DarkGray }
        break
    } catch {
        # file locked, try next suffix
    }
}
if (-not $moved) {
    Write-Host "  ERROR: All filenames locked. Close AutoCAD first." -ForegroundColor Red
    if (Test-Path $tmpDxf) { Remove-Item $tmpDxf -Force }
    Read-Host "Press Enter"; exit 1
}
$dxf = $finalDxf
$size = (Get-Item $dxf).Length
Write-Host "  DXF saved" -ForegroundColor Gray
Write-Host "  Size: $([math]::Round($size/1024, 1)) KB" -ForegroundColor Gray

# [4/4] Open in AutoCAD
Write-Host "`n[4/4] Opening AutoCAD..." -ForegroundColor Green
if (Test-Path $autocad) {
    Start-Process $autocad -ArgumentList "`"$dxf`"" -WindowStyle Normal
    Write-Host "  AutoCAD launched" -ForegroundColor Gray
} else {
    Write-Host "  AutoCAD 2021 not found. DXF is at:" -ForegroundColor Yellow
    Write-Host "  $dxf" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Done!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Start-Sleep -Seconds 2
