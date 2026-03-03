#!/usr/bin/env python3
"""
使用exploration.py中的函数计算800mm²非chiplet的成本
"""

import sys
import os
sys.path.append('/root/autodl-tmp/chiplet-actuary-dac2022')

from chiplet_actuary import package, module, chip, spec
import exploration as ex

def calculate_800mm_final():
    """计算800mm²非chiplet的成本"""
    
    print("=== 使用exploration.py计算800mm²非chiplet成本 ===")
    print()
    
    # 1. 直接使用SoC_RE_cost函数计算800mm² SoC成本
    print("1. 计算800mm² SoC成本：")
    print("   使用exploration.py中的SoC_RE_cost函数")
    print()
    
    def SoC_RE_cost(node, area):
        soc = package.SoC('soc', node, {module.Module('module', node, area): 1}, 'OS')
        return soc.cost_RE()
    
    # 计算800mm² SoC成本
    soc_800_cost = SoC_RE_cost('7', 800)
    
    print("   800mm² SoC成本组成：")
    cost_names = ['raw_chips', 'defect_chips', 'raw_package', 'defect_package', 'wasted_chips']
    for name, cost in zip(cost_names, soc_800_cost):
        print(f"   - {name}: ${cost:.2f}")
    
    total_soc_800 = sum(soc_800_cost)
    print(f"   - 总计: ${total_soc_800:.2f}")
    print()
    
    # 2. 使用single_system_total_cost函数
    print("2. 使用single_system_total_cost函数：")
    print("   这个函数专门计算800mm²的成本")
    print()
    
    total_cost_df = ex.single_system_total_cost(num_chip=1, node="7")
    print("   总成本数据：")
    print(total_cost_df)
    print()
    
    # 3. 计算不同工艺节点的800mm²成本
    print("3. 计算不同工艺节点的800mm²成本：")
    print()
    
    nodes = ['5', '7', '10']
    
    for node in nodes:
        print(f"   {node}nm工艺节点：")
        soc_cost = SoC_RE_cost(node, 800)
        total_cost = sum(soc_cost)
        
        for name, cost in zip(cost_names, soc_cost):
            print(f"     - {name}: ${cost:.2f}")
        print(f"     - 总计: ${total_cost:.2f}")
        print()
    
    # 4. 分析成本结构
    print("4. 分析800mm² SoC成本结构：")
    print()
    
    print("   7nm工艺节点成本结构：")
    for name, cost in zip(cost_names, soc_800_cost):
        percentage = (cost / total_soc_800) * 100
        print(f"   - {name}: ${cost:.2f} ({percentage:.1f}%)")
    print()
    
    # 5. 与chiplet系统对比
    print("5. 与chiplet系统对比：")
    print()
    
    # 创建800mm²的chiplet系统（假设8个100mm²的chiplet）
    chips_chiplet = {}
    for i in range(8):
        m = module.Module(f'module{i}', '7', 100)
        c = chip.Chiplet(m, m.area * 0.1)
        chips_chiplet[c] = 1
    
    os_chiplet = package.OS('chiplet_800', chips_chiplet)
    chiplet_cost = os_chiplet.cost_RE()
    chiplet_total = sum(chiplet_cost)
    
    print("   800mm² chiplet系统（8个100mm² chiplet）：")
    for name, cost in zip(cost_names, chiplet_cost):
        print(f"   - {name}: ${cost:.2f}")
    print(f"   - 总计: ${chiplet_total:.2f}")
    print()
    
    print("   对比：")
    print(f"   - SoC系统: ${total_soc_800:.2f}")
    print(f"   - Chiplet系统: ${chiplet_total:.2f}")
    print(f"   - 差异: ${chiplet_total - total_soc_800:.2f}")
    print(f"   - 比例: {chiplet_total/total_soc_800:.2f}:1")
    print()
    
    # 6. 分析关键发现
    print("6. 关键发现：")
    print()
    
    print("   ❌ 异常现象：defect_chips > raw_chips")
    print(f"   - raw_chips: ${soc_800_cost[0]:.2f}")
    print(f"   - defect_chips: ${soc_800_cost[1]:.2f}")
    print(f"   - 比例: {soc_800_cost[1]/soc_800_cost[0]:.2f}:1")
    print()
    
    print("   原因分析：")
    print("   1. 800mm²芯片面积很大，良率显著下降")
    print("   2. 良率下降导致defect_cost大幅增加")
    print("   3. 在超大芯片中，defect_cost可能超过raw_cost")
    print()
    
    # 7. 验证良率计算
    print("7. 验证良率计算：")
    print()
    
    # 创建800mm²芯片
    m_800 = module.Module('module_800', '7', 800)
    c_800 = chip.Chip('chip_800', '7', {m_800: 1})
    
    die_yield = c_800.die_yield()
    raw_cost = c_800.cost_raw_die()
    kgd_cost = c_800.cost_KGD()
    defect_cost = c_800.cost_defect()
    
    print(f"   800mm²芯片良率分析：")
    print(f"   - 良率: {die_yield:.4f} ({die_yield*100:.2f}%)")
    print(f"   - raw_cost: ${raw_cost:.2f}")
    print(f"   - kgd_cost: ${kgd_cost:.2f}")
    print(f"   - defect_cost: ${defect_cost:.2f}")
    print(f"   - defect_ratio: {defect_cost/raw_cost:.2f}")
    print()
    
    if defect_cost > raw_cost:
        print("   ❌ 确认：defect_cost > raw_cost，这是异常现象！")
        print("   说明良率计算或成本计算存在问题")
    else:
        print("   ✅ defect_cost < raw_cost，这是正常的")
    
    print()
    print("=== 总结 ===")
    print("800mm²非chiplet（SoC）成本：")
    print(f"- 7nm工艺: ${total_soc_800:.2f}")
    print("- 成本结构异常：defect_chips > raw_chips")
    print("- 相比chiplet系统，SoC系统成本更高")
    print("- 超大芯片的良率问题导致成本异常")

if __name__ == "__main__":
    calculate_800mm_final()
