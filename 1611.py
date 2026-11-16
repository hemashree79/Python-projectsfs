gender="F"
if gender == "M":
    print("HI sir")
elif gender == "F":
    print("Hi ma'am")
else:
    print("Hi")
    
    
for i in range (6):
    for j in range (i):
        print("*",end=" ")
    print()
    
"""n=5
for row in range(1,n-1):
for col in range(1,row-1):
print("*",end="")
print()"""
n=5
for row in range(1,n+1):
    for col in range(1,row+1):
        print("*",end=" ")
    print()
#_____________________________________________________
"""
min=0
max=100
g=(max+1)//2
print("Guess a number between 1 to 100")
for i in range (max):
    inp=input(f"Is your number  {g} (1.yes  2.greater than {g} 3.lesser than {g})")
    if(inp == 'greater'):
         min=g
         g=(min+max)//2
         print(g)
    elif(inp == 'lesser'):
         max=g
         g=(max+min)//2
    elif(inp == "yes"):
        print(f"I have guessed your number {g} in {i} number of steps")
        break;
    else:
        print("Enter a valid response")
"""
#_______________________________________________________
import random
ent=input("Rock Paper or Scissor")
comp=random.choice(("rock","paper","scissor"))
if((comp == "rock" and ent == "scissor"),(comp == "paper" and ent=="rock"),(comp =="scissor" and ent=="paper")):
    print("Computer wins you loose!!")
elif((ent == "rock" and comp == "scissor"),(ent == "paper" and comp =="rock"),(ent =="scissor" and comp =="paper")):
    print("You win !!! computer lost")
    