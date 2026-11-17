"""gender="F"
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
    
n=5
for row in range(1,n-1):
for col in range(1,row-1):
print("*",end="")
print()"""
#_________________________________________
#17/11/26
fruits = ["apple","mango","orange"]
fruits.insert(1,"banana")
fruits[2]="Pineapple"
fruits.remove("apple")
print(fruits)
print(fruits[-1])

fruits = ("apple","mango","orange")
print(fruits)

contact=("hemashree",20,"student")
name,age,designation = contact
print(name)
print(designation)

fruits = {"apple","mango","orange"}
fruits.add("orange")
print(fruits)
fruits.discard("apple")
print(fruits)

student= {
    "name" : "Hemashree",
    "dept":"CSE",
    "age": 25,
    "marks":85
}
print(student)
print(student["name"])
print(student["age"])
student["city"]="Banglore"
student["marks"]=90
print(student)
student.pop("age")
print(student)

for key,value in student.items():
    print(key,":",value)
    
print(student.keys())
print(student.values())

num=[1,2,3,4,5,6]
print(num[1:4])
print(num[::-1])
print(num[::2])

def welc():
    print("Hello!!")
welc()

def welc(message="guest"):
    print("Hello",message)
welc("Hemashree")
welc()

def add(a,b):
    return a+b
print(add(9,8))


def calc(a,b):
    return a+b,a*b
tot,pro=calc(12,34)
print(tot,"\n",pro)