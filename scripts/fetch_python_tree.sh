#!/usr/bin/env bash
# Fetch the optional TheAlgorithms/Python files that a few tests and the
# 2,562-program corpus evaluation (scripts/evaluate_ea_corpus.py) expect under ./Python/.
# Tested against upstream commit 574d100b7181956e9c8384552fd078165e4cc326 (MIT-licensed upstream).
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf .tmp_tap Python
git clone --filter=blob:none --sparse https://github.com/TheAlgorithms/Python .tmp_tap
git -C .tmp_tap sparse-checkout set genetic_algorithm machine_learning
mkdir -p Python
cp -r .tmp_tap/genetic_algorithm .tmp_tap/machine_learning Python/
rm -rf .tmp_tap
echo "Fetched Python/genetic_algorithm and Python/machine_learning"
