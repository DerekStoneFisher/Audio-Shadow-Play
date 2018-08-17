from tkinter import *

window = Tk()
window.title("Soundboard")
window.geometry("640x480")

buttonNames = ["dam", "whered you find this", "airhorn"]

for i in range(0, len(buttonNames)):
    button = Button(window, text=buttonNames[i])
    button.grid(column=i, row=0)

window.mainloop()