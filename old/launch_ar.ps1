$env:OPENBLAS_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
$env:OMP_NUM_THREADS="1"
$env:NUMEXPR_NUM_THREADS="1"
$env:VECLIB_MAXIMUM_THREADS="1"

$tag = "exp_ar_eval"
$seeds = 0..2

foreach ($s in $seeds) {
    $outLog = "ml_impl/runs/$tag/seed_${s}_out.txt"
    $errLog = "ml_impl/runs/$tag/seed_${s}_err.txt"
    New-Item -ItemType Directory -Force -Path "ml_impl/runs/$tag" | Out-Null
    Write-Host "Launching action-repeat seed $s"
    Start-Process -FilePath "python" -ArgumentList "scripts/run_exp.py","--seeds",$s,"--episodes","200","--n-steps","2000","--ego","--n-ego","3","--shape","0.5","--action-repeat","4","--tag",$tag,"--eval-seeds","20","--eval-offset","1000" -RedirectStandardOutput $outLog -RedirectStandardError $errLog -NoNewWindow
}
Write-Host "All 3 action-repeat seeds launched"