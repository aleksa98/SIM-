
from tkinter import*
import tkinter.messagebox as mb
import os #potrebno za pristup ekseternim aplikacijama
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
import serial
import time
from triggerhard import onetrigimage
from movefile import movefiles
from PIL import Image, ImageTk
from tifffile import tifffile
from skimage import io
import numpy as np
import os

arduino = serial.Serial(port='COM4', baudrate=9600, timeout=.1) #obratiti paznju na koji port je povezan arduino. Taj port mora da stoji ovde.

top_win = Tk() #deifinisanje glavnog (osnovnog) prozora
top_win.geometry("750x500") #podesavanje dimenzija naseg osnovnog prozora !!!! ima jos dugmica stavi velicinu 630x620 pa ce se svi dugmici videti
top_win.resizable(width=0, height=0)#fiksna velicina prozora
top_win.title("SIM BioPhysLab @ IPB")


path_maincode="C:/Users/user/Documents/Kamera/Scientific Camera Interfaces/SDK/Python Compact Scientific Camera Toolkit/examples"

common_image=PhotoImage(width=1, height=1)

frame= Frame(top_win, highlightbackground="black", highlightthickness=1).grid()

canvas = Canvas(frame,height=1000,width=1000, background=top_win["bg"]) #pravimo kanvas kako bi mogli da uokvirimo setove komands
canvas.grid()

canvas.create_rectangle(10, 10, 240, 150,outline="black",fill=top_win["bg"]) #laser
canvas.create_rectangle(250, 10, 480, 150,outline="red",fill=top_win["bg"], width=3) #ekspozicija
canvas.create_rectangle(490, 10, 740, 150,outline="black",fill=top_win["bg"]) #informacije o objektivima i laserima
canvas.create_rectangle(10, 160, 410, 280,outline="black",fill=top_win["bg"]) #motori
canvas.create_rectangle(10, 290, 410, 410,outline="black",fill=top_win["bg"]) #glavno snimanje
canvas.create_rectangle(10, 420, 410, 490,outline="black",fill=top_win["bg"]) #serijska komunikacija
canvas.create_rectangle(420, 230, 620, 490,outline="black",fill=top_win["bg"]) #komentar na sliku txt file



def clear_text(): #kada se pritisne dugme clear ciste se pojedini unosi
   ent_1.delete(0, END)
   ent_2.delete(0, END)
   ent_3.delete(0, END)
   ent_4.delete(0, END)
   ent_5.delete(0, END)
   ent_6.delete(0, END)
   text_1.delete(0., END)
   #imageinfo.delete(0., END)
   combo_angle.set('')
   combo_phase.set('')



def open_folder():
    print("Open folder")

def upload_file(): #otvaranje slika
    print("Open")

def close_something():
    print("Close")


def save_image():
    print("Save")
    name_ent = ent_5.get()
    print(name_ent)

def camera_live():
    print("Camera live Thorlabs")
    os.startfile("C:\Program Files\Thorlabs\Scientific Imaging\ThorCam\ThorCam.exe")

