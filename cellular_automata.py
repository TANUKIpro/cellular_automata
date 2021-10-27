import pprint
import threading

import numpy as np
from matplotlib import animation
from matplotlib import pyplot as plt

# <<global status>>
field_size = 100 # フィールド一辺の大きさ
nothing = 0

soil = 'soil'
soil_representation = -1     # 配列内での表現値
soil_depth          = 5      # 土の深さ

trunk                      = 'trunk'
trunk_DefoSize             = [1, 1, None, 1] # デフォルトのサイズパラメータ [w, h, d, weight]
trunk_representation       = 1               # 配列内での表現値
trunk_LifeSpam             = float('inf')    # 寿命
trunk_MentalStressCapacity = float('inf')    # メンタルストレス容量
trunk_GrowthRate           = 0.8             # 成長率
trunk_OccurrenceProb       = 0.7             # 生成確率

leaf                         = 'leaf'
leaf_DefoSize                = [2, 1, None, 0.2] # デフォルトのサイズパラメータ [w, h, d, weight]
leaf_representation          = 2                 # 配列内での表現値
leaf_LifeSpam                = float('inf')      # 寿命
leaf_MentalStressCapacity    = 40                # メンタルストレス容量
leaf_LightStressAccThreshold = 10                # 光由来のメンタルストレス受容閾値
leaf_GrowthRate              = 0.5               # 成長率
leaf_OccurrenceProb          = 1- trunk_OccurrenceProb
leaf_CutoffRatio             = 0.8

# Cartesian coordinates --> Python coordinates
def coordinateTranslator(targetHight, x, y, mode='CARTESIAN2PY'):
    if mode == 'CARTESIAN2PY':
        trX = targetHight - y
        trY = x
    if mode == 'PY2CARTESIAN':
        trX = y
        trY = targetHight - x
    return (trX, trY)

# Self-diagnostic functions
def cell_SelfChecker(_cells_InsList, _cell_ins, _index):
    if _cell_ins.survival == False:
        del _cells_InsList[_index]
    if _cell_ins.coordination is None:
        del _cells_InsList[_index]

class Cell:
    global field_size
    global soil, soil_representation
    global trunk, trunk_representation, trunk_LifeSpam, trunk_MentalStressCapacity
    global leaf, leaf_representation, leaf_LifeSpam, leaf_MentalStressCapacity, leaf_LightStressAccThreshold

    def __init__(self, name, coord, size_status):
        # <<init status>>
        self.name         = name         # trunk / leaf
        self.coordination = coord        # [[x, y, (z)]]
        self.size_status  = size_status  # [width, height, (depth), weight]
        
        # <<own status>>
        self.survival     = True         # True(live) / False(dead)
        self.age          = 0
        self.mentalStress = 0
        self.around_data  = None
        #self.physicalStress = 0
        
        # <<environmental　status>>
        self.lightness = 100
    
    def __del__(self):
        pass

    def getTrunkCoordination(self):
        _x, _y = self.coordination[0]
        return (_x, _y)

    def getLeafCoordination(self):
        _x, _y = self.coordination[:,0], self.coordination[:,-1][0]
        return (_x, _y)
    
    # 配列の更新用(描画)
    def paint(self, _field_array):
        targetHight = _field_array.shape[0]
        if self.name == trunk:
            x, y = self.getTrunkCoordination()
            x, y = coordinateTranslator(targetHight, x, y)
            if self.survival:
                _field_array[x, y] = trunk_representation
            else:
                _field_array[x, y] = nothing
        elif self.name == leaf:
            for cd in self.coordination:
                x, y = cd
                x, y = coordinateTranslator(targetHight, x, y)
                if self.survival:
                    _field_array[x, y] = leaf_representation
                else:
                    _field_array[x, y] = nothing
        return _field_array
    
    # 成長用
    def generation(self, _cells_list):
        # 生成の決定
        if np.random.rand() <= trunk_OccurrenceProb:
            new_element = trunk
        else:
            new_element = leaf

        # インスタンスの作成と初期設定
        if new_element == trunk:
            x, y = self.getTrunkCoordination()
            if self.age > 50:
                if np.random.rand() <= trunk_GrowthRate:
                    # 上方向へ成長
                    if np.random.rand() <= 0.5:
                        #上が0
                        if self.around_data[0][1] == nothing:
                            new_trunk = Cell(trunk, np.array([[x, y+1]]), trunk_DefoSize)
                            _cells_list.append(new_trunk)
                    # 左右方向へ成長
                    else:
                        if np.random.rand() <= 0.5:
                            #左が0
                            if self.around_data[1][0] == nothing:
                                new_trunk = Cell(trunk, np.array([[x-1, y]]), trunk_DefoSize)
                                _cells_list.append(new_trunk)
                        else:
                            #右が0
                            if self.around_data[1][-1] == nothing:
                                new_trunk = Cell(trunk, np.array([[x+1, y]]), trunk_DefoSize)
                                _cells_list.append(new_trunk)
        elif new_element == leaf:
            x, y = self.getTrunkCoordination()
            if self.age > 45:
                if np.random.rand() <= leaf_GrowthRate:
                    #左が0
                    if self.around_data[1][0] == nothing:
                        new_leaf = Cell(leaf, np.array([[x-1, y], [x-2, y]]), leaf_DefoSize)
                        _cells_list.append(new_leaf)
                    #右が0
                    elif self.around_data[1][-1] == nothing:
                        new_leaf = Cell(leaf, np.array([[x+1, y], [x+2, y]]), leaf_DefoSize)
                        _cells_list.append(new_leaf)
        return _cells_list
    
    # 周囲の状況把握用
    def look_around(self, _field_array):
        targetHight = _field_array.shape[0]
        if self.name == trunk:
            x, y = self.coordination[0]  #  <-- fixme
            x, y = coordinateTranslator(targetHight, x, y, mode='CARTESIAN2PY')
            yL = yR = y
        elif self.name == leaf:
            x, y = self.coordination[:,0], self.coordination[:,-1][0]  #  <-- fixme
            x, y = coordinateTranslator(targetHight, x, y, mode='CARTESIAN2PY')
            yL, yR = y
            
        upper  = _field_array[x-1,:][yL-1:yR+2]
        center = _field_array[x,  :][yL-1:yR+2]
        lower  = _field_array[x+1,:][yL-1:yR+2]
        
        self.around_data = np.array([upper, center, lower])

    # 頭上の情報把握用
    def look_up(self, _field_array):
        x, y = coordinateTranslator(field_size, *self.getLeafCoordination())
        overheads = _field_array[:,y][:x+1,:]
        return overheads
        
    # 光合成用
    def feel_sunlight(self, _field_array):
        if self.name == leaf:
            overheads = self.look_up(_field_array)
            shine = 0
            for i in range(overheads.shape[1]):
                ovhd = overheads[:,i]
                _trunk_num = np.count_nonzero(ovhd==trunk_representation)
                _leaf_num  = np.count_nonzero(ovhd==leaf_representation)
                if _trunk_num >= 1:
                    continue
                elif _leaf_num >= 1:
                    for _ in range(_leaf_num):
                        shine += self.lightness*(1-leaf_CutoffRatio)
            self.lightness = shine
    
    # seed(原点)から現在地までの距離
    def path_finder(self):
        pass
    
    # ペナルティ用
    def destruction(self):
        if self.name == trunk:
            # 寿命
            if self.age > trunk_LifeSpam:
                self.survival = False
            # 空中浮遊対策
            if np.count_nonzero(self.around_data==0) >= ((self.size_status[0]+2)*(self.size_status[1]+2))-1:
                self.survival = False
        elif self.name == leaf:
            # 寿命
            if self.age > leaf_LifeSpam:
                self.survival = False
            # 空中浮遊対策
            if np.count_nonzero(self.around_data==0) >= ((self.size_status[0]+2)*(self.size_status[1]+2))-1:
                self.survival = False
            # メンタルストレス死(日光不足)
            if self.mentalStress > leaf_MentalStressCapacity:
                self.survival = False
            # 日照不足によるメンタルストレス増加
            if self.lightness < leaf_LightStressAccThreshold:
                self.mentalStress += 1
    
    # セルのアップデート用
    def update(self, _cells_list, _my_index, _field_array):
        # delet myself
        if not self.survival:
            del _cells_list[_my_index]
        # 周辺確認
        self.look_around(_field_array)
        # 加齢
        self.age += 1
        # 日光浴
        self.feel_sunlight(_field_array)
        # ペナルティ
        self.destruction()
        # 成長
        if self.name == trunk:
            _cells_list = self.generation(_cells_list)
        # 描画
        _field_array = self.paint(_field_array)
        return (_cells_list, _field_array)

