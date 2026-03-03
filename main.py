import exploration as ex

# y1 = ex.yield_area()
# y2 = ex.single_chiplet_multiple_systems(5000)

# print(y1)
# print(y2)

#print(y1)
#print(y2)
result = ex.single_system_RE_cost(num_chip=32, node="7")
print(result)