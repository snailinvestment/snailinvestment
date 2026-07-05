import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 修复data-month值：从每张卡片的href中提取月份
old_pattern = 'data-month="" style="display:none"'
new_pattern_prefix = 'data-month="'
new_pattern_suffix = '" style="display:none"'

pos = 0
count = 0
while True:
    start = c.find(old_pattern, pos)
    if start == -1:
        break
    
    # 往后找卡片内的href
    card_content = c[start:start+800]
    
    # 尝试匹配A股SBI href
    href_m = re.search(r'href="(report-semiconductor-sbi-(\d{4})-(\d{2})-\d+\.html)"', card_content)
    
    if not href_m:
        # 尝试美股SBI href
        href_m = re.search(r'href="(report-us-hardware-sbi-(\d{4})-(\d{2})-\d+\.html)"', card_content)
    
    if href_m:
        year = href_m.group(2)
        mon = href_m.group(3)
        month_val = year + '-' + mon
        new_val = new_pattern_prefix + month_val + new_pattern_suffix
        c = c[:start] + new_val + c[start+len(old_pattern):]
        count += 1
        pos = start + len(new_val)
    else:
        print(f'WARNING: no href found near pos {start}')
        print(card_content[:200])
        pos = start + 1

print(f'Fixed {count} data-month values')

# 验证
samples = re.findall(r'data-month="([^"]+)"[^>]*style="display:none"', c)
from collections import Counter
dist = dict(Counter(samples))
print(f'data-month distribution: {dist}')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Done!')
