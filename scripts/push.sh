#!/bin/bash

# Quick git push script for PUM Content Generator
# Usage: ./scripts/push.sh [optional: custom message]
# If no message provided, auto-generates intelligent commit message with change details
# bash scripts/push.sh

set -e

cd "$(dirname "$0")/.."

# Stage all changes
git add -A

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "No changes to commit"
    exit 0
fi

# Get change information
CHANGES=$(git diff --cached --name-only)
DIFF=$(git diff --cached --stat)
DIFF_DETAILS=$(git diff --cached)
FILE_COUNT=$(echo "$CHANGES" | wc -l | tr -d ' ')

# Generate intelligent message if not provided
if [ -z "$1" ]; then
    echo "📊 Analyzing changes..."

    # Analyze what changed
    HAS_FEAT_CHANGES=false
    HAS_FIX_CHANGES=false
    HAS_TEST_CHANGES=false
    HAS_STYLE_CHANGES=false
    HAS_DOCS_CHANGES=false
    HAS_CONFIG_CHANGES=false
    HAS_BUILD_CHANGES=false

    # Check for feature changes (Python source files, excluding tests)
    if echo "$CHANGES" | grep -qE "\.py$"; then
        if echo "$CHANGES" | grep -E "\.py$" | grep -qvE "(test_|_test\.py$|tests/)"; then
            HAS_FEAT_CHANGES=true
        fi
    fi

    # Check for fixes (keywords in diff)
    if echo "$DIFF_DETAILS" | grep -qiE "\+.*(fix|error|bug|issue|resolve|correct)"; then
        HAS_FIX_CHANGES=true
    fi

    # Check for test changes
    if echo "$CHANGES" | grep -qE "(test_|_test\.py$|tests/)"; then
        HAS_TEST_CHANGES=true
    fi

    # Check for style/refactor
    if echo "$DIFF_DETAILS" | grep -qiE "refactor|cleanup|format|lint"; then
        HAS_STYLE_CHANGES=true
    fi

    # Check for documentation
    if echo "$CHANGES" | grep -qE "(\.md$|README|CHANGELOG|\.planning)"; then
        HAS_DOCS_CHANGES=true
    fi

    # Check for config changes
    if echo "$CHANGES" | grep -qE "(\.json$|\.yaml$|\.yml$|\.toml$|requirements\.txt|\.env)"; then
        HAS_CONFIG_CHANGES=true
    fi

    # Check for build/script changes
    if echo "$CHANGES" | grep -qE "(scripts/|Makefile|\.sh$|\.github/)"; then
        HAS_BUILD_CHANGES=true
    fi

    # Extract specific features from code (PUM Content features)
    FEATURE_KEYWORDS=""
    FEATURE_LIST=""

    if echo "$CHANGES" | grep -q "templates"; then
        FEATURE_KEYWORDS="templates"
        FEATURE_LIST="$FEATURE_LIST templates"
    fi
    if echo "$CHANGES" | grep -q "content_generator"; then
        [ -z "$FEATURE_KEYWORDS" ] && FEATURE_KEYWORDS="content-gen"
        FEATURE_LIST="$FEATURE_LIST content-generator"
    fi
    if echo "$CHANGES" | grep -q "research_sources"; then
        [ -z "$FEATURE_KEYWORDS" ] && FEATURE_KEYWORDS="research"
        FEATURE_LIST="$FEATURE_LIST research-sources"
    fi
    if echo "$CHANGES" | grep -q "email_sender"; then
        [ -z "$FEATURE_KEYWORDS" ] && FEATURE_KEYWORDS="email"
        FEATURE_LIST="$FEATURE_LIST email-sender"
    fi
    if echo "$CHANGES" | grep -q "main\.py"; then
        [ -z "$FEATURE_KEYWORDS" ] && FEATURE_KEYWORDS="pipeline"
        FEATURE_LIST="$FEATURE_LIST pipeline"
    fi
    if echo "$CHANGES" | grep -q "brand_config"; then
        [ -z "$FEATURE_KEYWORDS" ] && FEATURE_KEYWORDS="brand"
        FEATURE_LIST="$FEATURE_LIST brand-config"
    fi
    if echo "$CHANGES" | grep -q "\.github"; then
        [ -z "$FEATURE_KEYWORDS" ] && FEATURE_KEYWORDS="ci"
        FEATURE_LIST="$FEATURE_LIST ci-cd"
    fi
    if echo "$CHANGES" | grep -q "assets"; then
        [ -z "$FEATURE_KEYWORDS" ] && FEATURE_KEYWORDS="assets"
        FEATURE_LIST="$FEATURE_LIST assets"
    fi

    # Extract phase number if in planning
    PHASE=""
    if echo "$CHANGES" | grep -q "\.planning/phases"; then
        PHASE=$(echo "$CHANGES" | grep "\.planning/phases" | head -1 | sed -E 's|.*phases/([0-9]+).*|\1|')
    fi

    # Determine commit type and action
    if [ "$HAS_FIX_CHANGES" = true ]; then
        TYPE="fix"
        ACTION="fix issues"
    elif [ "$HAS_TEST_CHANGES" = true ]; then
        TYPE="test"
        ACTION="add/update tests"
    elif [ "$HAS_STYLE_CHANGES" = true ]; then
        TYPE="refactor"
        ACTION="refactor code"
    elif [ "$HAS_DOCS_CHANGES" = true ]; then
        TYPE="docs"
        ACTION="update documentation"
    elif [ "$HAS_BUILD_CHANGES" = true ]; then
        TYPE="build"
        ACTION="update build scripts"
    elif [ "$HAS_CONFIG_CHANGES" = true ]; then
        TYPE="chore"
        ACTION="update configuration"
    else
        TYPE="feat"
        ACTION="add features"
    fi

    # Build scope
    SCOPE=""
    if [ -n "$PHASE" ]; then
        SCOPE="phase-$PHASE"
    elif [ -n "$FEATURE_KEYWORDS" ]; then
        SCOPE="$FEATURE_KEYWORDS"
    fi

    # Build subject line
    if [ -n "$SCOPE" ]; then
        SUBJECT="$TYPE($SCOPE): $ACTION"
    else
        SUBJECT="$TYPE: $ACTION"
    fi

    # Get file change details
    ALL_FILES=$(echo "$CHANGES" | sed 's|^|  - |')

    # Categorize files
    PY_FILES=$(echo "$CHANGES" | grep -E "\.py$" || true)
    CONFIG_FILES=$(echo "$CHANGES" | grep -E "\.(json|yaml|yml|toml)$" || true)
    DOC_FILES=$(echo "$CHANGES" | grep -E "\.md$" || true)
    SCRIPT_FILES=$(echo "$CHANGES" | grep -E "\.sh$" || true)

    # Build detailed change summary
    CHANGE_SUMMARY=""

    if [ -n "$PY_FILES" ]; then
        PY_COUNT=$(echo "$PY_FILES" | wc -l | tr -d ' ')
        CHANGE_SUMMARY="$CHANGE_SUMMARY
