import time
'''
# 用法：
timer = FunctionTimer()

key = 'wait_me'

@timer._timer(key=key)
def wait_me(count):
    time.sleep(count)

wait_me(3)
print(timer.time_count[key])

输出：
3.00150203704834
'''
class FunctionTimer():
    def __init__(self) -> None:
        self.time_count = {}

    def _timer(self, key=0):
        def _timer_decorator(func):
            if key not in self.time_count:
                self.time_count[key] = 0
            def func_in(*s,**gs):
                start_time = time.time()
                _res_ = func(*s,**gs)
                end_time = time.time()
                self.time_count[key] += end_time - start_time
                return  _res_
            return  func_in
        return _timer_decorator

my_function_timer = FunctionTimer()