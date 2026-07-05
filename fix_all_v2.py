#!/usr/bin/env python3
"""
修复 index.html v2.5 (June 28 base) 的4个问题：
1. 将A股面板中的半导体SBI卡片移到新面板 panel-semi-cn
2. 将美股面板中的半导体SBI卡片移到新面板 panel-semi-us  
3. 补充港股PCT报告到科技互联网 sector-group
4. 更新侧边栏、validCats、tabConfig
"""

from bs4 import BeautifulSoup, NavigableString
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

# ============================================================
# 1. 从 panel-china 提取A股SBI卡片 → 创建 panel-semi-cn
# ============================================================
panel_china = soup.find('div', id='panel-china')
if panel_china:
    # 找 panel-china 里的 grid
    grid = panel_china.find('div', class_='grid')
    if grid:
        # 找所有包含 "A股半导体SBI泡沫指数" 的卡片
        sbi_cards = []
        for card in grid.find_all('div', class_='card', recursive=False):
            title = card.find(class_='card-title')
            if title and 'A股半导体SBI泡沫指数' in title.text:
                sbi_cards.append(card.extract())  # 从原grid中移除
        
        if sbi_cards:
            # 创建新面板 panel-semi-cn
            semi_cn_panel = soup.new_tag('div')
            semi_cn_panel['class'] = 'panel'
            semi_cn_panel['id'] = 'panel-semi-cn'
            
            # 添加 section header
            section_hd = soup.new_tag('div')
            section_hd['class'] = 'section-hd'
            h2 = soup.new_tag('h2')
            h2.string = 'A股半导体热度'
            muted = soup.new_tag('span')
            muted['class'] = 'muted'
            muted.string = '每日更新 · SBI泡沫指数'
            section_hd.append(h2)
            section_hd.append(muted)
            semi_cn_panel.append(section_hd)
            
            # 添加 grid 并放入SBI卡片
            new_grid = soup.new_tag('div')
            new_grid['class'] = 'grid'
            for card in sbi_cards:
                new_grid.append(card)
            semi_cn_panel.append(new_grid)
            
            # 将新面板插入到 panel-china 之后
            panel_china.insert_after(semi_cn_panel)
            print(f"✓ 创建 panel-semi-cn，移动了 {len(sbi_cards)} 个A股SBI卡片")
        else:
            print("WARNING: 未找到A股SBI卡片")
    else:
        print("ERROR: panel-china 中未找到 grid")
else:
    print("ERROR: 未找到 panel-china")

# ============================================================
# 2. 从 panel-us 提取美股SBI卡片 → 创建 panel-semi-us
# ============================================================
panel_us = soup.find('div', id='panel-us')
if panel_us:
    # 在 panel-us 中找 "美国半导体热度" 标题，然后提取其后的卡片
    # 实际上SBI卡片在 panel-us 的一个独立 section 中
    # 找所有包含 "美股半导体硬件SBI泡沫指数" 的卡片
    sbi_us_cards = []
    
    # 遍历 panel-us 中的所有 grid 的 card
    for grid in panel_us.find_all('div', class_='grid', recursive=True):
        cards_to_remove = []
        for card in grid.find_all('div', class_='card', recursive=False):
            title = card.find(class_='card-title')
            if title and ('美股半导体硬件SBI泡沫指数' in title.text or '美股硬件/半导体' in card.text):
                cards_to_remove.append(card)
        for card in cards_to_remove:
            sbi_us_cards.append(card.extract())
    
    if sbi_us_cards:
        # 创建新面板 panel-semi-us
        semi_us_panel = soup.new_tag('div')
        semi_us_panel['class'] = 'panel'
        semi_us_panel['id'] = 'panel-semi-us'
        
        section_hd = soup.new_tag('div')
        section_hd['class'] = 'section-hd'
        h2 = soup.new_tag('h2')
        h2.string = '美国半导体热度'
        muted = soup.new_tag('span')
        muted['class'] = 'muted'
        muted.string = '每日更新 · SBI泡沫指数'
        section_hd.append(h2)
        section_hd.append(muted)
        semi_us_panel.append(section_hd)
        
        new_grid = soup.new_tag('div')
        new_grid['class'] = 'grid'
        for card in sbi_us_cards:
            new_grid.append(card)
        semi_us_panel.append(new_grid)
        
        # 插入到 panel-us 之后
        panel_us.insert_after(semi_us_panel)
        print(f"✓ 创建 panel-semi-us，移动了 {len(sbi_us_cards)} 个美股SBI卡片")
    else:
        print("WARNING: 未找到美股SBI卡片")
else:
    print("ERROR: 未找到 panel-us")

