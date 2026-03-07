# myansible

```setup-wsl.ps1
# 1. WSL2 を有効化

wsl --install -d Ubuntu

# 2. WSL2 の設定ファイルを配置（メモリ制限など）

$wslConfig = @"
[wsl2]
memory=6GB
processors=4
swap=0
localhostForwarding=true
"@
Set-Content -Path "$env:USERPROFILE\.wslconfig" -Value $wslConfig

# 3. Ubuntu を初回起動（ユーザー作成）

wsl -d Ubuntu -- echo "WSL2 初期起動完了"

# 4. Ansible と Git をインストール

wsl -d Ubuntu -- sudo apt update
wsl -d Ubuntu -- sudo apt install ansible git -y

# 5. あなたの ansible リポジトリを clone

wsl -d Ubuntu -- git clone https://github.com/asao/ansible ~/ansible
```

```persist-wsl.ps1
# WSL2 永続起動スクリプト
$taskName = "WSL2-Persist"

# 既存タスクがあれば削除
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# アクション：WSL を root で起動し sleep infinity
$action = New-ScheduledTaskAction -Execute "wsl.exe" -Argument "-u root sleep infinity"

# トリガー：Windows 起動時
$trigger = New-ScheduledTaskTrigger -AtStartup

# 実行権限：最高権限
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -RunLevel Highest

# タスク登録
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal

Write-Host "WSL2 永続化タスクを登録しました。"
```

タスクスケジューラを管理者権限で起動
ユーザー：SYSTEM

powershell -ExecutionPolicy Bypass -File persist-wsl.ps1
