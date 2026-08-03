#Requires -Version 5
<#
  部署腳本：build 前端並部署到 Firebase Hosting。
  用法（在 D:\program\vocabbatcher 底下執行）：
    .\deploy.ps1
  若遇到「未經數位簽署的指令碼」錯誤，改用：
    powershell -ExecutionPolicy Bypass -File .\deploy.ps1
#>

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

try {
    Write-Host '== 1/2 建置前端 (npm run build) ==' -ForegroundColor Cyan
    Set-Location (Join-Path $root 'exam-vocab-batcher')
    npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "npm run build 失敗 (exit code $LASTEXITCODE)"
    }

    Write-Host '== 2/2 部署到 Firebase Hosting ==' -ForegroundColor Cyan
    Set-Location $root
    firebase deploy --only hosting
    if ($LASTEXITCODE -ne 0) {
        throw "firebase deploy 失敗 (exit code $LASTEXITCODE)"
    }

    Write-Host '== 部署完成 ==' -ForegroundColor Green
}
finally {
    Set-Location $root
}
