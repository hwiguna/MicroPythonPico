# Magic Colors
import random

colors = {"   Red":16, " Green":2, "  Blue":8, "Black":32, "Yellow":1, " Pink":4}

def main():
    
    for v in colors.keys():
        print(v, end=':\t\n')
        
        numbers = []
        for i in range(1,51):
            if i & colors[v]:
                numbers.append(i)

        if True:
            # Scramble
            n = len(numbers)
            for i in range(n):
                r = random.randrange(n)
                t = numbers[i]
                numbers[i] = numbers[r]
                numbers[r]=t
        
        c=0
        for i in numbers:
            print(i, end='\t')
            c+=1
            if c % 5 == 0:
                print()
            
        print()
        print()



def magic():
    number = 0
    for v in colors.keys():
        print("Is it on the", v, "card? (y/n) ", end='')
        answer=input()
        if answer.upper() == "Y":
            number += colors[v]
    print("You picked",number)

