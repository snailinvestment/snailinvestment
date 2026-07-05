#!/usr/bin/env python3
"""
修复 index.html v2.5 (June 28 base) 的4个问题：
1. 将A股面板中的半导体SBI卡片移到新面板 panel-semi-cn
2. 将美股面板中的半导体SBI卡片移到新面板 panel-semi-us  
3. 补充港股PCT报告
4. 更新侧边栏、validCats、tabConfig
"""

import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ============================================================
# 1. 提取A股SBI卡片，创建 panel-semi-cn
# ============================================================

# 找到A股面板中第一个SBI卡片的位置
idx_cn_sbi = html.find('A股半导体SBI泡沫指数', html.find('id="panel-china"'))
if idx_cn_sbi == -1:
    print("ERROR: A股 SBI cards not found")
    exit(1)

# 找到第一个SBI卡片的 <div class="card"> 起始位置
idx_card_start = html.rfind('<div class="card">', html.find('id="panel-china"'), idx_cn_sbi)
print(f"A股SBI卡片起始位置: {idx_card_start}")

# 找到 panel-china 里 grid 的结束 </div>
# 方法：从 idx_card_start 往后找，直到遇到 <!-- 港股 --> 之前的最后一个 </div>
idx_panel_china_end = html.find('<!-- 港股 -->', idx_card_start)
# 在 panel-china 范围内找 grid 的结束
# grid 结束后会有一个 </div> 然后是 </div><!-- /panel-china -->
# 找 "</div>\n\n<!-- 港股 -->" 之前的 grid 关闭
idx_grid_close = html.rfind('  </div>\n\n<!-- 港股 -->', 0, idx_panel_china_end)
if idx_grid_close == -1:
    # 换种方式：找 panel-china 中最后一个 card 之后的 </div>
    idx_last_card_end = html.rfind('</a>\n    </div>\n    <div class="card">', 0, idx_panel_china_end)
    if idx_last_card_end == -1:
        # 最后一个卡片的结束
        idx_sbi_end = html.rfind('</a>\n    </div>\n\n    <div class="card">', 0, idx_panel_china_end)
    
print(f"grid关闭位置: {idx_grid_close}")
print("Need to manually verify HTML structure")
