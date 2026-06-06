"""
pr.diff を読み込み、各変更行に実際の行番号を付与した
annotated_diff.txt を出力する。

例:
  -[L42] let value = some_result.unwrap();
  +[L42] let value = some_result?;
"""
import re
import sys

diff = open('pr.diff').read()
output = []
current_file = ''
new_line = 0

for line in diff.splitlines():
    # ファイルヘッダー
    if line.startswith('+++ b/'):
        current_file = line[6:]
        output.append(line)
        continue
    if line.startswith('---') or line.startswith('+++') or line.startswith('diff ') or line.startswith('index '):
        output.append(line)
        continue

    # hunkヘッダー: @@ -old_start,old_count +new_start,new_count @@
    hunk_match = re.match(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
    if hunk_match:
        new_line = int(hunk_match.group(1))
        output.append(line)
        continue

    # 変更行に行番号を付与
    if line.startswith('+'):
        output.append(f'+[L{new_line}] {line[1:]}')
        new_line += 1
    elif line.startswith('-'):
        output.append(f'-[L?] {line[1:]}')  # 削除行はnew側に行番号なし
    elif line.startswith(' '):
        output.append(f' [L{new_line}] {line[1:]}')
        new_line += 1
    else:
        output.append(line)

open('annotated_diff.txt', 'w').write('\n'.join(output))
print(f"annotated_diff.txt を作成しました ({len(output)} 行)")
