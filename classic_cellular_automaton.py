import numpy as np
from matplotlib import animation
from matplotlib import pyplot as plt

def moore_neighborhood(grid, _row, _col):
    gRow, gCol = grid.shape
    if (_row>0 and _col>0) and (_row<gRow-1 and _col<gCol-1):
        upper  = grid[_row-1][_col-1:_col+2]
        center = grid[ _row ][_col-1:_col+2]
        lower  = grid[_row+1][_col-1:_col+2]
        return np.array([upper, center, lower])
    else:
        return None

if __name__=='__main__':
    field_size = 100
    field_array = np.zeros((field_size, field_size))
    new_field = field_array.copy()

    ## 初期配置
    center = int(field_size/2)
    #'''
    field_array[center, center]   = 1
    field_array[center, center+1] = 1
    field_array[center, center-1] = 1
    field_array[center+1, center] = 1
    #'''
    '''
    field_array[center, center]     = 1
    field_array[center+1, center]   = 1
    field_array[center-1, center]   = 1
    field_array[center, center-1]   = 1
    field_array[center-1, center+1] = 1
    '''

    ## メイン処理
    fig_ims = []
    fig, ax = plt.subplots()
    im = ax.imshow(field_array)
    fig_ims.append([im])

    try:
        loop_num = 300
        for rng in range(loop_num):
            print('\r'+'STATUS : '+str(rng), end='')
            for row in range(field_size):
                for col in range(field_size):
                    my_status = field_array[row, col]
                    mn = moore_neighborhood(field_array, row, col)
                    if mn is not None:
                        mn_sum = np.sum(mn) - my_status
                        ## 隣接するセルがちょうど3個のとき、誕生
                        if my_status == 0 and mn_sum == 3:
                            new_field[row, col] = 1
                        ## 隣接するセルが2個または3個存在するとき、生存
                        elif my_status == 1 and mn_sum in (2, 3):
                            new_field[row, col] = 1
                        ## 隣接するセルが4個または1個以下のとき、死滅
                        elif my_status == 1 and mn_sum not in (2, 3):
                        #else:
                            new_field[row, col] = 0
            field_array[:] = new_field[:]
            im = ax.imshow(field_array)
            fig_ims.append([im])
    except:
        print('\nExit processing')
    finally:
        anim = animation.ArtistAnimation(fig, fig_ims)
        anim.save('/Users/ryotaro/Desktop/cellular_automata/old.mp4')
        plt.show()
        plt.close()
