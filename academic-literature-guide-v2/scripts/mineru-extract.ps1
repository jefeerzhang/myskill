# MinerU 自动化 PDF 提取脚本
# 用法：.\mineru-extract.ps1 -InputPath "C:\path\to\file.pdf" -OutputDir "./mineru_extract/output"

param(
    [Parameter(Mandatory=$true)]
    [string]$InputPath,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputDir,
    
    [switch]$ForceExtract  # 强制使用 extract 模式
)

# 检查 MinerU 是否安装
Write-Host "正在检查 MinerU 安装..." -ForegroundColor Cyan
try {
    $mineruVersion = mineru-open-api version 2>&1
    Write-Host "✓ MinerU 已安装：$mineruVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ MinerU 未安装！" -ForegroundColor Red
    Write-Host "请运行以下命令安装：" -ForegroundColor Yellow
    Write-Host "  npm install -g mineru-open-api" -ForegroundColor White
    exit 1
}

# 检查输入文件是否存在
if (-not (Test-Path $InputPath)) {
    Write-Host "✗ 文件不存在：$InputPath" -ForegroundColor Red
    exit 1
}

# 获取文件信息
$file = Get-Item $InputPath
$fileSizeMB = [math]::Round($file.Length / 1MB, 2)
Write-Host "文件信息：" -ForegroundColor Cyan
Write-Host "  名称：$($file.Name)"
Write-Host "  大小：$fileSizeMB MB"

# 自动选择提取模式
$useExtract = $false
if ($ForceExtract) {
    $useExtract = $true
    Write-Host "→ 强制使用 extract 模式（用户指定）" -ForegroundColor Yellow
} elseif ($fileSizeMB -gt 10) {
    $useExtract = $true
    Write-Host "→ 文件超过 10MB，使用 extract 模式" -ForegroundColor Yellow
} else {
    Write-Host "→ 使用 flash-extract 模式（快速）" -ForegroundColor Green
}

# 生成输出目录
if (-not $OutputDir) {
    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
    # 清理文件名中的特殊字符
    $safeName = $fileName -replace '[^\w\u4e00-\u9fa5\-]', '_'
    $safeName = $safeName -replace '_+', '_'
    
    # 生成 MD5 hash（前 6 位）
    $hash = [System.BitConverter]::ToString(
        [System.Security.Cryptography.MD5]::Create().ComputeHash(
            [System.Text.Encoding]::UTF8.GetBytes($file.FullName)
        )
    ).Replace('-', '').Substring(0, 6).ToLower()
    
    $OutputDir = ".\mineru_extract\$($safeName)_$hash"
}

# 创建输出目录
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    Write-Host "✓ 创建输出目录：$OutputDir" -ForegroundColor Green
}

# 执行提取
Write-Host "`n开始提取..." -ForegroundColor Cyan
if ($useExtract) {
    Write-Host "命令：mineru-open-api extract `"$InputPath`" -o `"$OutputDir`" --model vlm --verbose" -ForegroundColor Gray
    mineru-open-api extract $InputPath -o $OutputDir --model vlm --verbose
} else {
    Write-Host "命令：mineru-open-api flash-extract `"$InputPath`" -o `"$OutputDir`" --verbose" -ForegroundColor Gray
    mineru-open-api flash-extract $InputPath -o $OutputDir --verbose
}

# 检查提取结果
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✓ 提取成功！" -ForegroundColor Green
    
    # 列出生成的文件
    $outputFiles = Get-ChildItem $OutputDir
    Write-Host "输出文件：" -ForegroundColor Cyan
    foreach ($f in $outputFiles) {
        if ($f.PSIsContainer) {
            Write-Host "  📁 $($f.Name)"
        } else {
            $sizeKB = [math]::Round($f.Length / 1KB, 2)
            Write-Host "  📄 $($f.Name) ($sizeKB KB)"
        }
    }
    
    Write-Host "`n输出目录：$OutputDir" -ForegroundColor Green
} else {
    Write-Host "`n✗ 提取失败！请检查错误信息。" -ForegroundColor Red
    Write-Host "可能的原因：" -ForegroundColor Yellow
    Write-Host "  1. 文件加密或损坏"
    Write-Host "  2. MinerU API 配额用尽"
    Write-Host "  3. 网络连接问题"
    Write-Host "尝试解决方案："
    Write-Host "  - 检查文件是否可以正常打开"
    Write-Host "  - 等待几分钟后重试"
    Write-Host "  - 检查 MinerU Token 是否有效（运行：mineru-open-api auth --verify）"
    exit 1
}
