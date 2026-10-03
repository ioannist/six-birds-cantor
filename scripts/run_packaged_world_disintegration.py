#!/usr/bin/env python3
"""Record the actual-object world-law construction and its exact scope."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys


def run():
    root=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(root/'src'))
    from contextual_cantor.packaged_world_disintegration import certify_packaged_world_disintegration
    report=certify_packaged_world_disintegration()
    report['generated_at_utc']=datetime.now(timezone.utc).isoformat()
    inputs=['configs/mathematics/original_controlled_cycle.json',
        'configs/experiments/generated/continuous_full_loop_kernel_shell.json',
        'src/contextual_cantor/continuous_kernel_substrate.py',
        'src/contextual_cantor/rational_interval.py',
        'src/contextual_cantor/controlled_shell.py',
        'src/contextual_cantor/controlled_pressure_separation.py',
        'src/contextual_cantor/original_loop_extension.py',
        'src/contextual_cantor/packaged_world_disintegration.py',
        'scripts/run_packaged_world_disintegration.py',
        'lean/PackagedDisintegration.lean']
    report['input_sha256']={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in inputs}
    target=root/'results/packaged_world_disintegration/report.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(f'wrote {target}')
    return 0


if __name__=='__main__':
    raise SystemExit(run())