def image_control():
    print("Image control")
    expo_ent=ent_1.get() #vuce ekspopziciju
    print(expo_ent)
    if (len(expo_ent) ==0):
        print("Choose exposition!")
        mb.showinfo("Ops", "Choose exposition!")
        return #testira jel ovo radi jos jednom kad bude bilo vezivanje dugmica

    if (objective.get() == 0):
        print("Choose objective!")
        mb.showinfo("Ops", "Choose objective!")
        return

    x="C"+str(expo_ent).zfill(5) #pretvara unetu ekspoziciju u komadnu koju prepoznaje arduino C00033 (snimi kontrolnu sliku sa ekspozicijom 33ms)
    print(x)

    contents = open(os.path.join(path_maincode, "PATH.txt"), "r").readline() #povlaci path iz fajla PATH.txt koji se nalazi u folderu gde se nalazi i python code
    external_count = open(os.path.join(contents, "counter.txt"), "r").readline() #povlacni redni broj slike koja se trenutno snima iz faja counter.txt koji se nalazi u folderu gde se nalaze rezultati ovaj fajl se ne brise
    name_file = "control" + "_" + str(external_count).rjust(3, '0') #generise naziv txt fajla koji prati snimljenu sliku

    with open(os.path.join(contents, name_file + ".txt"), "w+") as f:
        if (objective.get() == 1): f.write("Objective: 10x / 0.25\nMore info: 11x (pixelsize  458.2 nm)\n")
        if (objective.get() == 2): f.write("Objective: 20x / 0.80\nMore info: 24.1x (pixelsize  209.1 nm)\n")
        if (objective.get() == 3): f.write("Objective: 100x/ 1.4\nMore info: 111.3x (pixel size  45.3 nm)\n")
        f.write("Exposition: " + str(expo_ent) + "ms\n") # u fajl koji prati snimljenu sliku unosi ekspoziciju
        f.write("Power: " + "A" + str(v1.get()) + "\n") # u fajl koji prati snimljenu sliku unosi snagu u obliku A79 na primer
        f.write("Comment: " + "\n")
        f.write(text_1.get("1.0", "end-1c")) #vuce komentar koji je unet iz prozora Comment:
        f.close()

    arduino.write(bytes(x, 'utf-8'))
    onetrigimage(int(expo_ent), 1, "img_control") #poziva skriptu da snimi jednu sliku sa zadatom ekspozicijom to je slika kontrola
    movefiles() #preme3sta snimljene slike u nas fajl koji smo napravili i u kom trenutno snimamao



def record():
    print("Record")

    expo_ent = ent_1.get() #vuce ekspopziciju
    print(expo_ent)
    if (len(expo_ent) ==0):
        print("Choose exposition!")
        mb.showinfo("Ops", "Choose exposition!")
        return #testira jel ovo radi jos jednom kad bude bilo vezivanje dugmica

    if (objective.get() == 0):
        print("Choose objective!")
        mb.showinfo("Ops", "Choose objective!")
        return

    if (len(combo_angle.get()) == 0): #vuce ugao
        print("Choose angle!")
        mb.showinfo("Ops", "Choose angle!")
        return  # testira jel ovo radi jos jednom kad bude bilo vezivanje dugmica

    if (len(combo_phase.get()) == 0): #vuce fazu
        print("Choose number of phase!")
        mb.showinfo("Ops", "Choose number of phase!")
        return  # testira jel ovo radi jos jednom kad bude bilo vezivanje dugmica
    else:
        n=int(combo_phase.get())
        print(n)

    if combo_angle.get()=="45\xb0":
        x="T"+str(expo_ent).zfill(5)+"2"+str(combo_phase.get())
        alfa=45
        print(45)
    if combo_angle.get()=="60\xb0":
        x = "T" + str(expo_ent).zfill(5) + "1" + str(combo_phase.get())
        alfa=60
        print(60)

    k=(180*n)/alfa
    print(int(k))

    contents = open(os.path.join(path_maincode, "PATH.txt"), "r").readline()
    external_count = open(os.path.join(contents, "counter.txt"), "r").readline()
    name_file = "img" + "_" + str(external_count).rjust(3, '0')

    with open(os.path.join(contents, name_file + ".txt"), "w+") as f:
        if (objective.get() == 1): f.write("Objective: 10x / 0.25\nMore info: 11x (pixelsize  458.2 nm)\n")
        if (objective.get() == 2): f.write("Objective: 20x / 0.80\nMore info: 24.1x (pixelsize  209.1 nm)\n")
        if (objective.get() == 3): f.write("Objective: 100x/ 1.4\nMore info: 111.3x (pixel size  45.3 nm)\n")
        f.write("Exposition: " + str(expo_ent) + "ms\n")
        f.write("Power: " + "A" + str(v1.get())+ "\n")
        f.write("Angle: " + str(alfa) + "\xb0\n")
        f.write("Phases: " + str(n) + "\n")
        f.write("Stack menu: angle - phase \n")
        f.write("Comment: " + "\n")
        f.write(text_1.get("1.0", "end-1c"))
        f.close()

    arduino.write(bytes(x, 'utf-8'))
    onetrigimage(int(expo_ent), int(k), "img")
    '''
    #kod u nastavku pravi stek od snimljenih slika kako ne bi slali n pojedinacnih slika vec stek

    listfiles = []

    for img_files in os.listdir(path_maincode):
        if img_files.endswith(".tiff"):
            listfiles.append(img_files)

    first_image = io.imread(path_maincode + '/'  +  listfiles[0])

    first_image.shape

    stack = np.zeros((len(listfiles), first_image.shape[0], first_image.shape[1]), np.uint16)


    io.imsave(path_maincode + '/' + listfiles[0][0:8] +str(expo_ent) +'ms_stack.tiff', stack, check_contrast=False)

    # kasnije se stek premesta u ciljani folder
    print(listfiles)

    for images in listfiles:
        os.remove(images)
    '''

    movefiles()

