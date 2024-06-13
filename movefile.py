
def movefiles():
    import os
    import shutil

    path_maincode=r"C:/Users/user/Documents/Kamera/Scientific Camera Interfaces/SDK/Python Compact Scientific Camera Toolkit/examples"
    contents=open(os.path.join(path_maincode,"PATH.txt"), "r").readline()


    images = [f for f in os.listdir(path_maincode) if '.tiff' in f.lower()]
    for image in images:
        print(image)
        print(contents)
        new_path = contents+"/" + image
        shutil.move(image, new_path)




