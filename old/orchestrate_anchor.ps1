$ErrorActionPreference = "Continue"
$project = "C:\Users\gbust\Downloads\Academic\Courses\Machine_learning_in_wireless_network\Project1"
Set-Location $project

$tag = "exp_anchor_eval"
$seedJson = @()
foreach ($s in 0..4) {
    $seedJson += "ml_impl/runs/$tag/seed_${s}.json"
}

Write-Host "Waiting for training seeds to complete..."
$deadline = (Get-Date).AddHours(4)
while ((Get-Date) -lt $deadline) {
    $done = $true
    foreach ($j in $seedJson) {
        if (-not (Test-Path $j)) { $done = $false; break }
    }
    if ($done) { break }
    Start-Sleep -Seconds 60
}
if (-not $done) {
    Write-Host "TIMEOUT waiting for training" 
    exit 2
}
Write-Host "All 5 seeds done."

# Check for python processes still running (eval must wait for training to fully finish)
$running = Get-Process | Where-Object { $_.ProcessName -match "python" }
Write-Host "python processes still running: $($running.Count)"

# 1. held-out evaluation
Write-Host "Running held-out evaluation..."
python scripts/eval_ckpt.py --tag $tag --eval-offset 1000 --eval-seeds 20
Write-Host "Held-out eval done."

# 2. stress evaluation (separate artifact so main report artifact is untouched)
Write-Host "Running stress evaluation..."
python scripts/eval_stress.py --tag $tag --out ml_impl/runs/stress_eval/stress_eval_anchor.json
Write-Host "Stress eval done."

# 3. summary
python -c "
import json
h = json.load(open('ml_impl/runs/$tag/eval_heldout.json', encoding='utf-8'))
s = json.load(open('ml_impl/runs/stress_eval/stress_eval_anchor.json', encoding='utf-8'))
print()
print('=== ANCHOR HEADLINE ===')
print('heldout mean over seeds:', round(h['mean_over_seeds'], 4), 'sd', round(h['sd_over_seeds'], 4))
for k, v in h['per_checkpoint'].items():
    print(' ', k, round(v['mean'], 4), 'det', round(v['det_mean'], 4))
print()
print('=== STRESS (anchor) ===')
for reg, v in s['regimes'].items():
    lm = v['learner_mean']
    lm_s = ('%.4f' % lm) if lm == lm else 'NA'
    lmr = v['learner_minus_rule']
    lmr_s = ('%+.4f' % lmr) if lmr is not None else '--'
    print(f'  {reg:14s} rule={v[\"best_rule_ck\"]:.4f} learner={lm_s} diff={lmr_s} headroom={v[\"headroom\"]:.4f}')
"
Write-Host "ALL DONE"