import random

import numpy

from ENV import *
from Functions import *

if __name__ == "__main__":

    i_num = 10
    j_num = 3
    random.seed(1)
    numpy.random.seed(1)

    # MD
    r_i_list = []
    c_i_list = []
    f_i_list = []
    N_i_list = []

    for i in range(i_num):
        r_i = 1.0 + 0.1 * i
        c_i = 100 + 50 * i
        f_i = 80 + 10 * i
        N_i = 1e-5
        # N_i = -174 + 0.1 * i

        r_i_list.append(r_i)
        c_i_list.append(c_i)
        f_i_list.append(f_i)
        N_i_list.append(N_i)

    # ES
    F_j_list = []
    B_j_list = []
    for j in range(j_num):
        F_j = 500 + 100 * j  # MHz
        B_j = 15.0 + 2 * j  # MHz

        F_j_list.append(F_j)
        B_j_list.append(B_j)

    # DC
    R_dc = 50.0  # Mb/s
    d = 1  # s
    t_dc = 0.1  # s

    # parameters
    P_ij_list = []
    D_ij_list = []
    f_ij = [0]  # 根据联盟组内MD个数平均分配 一维数组只跟j有关 后续调用update更新
    b_ij = [0]  # 根据联盟组内MD个数平均分配 一维数组只跟j有关 后续调用update更新
    a_ij = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]

    for i in range(i_num):
        P = []
        D = []
        for j in range(j_num):
            P_ij = 7.0 + j + i
            D_ij = random.randint(1, 50)
            P.append(P_ij)
            D.append(D_ij)

        P_ij_list.append(P)
        D_ij_list.append(D)

    md_list, es_list, dc, parameters = Creat_ENV(i_num=i_num, j_num=j_num,
                                                 r_i_list=r_i_list,
                                                 c_i_list=c_i_list,
                                                 f_i_list=f_i_list,
                                                 N_i_list=N_i_list,
                                                 F_j_list=F_j_list,
                                                 B_j_list=B_j_list,
                                                 R_dc=R_dc, d=d, t_dc=t_dc,
                                                 P_ij=P_ij_list,
                                                 D_ij=D_ij_list,
                                                 f_ij=f_ij,
                                                 b_ij=b_ij,
                                                 a_ij=a_ij,
                                                 )

    Ks_list, parameters = update_ENV(new_aij=parameters.a_ij,
                                     es_list=es_list, md_list=md_list,
                                     parameters=parameters)
    # print(parameters.lambda_ij_dc)
    print(sum(sum(parameters.a_ij)) / parameters.i_num)
    # print(parameters.D_ij)
    # RKm_list_old, RKm_old = cal_RKs(es=es_list[0], Ks=Ks_list[0], dc=dc, parameters=parameters)
    # print(RKm_old)
    # print(parameters.lambda_ij_dc)

    # RKm_list_old, RKm_old = cal_RKs(es=es_list[0], Ks=Ks_list[0], dc=dc, parameters=parameters)

    # print(sum(sum(parameters.a_ij)) / parameters.i_num)
    # Ks_list, parameters = Algorithm1(md_list=md_list, es_list=es_list, dc=dc, Ks_list=Ks_list, parameters=parameters)
    # print(parameters.a_ij)
    # parameters.lambda_ij_dc[1] = [1, 0, 0]
    #
    # RK, RK_list = cal_RK(es_list=es_list, Ks_list=Ks_list, parameters=parameters, dc=dc)
    #
    # print(RK, RK_list)
    # print(len(Ks_list))

    # Algorithm1(md_list=md_list, es_list=es_list, dc=dc, Ks_list=Ks_list, parameters=parameters)
    Algorithm2(md_list=md_list, es_list=es_list, dc=dc, Ks_list=Ks_list, parameters=parameters)
