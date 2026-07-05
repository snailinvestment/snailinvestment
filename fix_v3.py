"""
修复脚本：
1. 提取A股面板中的所有SBI卡片，移动到 panel-semi-cn 的 grid 中
2. 提取美股面板中的所有SBI卡片，移动到 panel-semi-us 的 grid 中
3. 清理原位置的 SBI section-hd 和卡片
"""

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# === Step 1: 找 A 股 SBI 卡片范围 ===
# 找到 "A股半导体热度" 的 section-hd (semi-cn-section)
semi_cn_section_start = None  # section-hd 行
semi_cn_grid_start = None   # grid 开始行
semi_cn_cards_end = None     # 最后一张 SBI 卡片结束行
# 新的 panel-semi-cn grid 位置
new_semi_cn_grid_line = None  # panel-semi-cn 内的空 grid 行

for i, line in enumerate(lines):
    if 'id="semi-cn-section"' in line:
        semi_cn_section_start = i
    if semi_cn_section_start and i > semi_cn_section_start and '<div class="grid">' in line:
        if semi_cn_grid_start is None:
            semi_cn_grid_start = i
    # 找新 panel-semi-cn 的空 grid
    if '<div class="panel" id="panel-semi-cn">' in line:
        for j in range(i+1, min(i+10, len(lines))):
            if '<div class="grid">' in lines[j]:
                new_semi_cn_grid_line = j
                break

# 找最后一张 SBI 卡片的 </div> - 在 <!-- A股半导体热度 --> 注释之前
for i in range(semi_cn_grid_start or 0, len(lines)):
    if '<!-- A股半导体热度 -->' in lines[i] and i > (semi_cn_grid_start or 0):
        # 往回找最后一个 card 关闭标签
        for j in range(i-1, (semi_cn_grid_start or 0), -1):
            stripped = lines[j].strip()
            if stripped == '</div>' and j > (semi_cn_grid_start or 0) + 5:
                # 验证这确实是一个 card 结束（前面应该有 card-btn 或 card-tags）
                for k in range(j-1, max(j-20, 0), -1):
                    if 'card-btn' in lines[k] or 'card-tags' in lines[k]:
                        semi_cn_cards_end = j
                        break
                if semi_cn_cards_end:
                    break
        break

print(f"A股 SBI: section_hd={semi_cn_section_start}, grid={semi_cn_grid_start}, cards_end={semi_cn_cards_end}")
print(f"新 panel-semi-cn grid at line: {new_semi_cn_grid_line}")

# === Step 2: 找美股 SBI 卡片范围 ===
semi_us_section_start = None
semi_us_grid_start = None
semi_us_cards_end = None
new_semi_us_grid_line = None

for i, line in enumerate(lines):
    if 'id="semi-us-section"' in line:
        semi_us_section_start = i
    if semi_us_section_start and i > semi_us_section_start and '<div class="grid">' in line:
        if semi_us_grid_start is None:
            semi_us_grid_start = i
    if '<div class="panel" id="panel-semi-us">' in line:
        for j in range(i+1, min(i+10, len(lines))):
            if '<div class="grid">' in lines[j]:
                new_semi_us_grid_line = j
                break

for i in range(semi_us_grid_start or 0, len(lines)):
    if '<!-- 美国半导体热度 -->' in lines[i] and i > (semi_us_grid_start or 0):
        for j in range(i-1, (semi_us_grid_start or 0), -1):
            stripped = lines[j].strip()
            if stripped == '</div>' and j > (semi_us_grid_start or 0) + 5:
                for k in range(j-1, max(j-20, 0), -1):
                    if 'card-btn' in lines[k] or 'card-tags' in lines[k]:
                        semi_us_cards_end = j
                        break
                if semi_us_cards_end:
                    break
        break

print(f"美股 SBI: section_hd={semi_us_section_start}, grid={semi_us_grid_start}, cards_end={semi_us_cards_end}")
print(f"新 panel-semi-us grid at line: {new_semi_us_grid_line}")

# === Step 3: 提取并移动卡片 ===

# 提取A股SBI卡片内容（从grid内的第一个card到最后一个</div>）
cn_sbi_cards_lines = []
in_cards = False
for i in range((semi_cn_grid_start or 0) + 1, (semi_cn_cards_end or 0) + 1):
    cn_sbi_cards_lines.append(lines[i])

# 提取美股SBI卡片内容
us_sbi_cards_lines = []
for i in range((semi_us_grid_start or 0) + 1, (semi_us_cards_end or 0) + 1):
    us_sbi_cards_lines.append(lines[i])

print(f"\n提取了 {len(cn_sbi_cards_lines)} 行A股SBI卡片")
print(f"提取了 {len(us_sbi_cards_lines)} 行美股SBI卡片")

# === Step 4: 构建新文件 ===

new_lines = []

# Part 1: 文件开头到 semi-cn-section 之前（保留A股非SBI内容）
for i in range(0, semi_cn_section_start):
    new_lines.append(lines[i])

# 跳过整个 semi-cn-section（section-hd + grid + 所有SBI卡片）直到 <!-- A股半导体热度 -->
# 找到 <!-- A股半导体热度 --> 注释的位置
semi_cn_comment_line = None
for i in range(semi_cn_cards_end or 0, len(lines)):
    if '<!-- A股半导体热度 -->' in lines[i]:
        semi_cn_comment_line = i
        break

print(f"\n<!-- A股半导体热度 --> 注释在行: {semi_cn_comment_line}")

# 从 semi_cn_comment_line 到文件末尾继续处理
i = semi_cn_comment_line or semi_cn_cards_end
while i < len(lines):
    line = lines[i]
    
    # 在新的 panel-semi-cn 的空 grid 里插入A股SBI卡片
    if i == new_semi_cn_grid_line:
        new_lines.append(line)  # <div class="grid">
        # 缩进插入卡片（每个卡片加4个空格缩进）
        for cl in cn_sbi_cards_lines:
            if cl.strip():  # 非空行加缩进
                new_lines.append('    ' + cl if not cl.startswith(' ') else '  ' + cl)
            else:
                new_lines.append('')
        new_lines.append('  </div>\n')  # 关闭 grid
        i += 1
        continue
    
    # 在新的 panel-semi-us 的空 grid 里插入美股SBI卡片
    if i == new_semi_us_grid_line:
        new_lines.append(line)  # <div class="grid">
        for cl in us_sbi_cards_lines:
            if cl.strip():
                new_lines.append('    ' + cl if not cl.startswith(' ') else '  ' + cl)
            else:
                new_lines.append('')
        new_lines.append('  </div>\n')  # 关闭 grid
        i += 1
        continue
    
    new_lines.append(line)
    i += 1

# 写入新文件
with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("\n✅ 文件已更新！")
