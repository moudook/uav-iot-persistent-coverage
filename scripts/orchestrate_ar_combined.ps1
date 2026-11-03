$ErrorActionPreference = "Continue"
$project = "C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1"
Set-Location $project

# Wait for AR training (3 seeds) to finish
$arJson = @()
foreach ($s in 0..2) { $arJson += "ml_impl/runs/exp_ar_eval/seed_${s}.json" }
$deadline = (Get-Date).AddHours(4)
$arDone = $false
while ((Get-Date) -lt $deadline) {
    $done = $true
    foreach ($j in $arJson) { if (-not (Test-Path $j)) { $done = $false; break } }
    if ($done) { $arDone = $true; break }
    Start-Sleep -Seconds 60
}
Write-Host "AR training done: $arDone"

# AR held-out eval (corrected protocol: repeat=1 at eval, 2000 steps)
if ($arDone) {
    Write-Host "Running AR held-out eval..."
    python scripts/eval_ckpt.py --tag exp_ar_eval --eval-offset 1000 --eval-seeds 20
}

# Wait for combined small_battery (3 seeds)
$cbJson = @()
foreach ($s in 0..2) { $cbJson += "ml_impl/runs/innov_currid_energy_anchor/seed_${s}.json" }
$cbDone = $false
while ((Get-Date) -lt $deadline) {
    $done = $true
    foreach ($j in $cbJson) { if (-not (Test-Path $j)) { $done = $false; break } }
    if ($done) { $cbDone = $true; break }
    Start-Sleep -Seconds 60
}
Write-Host "Combined small_battery training done: $cbDone"

if ($cbDone) {
    Write-Host "Running combined small_battery stress eval..."
    # evaluate on small_battery regime with the anchor config restored
    python scripts/eval_stress.py --tag innov_currid_energy_anchor --only small_battery --out ml_impl/runs/stress_eval/stress_eval_combined_anchor.json
}

Write-Host "ORCHESTRATION 2 COMPLETE"