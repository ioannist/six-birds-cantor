#!/bin/bash
# Protocol violation checker — Six Birds Emergence Ladder
# Blocks writes that introduce engineered substrates outside the six primitives.
# Runs as a PreToolUse hook on Edit|Write. Fast: one jq + one grep.

INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Only check .rs files
[[ "$FILE" =~ \.rs$ ]] || exit 0

# Grab the content being written (Write) or inserted (Edit)
TEXT=$(echo "$INPUT" | jq -r '.tool_input.content // .tool_input.new_string // empty')
[ -z "$TEXT" ] && exit 0

# Single grep for all banned patterns (fast, one pass)
MATCH=$(echo "$TEXT" | grep -nP 'build_coupled|coupled_blocks|build_block_decomp|MarkovKernel::new\s*\(|MarkovKernel::from_|from_matrix|from_rows' | head -3)

if [ -n "$MATCH" ]; then
  echo "PROTOCOL VIOLATION — $FILE" >&2
  echo "$MATCH" >&2
  echo "All structure must emerge from P1-P6 on MarkovKernel::random(). See .claude/CLAUDE.md" >&2
  exit 2
fi
exit 0
