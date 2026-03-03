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


def calculate_dram_chiplet_cost(
    compute_area: float,
    sram_area: float,
    num_chiplets: int,
    num_dram_dies: int,
    dram_die_cost: float,
    dram_die_area: float,
    packaging: str = 'FO',
    cost_adjustment_factor: float = 10.0,
    logger=None
):
    """
    Calculate the RE cost of a chiplet system with a generic DRAM type.
    
    Args:
    - compute_area: Area of the compute part of the logic chiplet (mm²)
    - sram_area: Area of the SRAM part of the logic chiplet (mm²)
    - num_chiplets: Number of logic chiplets
    - num_dram_dies: Number of DRAM dies per logic chiplet
    - dram_die_cost: Cost of a single DRAM die ($)
    - dram_die_area: Area of a single DRAM die (mm²)
    - packaging: Packaging method ('OS', 'FO', 'SI')
    - logger: Logger object for logging information
    
    Returns:
    - A dictionary containing the total RE cost and other cost breakdowns.
    """
    chiplet_area = compute_area + sram_area
    
    if logger:
        logger.info("=== Chiplet System with Generic DRAM RE Cost Calculation ===")
        logger.info(f"Config: compute_area={compute_area}mm², sram_area={sram_area}mm², total_chiplet_area={chiplet_area}mm², "
                    f"num_chiplets={num_chiplets}, num_dram_dies={num_dram_dies}, "
                    f"dram_cost=${dram_die_cost}, dram_area={dram_die_area}mm², pkg={packaging}")
    
    # Create chiplet system
    single_module = module.Module('multi_node_module', '7', chiplet_area)
    c = FOChiplet(single_module, chiplet_area * 0.1, chiplet_area) # D2D area is 10% of chiplet area
    c.modules = {single_module: num_chiplets}
    c.area = single_module.area * num_chiplets
    
    dram_area_per_chiplet = dram_die_area * num_dram_dies
    total_logic_and_dram_area = c.area + (dram_area_per_chiplet * num_chiplets)
    
    chips = {c: 1}
    
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
    dram_package_area = dram_die_area * num_dram_dies * num_chiplets
    total_package_area = base_package_area + dram_package_area
    
    # Calculate RE cost
    base_costs = package_obj.cost_RE()
    
    dram_total_cost = dram_die_cost * num_dram_dies * num_chiplets
    
    # Correct chiplet costs for the total number of chiplets
    single_node_raw_cost = c.cost_raw_die()
    corrected_raw_chips_cost = single_node_raw_cost * num_chiplets

    single_node_defect_cost = c.cost_defect()
    corrected_defect_chips_cost = single_node_defect_cost * num_chiplets
    
    base_chip_cost = corrected_raw_chips_cost + corrected_defect_chips_cost
    base_package_cost = base_costs[2] + base_costs[3] + base_costs[4]
    
    # Apportion package cost to DRAM based on area
    dram_package_cost = base_package_cost * (dram_package_area / base_package_area) if base_package_area > 0 else 0
    
    # Apply adjustment factor to all non-DRAM costs to make them more proportional
    adjusted_raw_chips_cost = corrected_raw_chips_cost * cost_adjustment_factor
    adjusted_defect_chips_cost = corrected_defect_chips_cost * cost_adjustment_factor
    adjusted_raw_package_cost = (base_costs[2] + dram_package_cost) * cost_adjustment_factor
    adjusted_defect_package_cost = base_costs[3] * cost_adjustment_factor
    adjusted_wasted_chips_cost = base_costs[4] * cost_adjustment_factor

    total_costs = {
        'raw_chips': adjusted_raw_chips_cost,
        'defect_chips': adjusted_defect_chips_cost,
        'raw_package': adjusted_raw_package_cost,
        'defect_package': adjusted_defect_package_cost,
        'wasted_chips': adjusted_wasted_chips_cost,
        'dram_cost': dram_total_cost  # DRAM cost is not adjusted
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
        'compute_area': compute_area,
        'sram_area': sram_area,
        'chiplet_area': chiplet_area,
        'num_chiplets': num_chiplets,
        'num_dram_dies': num_dram_dies,
        'packaging': packaging,
        'die_yield': die_yield,
        'cost_per_mm2': total_re_cost / total_logic_and_dram_area if total_logic_and_dram_area > 0 else 0,
        'dram_cost_ratio': (dram_total_cost / total_re_cost) if total_re_cost > 0 else 0,
        'logic_cost': adjusted_raw_chips_cost + adjusted_defect_chips_cost,
        'package_cost': adjusted_raw_package_cost + adjusted_defect_package_cost + adjusted_wasted_chips_cost,
        'dram_cost_total': dram_total_cost,
    }
    
    if logger:
        logger.info(f"Total RE cost: ${total_re_cost:.2f}")
        logger.info(f"DRAM cost ratio: {result['dram_cost_ratio']*100:.1f}%")
        logger.info(f"Die Yield: {die_yield:.4f} ({die_yield*100:.2f}%)")

    return result


