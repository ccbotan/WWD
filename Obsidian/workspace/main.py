import colour
import numpy as np
import pandas as pd
import os

def load_spectral_data(file_path):
    """
    读取光谱数据CSV文件, 包含错误处理和数据验证
    :param file_path:  CSV文件路径
    :return: tuple:(波长数组, 光强数组, CSV数据文件) 或者 (None, None, None)
    """

    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 - {file_path}")
        return None, None, None

    if not file_path.lower().endswith(".csv"):
        print(f"Error: file attribution is wrong, not '.csv' file - {file_path}")
        return None, None, None

    try:
        data = pd.read_csv(
            file_path,
            sep = None,
            engine = 'python',
            skip_blank_lines = True
        )

        if data.empty:
            print("Error: file is empty")
            return None, None, None

        required_columns = ['波长', '光强']

        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            print(f"Error: missing columns: {missing_columns}")
            return None, None, None

        wavelengths = data['波长'].to_numpy(dtype = np.float64)
        intensities = data['光强'].to_numpy(dtype = np.float64)

        print(f"成功读取数据: {os.path.basename(file_path)}")
        print(f"数据点数: {len(data)}")
        print(f"波长范围: {wavelengths.min():.1f} - {wavelengths.max():.1f} nm")
        print(f"光强范围: {intensities.min():.2f} - {intensities.max():.2f}")

        return data, wavelengths, intensities
    except Exception as e:
        print(f"读取文件时发生错误: {str(e)}")
        return None, None, None


if __name__ == "__main__":

    #文件路径
    csv_path = '../attachment/data.csv'

    # 读取数据
    wavelengths, intensities, data = load_spectral_data(csv_path)

    #构造SPD

    spd = colour.SpectralDistribution(
        data = intensities,
        wavelengths = wavelengths,
        name = 'SPD'
    )

    if spd is not None:
        # 插值到连续波长
        target_wavelengths = colour.SpectralShape(360, 780, 1)
        interpolated_spd = spd.interpolate(target_wavelengths)
        if interpolated_spd is None:
            print(f"the interpolated spectral distribution is None, failed")


    else:
        print(f"<UNK> SPD <UNK>")

    # 计算三刺激值XYZ (默认使用 CIE 1931 2°标准观察者
    xyz = colour.sd_to_XYZ(spd)
    print(f"CIE XYZ 三刺激值:{xyz}")


    # 转换为 CIE 1931(x,y) 色坐标
    xy = colour.XYZ_to_xy(xyz)
    print(f"CIE 1931 (x, y) 色坐标: {xy}")

    # 转换为 CIE 1960(u, v) 色坐标 (均匀色空间)
    uv_prime = colour.xy_to_UCS_uv(xy)
    print(f"CIE 1960UCS (u, v) 色坐标: {uv_prime}")


    #使用roboson 牛顿迭代法计算相关色温

    cct, delta_uv = colour.xy_to_CCT(xy, method='')

    # 注意这里的 xy_to_CCT 要手动写一个 2023年的版本







