# <<global status>>
field_size    = 100 # フィールド一辺の大きさ
nothing       = 0   # 空間の配列内での表現値
ROUTE_COST    = 1   # 全セル共通のルートコスト
max_lightness = 100 # 最大光量
nutrisition   = float('inf')

soil = 'soil'
soil_representation = -1     # 配列内での表現値
soil_depth          = 5      # 土の深さ

trunk                      = 'trunk'
trunk_DefaultSize          = [1, 1, None, 1] # デフォルトのサイズパラメータ [w, h, d, weight]
trunk_representation       = 1               # 配列内での表現値
trunk_LifeSpan             = float('inf')    # 寿命
trunk_MentalStressCapacity = float('inf')    # メンタルストレス容量
trunk_GrowthRate           = 0.8             # 成長確率
trunk_OccurrenceProb       = 0.7             # 生成確率

leaf                         = 'leaf'
leaf_DefaultSize             = [2, 1, None, 0.2] # デフォルトのサイズパラメータ [w, h, d, weight]
leaf_representation          = 2                 # 配列内での表現値
leaf_LifeSpan                = float('inf')      # 寿命
leaf_MentalStressCapacity    = 40                # メンタルストレス容量
leaf_LightStressAccThreshold = 10                # 光由来のメンタルストレス受容閾値
leaf_GrowthRate              = 0.5               # 成長確率
leaf_OccurrenceProb          = 1- trunk_OccurrenceProb
leaf_Transmittance           = 0.2               # 葉の透過率