Python files ($PY_COUNT):
$(echo "$PY_FILES" | sed 's|^|  - |')"
    fi

    if [ -n "$CONFIG_FILES" ]; then
        CONFIG_COUNT=$(echo "$CONFIG_FILES" | wc -l | tr -d ' ')
        CHANGE_SUMMARY="$CHANGE_SUMMARY
Config files ($CONFIG_COUNT):
$(echo "$CONFIG_FILES" | sed 's|^|  - |')"
    fi

    if [ -n "$DOC_FILES" ]; then
        DOC_COUNT=$(echo "$DOC_FILES" | wc -l | tr -d ' ')
        CHANGE_SUMMARY="$CHANGE_SUMMARY
Documentation ($DOC_COUNT):
$(echo "$DOC_FILES" | sed 's|^|  - |')"
    fi

    if [ -n "$SCRIPT_FILES" ]; then
        SCRIPT_COUNT=$(echo "$SCRIPT_FILES" | wc -l | tr -d ' ')
        CHANGE_SUMMARY="$CHANGE_SUMMARY
Scripts ($SCRIPT_COUNT):
$(echo "$SCRIPT_FILES" | sed 's|^|  - |')"
    fi

    # Get insertions/deletions stats
    STATS=$(git diff --cached --shortstat)

    # Build full commit message
    MESSAGE="$SUBJECT

## Summary
$FILE_COUNT file(s) changed
$STATS

## Features/Areas Affected
$(if [ -n "$FEATURE_LIST" ]; then echo "$FEATURE_LIST" | tr ' ' '\n' | grep -v '^$' | sed 's|^|  - |'; else echo "  - general"; fi)

## Files Changed$CHANGE_SUMMARY"

    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "📝 Auto-generated commit message:"
    echo "═══════════════════════════════════════════════════════════════"
    echo "$MESSAGE"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
else
    MESSAGE="$1"
    echo "📝 Using custom message: $MESSAGE"
fi

# Commit with co-author
git commit -m "$MESSAGE

Co-Authored-By: Claude <noreply@anthropic.com>"

# Show what was committed
echo ""
echo "📋 Commit created:"
git log -1 --pretty=format:"  Hash: %h%n  Author: %an%n  Date: %ad%n" --date=short

# Ensure we're using the correct GitHub account for this project
if command -v gh &> /dev/null; then
    CURRENT_USER=$(gh auth status 2>&1 | grep "Logged in to github.com account" | grep "Active account: true" | sed -E 's/.*account ([^ ]+).*/\1/')
    if [ "$CURRENT_USER" != "awthedev-888" ]; then
        echo "🔄 Switching to awthedev-888 account..."
        gh auth switch --user awthedev-888
    fi
fi

# Push to remote
echo ""
echo "🚀 Pushing to remote..."
git push

echo ""
echo "✅ Successfully pushed to $(git remote get-url origin)"
echo "   Branch: $(git branch --show-current)"
