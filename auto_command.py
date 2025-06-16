#!/usr/bin/env python3
"""
Git Repository Automation Script
Handles .gitignore creation and git operations for new and existing repositories.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, check=True):
    """Execute shell command and return result."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            check=check
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stdout.strip() if e.stdout else "", e.stderr.strip() if e.stderr else ""


def get_gitignore_content():
    """Get the standard .gitignore content."""
    return """# Virtual Environments and Dev Environment
venv/
.venv/
env/
.env/
.devenv/
.aider*/
.aider.*/
.devenv*/
devenv*/

# Development Tools
.aider.chat.history.md
.aider.input.history
.devenv.flake.nix
devenv.lock
devenv.nix
devenv.yaml

# Python
__pycache__/
*.py[cod]
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Jupyter Notebooks
*.ipynb
.ipynb_checkpoints/

# Project-specific directories
reports/
realtime_speech/microphone.ipynb
niceGUI/
tts/modul/

# Generated content
data/transcripts/
blogs/

# IDE and Editor files
.vscode/
.idea/
*.swp
*.swo
*~

# Environment variables
.env
.env.*

# Data and Media files
*.csv
*.json
*.pdf
*.xlsx
*.xls
*.txt
!requirements.txt
*.mp3
*.mp4
*.wav
*.db
*.sqlite
*.sqlite3

# Images
*.png
*.jpg
*.jpeg
*.gif
*.svg
*.ico

# Model files
*.ckpt
*.pt
*.pth
*.bin
*.model
*.h5
pretrained_models/

# Cache and temp files
.cache/
.pytest_cache/
.coverage
htmlcov/
.aider.tags.cache.v3/

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Binary and Library files
*.pyd
*.dll
*.lib
*.exe

# Large files and directories
*.model
*.bin
*.pdf
data/transcripts/
*.mp3
*.wav
*.mp4
.aider*
.pickle*
"""


def create_gitignore():
    """Create .gitignore file with common exclusions."""
    gitignore_content = get_gitignore_content()
    
    # Check if .gitignore already exists
    if os.path.exists('.gitignore'):
        try:
            with open('.gitignore', 'r') as f:
                existing_content = f.read()
            
            # Check if content matches exactly
            if existing_content.strip() == gitignore_content.strip():
                print("ℹ️  .gitignore file already exists with expected content")
                return True
            else:
                print("⚠️  .gitignore file exists but has different content")
                response = input("Do you want to overwrite it? (y/N): ").strip().lower()
                if response != 'y':
                    print("⏭️  Keeping existing .gitignore")
                    return True
        except Exception as e:
            print(f"⚠️  Could not read existing .gitignore: {e}")
    
    try:
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("✅ Created .gitignore file")
        return True
    except Exception as e:
        print(f"❌ Failed to create .gitignore: {e}")
        return False


def is_git_repo():
    """Check if current directory is already a git repository."""
    return os.path.exists('.git')


def has_remote_origin():
    """Check if remote origin is configured."""
    success, stdout, _ = run_command("git remote -v", check=False)
    return success and "origin" in stdout


def get_current_branch():
    """Get current git branch name."""
    success, stdout, _ = run_command("git branch --show-current", check=False)
    return stdout if success else "main"


def safe_git_add():
    """Safely add files to git, handling problematic files."""
    print("🔄 Adding files to git...")
    
    # First try normal git add
    success, _, error = run_command("git add .", check=False)
    if success:
        print("✅ Files added to staging")
        return True
    
    print(f"⚠️  Standard git add failed: {error}")
    print("🔄 Trying to add files individually...")
    
    # Try to add files one by one, skipping problematic ones
    try:
        # Get list of files to add
        success, stdout, _ = run_command("git status --porcelain", check=False)
        if not success:
            print("❌ Could not get git status")
            return False
        
        files_added = 0
        for line in stdout.split('\n'):
            if not line.strip():
                continue
                
            # Parse git status output
            status = line[:2]
            filename = line[3:].strip()
            
            # Skip files that are already tracked or deleted
            if status.strip() in ['D', 'R']:
                continue
                
            # Try to add this specific file
            success, _, file_error = run_command(f'git add "{filename}"', check=False)
            if success:
                files_added += 1
            else:
                print(f"⚠️  Skipped problematic file: {filename}")
        
        if files_added > 0:
            print(f"✅ Added {files_added} files to staging")
            return True
        else:
            print("ℹ️  No files to add")
            return True
            
    except Exception as e:
        print(f"❌ Error during selective file adding: {e}")
        return False


def initialize_new_repo():
    """Initialize new git repository."""
    print("🔄 Initializing new git repository...")
    
    # Git init
    success, _, error = run_command("git init")
    if not success:
        print(f"❌ Failed to initialize git repo: {error}")
        return False
    print("✅ Git repository initialized")
    
    # Git add with error handling
    if not safe_git_add():
        return False
    
    # Initial commit
    success, _, error = run_command('git commit -m "initial commit"')
    if not success:
        print(f"❌ Failed to commit: {error}")
        return False
    print("✅ Initial commit created")
    
    # Ask for remote URL
    while True:
        remote_url = input("🔗 Enter remote repository URL (or press Enter to skip): ").strip()
        if not remote_url:
            print("⏭️  Skipping remote setup")
            return True
            
        # Add remote origin
        success, _, error = run_command(f'git remote add origin "{remote_url}"')
        if not success:
            print(f"❌ Failed to add remote: {error}")
            continue
        print("✅ Remote origin added")
        
        # Get current branch
        current_branch = get_current_branch()
        
        # Push to remote
        success, _, error = run_command(f"git push -u origin {current_branch}")
        if not success:
            print(f"❌ Failed to push: {error}")
            print("You may need to create the repository on the remote first")
            return False
        print(f"✅ Pushed to origin/{current_branch}")
        return True


def update_existing_repo():
    """Update existing git repository."""
    print("🔄 Updating existing git repository...")
    
    # Git add with error handling
    if not safe_git_add():
        return False
    
    # Check if there are changes to commit
    success, stdout, _ = run_command("git status --porcelain")
    if success and not stdout:
        print("ℹ️  No changes to commit")
        return True
    
    # Commit changes
    success, _, error = run_command('git commit -m "changes"')
    if not success:
        print(f"❌ Failed to commit: {error}")
        return False
    print("✅ Changes committed")
    
    # Check if remote exists
    if not has_remote_origin():
        print("⚠️  No remote origin configured. Skipping push.")
        return True
    
    # Push changes
    current_branch = get_current_branch()
    success, _, error = run_command(f"git push origin {current_branch}")
    if not success:
        print(f"❌ Failed to push: {error}")
        return False
    print(f"✅ Pushed to origin/{current_branch}")
    return True


def main():
    """Main automation function."""
    print("🚀 Git Repository Automation Script")
    print("=" * 40)
    
    # Create .gitignore
    if not create_gitignore():
        sys.exit(1)
    
    # Check if this is a new or existing repo
    if is_git_repo():
        print("📁 Existing git repository detected")
        success = update_existing_repo()
    else:
        print("🆕 New repository - initializing...")
        success = initialize_new_repo()
    
    if success:
        print("\n🎉 Git automation completed successfully!")
    else:
        print("\n💥 Git automation failed!")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
