import serial
import struct
import time


# 初始化RS485串口
def init_serial(port, baudrate=115200):
    ser = serial.Serial(port, baudrate=baudrate)
    return ser

# 发送指令到灵巧手
def send_command(ser, cmd_frame):
    ser.write(cmd_frame)
    # 等待回应（根据实际情况调整等待时间和回应处理）
    response = ser.read()  # 读取足够长的字节以确保接收到回应
    print("Received Response:", response.hex())

# 构建设置角度的指令帧
def build_angle_set_cmd(hand_id, angles):
    # 寄存器起始地址
    # 构建指令帧的头部
    # 小拇指内部伺服电缸对应 ID 为1，
    # 无名指内部伺服电缸对应ID为2.
    # 中指内部伺服电缸对应 ID 为3，
    # 食指内部伺服电缸对应 ID 为4，
    # 大拇指弯曲运动内部伺服电缸对应 ID 为5，
    # 大拇指旋转运动内部伺服电缸对应 ID 为6。
    cmd_frame = bytearray([0xEB, 0x90, hand_id, 0x0F, 0x12, 0xCE, 0x05])
    # 添加角度值,
    for angle in angles:
        cmd_frame += struct.pack('<H', angle)  # 小端格式
    # 计算校验和
    checksum = sum(cmd_frame[2:]) & 0xFF
    cmd_frame.append(checksum)
    return cmd_frame

# 示例使用
if __name__ == '__main__':
    # 替换为实际的串口名称和波特率
    port_name = 'COM4'  # 或Windows上的'COMx'
    ser = init_serial(port_name, 115200)
    # 设置的角度值
    angles = [1000, 1000, 1000, 1000, 1000, 1000]
    # 构建指令帧
    cmd_frame = build_angle_set_cmd(1, angles)
    print("Sending Command:", cmd_frame.hex())
    # 发送指令帧
    send_command(ser, cmd_frame)
    time.sleep(3)



     # 设置的角度值
    angles = [1000, 500, 500, 500, 1000, 1000]
    # 构建指令帧
    cmd_frame = build_angle_set_cmd(1, angles)
    print("Sending Command:", cmd_frame.hex())
    # 发送指令帧
    send_command(ser, cmd_frame)
    # 关闭串口
    ser.close()
