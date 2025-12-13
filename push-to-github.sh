#!/bin/bash
# Script to push code to GitHub repository
# Make sure you've created the repository on GitHub first!

set -e

REPO_NAME="audio-transcription-cli"
GITHUB_USER="devopsdymry"

echo "🚀 Pushing audio-transcription-cli to GitHub..."
echo ""

# Check if remote already exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "✅ Remote 'origin' already configured"
    git remote -v
else
    echo "📝 Adding GitHub remote..."
    git remote add origin "https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
fi

echo ""
echo "📤 Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Successfully pushed to: https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo ""
echo "🌐 View your repository at:"
echo "   https://github.com/${GITHUB_USER}/${REPO_NAME}"

