
import random

userInput = input("Choose your word key (s/w/g): ").lower()
computer = random.choice([1, -1, 0])
yourDic = {"s" : 1, "w" : -1, "g" : 0}
reverseDic = {1 : "snake", -1 : "water", 0 : "gun"}

you =  yourDic[userInput]

print(f"Your choice is: {reverseDic[you]} \n Computer's choice is: {reverseDic[computer]}")

if you == computer:
    print("It's a tie!")
elif (you == 1 and computer == -1) or (you == -1 and computer == 0) or (you == 0 and computer == 1):
    print("You win!")
elif (you == -1 and computer == 1) or (you == 0 and computer == -1) or (you == 1 and computer == 0):
    print("Computer wins!")



