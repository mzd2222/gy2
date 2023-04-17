import copy
from typing import List
from Entity import *
import numpy


def Creat_ENV(i_num, j_num,

              # MD
              r_i_list: List,
              c_i_list: List,
              f_i_list: List,
              N_i_list: List,

              # ES
              F_j_list: List,
              B_j_list: List,

              # DC
              R_dc, d, t_dc,

              # Parameters
              P_ij: List[List],
              D_ij: List[List],
              f_ij: List[float],
              b_ij: List[float],
              a_ij: List[List],
              ):
    md_list = []
    es_list = []

    for i in range(i_num):
        md = MobileDevice(i=i, r_i=r_i_list[i], c_i=c_i_list[i], f_i=f_i_list[i], N_i=N_i_list[i])
        md_list.append(md)

    for j in range(j_num):
        es = EdgeServer(j=j, B_j=B_j_list[j], F_j=F_j_list[j])
        es_list.append(es)

    dc = DataCenter(R_dc=R_dc, d=d, t_dc=t_dc)

    parameters = Parameters(i_num=i_num, j_num=j_num,
                            P_ij=P_ij, D_ij=D_ij,
                            f_ij=f_ij, b_ij=b_ij,
                            a_ij=a_ij)

    return numpy.array(md_list), numpy.array(es_list), dc, parameters


def update_ENV(new_aij, md_list: List[MobileDevice], es_list: List[EdgeServer], parameters: Parameters):
    """
    aij更新之后 相应的更新bij fij 联盟组 等（后续补充）
    :param new_aij: 新的aij
    :param es_list:
    :param md_list:
    :param parameters: 老的参数
    :return: 返回新的联盟组list 以及更新后的parameters
    """
    old_aij = parameters.a_ij

    # 计算新的 lambda_ij_dc
    lie_list_old = old_aij.T
    lie_list_new = new_aij.T

    for idx, (lie_old, lie_new) in enumerate(zip(lie_list_old, lie_list_new)):
        if numpy.array_equal(lie_old, lie_new):
            pass

        # 删除
        elif sum(lie_old) > sum(lie_new):
            a = list(numpy.where(lie_old == 1)[0])
            b = list(numpy.where(lie_new == 1)[0])
            index_list = [_ for _ in range(len(a))]
            for x in b:
                index_list.remove(a.index(x))

            delete_index_lambda = index_list[0]
            parameters.lambda_ij_dc[idx][delete_index_lambda] = "NN"
            parameters.lambda_ij_dc[idx].remove("NN")

        # 新增
        elif sum(lie_old) < sum(lie_new):
            a = list(numpy.where(lie_old == 1)[0])
            b = list(numpy.where(lie_new == 1)[0])
            index_list = [_ for _ in range(len(b))]
            for x in a:
                index_list.remove(b.index(x))

            insert_index_lambda = index_list[0]
            parameters.lambda_ij_dc[idx].insert(insert_index_lambda, 0)

    # 更新aij
    parameters.a_ij = new_aij
    Ks_list = []
    b_ij = []
    f_ij = []
    for es in es_list:
        lie = parameters.a_ij[:, es.j]
        # 计算新的联盟组
        Ks_list.append(md_list[numpy.where(lie)])

        # 计算新的fij bij
        md_num = sum(lie)
        # 排除0错误
        if md_num == 0:
            md_num = 1
        b_ij.append(es.B_j / md_num)
        f_ij.append(es.F_j / md_num)

    parameters.b_ij = b_ij
    parameters.f_ij = f_ij

    return Ks_list, parameters

