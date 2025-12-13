#!/bin/bash
# Script to create GitHub repository and push code
# Requires GitHub Personal Access Token with repo permissions

set -e

REPO_NAME="audio-transcription"
GITHUB_USER="devopsdymry"
DESCRIPTION="Real-time audio transcription using LFM2-Audio-1.5B model with microphone recording support"

echo "🚀 Creating GitHub repository and pushing code..."
echo ""

# Check if GitHub token is available
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN environment variable not set"
    echo ""
    echo "To create the repository automatically, you need a GitHub Personal Access Token:"
    echo "1. Go to: https://github.com/settings/tokens"
    echo "2. Generate a new token with 'repo' permissions"
    echo "3. Export it: export GITHUB_TOKEN=your_token_here"
    echo ""
    echo "Alternatively, create the repository manually at:"
    echo "   https://github.com/new"
    echo "   Name: $REPO_NAME"
    echo "   Description: $DESCRIPTION"
    echo "   Visibility: Public"
    echo "   Then run: ./push-to-github.sh"
    echo ""
    exit 1
fi

# Check if remote already exists
if git remote get-url origin > /dev/null 2>&1; then
    echo "✅ Remote 'origin' already configured"
    CURRENT_REMOTE=$(git remote get-url origin)
    echo "   Current: $CURRENT_REMOTE"
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote remove origin
    else
        echo "Keeping existing remote. Pushing to existing repository..."
        git push -u origin main
        exit 0
    fi
fi

# Create repository using GitHub API
echo "📦 Creating repository on GitHub..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    https://api.github.com/user/repos \
    -d "{
        \"name\": \"$REPO_NAME\",
        \"description\": \"$DESCRIPTION\",
        \"private\": false,
        \"auto_init\": false
    }")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -eq 201 ]; then
    echo "✅ Repository created successfully!"
elif [ "$HTTP_CODE" -eq 422 ]; then
    echo "⚠️  Repository might already exist. Continuing..."
elif [ "$HTTP_CODE" -eq 401 ]; then
    echo "❌ Authentication failed. Please check your GITHUB_TOKEN"
    exit 1
else
    echo "❌ Failed to create repository. HTTP Code: $HTTP_CODE"
    echo "Response: $BODY"
    exit 1
fi

# Add remote
echo "📝 Adding GitHub remote..."
git remote add origin "https://github.com/${GITHUB_USER}/${REPO_NAME}.git"

# Push code
echo "📤 Pushing code to GitHub..."
git push -u origin main

echo ""
echo "✅ Successfully created and pushed to:"
echo "   https://github.com/${GITHUB_USER}/${REPO_NAME}"
echo ""
echo "🌐 View your repository at:"
echo "   https://github.com/${GITHUB_USER}/${REPO_NAME}"

