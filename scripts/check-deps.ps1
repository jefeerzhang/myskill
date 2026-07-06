<#
.SYNOPSIS
  检查 myskill 仓库中各技能的外部依赖是否就绪。
.DESCRIPTION
  遍历各技能目录，检查 SKILL.md 中提到的外部命令/服务是否可用。
  支持 -Install 参数尝试安装可选依赖。
.EXAMPLE
  .\scripts\check-deps.ps1
  .\scripts\check-deps.ps1 -Install
.PARAMETER Install
  尝试安装可选依赖（需要管理员权限）。
#>

param(
  [switch]$Install
)

$root = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
$results = @()
$hasErrors = $false

function Check-Command($name, $label) {
  $label = if ($label) { $label } else { $name }
  $ok = $null -ne (Get-Command $name -ErrorAction SilentlyContinue)
  if (-not $ok) { $global:hasErrors = $true }
  return $ok
}

function Check-PythonPackage($pkg) {
  $ok = $null -ne (python -c "import $pkg" 2>$null)
  if (-not $ok) { $global:hasErrors = $true }
  return $ok
}

# ===== 通用工具 =====
$results += [PSCustomObject]@{ Skill = "(通用)"; Dep = "git"; Status = $(Check-Command "git") }
$results += [PSCustomObject]@{ Skill = "(通用)"; Dep = "python3 / python"; Status = $(Check-Command "python3") -or $(Check-Command "python") }

# ===== academic-literature-guide-v2 =====
$results += [PSCustomObject]@{ Skill = "academic-literature-guide-v2"; Dep = "mineru-open-api CLI"; Status = $(Check-Command "mineru-open-api") }

# ===== proposal-review-expert =====
$results += [PSCustomObject]@{ Skill = "proposal-review-expert"; Dep = "mineru-open-api CLI (可选)"; Status = $(Check-Command "mineru-open-api") -or "(可选)" }

# ===== coefplot =====
$results += [PSCustomObject]@{ Skill = "coefplot"; Dep = "Stata"; Status = $(Check-Command "stata") -or $(Check-Command "stata-se") -or $(Check-Command "stata-mp") }

# ===== 口播视频制作 =====
$results += [PSCustomObject]@{ Skill = "口播视频制作"; Dep = "HyperFrames CLI"; Status = $(Check-Command "hyperframes") }
$results += [PSCustomObject]@{ Skill = "口播视频制作"; Dep = "FFmpeg"; Status = $(Check-Command "ffmpeg") }

# ===== ragflow-client =====
$results += [PSCustomObject]@{ Skill = "ragflow-client"; Dep = "Python requests"; Status = $(Check-PythonPackage "requests") }

# ===== mem0-memory-flow =====
$results += [PSCustomObject]@{ Skill = "mem0-memory-flow"; Dep = "Python requests"; Status = $(Check-PythonPackage "requests") }

# ===== 输出 =====
Write-Host "`n========== myskill 依赖检查 ==========" -ForegroundColor Cyan
Write-Host "仓库路径: $root`n" -ForegroundColor Gray

$results | Format-Table -Property @{Label="技能"; Width=32}, @{Label="依赖"; Width=28}, @{
  Label="状态"; Width=10; Expression={
    if ($_.Status -eq $true -or $_.Status -match "^\(可选") {
      if ($_.Status -match "^\(可选") { "⚠ 可选" }
      else { "✅ 就绪" }
    } else { "❌ 缺失" }
  }
} -AutoSize

Write-Host "`n"
if ($hasErrors) {
  Write-Host "⚠ 部分依赖未就绪，请参阅各技能 SKILL.md 安装说明。" -ForegroundColor Yellow
} else {
  Write-Host "✅ 核心依赖均已就绪。" -ForegroundColor Green
}

# ===== 安装模式 =====
if ($Install) {
  Write-Host "`n--- 尝试安装缺失依赖 ---" -ForegroundColor Cyan
  if (-not (Check-Command "mineru-open-api")) {
    Write-Host "安装 mineru-open-api..." -ForegroundColor Gray
    npm install -g mineru-open-api 2>&1 | Out-Null
    if (Check-Command "mineru-open-api") { Write-Host "  ✅ mineru-open-api 安装成功" -ForegroundColor Green }
    else { Write-Host "  ❌ 安装失败，请手动执行: npm install -g mineru-open-api" -ForegroundColor Red }
  }
  if (-not (Check-Command "hyperframes")) {
    Write-Host "安装 HyperFrames..." -ForegroundColor Gray
    npm install -g hyperframes 2>&1 | Out-Null
    if (Check-Command "hyperframes") { Write-Host "  ✅ HyperFrames 安装成功" -ForegroundColor Green }
    else { Write-Host "  ❌ 安装失败，请手动执行: npm install -g hyperframes" -ForegroundColor Red }
  }
  if (-not (Check-Command "ffmpeg")) {
    Write-Host "FFmpeg: 请从 https://ffmpeg.org/download.html 手动安装" -ForegroundColor Yellow
  }
}
