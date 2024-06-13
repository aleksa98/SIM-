from tkinter import*
from datetime import*
import datetime as dt
import tkinter.messagebox as mb
import os





top_win = Tk() #deifinisanje glavnog (osnovnog) prozora
top_win.geometry("400x450") #podesavanje dimenzija naseg osnovnog prozora !!!! ima jos dugmica stavi velicinu 630x620 pa ce se svi dugmici videti
top_win.resizable(width=0, height=0)#fiksna velicina prozora
top_win.title("SIM BioPhysLab @ IPB")

common_image=PhotoImage(width=1, height=1)

path = "C:/Users/user/Documents/Rezultati/" # mesto na kom ce se pravti novi folderi
path_maincode="C:/Users/user/Documents/Kamera/Scientific Camera Interfaces/SDK/Python Compact Scientific Camera Toolkit/examples" #ovde ispisuje path u kom treba da cuvamo slike

frame= Frame(top_win, highlightbackground="black", highlightthickness=1).grid()

def clear_text():
   ent_name.delete(0, END)
   ent_sample.delete(0, END)
   ent_mail.delete(0, END)
   ent_comm.delete(0, END)
   ent_pass.delete(0, END)


def submit():
    name=ent_name.get()
    sample=ent_sample.get()
    password=ent_pass.get()

    if(len(password)!=0): #proverava password ako se ukuca parword mihailo on pocinje cuvanja fajlova u foldetu test....
        if(password=="mihailo" or password=="aleksa"):
            print(str(date.today().year).rjust(4, '0')+"-"+str(date.today().month).rjust(2, '0')+"-"+str(date.today().day).rjust(2, '0')+"-test")
            newpath=path+str(date.today().year).rjust(4, '0')+"-"+str(date.today().month).rjust(2, '0')+"-"+str(date.today().day).rjust(2, '0')+"-test"
            print(newpath)
            if not os.path.exists(newpath):
                os.makedirs(newpath)
                f = open(os.path.join(newpath,"counter.txt"), "w+")
                f.write("0")
                print("Napravljen")
            ent_pass.delete(0, END)
        else:
            ent_pass.delete(0, END)

    else:
        if (len(name) == 0 or len(sample) == 0):
            print("Add name or sample")
            mb.showinfo("Ops", "Add name or sample")
            return
        else:
            print(str(date.today().year).rjust(4, '0')+"-"+str(date.today().month).rjust(2, '0')+"-"+str(date.today().day).rjust(2, '0')+"-"+name+"-"+sample)
            #newpath = path + str(date.today().year)+"-"+str(date.today().month)+"-"+str(date.today().day)+"-"+name+"-"+sample
            newpath = path + str(date.today().year).rjust(4, '0')+"-"+str(date.today().month).rjust(2, '0')+"-"+str(date.today().day).rjust(2, '0')+"-"+name+"-"+sample
            print(newpath)

            if not os.path.exists(newpath):
                os.makedirs(newpath)
                f = open(os.path.join(newpath,"counter.txt"), "w+")
                f.write("0")
                print("Napravljen")

    f = open(os.path.join(path_maincode, "PATH.txt"), "w+") #pravi txty file u kom pise path gde se snima kod, ovaj file se nalazi u path_maincode
    f.write(newpath)
    f.close()
    top_win.destroy()
    import appSIM






lab_name=Label(frame, text="Name:")
lab_name.place(x=50, y=50)

ent_name=Entry(frame)
ent_name.place(x=120, y=50)

lab_mail=Label(frame, text="Mail:")
lab_mail.place(x=50, y=100)

ent_mail=Entry(frame)
ent_mail.place(x=120, y=100)

lab_sample=Label(frame, text="Sample:")
lab_sample.place(x=50, y=150)

ent_sample=Entry(frame)
ent_sample.place(x=120, y=150)

lab_comm=Label(frame, text="Comment:")
lab_comm.place(x=50, y=200)

ent_comm=Entry(frame)
ent_comm.place(x=120, y=200)

date = dt.datetime.now()
label = Label(frame, text=f"{date:%B %d, %Y}",font='Helvetica 10 bold')
label.place(x=270, y=20)


lab_pass=Label(frame, text="Password:")
lab_pass.place(x=250, y=380)

ent_pass=Entry(frame,show='*')
ent_pass.place(x=250, y=400)

record_but = Button(frame, text="Submit", relief="groove",
               command=submit)  # definisanje dugmeta

record_but.place(x=130, y=250)


clear_but = Button(frame, text="Clear", relief="groove",
               command=clear_text)  # definisanje dugmeta

clear_but.place(x=20, y=400)



top_win.mainloop() #beskonacna petlja da prozor bude aktivan uvek