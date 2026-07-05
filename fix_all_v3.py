#!/usr/bin/env python3
"""修复 index.html v2.5 - 完整版
1. 将A股SBI卡片移到新面板 panel-semi-cn
2. 将美股SBI卡片移到新面板 panel-semi-us
3. 补充港股PCT报告
4. 更新侧边栏、validCats、tabConfig
"""

import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 1. 提取A股SBI卡片 → 创建 panel-semi-cn
# ============================================================
# 找 panel-china 中 grid 里的SBI卡片
# SBI卡片特征：card-icon背景 #0f2040，标题含"A股半导体SBI泡沫指数"

# 找 panel-china 的 grid 结束位置（在 <!-- 港股 --> 之前）
idx_panel_china = content.find('id="panel-china"')
idx_hk_comment = content.find('<!-- 港股 -->', idx_panel_china)

# 在 panel-china 范围内找所有SBI卡片
sbi_cn_cards = []
temp_idx = idx_panel_china
while True:
    idx = content.find('A股半导体SBI泡沫指数', temp_idx, idx_hk_comment)
    if idx == -1:
        break
    # 找这张卡片的起始 <div class="card">
    card_start = content.rfind('<div class="card">', temp_idx, idx)
    if card_start == -1:
        break
    # 找这张卡片的结束 </a> 后的 </div>
    card_end = content.find('</a>\n    </div>\n', card_start, idx_hk_comment)
    if card_end == -1:
        break
    card_end += len('</a>\n    </div>\n')
    sbi_cn_cards.append(content[card_start:card_end])
    temp_idx = card_end

print(f"找到 {len(sbi_cn_cards)} 个A股SBI卡片")

if sbi_cn_cards:
    # 创建 panel-semi-cn
    semi_cn_html = '''
<!-- A股半导体热度 -->
<div class="panel" id="panel-semi-cn">
  <div class="section-hd">
    <h2>A股半导体热度</h2>
    <span class="muted">每日更新 · SBI泡沫指数</span>
  </div>
  <div class="grid">
'''
    for card in sbi_cn_cards:
        # 修复卡片缩进
        card_lines = card.split('\n')
        padded = '\n'.join('    ' + l if l.strip() else l for l in card_lines)
        semi_cn_html += padded + '\n'
    semi_cn_html += '  </div>\n</div><!-- /panel-semi-cn -->\n'
    
    # 插入到 panel-china 结束后（<!-- 港股 --> 之前）
    insert_pos = idx_hk_comment
    content = content[:insert_pos] + semi_cn_html + content[insert_pos:]
    
    # 从 panel-china 中删除SBI卡片
    for card in sbi_cn_cards:
        card_lines = card.split('\n')
        padded = '\n'.join('    ' + l if l.strip() else l for l in card_lines)
        padded = padded + '\n'
        content = content.replace(padded, '', 1)
    
    print(f"✓ 创建 panel-semi-cn 并移除了 {len(sbi_cn_cards)} 个SBI卡片")

# ============================================================
# 2. 提取美股SBI卡片 → 创建 panel-semi-us
# ============================================================
idx_panel_us = content.find('id="panel-us"')
idx_macro_comment = content.find('<!-- 宏观周记 -->', idx_panel_us)

sbi_us_cards = []
temp_idx = idx_panel_us
while True:
    idx = content.find('美股半导体硬件SBI泡沫指数', temp_idx, idx_macro_comment)
    if idx == -1:
        break
    card_start = content.rfind('<div class="card">', temp_idx, idx)
    if card_start == -1:
        break
    card_end = content.find('</a>\n      </div>\n', card_start, idx_macro_comment)
    if card_end == -1:
        # 尝试其他格式
        card_end = content.find('</a>\n    </div>\n', card_start, idx_macro_comment)
    if card_end == -1:
        break
    # 找结束的 </div>
    end_tag = content.find('</div>\n', card_end)
    if end_tag == -1:
        break
    card_end = end_tag + len('</div>\n')
    sbi_us_cards.append(content[card_start:card_end])
    temp_idx = card_end

print(f"找到 {len(sbi_us_cards)} 个美股SBI卡片")

if sbi_us_cards:
    semi_us_html = '''
<!-- 美国半导体热度 -->
<div class="panel" id="panel-semi-us">
  <div class="section-hd">
    <h2>美国半导体热度</h2>
    <span class="muted">每日更新 · SBI泡沫指数</span>
  </div>
  <div class="grid">
'''
    for card in sbi_us_cards:
        card_lines = card.split('\n')
        padded = '\n'.join('    ' + l if l.strip() else l for l in card_lines)
        semi_us_html += padded + '\n'
    semi_us_html += '  </div>\n</div><!-- /panel-semi-us -->\n'
    
    insert_pos = idx_macro_comment
    content = content[:insert_pos] + semi_us_html + content[insert_pos:]
    
    for card in sbi_us_cards:
        card_lines = card.split('\n')
        padded = '\n'.join('    ' + l if l.strip() else l for l in card_lines)
        padded = padded + '\n'
        content = content.replace(padded, '', 1)
    
    print(f"✓ 创建 panel-semi-us 并移除了 {len(sbi_us_cards)} 个SBI卡片")

