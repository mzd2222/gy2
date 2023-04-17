import random

from ENV import *


if __name__ == "__main__":

    i_num = 10
    j_num = 3

    # MD
    r_i_list = []
    c_i_list = []
    f_i_list = []
    N_i_list = []

    for i in range(i_num):
        r_i = 1.0 + 0.1 * i
        c_i = 100 + 50 * i
        f_i = 80 + 10 * i
        N_i = -174 + 0.1 * i

        r_i_list.append(r_i)
        c_i_list.append(c_i)
        f_i_list.append(f_i)
        N_i_list.append(N_i)

    # ES
    F_j_list = []
    B_j_list = []
    for j in range(j_num):
        F_j = 500 + 200 * j  # MHz
        B_j = 15.0 + 2 * j  # MHz

        F_j_list.append(F_j)
        B_j_list.append(B_j)

    # DC
    R_dc = 50.0  # Mb/s
    d = 1        # s
    t_dc = 0.1   # s

    # parameters
    P_ij = []
    D_ij = []
    f_ij = []
    b_ij = []
    a_ij = [
            [1, 0, 0],
            [1, 0, 0],
            [0, 0, 0],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 0],
            [0, 1, 0],
            [1, 0, 0],
            [0, 0, 0],
            [0, 1, 0],
            ]
    lambda_ij_dc = [
                    [0, 0, 0],
                    [0, 0],
                    [0, 0]
                    ]

    for i in range(i_num):

        for j in range(j_num):
            P_ij = 7.0 + j + i
            D_ij = random.randint(0, 50)
            f_ij = 0  # 根据联盟组内MD个数平均分配
            b_ij = 0  # 根据联盟组内MD个数平均分配




    # md_list, es_list, dc, parameters = Creat_ENV()