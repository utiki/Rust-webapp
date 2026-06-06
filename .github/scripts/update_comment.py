import re

raw = open('existing_review.md').read()
fixed_str = open('fixed_numbers.txt').read().strip()
new_findings = open('new_findings.md').read().strip()
fixed_nums = [n.strip() for n in fixed_str.split(',') if n.strip()] if fixed_str else []

# ヘッダー（最初の --- まで）を除いた本文を取り出す
first_sep = raw.find('\n---\n')
body = raw[first_sep + 5:].strip() if first_sep >= 0 else raw.strip()

# アクティブ部分と修正済み部分を分割
resolved_sep = re.search(r'\n\n---\n\n### ✅ 修正済み', body)
if resolved_sep:
    active_part = body[:resolved_sep.start()]
    resolved_raw = body[resolved_sep.end():]
else:
    active_part = body
    resolved_raw = ''

# 既存の修正済みアイテムを個別取得
resolved_items = []
for line in resolved_raw.strip().split('\n'):
    line = line.strip()
    if line and line != 'なし' and not line.startswith('###'):
        resolved_items.append(line)

# 修正済み番号をアクティブ部分から取り出して移動
updated_active = active_part
for num in fixed_nums:
    pattern = re.compile(
        r'([🔴🟠🟡🟢] )\*\*' + re.escape(num) + r'\.\*\* .+?(?=\n[🔴🟠🟡🟢] \*\*\d+\.\*\*|\n> \[!|\n### |\Z)',
        re.DOTALL
    )
    match = pattern.search(updated_active)
    if match:
        full_block = match.group(0).strip()
        lines = full_block.split('\n')
        first_line = lines[0]
        rest = '\n'.join(lines[1:])
        # 1行目の番号の太字を外して取り消し線をつける
        clean_first = re.sub(r'\*\*' + re.escape(num) + r'\.\*\*', f'{num}.', first_line).strip()
        # 全文を保持して末尾に ✅ を付ける
        resolved_block = f'~~{clean_first}~~ ✅'
        if rest.strip():
            resolved_block += '\n' + rest
        resolved_items.append(resolved_block)
        updated_active = updated_active[:match.start()] + updated_active[match.end():]

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
            if re.search(none_pat, updated_active):
                updated_active = re.sub(none_pat, rf'\1{finding}', updated_active)
            else:
                sec_pat = re.compile(
                    rf'(> \[!{alert}\]\n> [^\n]+\n\n)(.*?)(\n\n> \[!|\Z)', re.DOTALL)
                def add(m, f=finding):
                    ex = m.group(2).rstrip()
                    return m.group(1) + (ex if ex != 'なし' else '') + ('\n\n' if ex and ex != 'なし' else '') + f + m.group(3)
                updated_active = sec_pat.sub(add, updated_active, count=1)

# サマリー件数を更新
c  = len(re.findall(r'🔴 \*\*\d+\.\*\*', updated_active))
ma = len(re.findall(r'🟠 \*\*\d+\.\*\*', updated_active))
mi = len(re.findall(r'🟡 \*\*\d+\.\*\*', updated_active))
s  = len(re.findall(r'🟢 \*\*\d+\.\*\*', updated_active))
updated_active = re.sub(r'\| 🔴 Critical \| \d+件 \|',   f'| 🔴 Critical | {c}件 |',   updated_active)
updated_active = re.sub(r'\| 🟠 Major \| \d+件 \|',      f'| 🟠 Major | {ma}件 |',     updated_active)
updated_active = re.sub(r'\| 🟡 Minor \| \d+件 \|',      f'| 🟡 Minor | {mi}件 |',     updated_active)
updated_active = re.sub(r'\| 🟢 Suggestion \| \d+件 \|', f'| 🟢 Suggestion | {s}件 |', updated_active)

# 修正済みセクションを末尾に配置（件数付き）
count = len(resolved_items)
resolved_section = f'### ✅ 修正済み（{count}件）\n\n'
resolved_section += '\n\n---\n\n'.join(resolved_items) if resolved_items else 'なし'

open('updated_comment.md', 'w').write(
    updated_active.rstrip() + '\n\n---\n\n' + resolved_section
)
print(f"修正済み: {fixed_nums}, 件数: {count}")
