
function Convert-ToWslPath {
    param([string]$Path = $PWD)

    if ($Path -match '^([A-Za-z]):') {
        $drive = $Matches[1].ToLower()
        return ($Path -replace '^([A-Za-z]):', "/mnt/$drive") -replace '\\','/'
    }
}

$basepath = Convert-ToWslPath
[string[]]$ary = @()

try {
  wsl --shutdown
  if (wsl -l -q | Select-String -SimpleMatch "Ubuntu") {
    wsl --unregister Ubuntu *> $null
    $ary += "✅ Unregister Ubuntu"
  }
  wsl --import Ubuntu E:\wsl\Ubuntu $PWD\image\Ubuntu-Dev.tar --version 2
  $ary += "✅ Import image"
  # --- 必要なディレクトリを WSL にコピー ---
  wsl bash -lc "rm -fr ~/ansible  && cp -r '$basepath/ansible-app' ~/ansible"
  wsl bash -lc "rm -fr ~/apps && cp -r '$basepath/apps/ocr' ~/projects"
  $ary += "✅ Copy file"
  # --- myansible に移動して ansible-playbook を実行 ---
  wsl -d Ubuntu bash -lc "cd ~/ansible && ansible-playbook site.yml --tags 'install'"
  $exit = $LASTEXITCODE
  # 正常終了なら export
  if ($exit -eq 0) {
    Write-Host "Ansible 正常終了"
    $ary += "✅ Execute Ansible"
  } else {
    Write-Host "Ansible が失敗したため export は実行しません (exit=$exit)"
  }  
}
catch {
  $ary += "❌ Error"
}

$ary
