import _thread

threadState=0 #0:Idle, 1=Input Ready, 2=Processing, 3=Result Ready
threadIn=5
threadOut=0

def myThread():
    global threadState, threadIn, threadOut
    threadState = 2
    threadOut = 0
    for i in range(threadIn):
        print("in CORE 1. Loop", i)
        threadOut += i
    threadState = 3

def loopy(paramIn):
    result = 0
    for i in range(paramIn):
        print("in core ZERO. Loop", i)
        result += i
    return result

def main():
    global threadState, threadIn, threadOut
    print("main begin")
    
    threadIn=50
    _thread.start_new_thread(myThread,())
    
    r=loopy(5)
    print("main result=",r)
    
    while threadState!=3:
        pass
    print("Thread Out=",threadOut)
    
    print("main end")