def noise_record():
    print("Noise record")
    expo_ent = ent_1.get()  # vuce ekspopziciju
    if (len(expo_ent) == 0):
        print("Choose exposition!")
        mb.showinfo("Ops", "Choose exposition!")
        return  # testira jel ovo radi jos jednom kad bude bilo vezivanje dugmica

    if (objective.get() == 0):
        print("Choose objective!")
        mb.showinfo("Ops", "Choose objective!")
        return

    x = "N" + str(expo_ent).zfill(5)
    contents = open(os.path.join(path_maincode, "PATH.txt"),
                    "r").readline()  # povlaci path iz fajla PATH.txt koji se nalazi u folderu gde se nalazi i python code
    external_count = open(os.path.join(contents, "counter.txt"),
                          "r").readline()  # povlacni redni broj slike koja se trenutno snima iz faja counter.txt koji se nalazi u folderu gde se nalaze rezultati ovaj fajl se ne brise
    name_file = "noise" + "_" + str(external_count).rjust(3,
                                                            '0')  # generise naziv txt fajla koji prati snimljenu sliku

    with open(os.path.join(contents, name_file + ".txt"), "w+") as f:
        if (objective.get() == 1): f.write("Objective: 10x / 0.25\nMore info: 11x (pixelsize  458.2 nm)\n")
        if (objective.get() == 2): f.write("Objective: 20x / 0.80\nMore info: 24.1x (pixelsize  209.1 nm)\n")
        if (objective.get() == 3): f.write("Objective: 100x/ 1.4\nMore info: 111.3x (pixel size  45.3 nm)\n")
        f.write("Exposition: " + str(expo_ent) + "ms\n")  # u fajl koji prati snimljenu sliku unosi ekspoziciju
        f.close()

    arduino.write(bytes(x, 'utf-8'))
    onetrigimage(int(expo_ent), 1,
                 "img_noise")  # poziva skriptu da snimi jednu sliku sa zadatom ekspozicijom to je slika kontrola
    movefiles()  # preme3sta snimljene slike u nas fajl koji smo napravili i u kom trenutno snimamao

def reconstruction():
    print("Reconstruction")

def motor_control():
    print("Motor")

    angle_ent = ent_3.get()
    print(angle_ent)
    linear_ent = ent_4.get()
    print(linear_ent)

    if (len(angle_ent) == 0 and len(linear_ent) == 0):
        print("Choose number of step or angle!")
        mb.showinfo("Ops", "Choose number of step or angle!")
        return  # testira jel ovo radi jos jednom kad bude bilo vezivanje dugmica

    status1=clockwise_check.get()
    status2=antiwise_check.get()

    if (status1==1 and status2==1):
        print("Choose one direction!")
        mb.showinfo("Ops", "Choose one direction!")
        return#testira jel ovo radi jos jednom kad bude bilo vezivanje dugmica
    if (status1==0 and status2==0):
        print("Choose direction!")
        mb.showinfo("Ops", "Choose direction!")
        return #testira jel ovo radi jos jednom kad bude bilo vezivanje dugmica
    if status1==1:
        print("Clockwise")
    if status2==1:
        print("Anti-clockwise")

    if (len(angle_ent) != 0 and len(linear_ent) != 0):
        mb.showinfo("Ops", "Choose one activity!")
        ent_3.delete(0, END)
        ent_4.delete(0, END)


    if (len(angle_ent) != 0):
        if(status1==1):
            x="R10"+str(angle_ent)
            #ent_3.delete(0, END)
            print(x)
        if(status2==1):
            x="R11"+str(angle_ent)
            #ent_3.delete(0, END)
            print(x)

    if (len(linear_ent) != 0):
        if(status1==1):
            x="R20"+str(linear_ent)
            #ent_4.delete(0, END)
            print(x)
        if(status2==1):
            x="R21"+str(linear_ent)
            #ent_4.delete(0, END)
            print(x)
    arduino.write(bytes(x, 'utf-8'))

