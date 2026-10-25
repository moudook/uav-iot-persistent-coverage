# overnight_arms.ps1
$ErrorActionPreference = "Continue"
$log = "C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\ml_impl\analysis\overnight.log"
$lock = "C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\ml_impl\analysis\overnight.lock"
# guard against duplicate triggers (schtasks + detached process both armed)
if (Test-Path $lock) {
    "Another overnight run already holds the lock ($lock). Exiting." | Tee-Object -FilePath $log -Append
    exit 0
}
New-Item -ItemType File -Path $lock -Force | Out-Null
$target = (Get-Date).Date.AddDays(1)  # midnight (00:00 next day)
# target is tomorrow 00:00; always in the future
$wait = ($target - (Get-Date)).TotalSeconds
"Armed at $(Get-Date). Sleeping $wait seconds until $target." | Tee-Object -FilePath $log
Start-Sleep -Seconds ([int]$wait)
"=== $(Get-Date) starting credit arm ===" | Tee-Object -FilePath $log -Append
$env:OPENBLAS_NUM_THREADS="1"; $env:OMP_NUM_THREADS="1"; $env:MKL_NUM_THREADS="1"; $env:UAV_DEVICE="cpu"
& "C:\Users\gbust\AppData\Local\Programs\Python\Python313\python.exe" -u "C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\ml_impl\analysis\ab_credit.py" --episodes 25 --seeds 8 --eval-seeds 5 *>> $log 2>&1
"=== $(Get-Date) credit done; starting energy arm ===" | Tee-Object -FilePath $log -Append
& "C:\Users\gbust\AppData\Local\Programs\Python\Python313\python.exe" -u "C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\ml_impl\analysis\ab_energy_management.py" --episodes 25 --seeds 8 --eval-seeds 5 *>> $log 2>&1
"=== $(Get-Date) arms done; running fill_tokens ===" | Tee-Object -FilePath $log -Append
& "C:\Users\gbust\AppData\Local\Programs\Python\Python313\python.exe" -u "C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\ml_impl\analysis\fill_tokens.py" *>> $log 2>&1
"=== $(Get-Date) running gate ===" | Tee-Object -FilePath $log -Append
& "C:\Users\gbust\AppData\Local\Programs\Python\Python313\python.exe" -u "C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\ml_impl\analysis\final_checks.py" *>> $log 2>&1
"=== $(Get-Date) compiling REPORT.tex (3 passes) ===" | Tee-Object -FilePath $log -Append
Push-Location "C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1"
for ($i=1; $i -le 3; $i++) {
    & pdflatex -interaction=nonstopmode "REPORT.tex" *>> $log 2>&1
}
Pop-Location
"=== $(Get-Date) overnight complete ===" | Tee-Object -FilePath $log -Append
# Persist a completion marker so the result survives even if the agent is
# offline when the run finishes.  The arm JSONs, the filled text and the
# compiled PDF are already on disk; this marker is the human-readable
# summary of what happened.
$marker = "C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1\ml_impl\analysis\OVERNIGHT_DONE.txt"
$tail = Get-Content $log -Tail 40 -ErrorAction SilentlyContinue
@(
  "OVERNIGHT RUN COMPLETE"
  "Finished: $(Get-Date)"
  "Lock removed; task can be re-run."
  ""
  "Last 40 lines of overnight.log:"
  ($tail -join "`n")
) | Set-Content -Path $marker -Encoding utf8
Remove-Item $lock -ErrorAction SilentlyContinue
