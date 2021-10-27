import pprint
import threading
import multiprocessing as mp

import numpy as np
from matplotlib import animation
from matplotlib import pyplot as plt
from matplotlib import rc

# <<global status>>
field_size = 100 # フィールド一辺の大きさ
nothing = 0

soil = 'soil'
soil_representation = -1     # 配列内での表現値
soil_depth          = 5      # 土の深さ

trunk                      = 'trunk'
trunk_DefoSize             = [1, 1, None, 1] # デフォルトのサイズパラメータ
trunk_representation       = 1               # 配列内での表現値
trunk_LifeSpam             = float('inf')    # 寿命
trunk_MentalStressCapacity = float('inf')    # メンタルストレス容量
trunk_GrowthRate           = 0.8             # 成長率
trunk_OccurrenceProb       = 0.7             # 生成確率

leaf                         = 'leaf'
leaf_DefoSize                = [2, 1, None, 1] # デフォルトのサイズパラメータ
leaf_representation          = 2               # 配列内での表現値
leaf_LifeSpam                = 1000             # 寿命
leaf_MentalStressCapacity    = 40              # メンタルストレス容量
leaf_LightStressAccThreshold = 10              # 光由来のメンタルストレス受容閾値
leaf_GrowthRate              = 0.5             # 成長率
leaf_OccurrenceProb          = 1- trunk_OccurrenceProb

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
            x, y = coordinateTranslator(targetHight, x, y, mode='CARTESIAN2PY')
            _field_array[x, y] = trunk_representation
        elif self.name == leaf:
            for cd in self.coordination:
                x, y = cd
                x, y = coordinateTranslator(targetHight, x, y, mode='CARTESIAN2PY')
                _field_array[x, y] = leaf_representation
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
                    # 90%で上方向へ成長
                    if np.random.rand() <= 0.7:
                        #上が0
                        if self.around_data[0][1] == nothing:
                            new_trunk = Cell(trunk, np.array([[x, y+1]]), trunk_DefoSize)
                            _cells_list.append(new_trunk)
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
        pass
        
    # 日照把握用
    def sunlight(self, _field_array):
        if self.mame == leaf:
            pass
    
    # ペナルティ部の更新用
    def destruction(self):
        if self.name == trunk:
            # 寿命
            if self.age > trunk_LifeSpam:
                self.survival = False
            # 空中浮遊対策
            if np.count_nonzero(self.around_data==0) >= ((self.size_status[0]+2)*(self.size_status[1]+2))-1:
                self.survival = False
            # メンタルストレス死
            if self.mentalStress > trunk_MentalStressCapacity:
                self.survival = False
        elif self.name == leaf:
            # 寿命
            if self.age > leaf_LifeSpam:
                self.survival = False
            # 空中浮遊対策
            if np.count_nonzero(self.around_data==0) >= ((self.size_status[0]+2)*(self.size_status[1]+2))-1:
                self.survival = False
            # メンタルストレス死
            if self.mentalStress > leaf_MentalStressCapacity:
                self.survival = False
            # 日照不足によるメンタルストレス増加
            if self.lightness < leaf_LightStressAccThreshold:
                self.mentalStress += 1

    # 消滅処理
    def annihilation(self, _cells_list, _my_index, _field_array):
        _x, _y = np.where(_field_array==1)
        _coord_list = np.concatenate([_x.reshape(len(_x), 1), _y.reshape(len(_y), 1)], 1)
        if np.any(_coord_list==self.coordination):
            del _cells_list[_my_index]
        return _cells_list
    
    def update(self, _cells_list, _my_index, _field_array):
        self.age += 1
        self.destruction()
        self.look_around(_field_array)
        if self.name == trunk:
            _cells_list = self.generation(_cells_list)
        _field_array = self.paint(_field_array)
        #_cells_list = self.annihilation(_cells_list, _my_index, _field_array)

        return (_cells_list, _field_array)

def main(parent_conn, cells_list, field_array):
    try_num = 5000
    while True:
        for index, cell in enumerate(cells_list):
            # update cells and field
            cells_list, field_array = cell.update(cells_list, index, field_array)
        # progress
        print("\r"+str(seed.age), end='')
        # result animation
        if cells_list[0].age%50 == 0:
            parent_conn.send((cells_list, field_array))
        # end condition
        if cells_list[0].age == try_num:
            break

def show_graph(connection):
    cells_list, field_array = connection.recv()
    fig_ims = []
    fig, ax = plt.subplots()
    
    im = ax.matshow(field_array)
    im.set_data(field_array)
    fig_ims.append([im])
    plt.pause(.01)
    
    #anim = animation.ArtistAnimation(fig, fig_ims)
    #anim.save('/Users/ryotaro/Desktop/cellular_automata/test.mp4')


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

    # threading & multiprocess
    parent_conn, child_conn = mp.Pipe()
    #child = mp.Process(target=show_graph, args=(child_conn,))

    p1 = mp.Process(target=main, args=(*(parent_conn, cells_list, field_array), ))
    p2 = mp.Process(target=show_graph, args=(child_conn, ))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
        
    ## RESULT ##
    soil_num  = np.count_nonzero(field_array==soil_representation)
    trunk_num = np.count_nonzero(field_array==trunk_representation)
    leaf_num  = np.count_nonzero(field_array==leaf_representation)
    print("\n")
    print("TOTAL INSTANCE : ", len(cells_list))
    print("soil : {0} \ntrunk : {1} \nleaf : {2}".format(soil_num, trunk_num, leaf_num))
