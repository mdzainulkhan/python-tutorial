# age = int(input("Enter your age: "))
# if (age >= 18) :
#     print("You are eligible to vote." , age , "is above 18.")

# else:
#     print("You are not eligible to vote." , age , "is under 18.")

# ageverification = int(input("Enter your age: "))


# if (ageverification >= 0 and ageverification <= 7):
#     print("You are a baby.")
# elif (ageverification >= 8 and ageverification <= 17):
#     print("You are a kid.")
# elif (ageverification >= 18 and ageverification <= 35):
#     print("You are an adult.")
# elif (ageverification >= 36 and ageverification <= 59):
#     print("You are a middle-aged adult.")
# else:
#     print("You are a senior citizen.")


# enter_number = int(input("Enter a number: "))
# if (enter_number % 2 == 0):
#     print("The number is even.")
# else:
#     print("The number is odd.")

# num1 = int(input("Enter first number: "))
# num2 = int(input("Enter second number: "))
# num3 = int(input("Enter third number: "))
# num4 = int(input("Enter fourth number: "))

# if (num1 > num2 and num1 > num3 and num1 > num4):
#     print("The first number is the greatest.")
# elif (num2 > num1 and num2 > num3 and num2 > num4
# ):
#     print("The second number is the greatest.")
# elif (num3 > num1 and num3 > num2 and num3 > num4):
#     print("The third number is the greatest.")
# else:
#     print("The fourth number is the greatest.")

mark1 = int(input("Enter your marks: "))
mark2 = int(input("Enter your marks: "))
mark3 = int(input("Enter your marks: "))

percentage = (mark1 + mark2 + mark3) / 300 * 100

if mark1 < 33 or mark2 < 33 or mark3 < 33:
    print(f"You have failed the exam. {percentage:.2f}%")
elif percentage >= 90:
    print(f"You have passed the exam with A grade. {percentage:.2f}%")
elif percentage >= 80:
    print(f"You have passed the exam with B grade. {percentage:.2f}%")
elif percentage >= 50:
    print(f"You have passed the exam with C grade. {percentage:.2f}%")
else:
    print(f"You have passed the exam with D grade. {percentage:.2f}%")