def serial_send():
    ser_send=ent_2.get()
    x=ser_send
    print("Serial communication")
    print(x)
    arduino.write(bytes(x, 'utf-8'))

def generate_file():
    name_file=ent_6.get()
    text=text_1.get("1.0", "end-1c")
    print(name_file)
    print(text)
    ent_6.delete(0, END)
    text_1.delete("1.0",END)

    contents=open(os.path.join(path_maincode,"PATH.txt"), "r").readline()


    with open(os.path.join(contents, name_file+".txt"), "w+") as f:
        f.write(text)
        f.close()

def power_apply():
    power=v1.get()
    x="A"+str(power)
    print(x)
    arduino.write(bytes(x, 'utf-8'))


def image_info_text():
    if(objective.get() == 1):
        imageinfo.delete(1.0,"end")
        imageinfo.insert(1.0, "Field of view: 880um x 495um")
    if (objective.get() == 2):
        imageinfo.delete(1.0, "end")
        imageinfo.insert(1.0, "Field of view: 401um x 226um")
    if (objective.get() == 3):
        imageinfo.delete(1.0,END)
        imageinfo.insert(1.0, "Field of view: 87um x 49um")
    if (objective.get() == 4):
        imageinfo.delete(1.0,END)
        imageinfo.insert(1.0, "Add info about objective!")

def exit_function():
    # Put any cleanup here.
    x = "A0" #resetuje ad konvertor na nulu
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(2)#ceka malo da se izvrsi prva naredba pa iskljucuje diodu
    y = "L" #iskljucuje diodu ako je bila ukljucena
    arduino.write(bytes(y, 'utf-8'))
    print(x)
    print(y)
    top_win.destroy()


def lasertoggle():
    if toggle_button.config('text')[-1] == 'ON':
        toggle_button.config(text='OFF')
        x = "L"
        arduino.write(bytes(x, 'utf-8'))
        print(x)
        print("Laser on")

    else:
        toggle_button.config(text='ON')
        x = "H"
        arduino.write(bytes(x, 'utf-8'))
        print(x)
        print("Laser on")



clockwise_check=IntVar()
antiwise_check=IntVar()


chbutton_1=Checkbutton(frame, text="Clockwise", variable=clockwise_check)
chbutton_1.place(x=120, y=250)

chbutton_2=Checkbutton(frame, text="Anti-clockwise", variable=antiwise_check)
chbutton_2.place(x=220, y=250)



toggle_button = Button(frame, text="OFF", width=7,relief="groove", command=lasertoggle)
toggle_button.place(x=170, y=20)


open_folder_but = Button(frame, text="Open image", relief="groove",
               command = lambda:upload_file())  # definisanje dugmeta

open_folder_but.place(x=50, y=550)


close_but = Button(frame, text="Close", relief="groove",
               command=close_something)  # definisanje dugmeta

close_but.place(x=150, y=550)


camera_live_but = Button(frame, text="Live", relief="groove",width=15,
               command=camera_live)  # definisanje dugmeta

camera_live_but.place(x=270, y=100)


image_control_but = Button(frame, text="Control", relief="groove",
               command=image_control)  # definisanje dugmeta

image_control_but.place(x=420, y=47)


record_but = Button(frame, text="Record", relief="groove",
               command=record)  # definisanje dugmeta

record_but.place(x=50, y=310)


reconstruction_but = Button(frame, text="Reconstruction", relief="groove", state=DISABLED,
               command=reconstruction)  # definisanje dugmeta

reconstruction_but.place(x=450, y=550)


motor_but = Button(frame, text="Motor", relief="groove",
               command=motor_control)  # definisanje dugmeta

motor_but.place(x=50, y=200)