def compare_dram_configurations():
    """Example usage: Compare costs of different DRAM configurations"""
    
    print("=== Compare costs of different DRAM configurations ===")

    # --- Define DRAM Types for comparison ---
    # For simplicity, area is kept constant as requested
    DRAM_DIE_AREA = 80 # mm²
    
    DRAM_TYPES = {
        "GDDR6": {"cost": 50},
        "HBM3": {"cost": 233},
        "LPDDR5": {"cost": 35},
    }

    # --- Configuration 1: 4 chiplets, 4 dies of GDDR6 ---
    gddr6_config = DRAM_TYPES["GDDR6"]
    config1 = calculate_dram_chiplet_cost(
        compute_area=150,
        sram_area=50,
        num_chiplets=4, 
        num_dram_dies=4, 
        dram_die_cost=gddr6_config['cost'], 
        dram_die_area=DRAM_DIE_AREA
    )
    print("\n--- Config 1: 4x200mm² chiplets, 4 dies/chiplet (GDDR6) ---")
    for key, val in config1.items():
        if isinstance(val, dict):
            print(f"{key}:")
            for k, v in val.items():
                print(f"  {k}: {v:.2f}" if isinstance(v, float) else f"  {k}: {v}")
        else:
            print(f"{key}: {val:.4f}" if isinstance(val, float) else f"{key}: {val}")
    
    # --- Configuration 2: 4 chiplets, 4 dies of HBM3 ---
    hbm3_config = DRAM_TYPES["HBM3"]
    config2 = calculate_dram_chiplet_cost(
        compute_area=150,
        sram_area=50,
        num_chiplets=4, 
        num_dram_dies=4, 
        dram_die_cost=hbm3_config['cost'], 
        dram_die_area=DRAM_DIE_AREA
    )
    print("\n--- Config 2: 4x200mm² chiplets, 4 dies/chiplet (HBM3) ---")
    for key, val in config2.items():
        if isinstance(val, dict):
            print(f"{key}:")
            for k, v in val.items():
                print(f"  {k}: {v:.2f}" if isinstance(v, float) else f"  {k}: {v}")
        else:
            print(f"{key}: {val:.4f}" if isinstance(val, float) else f"{key}: {val}")

    # --- Summary Comparison ---
    print("\n" + "="*50)
    print("Summary Comparison")
    print(f"{'Configuration':<25} {'Total Cost':<15} {'DRAM Cost Ratio':<15}")
    print("-" * 60)
    
    print(f"{'4x Chiplet, 4x GDDR6':<25} ${config1['total_cost']:<14.2f} {config1['dram_cost_ratio']*100:<14.1f}%")
    print(f"{'4x Chiplet, 4x HBM3':<25} ${config2['total_cost']:<14.2f} {config2['dram_cost_ratio']*100:<14.1f}%")
    print("="*50)


if __name__ == '__main__':
    compare_dram_configurations()
