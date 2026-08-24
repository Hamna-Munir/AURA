# run_phase9.py
import sys
from src.core.orchestrator import run_cycle

if __name__ == "__main__":
    # command line se "execute" likho to asli order bhejega, warna dry run
    execute = "execute" in sys.argv

    print(f"\n{'='*62}")
    print(f"  AURA :: Autonomous Cycle  (execute={execute})")
    print(f"{'='*62}\n")

    summary = run_cycle(execute=execute)

    print(f"\n{'SYM':>6} | {'ACTION':>6} | {'CRITIC':>7} | {'STATUS':>9} | EXPOSURE")
    print("-" * 62)
    for r in summary["results"]:
        if r["status"] == "ERROR":
            print(f"{r['symbol']:>6} | ERROR: {r.get('error')}")
            continue
        exp = f"{r['running_exposure']*100:.0f}%"
        print(f"{r['symbol']:>6} | {r['action']:>6} | "
              f"{r['critic_score']:>5}/100 | {r['status']:>9} | {exp}")
        # exposure-based rejection ko highlight karo (signature moment)
        for rej in r.get("rejections", []):
            if "exposure" in rej:
                print(f"        └─ 🛡️  AURA refused: {rej}")

    print("-" * 62)
    print(f"\n  Approved: {summary['approved']}  |  "
          f"Rejected: {summary['rejected']}  |  "
          f"Executed: {summary['executed']}")
    print(f"  Final portfolio exposure: {summary['portfolio_end_exposure']*100:.0f}%\n")