serial_but = Button(frame, text="Send", relief="groove",
               command=serial_send)  # definisanje dugmeta

serial_but.place(x=200, y=460)


save_but = Button(frame, text="Save", relief="groove",
               command=save_image)  # definisanje dugmeta

save_but.place(x=250, y=550)

noise_but = Button(frame, text="  Noise ", relief="groove",
               command=noise_record)  # definisanje dugmeta

noise_but.place(x=420, y=87)


objective = IntVar(value=0)# ovde definisemo objective i njihove karakteristike

r1 = Radiobutton(frame, text="10x / 0.25", variable=objective, value=1, command = image_info_text)
r1. config(height=1,width=10)
r1.place(x=500, y=40)

r2 = Radiobutton(frame, text="20x / 0.80", variable=objective, value=2, command = image_info_text)
r2. config(height=1,width=10)
r2.place(x=500, y=70)

r3 = Radiobutton(frame, text="100x / 1.4", variable=objective, value=3, command = image_info_text)
r3. config(height=1,width=10)
r3.place(x=500, y=100)

r4 = Radiobutton(frame, text="particular", variable=objective, value=4, command = image_info_text)
r4. config(height=1,width=10)
r4.place(x=500, y=125)

imageinfo= Text(frame, height = 6, width = 15,  bg = "light yellow")
imageinfo.place(x=600, y=40)


lab_1=Label(frame, text="Exposition:",font='Helvetica 10 bold')
lab_1.place(x=270, y=20)

ent_1=Entry(frame)
ent_1.place(x=270, y=50)

lab_2=Label(frame, text="Serial communication:")
lab_2.place(x=50, y=430)

ent_2=Entry(frame)
ent_2.place(x=50, y=460)

lab_3=Label(frame, text="Number of step 1")
lab_3.place(x=120, y=185)

ent_3=Entry(frame)
ent_3.place(x=120, y=210)

lab_4=Label(frame, text="Number of step 2")
lab_4.place(x=250, y=185)

ent_4=Entry(frame)
ent_4.place(x=250, y=210)


lab_5=Label(frame, text="Name of image")
lab_5.place(x=300, y=550)

ent_5=Entry(frame)
ent_5.place(x=300, y=580)

lab_6=Label(frame, text="Comment:")
lab_6.place(x=430, y=300)

text_1=Text(frame, height=10, width=20)
text_1.place(x=430, y=320)

lab_7=Label(frame, text="File name:")
lab_7.place(x=430, y=250)

ent_6=Entry(frame)
ent_6.place(x=430, y=270)




lab_power=Label(frame, text="Power (488 nm):")
lab_power.place(x=25, y=20)

lab_objective=Label(frame, text="Objective:")
lab_objective.place(x=500, y=20)


v1 = IntVar()
ent_7=Entry(frame, width=4,textvariable = v1)
ent_7.place(x=140, y=60)

scale_power = Scale(frame, variable = v1, from_ = 0, to = 230, orient = HORIZONTAL)
scale_power.place(x=25, y=40)

label_power = Label(frame, textvariable = v1)
label_power.place(x=125, y=20)


power_but = Button(frame, text="Apply", relief="groove",
               command=power_apply)  # definisanje dugmeta

power_but.place(x=185, y=57)


lab_angle=Label(frame, text="Select an angle:")
lab_angle.place(x=50, y=350)
combo_angle = ttk.Combobox(state="readonly",values=["45\xb0", "60\xb0"])
combo_angle.place(x=50, y=370)


lab_phase=Label(frame, text="Select number of phase:")
lab_phase.place(x=230, y=350)
combo_phase = ttk.Combobox(state="readonly", values=[1,3,6])
combo_phase.place(x=230, y=370)


clear_but = Button(frame, text="Clear", relief="groove",
               command=clear_text)  # definisanje dugmeta

clear_but.place(x=700, y=460)

comment_but = Button(frame, text="Ok", relief="groove",width=3,
               command=generate_file)  # definisanje dugmeta

comment_but.place(x=570, y=265)


top_win.protocol('WM_DELETE_WINDOW', exit_function)
top_win.mainloop() #beskonacna petlja da prozor bude aktivan uvek