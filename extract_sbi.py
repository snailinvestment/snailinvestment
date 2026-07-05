"""
将A股和美股中的SBI section提取为独立面板。
基于v2.5（干净6月28日版本 + PCT + validCats修复）
"""

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. 提取A股SBI section (L383-L561, 0-indexed: 382-560)
semi_cn_start = 382  # <div class="section-hd" id="semi-cn-section"
semi_cn_end = 560     # 最后一个</div>

semi_cn_lines = lines[semi_cn_start:semi_cn_end+1]
print(f"提取A股SBI: L{semi_cn_start+1} ~ L{semi_cn_end+1} ({len(semi_cn_lines)}行)")

# 2. 提取美股SBI section (L1101-L1265, 0-indexed: 1100-1264)
# 注意：删除A股SBI后行号会变，所以先处理美股
semi_us_start = 1100
semi_us_end = 1264

semi_us_lines = lines[semi_us_start:semi_us_end+1]
print(f"提取美股SBI: L{semi_us_start+1} ~ L{semi_us_end+1} ({len(semi_us_lines)}行)")

# 3. 构建新的面板HTML
def build_semi_panel(panel_id, title, subtitle, semi_html_lines):
    """将section-hd+grid包装为独立panel"""
    # 去掉原来的section-hd和它的关闭标签（前几行），保留grid内容
    # semi_html_lines[0] 是 <div class="section-hd" ...>
    # 找到第一个 </div>\n 后面的内容就是grid开始
    
    # 找grid开始位置（跳过section-hd）
    grid_start = None
    for i, line in enumerate(semi_html_lines):
        if '<div class="grid">' in line:
            grid_start = i
            break
    
    if grid_start is None:
        print("ERROR: 没找到grid!")
        return ""
    
    grid_content = semi_html_lines[grid_start:]
    
    panel_html = f'''
<!-- {title} -->
<div class="panel" id="{panel_id}">
  <div class="section-hd">
    <h2>{title}</h2>
    <span class="muted">{subtitle}</span>
  </div>
{''.join(grid_content)}
</div>
<!-- /{panel_id} -->
'''
    return panel_html

semi_cn_panel = build_semi_panel(
    "panel-semi-cn",
    "A股半导体热度",
    "每日更新 · 覆盖设计/制造/设备/材料全产业链",
    semi_cn_lines
)

semi_us_panel = build_semi_panel(
    "panel-semi-us",
    "美国半导体热度",
    "每日更新 · 覆盖GPU/网络/存储/制造全产业链",
    semi_us_lines
)

print(f"\nA股半导体面板: {len(semi_cn_panel)} 字符")
print(f"美国半导体面板: {len(semi_us_panel)} 字符")

# 4. 从原位置删除两个section（先删后面的，避免行号偏移）

# 删除美股SBI section (先删，因为行号更大)
del lines[semi_us_start:semi_us_end+1]
print(f"\n已删除美股SBI: 原L{semi_us_start+1}-L{semi_us_end+1}")

# 删除A股SBI section
del lines[semi_cn_start:semi_cn_end+1]
print(f"已删除A股SBI: 原L{semi_cn_start+1}-L{semi_cn_end+1}")

# 5. 在 </div><!-- /content --> 之前插入两个新面板
# 找到 /content 的位置
insert_pos = None
for i, line in enumerate(lines):
    if '</content>' in line or '/content' in line and '<' in line:
        insert_pos = i
        break

if insert_pos is None:
    # 备选：找 /main-wrap 或 </div></body>
    for i, line in enumerate(lines):
        if '</main-wrap>' in line or '/main-wrap' in line:
            insert_pos = i
            break

if insert_pos is None:
    print("ERROR: 找不到插入位置!")
else:
    # 在 /content 注释之前插入
    lines.insert(insert_pos, semi_us_panel)
    lines.insert(insert_pos, semi_cn_panel)
    print(f"\n在L{insert_pos+1}前插入了两个新面板")

# 6. 写回文件
with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("\nDone! 文件已更新。")
