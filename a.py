import _thread

result = 0

def add(a,b):
    return a+b

def myThread(a,b):
    global result
    result = add(a,b)
    _thread.exit()

def main():
    print("Main Starts")
    
    
    for st in range(0,6):
        aa,bb= st,st+1
        th = _thread.start_new_thread(myThread,(aa,bb))
        
        a,b=6+st,6+st+1
        c = add(a,b)

        while result==0:
            pass
        
        print("T", aa,bb,result)
     
        print("M", a,b,c)
        
    print("Main Ends")
    