import os
import subprocess
import sys

def run_cmd(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing: {command}\nStderr: {e.stderr}", file=sys.stderr)
        return None

def autonomous_git_sync(commit_type, scope, message):
    print("🤖 AI Agent initiating autonomous Git sync routine...")
    
    # 1. Pull latest upstream changes
    run_cmd("git pull origin main --rebase")
    
    # 2. Stage verified files
    run_cmd("git add .")
    
    # 3. Commit with Conventional Specifications
    full_message = f"{commit_type}({scope}): {message}"
    commit_res = run_cmd(f'git commit -m "{full_message}"')
    
    if commit_res and "nothing to commit" in commit_res:
        print("ℹ️ Workspace clean. No modifications detected for staging.")
        return
        
    # 4. Push to remote repository securely
    push_res = run_cmd("git push origin main")
    if push_res is not None:
        print(f"🚀 [SUCCESS] Codebase synced to GitHub with message: {full_message}")
    else:
        print("⚠️ [CRITICAL] Push rejected. Potential merge conflict detected. Awaiting manual override.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python git_sync.py <type> <scope> <message>")
        sys.exit(1)
    autonomous_git_sync(sys.argv[1], sys.argv[2], sys.argv[3])
