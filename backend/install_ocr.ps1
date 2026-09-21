$ErrorActionPreference = "Stop"
$BinDir = "e:\AI_Second_Brain_DAU\backend\bin"

if (-not (Test-Path $BinDir)) {
    New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
}

Write-Host "1. Dang tai Poppler..."
$PopplerUrl = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.07.0-0/Release-24.07.0-0.zip"
$PopplerZip = "$BinDir\poppler.zip"
Invoke-WebRequest -Uri $PopplerUrl -OutFile $PopplerZip
Write-Host "Dang giai nen Poppler..."
Expand-Archive -Path $PopplerZip -DestinationPath $BinDir -Force
Remove-Item $PopplerZip -Force
if (Test-Path "$BinDir\poppler-24.07.0") {
    Rename-Item "$BinDir\poppler-24.07.0" "$BinDir\poppler" -Force
}

Write-Host "2. Dang tai Tesseract Installer..."
$TessUrl = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
$TessExe = "$BinDir\tesseract-setup.exe"
$TessDir = "$BinDir\Tesseract-OCR"
Invoke-WebRequest -Uri $TessUrl -OutFile $TessExe
Write-Host "Dang cai dat Tesseract vao thu muc cuc bo (khoang 1-2 phut)..."
Start-Process -FilePath $TessExe -ArgumentList "/S", "/D=$TessDir" -Wait -NoNewWindow
Remove-Item $TessExe -Force

Write-Host "3. Dang tai goi ngon ngu Tieng Viet (vie.traineddata) cho Tesseract..."
$VieUrl = "https://github.com/tesseract-ocr/tessdata/raw/main/vie.traineddata"
$TessDataDir = "$TessDir\tessdata"
Invoke-WebRequest -Uri $VieUrl -OutFile "$TessDataDir\vie.traineddata"

Write-Host "Hoan tat cai dat Tesseract va Poppler tai $BinDir!"
