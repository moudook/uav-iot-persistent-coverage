param(
  [string]$seeds = "0",
  [string]$device = "cpu",
  [string]$tag = "exp_ego_fixed"
)
# Sequential driver with restart-on-crash.  One seed at a time per stream so a
# memory spike kills at most the current run; the loop restarts it (up to 3
# attempts) before moving on.  Completion is detected by the per-seed json.
$env:PYTHONPATH = "ml_impl"
foreach ($s in $seeds.Split(",")) {
    $done = "ml_impl/runs/$tag/seed_$s.json"
    $tries = 0
    while (-not (Test-Path $done) -and $tries -lt 3) {
        $tries++
        Write-Host "[$device] seed $s attempt $tries -> $done"
        python scripts/run_exp.py --seeds $s --episodes 200 --n-steps 2000 `
            --ego --shape 0.5 --tag $tag --device $device `
            *>> "ml_impl/runs/$tag/seed_${s}_out.txt"
    }
    if (Test-Path $done) { Write-Host "[$device] seed $s done" }
    else { Write-Host "[$device] seed $s FAILED after 3 attempts" }
}
