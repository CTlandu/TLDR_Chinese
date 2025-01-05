# 工作进程数
workers = 4

# 每个工作进程的线程数
threads = 2

# 监听地址和端口
bind = '0.0.0.0:5000'

# 超时设置（秒）
timeout = 120

# 工作模式
worker_class = 'sync'

# 日志级别
loglevel = 'info'

# 是否后台运行
daemon = False

# 重载
reload = True

# 进程名称
proc_name = 'tldr-chinese' 