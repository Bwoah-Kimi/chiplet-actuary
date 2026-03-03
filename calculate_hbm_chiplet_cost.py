import math

from chiplet_actuary import package, module, chip, spec


class FOChiplet(chip.Chiplet):
    """Chiplet with FO packaging and critical_level"""
    def __init__(self, module, D2DArea, single_chip_area):
        super().__init__(module, D2DArea)
        self.single_chip_area = single_chip_area  # Area of a single chip
    
    def die_yield(self):
        # Die yield calculation using single chip area and FO packaging's critical_level
        return (1 + spec.Defect_Density_Die[self.node] / 100 * self.single_chip_area / spec.critical_level_rdl)**(-spec.critical_level_rdl)
    
    def N_die_total(self):
        # Calculate N_die_total using single chip area
        Area_chip = self.single_chip_area + 2 * spec.scribe_lane * math.sqrt(self.single_chip_area) + spec.scribe_lane**2
        N_total = math.pi * (spec.wafer_diameter / 2 - spec.edge_loss)**2 / Area_chip - math.pi * (
            spec.wafer_diameter - 2 * spec.edge_loss) / math.sqrt(2 * Area_chip)
        return N_total

def calculate_hbm_chiplet_cost(chiplet_area, num_chiplets, num_hbm, packaging='FO', logger=None):
    """
    Calculate the RE cost of a chiplet system with HBM.
    
    Args:
    - chiplet_area: Area of a single chiplet (mm²)
    - num_chiplets: Number of chiplets
    - num_hbm: Number of HBMs
    - packaging: Packaging method ('OS', 'FO', 'SI')
    - logger: Logger object for logging information
    
    Returns:
    - A dictionary containing the total RE cost and other cost breakdowns.
    """

    SINGLE_HBM_COST = 233  # Cost of a single HBM ($)
    SINGLE_HBM_AREA = 80   # Area of a single HBM (mm²)

    if logger:
        logger.info("=== Chiplet System RE Cost Calculation ===")
        logger.info(f"Configuration: chiplet_area={chiplet_area}mm², num_chiplets={num_chiplets}, num_hbm={num_hbm}, packaging={packaging}")
    
    # Create chiplet system with HBM
    single_module = module.Module('multi_node_module', '7', chiplet_area)
    c = FOChiplet(single_module, chiplet_area * 0.1, chiplet_area) # D2D area is 10% of chiplet area
    c.modules = {single_module: num_chiplets}
    c.area = single_module.area * num_chiplets
    
    hbm_area_per_chiplet = SINGLE_HBM_AREA * num_hbm  # HBM area per chiplet (mm²)
    hbm_cost_per_chiplet = SINGLE_HBM_COST * num_hbm  # HBM cost per chiplet ($)
    total_chiplet_area = c.area + hbm_area_per_chiplet
    
    chips = {c: 1}  # Only one chiplet
    
    # Calculate package area
    if packaging == 'OS':
        package_obj = package.OS('hbm_integration', chips)
    elif packaging == 'FO':
        package_obj = package.FO('hbm_integration', chips, chip_last=1)
    elif packaging == 'SI':
        package_obj = package.SI('hbm_integration', chips)
    else:
        raise ValueError(f"Unsupported packaging method: {packaging}")
    
    base_package_area = package_obj.area()
    hbm_package_area = SINGLE_HBM_AREA * num_hbm * num_chiplets
    total_package_area = base_package_area + hbm_package_area
    
    # Calculate RE cost
    base_costs = package_obj.cost_RE()
    cost_names = ['raw_chips', 'defect_chips', 'raw_package', 'defect_package', 'wasted_chips']
    
    hbm_total_cost = SINGLE_HBM_COST * num_hbm * num_chiplets
    
    # Calculate total cost
    single_node_raw_cost = c.cost_raw_die()  # Raw chip cost for a single node
    corrected_raw_chips_cost = single_node_raw_cost * num_chiplets  # Total raw chip cost

    single_node_defect_cost = c.cost_defect()  # Defect chip cost of a single node
    corrected_defect_chips_cost = single_node_defect_cost * num_chiplets  # Total defect chip cost
    
    base_chip_cost = corrected_raw_chips_cost + corrected_defect_chips_cost
    base_package_cost = base_costs[2] + base_costs[3] + base_costs[4]
    
    if base_package_area > 0:
        hbm_package_cost = base_package_cost * (hbm_package_area / base_package_area)
    else:
        hbm_package_cost = 0
    
    total_costs = {
        'raw_chips': corrected_raw_chips_cost,
        'defect_chips': corrected_defect_chips_cost,
        'raw_package': base_costs[2] + hbm_package_cost,
        'defect_package': base_costs[3],
        'wasted_chips': base_costs[4],
        'hbm_cost': hbm_total_cost
    }
    
    total_re_cost = sum(total_costs.values())
    
    # Yield analysis
    first_chiplet = list(chips.keys())[0]
    die_yield = first_chiplet.die_yield()
    
    # Return results
    result = {
        'total_cost': total_re_cost,
        'cost_breakdown': total_costs,
        'package_area': total_package_area,
        'chiplet_area': chiplet_area,
        'num_chiplets': num_chiplets,
        'num_hbm': num_hbm,
        'packaging': packaging,
        'die_yield': die_yield,
        'cost_per_chiplet': total_re_cost,
        'cost_per_mm2': total_re_cost / total_chiplet_area,
        'hbm_cost_ratio': (hbm_total_cost / total_re_cost),
        'logic_cost': base_chip_cost,
        'package_cost': base_package_cost + hbm_package_cost,
        'hbm_cost_total': hbm_total_cost,
        'single_node_raw_cost': single_node_raw_cost,
        'single_node_defect_cost': single_node_defect_cost,
        'hbm_area_per_chiplet': hbm_area_per_chiplet,
        'hbm_package_area': hbm_package_area
    }
    
    if logger:
        logger.info(f"Total RE cost: ${total_re_cost:.2f}")
        logger.info(f"Cost per chiplet: ${total_re_cost:.2f}")
        logger.info(f"Cost per mm²: ${total_re_cost/total_chiplet_area:.3f}")
        logger.info(f"HBM cost ratio: {(hbm_total_cost/total_re_cost)*100:.1f}%")
        logger.info(f"Die Yield: {die_yield:.4f} ({die_yield*100:.2f}%)")

    return result

