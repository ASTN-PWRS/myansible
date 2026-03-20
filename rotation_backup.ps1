# ================================
# WSL Backup Script (ASAO Version)
# ================================

# === Parameters ===
$BackupDir = "E:\WSL_Backup"     # 保存先
$RetentionDays = 10              # ローテーション日数
$DistroName = "Ubuntu"           # バックアップ対象のディストリ名

# === Functions ===

function Write-Log($msg) {
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    Write-Output "[$timestamp] $msg"
}

function Remove-OldBackups {
    Write-Log "Rotating backups older than $RetentionDays days..."
    Get-ChildItem -Path $BackupDir -Filter "*.tar" |
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$RetentionDays) } |
        ForEach-Object {
            Write-Log "Deleting old backup: $($_.FullName)"
            Remove-Item $_.FullName -Force
        }
}

function Backup-WSL {
    # Ensure backup directory exists
    if (!(Test-Path $BackupDir)) {
        Write-Log "Backup directory not found. Creating: $BackupDir"
        New-Item -ItemType Directory -Path $BackupDir | Out-Null
    }

    # Shutdown WSL
    Write-Log "Shutting down WSL..."
    wsl --shutdown
    Start-Sleep -Seconds 3

    # Create backup filename
    $date = (Get-Date).ToString("yyyyMMdd_HHmmss")
    $BackupFile = Join-Path $BackupDir "$DistroName-$date.tar"

    # Export
    Write-Log "Exporting WSL distro '$DistroName' to $BackupFile ..."
    wsl --export $DistroName $BackupFile

    Write-Log "Backup completed."
}

# === Main ===

Write-Log "=== WSL Backup Script Started ==="

Remove-OldBackups
Backup-WSL

Write-Log "=== WSL Backup Script Finished ==="
