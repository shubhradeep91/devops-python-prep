import os

folders = input("Enter list of folders with spaces: ").split()

for folder in folders:
    files = os.listdir(folder)
    print("The files in " + folder + " are: ")
    for file in files:
        print(file)