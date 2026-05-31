#!/usr/bin/env python3
"""Auto-resolve rebase conflicts for hermes-agent fork update.

Pattern: every remaining commit touches local state files (gitignored or deleted)
AND skill files we want to keep. Auto-resolve in batch.
"""
import subprocess, os, sys

os.chdir(os.path.expanduser("~/.hermes/hermes-agent"))

def run(cmd, check=False):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"FAIL: {cmd}\n{r.stderr[:500]}")
    return r

def auto_resolve():
    # Check unmerged files
    r = run("git ls-files --unmerged | awk '{print $4}' | sort -u")
    files = [f for f in r.stdout.strip().split('\n') if f]
    
    if not files:
        print("No conflicts!")
        return False
    
    for f in files:
        # Local state files that upstream deleted → accept ours (deleted)
        if any(x in f for x in [
            'channel_directory.json', 'memory_store.db', 
            'sessions/sessions.json', 'skills/.usage.json',
            'weixin/accounts/', '.env.', '.venv/', 'node_modules/'
        ]):
            run(f"rm -f '{f}' && git rm --cached '{f}' 2>/dev/null")
            print(f"DELETE: {f}")
            continue
        
        # Memories are gitignored → just restore local version
        if 'memories/' in f:
            run(f"git checkout --ours '{f}' 2>/dev/null")
            print(f"SKIP (gitignore): {f}")
            continue
        
        # Skills we want to keep → accept their version (from this commit)
        run(f"git checkout --theirs '{f}' 2>/dev/null && git add '{f}'")
        print(f"KEEP: {f}")
    
    # Try to continue rebase
    r = run("git -c core.editor=true rebase --continue 2>&1 | tail -10")
    print(r.stdout[-1000:])
    if r.stderr:
        print("STDERR:", r.stderr[-500:])
    return True

if __name__ == '__main__':
    while auto_resolve():
        pass
    print("\nDone. Checking remaining state...")
    run("git status --short | head -30")