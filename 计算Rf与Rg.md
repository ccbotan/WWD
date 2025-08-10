  
> TM-30 的**核心计算框架**、样本集、使用的色度函数与颜色空间、参考光源规则以及最终的指数定义都写在 ANSI/IES TM-30-20 里；Royer 的 tutorial 给出理解与推导依据、设计理由和计算流程的逐项解释

# 1）输入与总体思想（参考）

- **输入**：测试光源的光谱功率分布$P_{test}(\lambda)$（通常 380–780 nm 或 400–700 nm），以及 TM-30 标准规定的 **99 个色样反射率函数** $R_i(\lambda)（i=1..99）$。参考光源$P_{ref}(\lambda)$根据测试光源的$CCT$ 选取（黑体或 CIE D 系列，4500–5500K 间按标准混合）；这些都是 TM-30 指定的。
    
- **基本思想**：对每个样本 $i$，把反射率乘以光源 SPD 得到刺激，再用**CIE 1964 10° 色匹配函数**计算三刺激，做色适应并投影到 **CAM02-UCS**，在 CAM02-UCS 空间里计算测试与参考条件下每个样本的颜色差，然后把这些差异汇总得到 Rf（保真）与 Rg（色域）等指标

# 2）详细数值流程（逐步 + 公式）

## 步骤 1 — 计算每个样本在测试与参考光源下的光谱刺激
![[CIE_srf_cfi_1nm 2.csv]]
对每个样本 ：

$$S_{test,i}(\lambda)=P_{test}(\lambda)\cdot R_i(\lambda) \qquad S_{ref,i}(\lambda)=P_{ref}(\lambda)\cdot R_i(\lambda)$$

## 步骤 2 — 用 **CIE 1964 10° 色匹配函数** 得到三刺激
![[CIE_cc_1964_10deg 3.csv]]
记色匹配函数为 $\bar x_{10}(\lambda),\ \bar y_{10}(\lambda),\ \bar z_{10}(\lambda)$。对每个样本 i 计算：

$X_{t,i}=\int S_{test,i}(\lambda)\,\bar x_{10}(\lambda)\,d\lambda$
$Y_{t,i}=\int S_{test,i}(\lambda)\,\bar y_{10}(\lambda)\,d\lambda$
$Z_{t,i}=\int S_{test,i}(\lambda)\,\bar z_{10}(\lambda)\,d\lambda$
==同理得到参考光源$X_{r,i},Y_{r,i},Z_{r,i}$。==

## 步骤 3 — 把三刺激值送入 **CIECAM02 / CAM02-UCS** 的流程（含色适应）

TM-30 的核心采用 CAM02-UCS（基于 CIECAM02），流程（简要）：

1. 把 $X,Y,Z$ 转到 LMS常用 CAT02 变换矩阵

$$\begin{bmatrix} L \\ M \\ S \end{bmatrix}
=
\mathbf{M}_{CAT02}
\begin{bmatrix} X \\ Y \\ Z \end{bmatrix},

\quad
\mathbf{M}_{CAT02} =
\begin{bmatrix}
0.7328 & 0.4296 & -0.1624 \\
-0.7036 & 1.6975 & 0.0061 \\
0.0030 & 0.0136 & 0.9834
\end{bmatrix}$$

    同理计算参考光源在LMS下的值
    $$\begin{bmatrix} L_w \\ M_w \\ S_w \end{bmatrix}
=
\mathbf{M}_{CAT02}
\begin{bmatrix} X_w \\ Y_w \\ Z_w \end{bmatrix},

\quad
\begin{bmatrix} L_{wr} \\ M_{wr} \\ S_{wr} \end{bmatrix}
=
\mathbf{M}_{CAT02}
\begin{bmatrix} X_{wr} \\ Y_{wr} \\ Z_{wr} \end{bmatrix}
$$
2. 计算适应度D(degree of adaptation)  
$$D = F \left( 1 - \frac{1}{3.6} \exp\left( - \frac{L_A + 42}{92} \right) \right)
	$$
其中:
$F$是视觉场周边因子（$F=1.0$）
$L_A=64 cd/m^2$是适应场亮度


3. 用 D 做 von-Kries 风格的比例适应（对 LMS 分量逐分量缩放）
对每个分量按下列式子得到**适配后的**$L_c,M_c,S_c$
：
$$L_c = \left( \frac{L_{wr}}{L_w} D + (1 - D) \right) L$$
$$M_c = \left( \frac{M_{wr}}{M_w} D + (1 - D) \right) M
$$
$$S_c = \left( \frac{S_{wr}}{S_w} D + (1 - D) \right) S$$
  4.把适配后的 LMS 变换到 Hunt (HPE) 空间
  $$\begin{bmatrix} L' \\ M' \\ S' \end{bmatrix}
=
\mathbf{M}_H
\begin{bmatrix} X_c \\ Y_c \\ Z_c \end{bmatrix},

\quad
\mathbf{M}_H =
\begin{bmatrix}
0.38971 & 0.68898 & -0.07868 \\
-0.22981 & 1.18340 & 0.04641 \\
0.00000 & 0.00000 & 1.00000
\end{bmatrix}
$$

  5.计算亮度适应因子$F_L$（用于非线性压缩）
  $$k = \frac{1}{5 L_A + 1}$$

$$F_L = 0.2 \, k^4 (5 L_A) + 0.1 (1 - k^4)^2 (5 L_A)^{1/3}

