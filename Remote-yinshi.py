import socket
import struct
import serial
import time

# 初始化RS485串口
def init_serial(port, baudrate=115200):
    try:
        ser = serial.Serial(port, baudrate=baudrate)
        return ser
    except serial.SerialException as e:
        print(f"Failed to open serial port: {e}")
        return None

# 发送指令到灵巧手
def send_command(ser, cmd_frame):
    try:
        ser.write(cmd_frame)
        # 等待回应（根据实际情况调整等待时间和回应处理）
        response = ser.read()  # 读取足够长的字节以确保接收到回应
        print("Received Response:", response.hex())
    except serial.SerialException as e:
        print(f"Serial communication error: {e}")

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

def main():
    # 通过udp接收手套数据
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('127.0.0.1', 8082)
    udp_socket.bind(server_address)
    print("Listening for data on {} port {}...".format(*server_address))
    
    port_name = 'COM8'  # 或Windows上的'COMx'
    ser = init_serial(port_name, 115200)
    if ser is None:
        return

    current_angles = [1000, 1000, 1000, 1000, 1000, 1000]
    # cmd_frame = build_angle_set_cmd(1, current_angles)
    # # send_command(ser, cmd_frame)
    # time.sleep(3)  
    num = 0
    try:
        while True:
            data, address = udp_socket.recvfrom(1024)
            floats = struct.unpack('25f', data)
            print("data:", floats)

            thumb_angles = floats[1:4]
            index_angles = floats[6:9]
            middle_angles = floats[11:14]
            ring_angles = floats[16:19]
            pinky_angles = floats[21:24]
            print(sum(thumb_angles))
            print(sum(index_angles))
            print(sum(middle_angles))
            print(sum(ring_angles))
            print(sum(pinky_angles))

            current_angles[5] = 700-round(sum(thumb_angles))*3
            current_angles[4] = 1000-round(sum(thumb_angles))*3
            current_angles[3] = 1000-round(sum(index_angles))*3
            current_angles[2] = 1000-round(sum(middle_angles))*3
            current_angles[1] = 1000-round(sum(ring_angles))*3
            current_angles[0] = 1000-round(sum(pinky_angles))*3
            # 构建指令帧
            cmd_frame = build_angle_set_cmd(1, current_angles)
            print("Sending Command:", cmd_frame.hex())
            
            print(f"Current angles: {current_angles}")
            send_command(ser, cmd_frame)
            # num += 1
            # if num % 30 == 0:
            #     # 发送指令帧
            #     send_command(ser, cmd_frame)

    except KeyboardInterrupt:
        print("程序被手动中止")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        udp_socket.close()
        ser.close()

if __name__ == '__main__':
    main()
