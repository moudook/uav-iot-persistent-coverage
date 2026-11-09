$env:OPENBLAS_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
$env:OMP_NUM_THREADS="1"
$env:NUMEXPR_NUM_THREADS="1"
$env:VECLIB_MAXIMUM_THREADS="1"

# Combined curriculum+energy+anchor on small_battery (Innov 1+2+11)
# Matches innov_curriculum_energy config (energy_kappa 0.3, curriculum,
# rf_at 100) plus the critical-coverage anchor feature.
$tag = "innov_currid_energy_anchor"
$seeds = 0..2

foreach ($s in $seeds) {
    $outLog = "ml_impl/runs/$tag/seed_${s}_out.txt"
    $errLog = "ml_impl/runs/$tag/seed_${s}_err.txt"
    New-Item -ItemType Directory -Force -Path "ml_impl/runs/$tag" | Out-Null
    Write-Host "Launching combined small_battery seed $s"
    Start-Process -FilePath "python" -ArgumentList "scripts/run_exp.py","--seeds",$s,"--episodes","200","--n-steps","2000","--ego","--n-ego","3","--shape","0.5","--energy-kappa","0.3","--curriculum","--rf-at","100","--anchor","--regime","small_battery","--tag",$tag,"--eval-seeds","5","--eval-offset","1000" -RedirectStandardOutput $outLog -RedirectStandardError $errLog -NoNewWindow
}
Write-Host "All 3 combined seeds launched"