import re

raw = open('existing_review.md').read()
fixed_str = open('fixed_numbers.txt').read().strip()
new_findings = open('new_findings.md').read().strip()
fixed_nums = [n.strip() for n in fixed_str.split(',') if n.strip()] if fixed_str else []

# ヘッダー（最初の --- まで）を除いた本文を取り出す
first_sep = raw.find('\n---\n')
body = raw[first_sep + 5:].strip() if first_sep >= 0 else raw.strip()

# 修正済み番号の指摘に取り消し線をつける（移動はしない）
updated = body
for num in fixed_nums:
    pattern = re.compile(
        r'([🔴🟠🟡🟢] )\*\*' + re.escape(num) + r'\.\*\*(.+?)(?=\n[🔴🟠🟡🟢] \*\*\d+\.\*\*|\n> \[!|\n### |\Z)',
        re.DOTALL
    )
    match = pattern.search(updated)
    if match:
        block = match.group(0)
        # すでに取り消し線がついていればスキップ
        if '~~' not in block:
            lines = block.split('\n')
            # 1行目の番号の太字を外して取り消し線をつける
            first = re.sub(r'\*\*' + re.escape(num) + r'\.\*\*', f'{num}.', lines[0]).strip()
            rest = '\n'.join(lines[1:])
            new_block = f'~~{first}~~ ✅'
            if rest.strip():
                new_block += '\n' + rest
            updated = updated[:match.start()] + new_block + updated[match.end():]

# 新規指摘をカテゴリセクションに追加
if new_findings and new_findings.strip() not in ('なし', ''):
    for alert, emoji in [('CAUTION','🔴'),('WARNING','🟠'),('NOTE','🟡'),('TIP','🟢')]:
        cat_findings = re.findall(
            rf'{re.escape(emoji)} \*\*\d+\.\*\*.+?(?=\n[🔴🟠🟡🟢] \*\*\d|\n> \[!|\Z)',
            new_findings, re.DOTALL
        )
        for finding in cat_findings:
            finding = finding.strip()
            none_pat = rf'(> \[!{alert}\]\n> [^\n]+\n\n)なし'
            if re.search(none_pat, updated):
                updated = re.sub(none_pat, rf'\1{finding}', updated)
            else:
                sec_pat = re.compile(
                    rf'(> \[!{alert}\]\n> [^\n]+\n\n)(.*?)(\n\n> \[!|\Z)', re.DOTALL)
                def add(m, f=finding):
                    ex = m.group(2).rstrip()
                    return m.group(1) + (ex if ex != 'なし' else '') + ('\n\n' if ex and ex != 'なし' else '') + f + m.group(3)
                updated = sec_pat.sub(add, updated, count=1)

# サマリー件数を更新（取り消し線なしのものだけカウント）
def count_active(emoji, text):
    return len(re.findall(rf'{re.escape(emoji)} \*\*\d+\.\*\*(?!.*~~)', text))

c  = len(re.findall(r'(?<!~~)🔴 \*\*\d+\.\*\*', updated))
ma = len(re.findall(r'(?<!~~)🟠 \*\*\d+\.\*\*', updated))
mi = len(re.findall(r'(?<!~~)🟡 \*\*\d+\.\*\*', updated))
s  = len(re.findall(r'(?<!~~)🟢 \*\*\d+\.\*\*', updated))
updated = re.sub(r'\| 🔴 Critical \| \d+件 \|',   f'| 🔴 Critical | {c}件 |',   updated)
updated = re.sub(r'\| 🟠 Major \| \d+件 \|',      f'| 🟠 Major | {ma}件 |',     updated)
updated = re.sub(r'\| 🟡 Minor \| \d+件 \|',      f'| 🟡 Minor | {mi}件 |',     updated)
updated = re.sub(r'\| 🟢 Suggestion \| \d+件 \|', f'| 🟢 Suggestion | {s}件 |', updated)

open('updated_comment.md', 'w').write(updated)
print(f"取り消し線: {fixed_nums}")
