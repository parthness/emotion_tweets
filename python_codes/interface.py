from tkinter import *
from project import runSingleTweet
root = Tk()
root.geometry("600x400+100+100") 
text=StringVar()
def analyze(written):
    tweet=text.get()
    runSingleTweet(tweet)
    #print(tweet)

label_1 = Label(root, text="Your Text")
entry_1 = Entry(root,textvariable=text)

# widgets centered by default, sticky option to change
label_1.grid(row=0, sticky=E)
entry_1.grid(row=0, column=1)

button_1 = Button(root, text="Analyze",command=analyze)
# <Button-1> is an event that means "clicked left mouse button"
button_1.bind("<Button-1>", analyze)
button_1.grid(row=2,column=1)

root.mainloop()