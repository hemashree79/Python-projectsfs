import math
class rectangle:
    def __init__(self,breadth,height):
     self.breadth=breadth
     self.height=height
    def area(self):
        return self.breadth*self.height 
    def perimeter(self):
        return 2*(self.breadth+self.height)
class circle:
    def __init__(self,radius):
        self.radius=radius
    def area(self):
      
        return math.pi*self.radius*self.radius      
    def perimeter(self):
        return (2*math.pi*r)
class triangle:
    def __init__(self,base,height):
        self.base=base
        self.height=height
    def area(self):
        return 1//2*self.base*self.height
    def perimeter(self):
        return (self.breadth+self.height+self.btreadth)
class square:
    def __init__(self,side):
        self.side=side
    def area(self):
        return self.side*self.side
    def perimeter(self):
        return 4*(self.side)
while True:
    sh=int(input("Select a shape to find area and perimeter for: \n 1.rectangle \n 2.circle \n 3.triangle \n  4.square"))
    if (sh == 1):
        c=int(input("What do you want to find \n1.Area\n2.Perimeter"))
        if(c==1):
            b=int(input("Enter breadth of rectangle : "))
            h=int(input("Enter height of rectangle : "))
            r1=rectangle(b,h)
            print(f"Area of rectangle is :")
            print(r1.area())
        elif(c==2):
            b=int(input("Enter breadth of rectangle : "))
            h=int(input("Enter height of rectangle : "))
            r1=rectangle(b,h)
            print(f"Perimeter of rectangle is {r1.perimeter()}")
    elif(sh==2):
        c=int(input("What do you want to find \n1.Area\n2.Perimeter"))
        if(c==1):
            r=int(input("Enter the radius of circle"))
            c1=circle(r)
            print(f"Area of circle is : {c1.area()}")
        elif(c==2):
            r=int(input("Enter the radius of circle"))
            c1=circle(r)
            print(f"Perimeter of circle is : {c1.perimeter()}")
    elif(sh ==3):
        c=int(input("What do you want to find \n1.Area\n2.Perimeter"))
        if (c==1):
            b=int(input("Enter base of triangle : "))
            h=int(input("Enter height of triangle : "))
            t1=triangle(b,h)
            print(f"Area of triangle is {t1.area()}")
        elif(c==2):
            b=int(input("Enter base of triangle : "))
            h=int(input("Enter height of triangle : "))
            t1=triangle(b,h)
            print(f"preimeter of triangle is {t1.perimeter()}")
    elif(sh ==4):
        c=int(input("What do you want to find \n1.Area\n2.Perimeter"))
        if(c==1):
            s=int(input("Enter side of square : "))
            s1=square(s)
            print(f"The area of square is {s1.area()}")
        elif(c==2):
            s=int(input("Enter side of square : "))
            s1=square(s)
            print(f"The perimeter of square is {s1.perimeter()}")
            