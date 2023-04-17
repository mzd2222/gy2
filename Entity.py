import math
import numpy
from typing import List

# MD
class MobileDevice:

    def __init__(self, i: int, r_i: float, c_i: float, f_i: float, N_i: float):

        self.i = i  # MD编号

        self.r_i = r_i  # MD上该任务需要处理的数据量大小
        self.c_i = c_i  # 理处1-bit数据需要的CPU cycles
        self.f_i = f_i  # MD的CPU频率，即本地计算能力
        self.N_i = N_i  # MD的噪声功率谱密度


# ES
class EdgeServer:

    def __init__(self, j: int, F_j, B_j):

        self.j = j      # ES编号

        self.F_j = F_j  # 边缘服务器sj总计算能力
        self.B_j = B_j  # 边缘服务器sj总无线信道带宽


# DC
class DataCenter:

    def __init__(self, R_dc: float, d: float, t_dc: float):

        self.R_dc = R_dc  # 网络平均传输速率
        self.d = d        # 网络平均传输延迟
        self.t_dc = t_dc  # 假定任意大小数据，完成处理的时间



class Parameters:
    """
    输入i_num为UE数量，j_num为ES数量，其中所有数据都是维度为[i_num, j_num]的矩阵，表示UE和ES共用的变量
    a[:, 0]为提取一列的方法
    a[0]为提取一行的方法
    """

    def __init__(self,
                 i_num: int, j_num: int,
                 P_ij: List[List],
                 D_ij: List[List],
                 f_ij: List[float],
                 b_ij: List[float],
                 a_ij: List[List],
                 ):

        self.i_num = i_num  # MD数量
        self.j_num = j_num  # ES数量
        self.f_ij = numpy.array(f_ij)  # 一维数组 表示第j个es平均分配的资源
        self.b_ij = numpy.array(b_ij)  # 一维数组 表示第j个es平均分配的资源
        self.P_ij = numpy.array(P_ij)  # MD与ES进行无线通讯时的发射功率
        self.D_ij = numpy.array(D_ij)  # MD到ES的距离
        self.a_ij = numpy.array(a_ij)  # 第一层MD对ES的卸载决策

        self.lambda_ij_dc = []  # 自动计算第二层卸载决策
        for idx in range(j_num):
            self.lambda_ij_dc.append([0 for _ in range(sum(self.a_ij.T[idx]))])

