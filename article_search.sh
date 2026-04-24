#!/bin/bash
set -e

# 1. Setup variables
URL=$1
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="./docs/articles/research_report_${TIMESTAMP}.md"

if [ -z "$URL" ]; then
    echo "Usage: ./article_search.sh [URL]"
    exit 1
fi

echo "🌐 Fetching content..."
# Save the text to a variable so we don't hit the website twice
CONTENT=$(w3m -dump "$URL")

echo "🧠 Generating Research Report..."

# 2. Start the file with a header
echo "# Research Report: $URL" > "$OUTPUT_FILE"
echo "Date: $(date)" >> "$OUTPUT_FILE"
echo -e "\n---\n" >> "$OUTPUT_FILE"

# 3. Run the FIRST pattern (Summarize)
echo "📝 Summarizing..."
echo "## Executive Summary" >> "$OUTPUT_FILE"
echo "$CONTENT" | fabric -p summarize >> "$OUTPUT_FILE"

echo -e "\n---\n" >> "$OUTPUT_FILE"

# 4. Run the SECOND pattern (Extract Wisdom)
echo "💎 Extracting Wisdom..."
echo "## Core Wisdom & Insights" >> "$OUTPUT_FILE"
echo "$CONTENT" | fabric -p extract_wisdom >> "$OUTPUT_FILE"

echo "✅ Done! Report saved to: $OUTPUT_FILE"