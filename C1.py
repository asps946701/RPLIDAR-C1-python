import serial
import time
 
PORT = 'COM10'
BAUD = 460800
ser = serial.Serial(PORT, BAUD, timeout=1)
 
# 1. 啟動前先STOP
ser.write(bytes([0xA5, 0x25]))
time.sleep(0.05)
 
# 2. 發送啟動命令
ser.write(bytes([0xA5, 0x20]))
time.sleep(0.05)
 
# 3. 等待同步頭
def wait_sync(ser):
    sync = b''
    while True:
        b = ser.read(1)
        if not b:
            continue
        sync += b
        if len(sync) > 2:
            sync = sync[-2:]
        if sync == b'\xA5\x5A':
            print("同步頭已找到")
            return
 
wait_sync(ser)
desc = ser.read(7)
print("描述符:", desc.hex())
 
# 4. 進入資料解碼
def parse_point(data):
    if len(data) != 5:
        return None
    b = data
    quality = b[0] >> 2
    check_bit = (b[0] & 0x01)
    start_bit = (b[0] & 0x02) >> 1
    angle = ((b[1] >> 1) | (b[2] << 7)) / 64.0
    distance = ((b[3]) | (b[4] << 8)) / 4.0
    return angle, distance, quality, start_bit, check_bit
 
buffer = bytearray()
print("開始解碼資料點（Ctrl+C結束）")
try:
    while True:
        buffer += ser.read(512)
        while len(buffer) >= 5:
            point = parse_point(buffer[:5])
            buffer = buffer[5:]
            if point:
                angle, distance, quality, start_bit, check_bit = point
                if 0 <= angle <= 360 and distance > 0:
                    print(f"角度: {angle:.2f}°, 距離: {distance:.2f} mm, 品質: {quality}, start: {start_bit}")
except KeyboardInterrupt:
    print("結束")
finally:
    ser.close()