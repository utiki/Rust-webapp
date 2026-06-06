import re
 
body = open('first_review_full.md').read()
fixed_str = open('fixed_numbers.txt').read().strip()
new_findings = open('new_findings.md').read().strip()
 
if fixed_str:
    for n in fixed_str.split(','):
        n = n.strip()
        if n:
            body = re.sub(
                r'(\*\*' + re.escape(n) + r'\.\*\*)',
                r'~~\1~~ ✅ 修正済み',
                body
            )
 
if new_findings and new_findings.strip() != 'なし':
    body += '\n\n---\n\n### 🆕 新規指摘\n\n' + new_findings
 
open('updated_first_review.md', 'w').write(body)
 