if __name__ == '__main__':
    field_array = np.zeros((field_size, field_size))  # 空のフィールドを作成(ゼロ埋め)
    field_array[-soil_depth:,:] += soil_representation # 土の領域を更新

    ## plant seed
    seed_cd = np.array([[int(field_size/2), soil_depth+1]])
    seed = Cell(trunk, seed_cd, trunk_DefoSize)         # seedのインスタンスを作成
    field_array = seed.paint(field_array)               # seedの座標をfield_arrayへ追加
    seed.look_around(field_array)                       # seed周辺の環境を更新

    for key, val in seed.__dict__.items():
        pprint.pprint(key+' : '+str(val))

    cells_list = []
    cells_list.append(seed)

    # show
    fig_ims = []
    fig, ax = plt.subplots()

    try_num = 5000
    try:
        while True:
            # end condition
            columL = np.count_nonzero(field_array[:-soil_depth,0]!=nothing)
            columR = np.count_nonzero(field_array[:-soil_depth,-1]!=nothing)
            rowTop = np.count_nonzero(field_array[0]!=nothing)
            if columL or columR or rowTop > 0:
                break
            if seed.age == try_num:
                break
            # update cells and field
            for index, cell in enumerate(cells_list):
                cells_list, field_array = cell.update(cells_list, index, field_array)
            # progress
            print("\r"+"PROGRESS : "+str(seed.age)+" / "+str(try_num), end='')
            # result animation
            if seed.age%50 == 0:
                im = ax.matshow(field_array)
                fig_ims.append([im])
    finally:
        ## RESULT ##
        soil_num  = np.count_nonzero(field_array==soil_representation)
        trunk_num = np.count_nonzero(field_array==trunk_representation)
        leaf_num  = np.count_nonzero(field_array==leaf_representation)
        trunk_weight = trunk_num*trunk_DefoSize[3]
        leaf_weight  = leaf_num*leaf_DefoSize[3]
        print("\n")
        print("instance num : ", len(cells_list))
        print("soil  : num={0}".format(soil_num))
        print("trunk : num={0}, weight={1}".format(trunk_num, trunk_weight))
        print("leaf  : num={0}, weight={1}".format(leaf_num, leaf_weight))
        print("TOTAL : weight={0}".format(trunk_weight+leaf_weight))
    
        anim = animation.ArtistAnimation(fig, fig_ims)
        anim.save('/Users/ryotaro/Desktop/cellular_automata/test.mp4')
        plt.show()
        plt.close()