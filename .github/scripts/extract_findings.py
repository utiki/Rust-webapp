import re

body = open('existing_review.md').read()

# アクティブな指摘（修正済みセクション以前）だけ対象にする
active_part = body.split('### ✅ 修正済み')[0]

# 各指摘を抽出: 絵文字 **N.** `file:line` の行を探す
findings = []
lines = active_part.split('\n')
i = 0
while i < len(lines):
    match = re.match(r'([🔴🟠🟡🟢]) \*\*(\d+)\.\*\* (.+)', lines[i])
    if match:
        emoji, num, location = match.groups()
        description_lines = []
        i += 1
        while i < len(lines):
            line = lines[i]
            if re.match(r'[🔴🟠🟡🟢] \*\*\d+\.\*\*', line):
                break
            description_lines.append(line)
            i += 1
        description = '\n'.join(description_lines).strip()
        findings.append(f"[{num}] {location}\n{description}")
    else:
        i += 1

with open('findings_list.txt', 'w') as f:
    f.write('\n\n---\n\n'.join(findings))

print(f"{len(findings)}件の指摘を抽出しました")
