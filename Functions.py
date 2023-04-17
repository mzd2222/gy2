import random

from Entity import *
from ENV import *
import copy
import math
import numpy


def cal_Rij(md: MobileDevice, es: EdgeServer, parameters: Parameters):
    """
    计算 mdi到esj的传输速率
    :param md:
    :param es:
    :param parameters:
    :return: Rij
    """
    b_ij = parameters.b_ij[es.j]
    D_ij = parameters.D_ij[md.i, es.j]
    P_ij = parameters.P_ij[md.i, es.j]
    N_i = md.N_i

    # print(D_ij, N_i)

    R_ij = b_ij * math.log2(1 + P_ij / ((D_ij ** 4) * N_i))

    # print(R_ij)
    return R_ij


def cal_RKs(es: EdgeServer, Ks: List[MobileDevice], dc: DataCenter, parameters: Parameters):
    """
    计算第一层联盟组的增益，此函数只用于计算在ES上的联盟组；
    对于不卸载的MD组成的联盟组，收益为0
    :param es: 联盟组对应的边缘服务器es
    :param Ks: 联盟组的MD成员
    :param dc: DataCenter
    :param parameters: 总参数
    :return: 返回最后计算得到的增益
    """

    RKs_list = []

    for idx, md in enumerate(Ks):
        c_i = md.c_i
        r_i = md.r_i
        f_i = md.f_i
        R_is = cal_Rij(md=md, es=es, parameters=parameters)
        f_is = parameters.f_ij[es.j]

        lambda_is_dc = parameters.lambda_ij_dc[es.j][idx]

        R_dc = dc.R_dc
        d = dc.d
        t_dc = dc.t_dc

        RKs_list.append(
            c_i * r_i / f_i - \
            (r_i / R_is + c_i * r_i / f_is + lambda_is_dc * (r_i / R_dc + d + t_dc - c_i * r_i / f_is))
        )

    return RKs_list, sum(RKs_list)


def cal_RK(es_list: List[EdgeServer], Ks_list: List[List[MobileDevice]], dc: DataCenter, parameters: Parameters):
    """
    计算第二层联盟组的增益，此函数只用于计算在ES上的联盟组；
    :param es_list:
    :param Ks_list:
    :param dc: DataCenter
    :param parameters: 总参数
    :return: 返回最后计算得到的增益
    """
    R_K = 0
    R_K_list = []
    Rj_K_list = []

    for es, lambda_list, md_list in zip(es_list, parameters.lambda_ij_dc, Ks_list):
        Rj_K_list.clear()
        for lambda_ij, md in zip(lambda_list, md_list):
            c_i = md.c_i
            r_i = md.r_i
            f_is = parameters.f_ij[es.j]
            R_dc = dc.R_dc
            d = dc.d
            t_dc = dc.t_dc

            Rj_K = -lambda_ij * (r_i / R_dc + d + t_dc - c_i * r_i / f_is)
            R_K += Rj_K
            Rj_K_list.append(Rj_K)
        R_K_list.append(copy.copy(Rj_K_list))

    return R_K, R_K_list