# ============================================================
# 3. 补充港股PCT报告
# ============================================================
pct_card = '''
    <div class="card">
      <div class="card-top">
        <div class="card-icon" style="background:#dbeafe;color:#1d4ed;">HK</div>
        <div>
          <div class="card-title">PCT（栢能集团，0999.HK）投资研究报告</div>
          <div class="card-sub">2026年7月1日 · 最新</div>
        </div>
      </div>
      <div class="card-desc">PCT（栢能集团）深度投研报告，覆盖AI算力产业链、估值分析、风险提示。</div>
      <div class="card-tags"><span class="tag">港股</span><span class="tag">科技互联网</span><span class="tag">AI算力</span><span class="tag">最新</span></div>
      <a class="card-btn" href="PCT_投资研究报告_SnailBird.html">阅读报告</a>
    </div>
'''

if 'PCT_投资研究报告' not in content:
    # 找到港股面板中科技互联网的 grid
    idx_hk = content.find('id="panel-hk"')
    idx_hk_grid = content.find('<div class="grid">', idx_hk)
    if idx_hk_grid != -1:
        # 插入到 grid 结束后（第一个 </div> 前）
        grid_end = content.find('  </div>\n', idx_hk_grid)
        # 找科技互联网 sector-group 的 grid
        idx_tech = content.find('科技互联网', idx_hk)
        if idx_tech != -1:
            idx_tech_grid = content.find('<div class="grid">', idx_tech)
            if idx_tech_grid != -1:
                # 在 grid 里的第一个 </div> 前插入
                insert_pos = content.find('\n', idx_tech_grid) + 1
                # 找 grid 中第一个卡片后的位置
                first_card_end = content.find('</a>\n    </div>\n', idx_tech_grid)
                if first_card_end != -1:
                    insert_pos = content.find('\n', first_card_end) + 1
                    content = content[:insert_pos] + pct_card + content[insert_pos:]
                    print("✓ 添加PCT报告到港股科技互联网板块")
                else:
                    print("WARNING: 未找到港股科技互联网卡片结束位置")
            else:
                print("WARNING: 未找到港股科技互联网grid")
        else:
            print("WARNING: 未找到港股科技互联网sector")
    else:
        print("WARNING: 未找到港股panel的grid")
else:
    print("PCT报告已存在，跳过")

# ============================================================
# 4. 更新侧边栏导航
# ============================================================
# 在 "美股" 和 "宏观周记" 之间添加半导体热度子菜单
# 先检查是否已有 semi-cn 和 semi-us 链接
if 'data-cat="semi-cn"' not in content:
    # 在 sidebar 的 us nav-item 后添加子菜单
    # 找美股 nav-item
    us_nav_pattern = r'(<a href="#" class="nav-item" data-cat="us"[^>]*>.*?</a>)'
    # 简化：直接找 </a> 后的 </div> 关闭 nav-item
    # 实际HTML结构：nav-item 后可能有 nav-sub
    # 让我直接检查 sidebar 结构
    print("INFO: 需要手动添加侧边栏半导体热度链接")

# ============================================================
# 5. 更新 JS validCats 和 tabConfig
# ============================================================
# 更新 validCats
old_valid = "const validCats = ['china','hk','us','macro'];"
new_valid = "const validCats = ['china','hk','us','macro','semi-cn','semi-us','research'];"
if old_valid in content:
    content = content.replace(old_valid, new_valid)
    print("✓ 更新 validCats")
else:
    print(f"WARNING: 未找到 validCats 定义，当前内容: {content[content.find('validCats'):content.find('validCats')+80]}")

# 更新 tabConfig 添加 semi-cn 和 semi-us
tab_config_semi = '''
  'semi-cn': [
    {text:'SBI泡沫指数', target:'panel-semi-cn', active:true},
  ],
  'semi-us': [
    {text:'SBI泡沫指数', target:'panel-semi-us', active:true},
  ],
'''
if "'semi-cn'" not in content:
    # 在 research 配置后添加
    content = content.replace(
        "  research: [\n    {text:'深度研究', target:'panel-research', active:true},\n  ],",
        "  research: [\n    {text:'深度研究', target:'panel-research', active:true},\n  ]," + tab_config_semi
    )
    print("✓ 更新 tabConfig 添加 semi-cn 和 semi-us")

# ============================================================
# 保存
# ============================================================
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ 修复完成！请检查 index.html")
