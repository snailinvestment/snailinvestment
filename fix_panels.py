#!/usr/bin/env python3
"""
修复 index.html 的4个问题：
1. 将A股面板中的半导体SBI卡片移到独立面板 panel-semi-cn
2. 将美股面板中的半导体SBI卡片移到独立面板 panel-semi-us
3. 补充港股缺失内容（PCT报告等）
4. 补充宏观周记W4报告链接
5. 更新侧边栏、validCats、tabConfig
"""

import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# 1. 从 panel-china 中提取A股SBI卡片，创建 panel-semi-cn
# ============================================================

# 找到A股面板中SBI卡片的开始位置（第一个"A股半导体SBI泡沫指数"卡片）
# 在 panel-china 的 grid 中，SBI卡片在化工价格卡片之后
sbi_cn_start = html.find('A股半导体SBI泡沫指数', html.find('panel-china'))
if sbi_cn_start == -1:
    print("ERROR: Could not find A股 SBI cards in panel-china")
else:
    # 找到这个卡片的起始 <div class="card"> 标签
    card_start = html.rfind('<div class="card">', html.find('panel-china'), sbi_cn_start)
    # 找到 panel-china 中 grid 的结束 </div>
    # 找到 card_start 之后的第一个 </div><!-- /grid --> 或简单的 </div>
    grid_end = html.find('</div>\n\n<!-- 港股 -->', card_start)
    if grid_end == -1:
        print("ERROR: Could not find grid end in panel-china")
    else:
        # 提取SBI卡片HTML（从第一个SBI card到grid关闭前）
        # 实际上SBI卡片后面还有非SBI卡片吗？让我看看结构
        # 从输出看，L388之后的所有card都是SBI卡片，直到grid关闭
        pass

print("Step 1: Extract A股 SBI cards...")
print(f"  SBI start position: {sbi_cn_start}")
print(f"  First card start: {card_start if 'card_start' in dir() else 'N/A'}")
