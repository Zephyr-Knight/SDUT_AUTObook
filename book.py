from main import book_seat

seat_id = ''     # 座位ID
start_time = '-1'  # 开始时间（输入整点，-1表示立即预订）
end_time = '16'    # 结束时间(输入整点）

# 将预约时间转为分钟
if start_time != '-1':
    start_time = int(start_time) * 60
end_time = int(end_time) * 60
# 调用预约函数
book_seat(seat_id, str(start_time), str(end_time))