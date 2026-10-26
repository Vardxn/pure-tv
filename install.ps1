# Pure TV one-command installer for Windows (PowerShell).
#   irm https://raw.githubusercontent.com/Vardxn/pure-tv/main/install.ps1 | iex
#   undo:  & ([scriptblock]::Create((irm https://raw.githubusercontent.com/Vardxn/pure-tv/main/install.ps1))) rollback
#   or, from a clone:  .\install.ps1 [tv-ip]        undo:  .\install.ps1 rollback [tv-ip]
# Leave out the IP and the TV is found on the local network. Run through irm | iex, nothing is
# saved as a script file, so PowerShell's execution policy doesn't get in the way.
# Sets up a private Python environment in %USERPROFILE%\.puretv, then runs tools\puretv.py.

# Everything sits in a function so that, run through iex, a failure returns instead of closing the
# PowerShell window, and the settings below stay out of the user's session.
function Install-PureTV {
    $ErrorActionPreference = "Stop"
    $Repo = "Vardxn/pure-tv"
    $HomeDir = if ($env:PURETV_HOME) { $env:PURETV_HOME } else { Join-Path $env:USERPROFILE ".puretv" }

    $py = Get-Command python -ErrorAction SilentlyContinue
    # The python.exe in WindowsApps is the Microsoft Store stub: it opens the Store instead of running.
    if ($py -and $py.Source -like "*\WindowsApps\*") { $py = $null }
    if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
    if (-not $py) {
        Write-Host "Pure TV needs Python 3: install it from https://www.python.org/downloads/ (tick 'Add python.exe to PATH'),"
        Write-Host "then close this window, open a new PowerShell and run the same command again."
        return
    }

    $here = if ($PSScriptRoot) { $PSScriptRoot } else { "" }
    if ($here -and (Test-Path (Join-Path $here "tools\puretv.py"))) {
        $Src = $here
    } else {
        $Src = Join-Path $HomeDir "src"
        if (Test-Path $Src) { Remove-Item -Recurse -Force $Src }
        New-Item -ItemType Directory -Force -Path $HomeDir | Out-Null
        Write-Host "Downloading Pure TV tools..."
        $zip = Join-Path $HomeDir "src.zip"
        Invoke-WebRequest "https://github.com/$Repo/archive/refs/heads/main.zip" -OutFile $zip -UseBasicParsing
        Expand-Archive $zip -DestinationPath $HomeDir -Force
        Move-Item (Get-ChildItem $HomeDir -Directory | Where-Object Name -like "pure-tv-*" | Select-Object -First 1).FullName $Src
        Remove-Item $zip
    }

    $venvPy = Join-Path $HomeDir "venv\Scripts\python.exe"
    if (-not (Test-Path $venvPy)) {
        Write-Host "Setting up a private Python environment in $HomeDir (one time)..."
        & $py.Source -m venv (Join-Path $HomeDir "venv")
    }
    & $venvPy -m pip install -q --disable-pip-version-check -r (Join-Path $Src "tools\requirements.txt")

    # No IP needed: without one, the installer finds the TV on this network itself.
    $argv = @($args)
    if ($argv.Count -eq 0 -or $argv[0] -notin @("install", "rollback", "probe", "find")) {
        $argv = @("install") + $argv
    }
    & $venvPy -I (Join-Path $Src "tools\puretv.py") @argv
}

Install-PureTV @args
