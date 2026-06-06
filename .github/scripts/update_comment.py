import re

raw = open('existing_review.md').read()

# ヘッダー（--- より前）とフッター（最後の --- 以降）を除いた本文だけ取り出す
parts = raw.split('\n---\n')
if len(parts) >= 3:
    # 最初の --- より後、最後の --- より前が本文
    body = '\n---\n'.join(parts[1:-1]).strip()
elif len(parts) == 2:
    body = parts[1].strip()
else:
    body = raw.strip()

fixed_str = open('fixed_numbers.txt').read().strip()
new_findings = open('new_findings.md').read().strip()

fixed_nums = [n.strip() for n in fixed_str.split(',') if n.strip()] if fixed_str else []

# 既存コメントをアクティブ部分と修正済み部分に分割
if '### ✅ 修正済み' in body:
    active_part, resolved_part = body.split('### ✅ 修正済み', 1)
    # 既存の修正済み内容を取得（「なし」以外）
    resolved_content = resolved_part.strip()
    if resolved_content.startswith('\n'):
        resolved_content = resolved_content[1:]
    # 「なし」だけの場合は空にする
    if resolved_content.strip() == 'なし':
        resolved_items = []
    else:
        resolved_items = [resolved_content.strip()] if resolved_content.strip() else []
else:
    active_part = body
    resolved_items = []

# 修正済み番号の指摘をアクティブ部分から抽出して修正済みに移動
newly_resolved = []
updated_active = active_part

for num in fixed_nums:
    # **N.** から始まる指摘ブロックを抽出
    pattern = re.compile(
        r'([🔴🟠🟡🟢] \*\*' + re.escape(num) + r'\.\*\* .+?)(?=\n[🔴🟠🟡🟢] \*\*\d+\.\*\*|\n### |\n---|\Z)',
        re.DOTALL
    )
    match = pattern.search(updated_active)
    if match:
        finding_text = match.group(1).strip()
        # 取り消し線を付けて修正済みに追加
        first_line = finding_text.split('\n')[0]
        resolved_line = re.sub(
            r'(\*\*' + re.escape(num) + r'\.\*\*)',
            r'~~\1~~',
            first_line
        ) + ' ✅'
        newly_resolved.append(resolved_line)
        # アクティブ部分から削除
        updated_active = updated_active[:match.start()] + updated_active[match.end():]

# 新規指摘をアクティブ部分に追加
# 既存の最大番号を取得
existing_nums = re.findall(r'\*\*(\d+)\.\*\*', updated_active)
max_num = max([int(n) for n in existing_nums], default=0)

# 新規指摘の番号を振り直す（もし番号が重複する場合）
if new_findings and new_findings.strip() not in ('なし', ''):
    # 新規指摘の番号を調整
    counter = max_num + 1
    def renumber(m):
        global counter
        result = m.group(0).replace(m.group(1), str(counter))
        counter += 1
        return result

    new_findings_renumbered = re.sub(
        r'([🔴🟠🟡🟢]) \*\*\d+\.\*\*',
        lambda m: m.group(0),
        new_findings
    )

    # カテゴリ別に分けて既存のカテゴリセクションに追加
    for category, alert, emoji in [
        ('Critical', 'CAUTION', '🔴'),
        ('Major', 'WARNING', '🟠'),
        ('Minor', 'NOTE', '🟡'),
        ('Suggestion', 'TIP', '🟢'),
    ]:
        cat_findings = re.findall(
            rf'{re.escape(emoji)} \*\*\d+\.\*\*.*?(?=\n[🔴🟠🟡🟢] \*\*\d+\.\*\*|\n> \[!|\n---|\Z)',
            new_findings_renumbered,
            re.DOTALL
        )
        if cat_findings:
            # 既存のカテゴリセクションに追加
            section_pattern = re.compile(
                rf'(> \[!{alert}\].*?> 🔴|🟠|🟡|🟢 \*\*{category}.*?\n)(なし|\n)',
                re.DOTALL
            )
            for finding in cat_findings:
                finding_clean = finding.strip()
                # 「なし」を実際の指摘に置き換える、またはセクションに追記
                updated_active = re.sub(
                    rf'(> \[!{alert}\]\n> [^\n]+\n\nなし)',
                    rf'\1\n\n{finding_clean}',
                    updated_active
                )
                if finding_clean not in updated_active:
                    # セクションの末尾に追記
                    insert_pattern = re.compile(
                        rf'(> \[!{alert}\]\n> [^\n]+\n\n)(.*?)(\n\n> \[!|\n\n---)',
                        re.DOTALL
                    )
                    def insert_finding(m):
                        existing = m.group(2).strip()
                        return m.group(1) + existing + '\n\n' + finding_clean + m.group(3)
                    updated_active = insert_pattern.sub(insert_finding, updated_active, count=1)

# 修正済みセクションを再構成
all_resolved = resolved_items + newly_resolved
resolved_section = '### ✅ 修正済み\n\n'
if all_resolved:
    resolved_section += '\n'.join(all_resolved)
else:
    resolved_section += 'なし'

# 最終的なコメントを組み立て
# サマリーの件数を更新
active_nums = re.findall(r'\*\*(\d+)\.\*\*(?!.*~~)', updated_active)
critical_count = len(re.findall(r'🔴 \*\*\d+\.\*\*', updated_active))
major_count = len(re.findall(r'🟠 \*\*\d+\.\*\*', updated_active))
minor_count = len(re.findall(r'🟡 \*\*\d+\.\*\*', updated_active))
suggestion_count = len(re.findall(r'🟢 \*\*\d+\.\*\*', updated_active))

# サマリーテーブルを更新
def update_summary(text):
    text = re.sub(r'\| 🔴 Critical \| \d+件 \|', f'| 🔴 Critical | {critical_count}件 |', text)
    text = re.sub(r'\| 🟠 Major \| \d+件 \|', f'| 🟠 Major | {major_count}件 |', text)
    text = re.sub(r'\| 🟡 Minor \| \d+件 \|', f'| 🟡 Minor | {minor_count}件 |', text)
    text = re.sub(r'\| 🟢 Suggestion \| \d+件 \|', f'| 🟢 Suggestion | {suggestion_count}件 |', text)
    return text

updated_active = update_summary(updated_active)

# コメント全体を再構成
final = updated_active.rstrip() + '\n\n---\n\n' + resolved_section

open('updated_comment.md', 'w').write(final)
print(f"修正済み: {fixed_nums}, 新規追加: {bool(new_findings and new_findings.strip() not in ('なし', ''))}")
