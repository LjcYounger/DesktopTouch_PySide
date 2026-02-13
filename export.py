import UnityPy

# prefab文件路径常量
PREFAB_PATH = r"D:\WIN_202408202213\characters_assets_shirokoall.bundle"

def extract_and_print_prefab(path):
    """提取并打印prefab结构"""
    env = UnityPy.load(path)
    
    print(f"=== Prefab Structure: {path} ===")
    print(f"Total objects: {len(env.objects)}")
    
    # 统计对象类型
    type_stats = {}
    for obj in env.objects:
        type_name = obj.type.name
        type_stats[type_name] = type_stats.get(type_name, 0) + 1
    
    print("\nObject type statistics:")
    for type_name, count in sorted(type_stats.items()):
        print(f"  {type_name}: {count}")
    
    print("\nDetailed object list:")
    for i, obj in enumerate(env.objects):
        data = obj.read()
        name = getattr(data, 'name', 'Unnamed')
        print(f"[{i}] {obj.type.name} (PathID: {obj.path_id}) - Name: {name}")
        
        # 显示GameObject的组件
        if obj.type.name == "GameObject" and hasattr(data, 'm_Components'):
            print(f"    Components: {len(data.m_Components)}")
            for j, comp in enumerate(data.m_Components[:3]):
                print(f"      {j}: Component PathID {comp.path_id}")
            if len(data.m_Components) > 3:
                print(f"      ... and {len(data.m_Components) - 3} more components")

# 直接执行
extract_and_print_prefab(PREFAB_PATH)