def Algorithm1(md_list: List[MobileDevice], es_list: List[EdgeServer],
               Ks_list: List[List[MobileDevice]], parameters: Parameters,
               dc: DataCenter):
    parameters_ = copy.deepcopy(parameters)
    Ks_list_ = Ks_list
    num = 0

    END = False

    print("第一层博弈开始")

    while not END:
        for md_id in range(10):
            md = md_list[md_id]
            group_id_old = "N"
            # 获取group id
            for ii, group in enumerate(Ks_list_):
                if md in group:
                    group_id_old = ii

            # 随机选择目的地组
            choose_list = [i for i in range(len(Ks_list_))]
            choose_list.append("N")
            choose_list.remove(group_id_old)

            # print(choose_list)

            group_id_new = random.choice(choose_list)

            print("md" + str(md.i), "group_id:" + str(group_id_old), "random_choose:" + str(group_id_new), end=" ")

            change, change_N, change1, change2 = True, True, True, True

            # 自己一个联盟组
            if group_id_old == "N":

                # 目的地组Km 原始计算增益RKm
                RKm_list_old, RKm_old = cal_RKs(es=es_list[group_id_new], Ks=Ks_list_[group_id_new], dc=dc,
                                                parameters=parameters_)
                # 源组
                RKs_list_old, RKs_old = [], 0

                # 更新aij和相关参数
                new_aij = copy.deepcopy(parameters_.a_ij)
                new_aij[md_id, group_id_new] = 1
                Ks_list_, parameters_ = update_ENV(new_aij=new_aij,
                                                   es_list=es_list, md_list=md_list,
                                                   parameters=parameters_)
                # 计算新的 目的
                RKm_list_new, RKm_new = cal_RKs(es=es_list[group_id_new], Ks=Ks_list_[group_id_new], dc=dc,
                                                parameters=parameters_)
                # 计算新的 源组
                RKs_list_new, RKs_new = [], 0

                if RKm_new + RKs_new > RKm_old + RKs_old:
                    for idx, item1 in enumerate(RKm_list_new):
                        if idx == numpy.where(Ks_list_[group_id_new] == md)[0]:
                            print("jump1", end=' ')
                            continue
                        elif item1 >= 0:
                            change = True
                        else:
                            record_item = item1
                            record_idx = idx
                            change = False
                            break

                    # 满足条件 确认换联盟组
                    if change:
                        print("更新组：" + "md{}从组{}移动到组{}".format(md_id, group_id_old, group_id_new), end=" ")
                        parameters = copy.deepcopy(parameters_)
                        Ks_list = Ks_list_
                        num = 0
                    # 不满足条件 把参数改回来
                    else:
                        print("不更新组：" + "组{}Rj_Km第{}个{}<0".format(group_id_new, record_idx, record_item), end=" ")
                        parameters_ = copy.deepcopy(parameters)
                        Ks_list_ = Ks_list
                        num += 1

                else:
                    print("不更新组：", "RKm_new + RKs_new < RKm_old + RKs_old", RKm_new + RKs_new, "<", RKm_old + RKs_old,
                          end=" ")
                    parameters_ = copy.deepcopy(parameters)
                    Ks_list_ = Ks_list
                    num += 1

            # 边缘服务器联盟组
            else:
                # 目的转移组为N 即转移为不卸载
                if group_id_new == "N":

                    # 目的地组Km 原始计算增益RKm
                    RKm_list_old, RKm_old = [], 0
                    # 源组
                    RKs_list_old, RKs_old = cal_RKs(es=es_list[group_id_old], Ks=Ks_list_[group_id_old], dc=dc,
                                                    parameters=parameters_)

                    # 更新aij和相关参数
                    new_aij = copy.deepcopy(parameters_.a_ij)
                    new_aij[md_id, group_id_old] = 0
                    Ks_list_, parameters_ = update_ENV(new_aij=new_aij,
                                                       es_list=es_list, md_list=md_list,
                                                       parameters=parameters_)
                    # 计算新的 目的
                    RKm_list_new, RKm_new = [], 0
                    # 计算新的 源组
                    RKs_list_new, RKs_new = cal_RKs(es=es_list[group_id_old], Ks=Ks_list_[group_id_old], dc=dc,
                                                    parameters=parameters_)

                    if RKm_new + RKs_new > RKm_old + RKs_old:
                        for idx, item1 in enumerate(RKs_list_new):
                            if item1 >= 0:
                                change_N = True
                            else:
                                record_item = item1
                                record_idx = idx
                                change_N = False
                                break

                        # 满足条件 确认换联盟组
                        if change_N:
                            print("更新组：" + "md{}从组{}移动到组{}, 变为不卸载".format(md_id, group_id_old, group_id_new), end=" ")
                            parameters = copy.deepcopy(parameters_)
                            Ks_list = Ks_list_
                            num = 0
                        # 不满足条件 把参数改回来
                        else:
                            print("不更新组：" + "组{}Rj_Km第{}个{}<0".format(group_id_new, record_idx, record_item), end=" ")
                            parameters_ = copy.deepcopy(parameters)
                            Ks_list_ = Ks_list
                            num += 1

                    else:
                        print("不更新组：", "RKm_new + RKs_new < RKm_old + RKs_old", RKm_new + RKs_new, "<",
                              RKm_old + RKs_old,
                              end=" ")
                        parameters_ = copy.deepcopy(parameters)
                        Ks_list_ = Ks_list
                        num += 1
                # 目的转移组为别的组
                else:
                    # 目的地组Km 原始计算增益RKm_old
                    RKm_list_old, RKm_old = cal_RKs(es=es_list[group_id_new], Ks=Ks_list_[group_id_new], dc=dc,
                                                    parameters=parameters_)
                    # 源组 原始计算增益RKs_old
                    RKs_list_old, RKs_old = cal_RKs(es=es_list[group_id_old], Ks=Ks_list_[group_id_old], dc=dc,
                                                    parameters=parameters_)

                    # 更新aij和相关参数
                    new_aij = copy.deepcopy(parameters_.a_ij)
                    new_aij[md_id, group_id_new] = 1
                    new_aij[md_id, group_id_old] = 0
                    Ks_list_, parameters_ = update_ENV(new_aij=new_aij,
                                                       es_list=es_list, md_list=md_list,
                                                       parameters=parameters_)
                    # 计算新的 目的RKm
                    RKm_list_new, RKm_new = cal_RKs(es=es_list[group_id_new], Ks=Ks_list_[group_id_new], dc=dc,
                                                    parameters=parameters_)
                    # 计算新的 源组
                    RKs_list_new, RKs_new = cal_RKs(es=es_list[group_id_old], Ks=Ks_list_[group_id_old], dc=dc,
                                                    parameters=parameters_)

                    if RKm_new + RKs_new > RKm_old + RKs_old:
                        for idx1, Rj_Km in enumerate(RKm_list_new):
                            if idx1 == numpy.where(Ks_list_[group_id_new] == md)[0]:
                                print("jump3", end=' ')
                                continue
                            elif Rj_Km >= 0:
                                change1 = True
                            else:
                                record_Rj_Km = Rj_Km
                                record_idx1 = idx1
                                change1 = False
                                break

                        for idx2, Rj_Ks in enumerate(RKs_list_new):
                            if idx2 == numpy.where(Ks_list_[group_id_old] == md)[0]:
                                print("jump4", end=' ')
                                continue
                            elif Rj_Ks >= 0:
                                change2 = True
                            else:
                                record_Rj_Ks = Rj_Ks
                                record_idx2 = idx2
                                change2 = False
                                break

                        # 满足条件 确认换联盟组
                        if change1 and change2:
                            print("更新组：" + "md{}从组{}移动到组{}".format(md_id, group_id_old, group_id_new), end=" ")
                            parameters = copy.deepcopy(parameters_)
                            Ks_list = Ks_list_
                            num = 0
                        # 不满足条件 把参数改回来
                        else:
                            if not change1:
                                print("不更新组：" + "组{} Rj_Km第{}个 {}<0".format(group_id_new, record_idx1, record_Rj_Km), end=" ")
                            if not change2:
                                print("不更新组：" + "组{} Rj_Km第{}个 {}<0".format(group_id_new, record_idx2, record_Rj_Ks), end=" ")
                            parameters_ = copy.deepcopy(parameters)
                            Ks_list_ = Ks_list
                            num += 1

                    else:
                        print("不更新组：", "RKm_new + RKs_new < RKm_old + RKs_old", RKm_new + RKs_new, "<", RKm_old + RKs_old,
                              end=" ")
                        parameters_ = copy.deepcopy(parameters)
                        Ks_list_ = Ks_list
                        num += 1

            print("lambda_ij_dc:", parameters_.lambda_ij_dc, end=" ")
            print("num={}".format(num))

            if num >= parameters.i_num * 10:
                END = True
                break

    # print(parameters.a_ij)
    print("第一层博弈结束")

    return Ks_list, parameters