def compare_hbm_configurations():
    """Compare costs of different HBM configurations"""
    
    print("=== Compare costs of different HBM configurations ===")

    # Configuration 1: 4×200mm² chiplet, 4 HBMs
    config1 = calculate_hbm_chiplet_cost(200, 4, 4, 'FO')
    
    print("\n" + "="*50 + "\n")
    
    # Configuration 2: 4×200mm² chiplet, 8 HBMs
    config2 = calculate_hbm_chiplet_cost(200, 4, 8, 'FO')
    
    print("\n" + "="*50 + "\n")
    
    # Configuration 3: 16×200mm² chiplet, 4 HBMs
    config3 = calculate_hbm_chiplet_cost(200, 16, 4, 'FO')
    
    print("\n" + "="*50 + "\n")
    
    # Configuration 4: 4×800mm² chiplet, 4 HBMs
    config4 = calculate_hbm_chiplet_cost(800, 4, 4, 'FO')
    
    print("\n" + "="*50 + "\n")
    
    # Comparison analysis
    print("Configuration Comparison Analysis")
    
    configs = [
        ("4×200mm², 4HBM", config1),
        ("4×200mm², 8HBM", config2),
        ("16×200mm², 4HBM", config3),
        ("4×800mm², 4HBM", config4)
    ]
    
    print("Configuration Comparison:")
    print(f"{'Configuration':<20} {'Total Cost':<12} {'Cost per chiplet':<15} {'HBM Cost Ratio':<12}")
    print("-" * 60)
    
    for name, config in configs:
        hbm_ratio = (config['cost_breakdown']['hbm_cost'] / config['total_cost']) * 100
        print(f"{name:<20} ${config['total_cost']:<11.2f} ${config['cost_per_chiplet']:<14.2f} {hbm_ratio:<11.1f}%")
    
    print()
