import subprocess,sys
cmds=[
 [sys.executable,'-m','quantumcloudguard','demo'],
 [sys.executable,'-m','quantumcloudguard','experiment','--profile','quick','--out','results'],
 [sys.executable,'experiments/attack_suite.py'],
 [sys.executable,'experiments/security_suite.py'],
 [sys.executable,'experiments/recovery_matrix.py'],
 [sys.executable,'experiments/baselines.py'],
 [sys.executable,'experiments/ablation.py'],
 [sys.executable,'experiments/plot_results.py'],
]
for c in cmds:
 print('RUN',' '.join(c)); subprocess.check_call(c)
print('All quick experiments completed.')
