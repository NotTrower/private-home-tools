import sys
import random
from time import sleep
from datetime import datetime

if __name__ == '__main__':
    argc = len(sys.argv)
    if argc > 2:
        exit(1)
    if argc == 2:
        path = sys.argv[1]
    else:
        path = input("Enter the path to the txt file:\n")
    with open(path, 'r') as f:
        lines = f.readlines()
    mome = datetime.now()
    rng = random.Random()
    maxi = len(lines)
    rng.seed(int(mome.timestamp()))
    print(f"Pseudorandom numbers generated from seed {mome}")
    print(f"Number of lines read: {maxi}")
    print("Selection starts in ", end="")
    sleep(1)
    print("3, ", end="")
    sleep(1)
    print("2, ", end="")
    sleep(1)
    print("1...")
    sleep(1.70)
    rng.shuffle(lines)
    for i in range(maxi - 1, -1, -1):
        if i == 0:
            sleep(1)
            print("The chosen element on the list is...")
            sleep(3)
            print(f"{i+1} - {lines[i]}", end="")
            sleep(20)
        elif i < 3:
            sleep(0.75)
            print(f"{i+1} - {lines[i]}", end="")
        elif i < 5:
            sleep(0.625)
            print(f"{i+1} - {lines[i]}", end="")
        elif i < 10:
            sleep(0.5)
            print(f"{i+1} - {lines[i]}", end="")
        elif i < 20:
            sleep(0.25)
            print(f"{i+1} - {lines[i]}", end="")
        elif i < 100:
            sleep(0.1)
            print(f"{i+1} - {lines[i]}", end="")
        else:
            sleep(0.01)
            print(f"{i+1} - {lines[i]}", end="")