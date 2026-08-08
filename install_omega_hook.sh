#!/bin/bash
# Install omega formula enforcement as a git pre-commit hook
# Run from repo root: bash install_omega_hook.sh

set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
HOOKS_DIR="$REPO_ROOT/.git/hooks"
CHECKER="$REPO_ROOT/check_omega_formula.py"

echo "Installing omega formula enforcement hook..."

# Copy checker to repo root (so it's version-controlled)
cp "$(dirname "$0")/check_omega_formula.py" "$REPO_ROOT/check_omega_formula.py"

# Write the pre-commit hook
cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/bin/bash
# EPS Research — omega formula enforcement pre-commit hook
python3 "$(git rev-parse --show-toplevel)/check_omega_formula.py"
EOF

chmod +x "$HOOKS_DIR/pre-commit"

echo "✓ Pre-commit hook installed at $HOOKS_DIR/pre-commit"
echo "✓ Checker script at $REPO_ROOT/check_omega_formula.py"
echo ""
echo "Test it now with:"
echo "  python3 check_omega_formula.py <file>"
echo ""
echo "The hook will run automatically on every git commit."