# ============================================================
# 3. 补充港股PCT报告到科技互联网 sector-group
# ============================================================
panel_hk = soup.find('div', id='panel-hk')
if panel_hk:
    # 找 "科技互联网" sector-group
    sector_groups = panel_hk.find_all('div', class_='sector-group')
    tech_sector = None
    for sg in sector_groups:
        hd = sg.find('div', class_='sector-hd')
        if hd and '科技互联网' in hd.text:
            tech_sector = sg
            break
    
    if tech_sector:
        # 检查PCT报告是否已存在
        existing = tech_sector.find(text=re.compile('PCT|栢能集团', re.I))
        if not existing:
            # 创建PCT报告卡片
            pct_card = soup.new_tag('div')
            pct_card['class'] = 'card'
            
            card_top = soup.new_tag('div')
            card_top['class'] = 'card-top'
            
            card_icon = soup.new_tag('div')
            card_icon['class'] = 'card-icon'
            card_icon['style'] = 'background:#dbeafe;color:#1d4ed;'
            card_icon.string = 'HK'
            
            card_top_right = soup.new_tag('div')
            card_title = soup.new_tag('div')
            card_title['class'] = 'card-title'
            card_title.string = 'PCT（栢能集团，0999.HK）投资研究报告'
            card_sub = soup.new_tag('div')
            card_sub['class'] = 'card-sub'
            card_sub.string = '2026年7月1日 · 最新'
            
            card_top_right.append(card_title)
            card_top_right.append(card_sub)
            card_top.append(card_icon)
            card_top.append(card_top_right)
            
            card_desc = soup.new_tag('div')
            card_desc['class'] = 'card-desc'
            card_desc.string = 'PCT（栢能集团）深度投研报告，覆盖AI算力产业链、估值分析、风险提示。'
            
            card_tags = soup.new_tag('div')
            card_tags['class'] = 'card-tags'
            for tag_text in ['港股', '科技互联网', 'AI算力', '最新']:
                tag = soup.new_tag('span')
                tag['class'] = 'tag'
                tag.string = tag_text
                card_tags.append(tag)
            
            card_btn = soup.new_tag('a')
            card_btn['class'] = 'card-btn'
            card_btn['href'] = 'PCT_投资研究报告_SnailBird.html'
            card_btn.string = '阅读报告'
            
            pct_card.append(card_top)
            pct_card.append(card_desc)
            pct_card.append(card_tags)
            pct_card.append(card_btn)
            
            # 插入到 tech_sector 的 grid 中
            grid = tech_sector.find('div', class_='grid')
            if grid:
                grid.insert(0, pct_card)
                print("✓ 添加PCT报告到港股科技互联网板块")
            else:
                # 创建grid
                new_grid = soup.new_tag('div')
                new_grid['class'] = 'grid'
                new_grid.append(pct_card)
                tech_sector.append(new_grid)
                print("✓ 添加PCT报告到港股科技互联网板块（新建grid）")
        else:
            print("PCT报告已存在，跳过")
    else:
        print("WARNING: 未找到港股科技互联网sector-group")
else:
    print("ERROR: 未找到 panel-hk")

# ============================================================
# 4. 更新侧边栏导航
# ============================================================
sidebar_nav = soup.find('div', id='sidebarNav')
if sidebar_nav:
    # 在 "美股" 和 "宏观周记" 之间添加 "A股半导体热度" 和 "美国半导体热度"
    # 先找 id="us-link" 的 nav-item
    us_nav = sidebar_nav.find('a', attrs={'data-cat': 'us'})
    if us_nav:
        # 创建A股半导体热度链接（作为子菜单）
        # 实际上应该作为 "A股" 的子项，或作为独立项
        # 根据之前的设计，半导体热度是作为子菜单存在的
        # 让我检查现有结构
        print("INFO: 侧边栏现有结构需要手动调整")
    
    # 检查是否已有 semi-cn 和 semi-us 链接
    existing_semi = sidebar_nav.find('a', attrs={'data-cat': 'semi-cn'})
    if not existing_semi:
        print("WARNING: 侧边栏缺少 semi-cn 链接，需要手动添加")
else:
    print("ERROR: 未找到 sidebarNav")

# ============================================================
# 5. 更新 JS validCats 和 tabConfig
# ============================================================
# 在 </script> 之前更新
script_tag = soup.find('script')
if script_tag and script_tag.string:
    js = script_tag.string
    
    # 更新 validCats
    js = re.sub(r"const validCats = \[.*?\];", 
                "const validCats = ['china','hk','us','macro','semi-cn','semi-us','research'];", 
                js, flags=re.DOTALL)
    
    # 更新 tabConfig 添加 semi-cn 和 semi-us
    # 检查是否已有 semi-cn 配置
    if "'semi-cn'" not in js:
        # 在 tabConfig 中添加
        js = js.replace(
            "  us: [\n    {text:'深度投研', target:'panel-us', active:true},\n    {text:'半导体热度', target:'semi-us-section'},\n  ],",
            "  us: [\n    {text:'深度投研', target:'panel-us', active:true},\n    {text:'半导体热度', target:'panel-semi-us'},\n  ],\n  'semi-cn': [\n    {text:'SBI泡沫指数', target:'panel-semi-cn', active:true},\n  ],\n  'semi-us': [\n    {text:'SBI泡沫指数', target:'panel-semi-us', active:true},\n  ],"
        )
    
    script_tag.string = js
    print("✓ 更新 validCats 和 tabConfig")
else:
    print("WARNING: 未找到 script 标签或内容为空")

# 保存
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))

print("\n✅ 修复完成！请检查 index.html")
