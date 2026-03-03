#!/usr/bin/env python3
"""
计算7nm工艺下4×200mm²和4×800mm² chiplet的RE成本
"""

import sys
import os
sys.path.append('/root/autodl-tmp/chiplet-actuary-dac2022')

from chiplet_actuary import package, module, chip, spec

def calculate_chiplet_costs():
    """计算4×200mm²和4×800mm² chiplet的RE成本"""
    
    print("=== 计算7nm工艺下chiplet的RE成本 ===")
    print()
    
    # 1. 计算4×200mm² chiplet系统
    print("1. 计算4×200mm² chiplet系统：")
    print("   - 总系统面积：800mm²")
    print("   - 芯片数量：4个")
    print("   - 每个chiplet面积：200mm²")
    print("   - 工艺节点：7nm")
    print()
    
    # 创建4×200mm² chiplet系统
    chips_4x200 = {}
    for i in range(4):
        m = module.Module(f'module{i}', '7', 200)  # 200mm²
        c = chip.Chiplet(m, m.area * 0.1)  # D2D面积
        chips_4x200[c] = 1
        if i == 0:  # 显示第一个chiplet的信息
            print(f"   第一个chiplet：")
            print(f"   - 模块面积：{m.area}mm²")
            print(f"   - D2D面积：{c.D2DArea}mm²")
            print(f"   - 总芯片面积：{c.area}mm²")
            print(f"   - 良率：{c.die_yield():.4f} ({c.die_yield()*100:.2f}%)")
            print()
    
    # 计算OS封装成本
    os_4x200 = package.OS('integration_4x200', chips_4x200)
    os_4x200_costs = os_4x200.cost_RE()
    
    print("   4×200mm² chiplet系统成本组成：")
    cost_names = ['raw_chips', 'defect_chips', 'raw_package', 'defect_package', 'wasted_chips']
    for name, cost in zip(cost_names, os_4x200_costs):
        print(f"   - {name}: ${cost:.2f}")
    
    total_4x200 = sum(os_4x200_costs)
    print(f"   - 总计: ${total_4x200:.2f}")
    print(f"   - 每个chiplet平均成本: ${total_4x200/4:.2f}")
    print()
    
    # 2. 计算4×800mm² chiplet系统
    print("2. 计算4×800mm² chiplet系统：")
    print("   - 总系统面积：3200mm²")
    print("   - 芯片数量：4个")
    print("   - 每个chiplet面积：800mm²")
    print("   - 工艺节点：7nm")
    print()
    
    # 创建4×800mm² chiplet系统
    chips_4x800 = {}
    for i in range(4):
        m = module.Module(f'module{i}', '7', 800)  # 800mm²
        c = chip.Chiplet(m, m.area * 0.1)  # D2D面积
        chips_4x800[c] = 1
        if i == 0:  # 显示第一个chiplet的信息
            print(f"   第一个chiplet：")
            print(f"   - 模块面积：{m.area}mm²")
            print(f"   - D2D面积：{c.D2DArea}mm²")
            print(f"   - 总芯片面积：{c.area}mm²")
            print(f"   - 良率：{c.die_yield():.4f} ({c.die_yield()*100:.2f}%)")
            print()
    
    # 计算OS封装成本
    os_4x800 = package.OS('integration_4x800', chips_4x800)
    os_4x800_costs = os_4x800.cost_RE()
    
    print("   4×800mm² chiplet系统成本组成：")
    for name, cost in zip(cost_names, os_4x800_costs):
        print(f"   - {name}: ${cost:.2f}")
    
    total_4x800 = sum(os_4x800_costs)
    print(f"   - 总计: ${total_4x800:.2f}")
    print(f"   - 每个chiplet平均成本: ${total_4x800/4:.2f}")
    print()
    
    # 3. 对比分析
    print("3. 对比分析：")
    print()
    
    print("   总成本对比：")
    print(f"   - 4×200mm²系统: ${total_4x200:.2f}")
    print(f"   - 4×800mm²系统: ${total_4x800:.2f}")
    print(f"   - 成本比例: {total_4x800/total_4x200:.2f}:1")
    print()
    
    print("   每个chiplet成本对比：")
    cost_per_chiplet_200 = total_4x200 / 4
    cost_per_chiplet_800 = total_4x800 / 4
    print(f"   - 200mm² chiplet: ${cost_per_chiplet_200:.2f}")
    print(f"   - 800mm² chiplet: ${cost_per_chiplet_800:.2f}")
    print(f"   - 成本比例: {cost_per_chiplet_800/cost_per_chiplet_200:.2f}:1")
    print()
    
    # 4. 成本结构分析
    print("4. 成本结构分析：")
    print()
    
    print("   4×200mm²系统成本结构：")
    for name, cost in zip(cost_names, os_4x200_costs):
        percentage = (cost / total_4x200) * 100
        print(f"   - {name}: ${cost:.2f} ({percentage:.1f}%)")
    print()
    
    print("   4×800mm²系统成本结构：")
    for name, cost in zip(cost_names, os_4x800_costs):
        percentage = (cost / total_4x800) * 100
        print(f"   - {name}: ${cost:.2f} ({percentage:.1f}%)")
    print()
    
    # 5. 良率影响分析
    print("5. 良率影响分析：")
    print()
    
    # 获取第一个chiplet的良率信息
    chiplet_200 = list(chips_4x200.keys())[0]
    chiplet_800 = list(chips_4x800.keys())[0]
    
    yield_200 = chiplet_200.die_yield()
    yield_800 = chiplet_800.die_yield()
    
    print(f"   良率对比：")
    print(f"   - 200mm² chiplet良率: {yield_200:.4f} ({yield_200*100:.2f}%)")
    print(f"   - 800mm² chiplet良率: {yield_800:.4f} ({yield_800*100:.2f}%)")
    print(f"   - 良率比例: {yield_200/yield_800:.2f}:1")
    print()
    
    # 6. 封装面积分析
    print("6. 封装面积分析：")
    print()
    
    area_4x200 = os_4x200.area()
    area_4x800 = os_4x800.area()
    
    print(f"   封装面积对比：")
    print(f"   - 4×200mm²系统封装面积: {area_4x200:.1f}mm²")
    print(f"   - 4×800mm²系统封装面积: {area_4x800:.1f}mm²")
    print(f"   - 面积比例: {area_4x800/area_4x200:.2f}:1")
    print()
    
    # 7. 成本效率分析
    print("7. 成本效率分析：")
    print()
    
    # 计算每mm²的成本
    cost_per_mm2_200 = total_4x200 / 800  # 总系统面积800mm²
    cost_per_mm2_800 = total_4x800 / 3200  # 总系统面积3200mm²
    
    print(f"   每mm²成本对比：")
    print(f"   - 4×200mm²系统: ${cost_per_mm2_200:.3f}/mm²")
    print(f"   - 4×800mm²系统: ${cost_per_mm2_800:.3f}/mm²")
    print(f"   - 效率比例: {cost_per_mm2_200/cost_per_mm2_800:.2f}:1")
    print()
    
    print("=== 总结 ===")
    print("7nm工艺下chiplet系统成本分析：")
    print(f"1. 4×200mm²系统总成本: ${total_4x200:.2f}")
    print(f"2. 4×800mm²系统总成本: ${total_4x800:.2f}")
    print(f"3. 800mm² chiplet成本是200mm²的 {cost_per_chiplet_800/cost_per_chiplet_200:.2f} 倍")
    print(f"4. 良率是影响成本的主要因素：200mm²({yield_200*100:.1f}%) vs 800mm²({yield_800*100:.1f}%)")
    print(f"5. 4×200mm²系统在成本效率上更优")

if __name__ == "__main__":
    calculate_chiplet_costs()