$$
6.对 $L′,M′,S′$ 做非线性压缩（得到 $L'_a,M'_a,S'_a​$）
$$L'_a = \frac{400 \left( \frac{F_L L'}{100} \right)^{0.42} }{27.13 + \left( \frac{F_L L'}{100} \right)^{0.42} } + 0.1$$

$$M'_a = \frac{400 \left( \frac{F_L M'}{100} \right)^{0.42} }{27.13 + \left( \frac{F_L M'}{100} \right)^{0.42} } + 0.1$$

$$S'_a = \frac{400 \left( \frac{F_L S'}{100} \right)^{0.42} }{27.13 + \left( \frac{F_L S'}{100} \right)^{0.42} } + 0.1
$$
7,求得$a,b$
$$\begin{aligned}
a &= L'_a - \tfrac{12}{11} M'_a + \tfrac{1}{11} S'_a \\
b &= \tfrac{1}{9} (L'_a + M'_a - 2 S'_a)
\end{aligned}
$$
8.求得$J$
$$n = \frac{Y_b}{Y_w}   \quad (Y_b \text为20)$$

$$N_{bb} = N_{cb} = 0.725 \, n^{-0.2}$$

$$A = (2 L'_a + M'_a + \tfrac{1}{20} S'_a - 0.305) \, N_{bb}$$
$$z = 1.48 + \sqrt{n}$$

$$J = 100 \left( \frac{A}{A_w} \right)^{c z}$$

## 步骤 4 — 在 CAM02-UCS 空间计算单个样本的颜色差（ΔE）

对每个样本 i，得到测试与参考的 CAM02-UCS 坐标$(J'_{t,i},a'_{t,i},b'_{t,i})$与$(J'_{r,i},a'_{r,i},b'_{r,i})$。定义欧氏差：

==$\Delta E_i=\sqrt{(J'_{t,i}-J'_{r,i})^2+(a'_{t,i}-a'_{r,i})^2+(b'_{t,i}-b'_{r,i})^2}$==
## 步骤 5 — 计算 **每个色样的“样本保真度值”**（$Rf$）并合并为系统 Rf

TM-30 的总体思想：先把每个样本的色差 $\Delta E_i$ 通过某个 **尺度/映射** 转成“保真度分数”（范围 0–100），再对 99 个样本聚合得到 Rf。

1. 先求所有样本的平均色差（或对每个样本做逐样本映射后再平均；TM-30 的实现会对 individual fidelity 做映射避免负值）。
    
2. 用缩放系数把平均差映射到 [0,100]，并应用对数或指数型的限制，确保不会小于 0，100 表示完全匹配。
    

用文字公式表述（概念性）：

$\bar{\Delta E}=\frac{1}{99}\sum_{i=1}^{99}$$Rf = 100 - S(\bar{\Delta E})$

其中$S(\cdot)$ 表示按 TM-30 规范指定的缩放与（对数）修正函数；TM-30-20 文档给出精确的 $S$ 形式与系数（在不同版本中有轻微调整以与 CIE 224:2017 一致）。**具体系数与公式请参见 ANSI/IES TM-30-20 的“Rf 计算”栏目**，Royer tutorial 也描述了该映射的原理与由来。

---

## 步骤 6 — 计算色域$Rg$

TM-30 把 99 个色样分成 16 个 hue-bin（16 个色相箱），在 CAM02-UCS 的$a',b'$ 平面上：

1. 对每个 hue-bin，计算 bin 内样本的平均 a′,b′a',b'，16 个 bin 得到 16 个顶点，构成一个 16 边形（多边形）。分别对测试与参考产生 2 个多边形。
2. 计算两多边形面积：$A_{test}$ 与 $A_{ref}$。（多边形面积可用常见的多边形面积公式 / 叉积法计算。）
3. 定义：
$$Rg = 100 \times \frac{A_{test}}{A_{ref}}$$

- Rg=100 Rg=100 表示平均饱和度与参考相同；Rg>100Rg>100 表示平均饱和度增加（更鲜艳），Rg<100Rg<100 表示减少。

# 4）原文依据

1. **使用 99 个色样并其来源/目的** —— 见 TM-30 标准对 99 CES 的描述与样本选择方法（统计抽样、覆盖色域、均匀性），以及 Royer 对选择理由及优点的讨论。
2. **使用 CIE 1964 10° CMFs、CAM02-UCS，以及 CIECAM02 的色适应流程** —— TM-30-20 的核心计算框架部分明确规定这些组件；Royer 解释了它们对一致性与准确性的影响。
3. **在 CAM02-UCS 空间用欧氏距离作为单样本色差** —— TM-30-20 中用于计算 ΔEi\Delta E_i 的规定；Royer 说明此处使用 CAM02-UCS 的理由（更均匀）。
4. **Rf 的聚合/缩放与对数变换（防止负值）** —— Royer 在 tutorial 中描述 Rf 的概念性公式与为何采用对数/截断使得范围固定在 0–100；而 ANSI/IES TM-30-20 给出精确的缩放常数与实现步骤（标准文件）。
5. **Rg 的面积比定义** —— 在 TM-30 标准中给出：把 16 个 hue-bin 的平均 a′,b′a',b' 作为多边形顶点，用面积比乘 100 得到 Rg；Royer 对其物理含义与示例进行了说明。