def Algorithm2(md_list: List[MobileDevice], es_list: List[EdgeServer],
               Ks_list: List[List[MobileDevice]], parameters: Parameters,
               dc: DataCenter):
    for epoch in range(5):

        print("epoch:{} ".format(epoch), end=" ")

        Ks_list, parameters = Algorithm1(md_list=md_list, es_list=es_list, Ks_list=Ks_list,
                                         parameters=parameters, dc=dc)
        parameters_ = copy.deepcopy(parameters)
        num = 0

        print("第二层博弈开始")
        END = False
        while not END:
            for idx_j, lambda_ij_dcs in enumerate(parameters_.lambda_ij_dc):
                if END:
                    break
                for idx_i in range(len(lambda_ij_dcs)):
                    print("group_id:" + str(idx_j),  "第{}个任务".format(idx_i), end="-")

                    # 计算原始Rk
                    Rk_old, R_K_list_old = cal_RK(es_list=es_list, Ks_list=Ks_list, parameters=parameters_, dc=dc)

                    if parameters_.lambda_ij_dc[idx_j][idx_i]:
                        parameters_.lambda_ij_dc[idx_j][idx_i] = 0
                        print("从:1->0", end=", ")
                    else:
                        parameters_.lambda_ij_dc[idx_j][idx_i] = 1
                        print("从:0->1", end=", ")

                    Rk_new, R_K_list_new = cal_RK(es_list=es_list, Ks_list=Ks_list, parameters=parameters_, dc=dc)

                    if Rk_new > Rk_old:
                        # 满足条件 确定变更
                        parameters = copy.deepcopy(parameters_)
                        num = 0
                        print("更新组：" + "λij_dc组{}第{}个更新为{}".format(idx_j, idx_i, parameters_.lambda_ij_dc[idx_j][idx_i]),
                              end=" ")
                    else:
                        # 不变更
                        parameters_ = copy.deepcopy(parameters)
                        num += 1
                        print("不更新组：" + "Rk_new < Rk_old {} < {}".format(Rk_new, Rk_old),
                              end=" ")

                    print(parameters.lambda_ij_dc, end=" ")
                    print("num={}".format(num))
                    if num > 30:
                        END = True
                        break
        print("第二层博弈结束")


