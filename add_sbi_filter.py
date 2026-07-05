import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# ===== 1. 在A股SBI grid前插入月份筛选栏 =====
filter_bar_cn = '''  <div class="sbi-filter-bar" id="sbi-filter-cn" style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;">
    <button class="sbi-filter-btn active" onclick="filterSBICards('cn','all',this)" style="padding:6px 16px;border-radius:20px;border:1px solid #2563eb;background:#2563eb;color:#fff;cursor:pointer;font-size:13px;">全部</button>
    <button class="sbi-filter-btn" onclick="filterSBICards('cn','2026-07',this)" style="padding:6px 16px;border-radius:20px;border:1px solid #2563eb;background:transparent;color:#2563eb;cursor:pointer;font-size:13px;">2026年7月</button>
    <button class="sbi-filter-btn" onclick="filterSBICards('cn','2026-06',this)" style="padding:6px 16px;border-radius:20px;border:1px solid #2563eb;background:transparent;color:#2563eb;cursor:pointer;font-size:13px;">2026年6月</button>
  </div>
'''

# 找A股SBI grid位置
pattern_cn = r'(<h2>A股半导体热度</h2>\s*<span[^>]*>每日更新[^<]*</span>\s*</div>\s*<div class="grid">)'
m_cn = re.search(pattern_cn, c)
if m_cn:
    pos = m_cn.end()
    c = c[:pos] + '\n' + filter_bar_cn + c[pos:]
    print('[OK] A股SBI月份筛选栏已插入')
else:
    print('[FAIL] 找不到A股SBI grid')

# ===== 2. 在美股SBI grid前插入月份筛选栏 =====
filter_bar_us = '''  <div class="sbi-filter-bar" id="sbi-filter-us" style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;">
    <button class="sbi-filter-btn active" onclick="filterSBICards('us','all',this)" style="padding:6px 16px;border-radius:20px;border:1px solid #2563eb;background:#2563eb;color:#fff;cursor:pointer;font-size:13px;">全部</button>
    <button class="sbi-filter-btn" onclick="filterSBICards('us','2026-07',this)" style="padding:6px 16px;border-radius:20px;border:1px solid #2563eb;background:transparent;color:#2563eb;cursor:pointer;font-size:13px;">2026年7月</button>
    <button class="sbi-filter-btn" onclick="filterSBICards('us','2026-06',this)" style="padding:6px 16px;border-radius:20px;border:1px solid #2563eb;background:transparent;color:#2563eb;cursor:pointer;font-size:13px;">2026年6月</button>
  </div>
'''

pattern_us = r'(<div class="section-hd" id="semi-us-section"[^>]*>\s*<h2>美国半导体热度</h2>\s*<span[^>]*>每日更新[^<]*</span>\s*</div>\s*<div class="grid">)'
m_us = re.search(pattern_us, c)
if m_us:
    pos = m_us.end()
    c = c[:pos] + '\n' + filter_bar_us + c[pos:]
    print('[OK] 美股SBI月份筛选栏已插入')
else:
    print('[FAIL] 找不到美股SBI grid')

# ===== 3. 为A股SBI卡片添加 data-month 属性 =====
cn_start = c.find('id="semi-cn-section"')
us_start = c.find('id="semi-us-section"')

pos = cn_start
while True:
    href_m = re.search(r'<a class="card-btn" href="report-semiconductor-sbi-(\d{4})-(\d{2})-\d{2}\.html">阅读报告</a>', c[pos:us_start])
    if not href_m:
        break
    abs_pos = pos + href_m.start()
    # 往前找最近的 <div class="card">
    card_start = c.rfind('<div class="card">', pos, abs_pos)
    if card_start > cn_start:
        snippet = c[card_start:card_start+60]
        if 'data-month' not in snippet:
            month_str = href_m.group(1) + '-' + href_m.group(2)
            old = '<div class="card">'
            new = '<div class="card" data-month="' + month_str + '">'
            c = c[:card_start] + new + c[card_start+len(old):]
            delta = len(new) - len(old)
            us_start += delta
            pos = card_start + len(new)
        else:
            pos = card_start + 1
    else:
        pos = abs_pos + 1

print('[OK] A股SBI卡片 data-month 属性已添加')

# ===== 4. 为美股SBI卡片添加 data-month 属性 =====
# 找到美股SBI grid的范围
us_grid_pos = c.find('<div class="grid">', m_us.end() if m_us else us_start)
# 找到grid对应的关闭</div>
grid_close = -1
if us_grid_pos > 0:
    depth = 0
    in_script = False
    i = us_grid_pos
    while i < len(c):
        if c[i:i+7] == '<script':
            in_script = True
        if c[i:i+9] == '</script>':
            in_script = False
        if not in_script:
            if c[i:i+5] == '<div ' or c[i:i+4] == '<div>':
                # 简单处理：只计算顶级grid的div
                pass
            if c[i:i+6] == '<div>' or c[i:i+12] == '<div class=':
                depth += 1
            if c[i:i+7] == '</div>':
                depth -= 1
                if depth == 0:
                    grid_close = i
                    break
        i += 1

print(f'美股SBI grid关闭位置: {grid_close}')

pos = us_grid_pos
search_end = grid_close if grid_close > 0 else len(c)
while True:
    href_m = re.search(r'<a class="card-btn" href="report-us-hardware-sbi-(\d{4})-(\d{2})-\d{2}\.html">阅读报告</a>', c[pos:search_end])
    if not href_m:
        break
    abs_pos = pos + href_m.start()
    card_start = c.rfind('<div class="card">', pos, abs_pos)
    if card_start > 0:
        snippet = c[card_start:card_start+60]
        if 'data-month' not in snippet:
            month_str = href_m.group(1) + '-' + href_m.group(2)
            old = '<div class="card">'
            new = '<div class="card" data-month="' + month_str + '">'
            c = c[:card_start] + new + c[card_start+len(old):]
            delta = len(new) - len(old)
            if grid_close > 0:
                grid_close += delta
            search_end += delta
            pos = card_start + len(new)
        else:
            pos = card_start + 1
    else:
        pos = abs_pos + 1

print('[OK] 美股SBI卡片 data-month 属性已添加')

# ===== 5. 添加JS函数 =====
js_func = '''
  <script>
  function filterSBICards(section, month, btn) {
    var bar = btn.parentElement;
    var buttons = bar.querySelectorAll('.sbi-filter-btn');
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].style.background = 'transparent';
      buttons[i].style.color = '#2563eb';
      buttons[i].classList.remove('active');
    }
    btn.style.background = '#2563eb';
    btn.style.color = '#fff';
    btn.classList.add('active');
    var gridId = section === 'cn' ? 'semi-cn-section' : 'semi-us-section';
    var sectionEl = document.getElementById(gridId);
    if (!sectionEl) return;
    var grid = sectionEl.querySelector('.grid');
    if (!grid) return;
    var cards = grid.querySelectorAll('.card[data-month]');
    for (var j = 0; j < cards.length; j++) {
      var card = cards[j];
      if (month === 'all') {
        card.style.display = '';
      } else {
        var cardMonth = card.getAttribute('data-month');
        card.style.display = cardMonth === month ? '' : 'none';
      }
    }
  }
  </script>
'''

body_close = c.rfind('</body>')
if body_close > 0:
    c = c[:body_close] + js_func + '\n' + c[body_close:]
    print('[OK] JS filterSBICards 函数已插入')
else:
    print('[FAIL] 找不到 </body> 标签')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('\n=== 全部完成 ===')
print('已添加月份筛选栏、data-month属性、JS筛选函数')
