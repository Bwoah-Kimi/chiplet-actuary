#!/usr/bin/env python3
"""
使用exploration.py中的函数计算800mm²非chiplet的成本
"""

import sys
import os
sys.path.append('/root/autodl-tmp/chiplet-actuary-dac2022')

from chiplet_actuary import package, module, chip, spec
import exploration as ex

def calculate_800mm_simple():
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
    
    # 6. 使用single_system_RE_cost函数获取标准化数据
    print("6. 使用single_system_RE_cost函数获取标准化数据：")
    print()
    
    result_df = ex.single_system_RE_cost(num_chip=1, node="7")
    
    # 查找800mm²的数据
    if (800, 'SoC OS') in result_df.index:
        soc_800_standardized = result_df.loc[(800, 'SoC OS')]
        print("   800mm² SoC标准化值：")
        for name, value in zip(cost_names, soc_800_standardized):
            print(f"   - {name}: {value:.3f}")
        print()
        
        # 反推绝对值成本
        soc_100_cost = SoC_RE_cost('7', 100)
        soc_100_total = sum(soc_100_cost)
        standardization_factor = soc_100_total * 8
        
        soc_800_absolute = soc_800_standardized * standardization_factor
        
        print("   反推的800mm² SoC绝对值成本：")
        for name, cost in zip(cost_names, soc_800_absolute):
            print(f"   - {name}: ${cost:.2f}")
        
        total_absolute = sum(soc_800_absolute)
        print(f"   - 总计: ${total_absolute:.2f}")
        print()
        
        # 验证计算
        print("   验证计算：")
        print(f"   - 直接计算: ${total_soc_800:.2f}")
        print(f"   - 反推计算: ${total_absolute:.2f}")
        print(f"   - 差异: ${abs(total_soc_800 - total_absolute):.2f}")
        print()
    
    print("=== 总结 ===")
    print("800mm²非chiplet（SoC）成本：")
    print(f"- 7nm工艺: ${total_soc_800:.2f}")
    print("- 成本结构以芯片成本为主")
    print("- 相比chiplet系统，SoC系统成本更低")
    print("- 适合单一大芯片的应用场景")

if __name__ == "__main__":
    calculate_800mm_simple()
