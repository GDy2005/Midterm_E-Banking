import redis

def get_redis_connection():
    return redis.StrictRedis(
    host='127.0.0.1',
    port=6379,
    db=0,               # database index (0-15)
    decode_responses=True  # chuyển byte → string tự động
)


# Kiểm tra kết nối
# try:
#     response = r.ping()
#     print("Connected to Redis:", response)
# except redis.ConnectionError:
#     print("Redis connection failed!")
