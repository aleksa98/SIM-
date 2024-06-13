def onetrigimage(expo, nimage, imgname):
    try:
        # if on Windows, use the provided setup script to add the DLLs folder to the PATH
        from windows_setup import configure_path
        configure_path()
    except ImportError:
        configure_path = None

    import os
    import tifffile
    from PIL import Image
    import serial

    from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
    from thorlabs_tsi_sdk.tl_mono_to_color_processor import MonoToColorProcessorSDK
    from thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE

    #arduino = serial.Serial(port='COM5', baudrate=9600, timeout=.1)

    NUMBER_OF_IMAGES = nimage  # Number of TIFF images to be saved

    OUTPUT_DIRECTORY = os.path.abspath(r'.')  # Directory the TIFFs will be saved to

    path_maincode = "C:/Users/user/Documents/Kamera/Scientific Camera Interfaces/SDK/Python Compact Scientific Camera Toolkit/examples"
    #OUTPUT_DIRECTORY =open(os.path.join(path_maincode, "PATH.txt"), "r").readline()
    #print(OUTPUT_DIRECTORY)

    #print(NUMBER_OF_IMAGES)

    TAG_BITDEPTH = 32768
    TAG_EXPOSURE = 32769

    path_image_folder=open(os.path.join(path_maincode, "PATH.txt"), "r").readline()
    external_count=open(os.path.join(path_image_folder, "counter.txt"), "r").readline()
    print(external_count)



    with TLCameraSDK() as sdk:
        cameras = sdk.discover_available_cameras()
        if len(cameras) == 0:
            print("Error: no cameras detected!")

        with sdk.open_camera(cameras[0]) as camera:

            #  setup the camera for continuous acquisition
            camera.frames_per_trigger_zero_for_unlimited = 1
            camera.image_poll_timeout_ms = 20000  # 2 second timeout

            camera.operation_mode = 1
            camera.trigger_polarity = 0

            camera.exposure_time_us = expo * 1000

            image_counted = 0

            #arduino.write(bytes('C'+expo, 'utf-8'))
            while image_counted < NUMBER_OF_IMAGES:

                camera.arm(2)

                # save these values to place in our custom TIFF tags later
                bit_depth = camera.bit_depth
                exposure = camera.exposure_time_us

                # need to save the image width and height for color processing
                image_width = camera.image_width_pixels
                image_height = camera.image_height_pixels

                frame = camera.get_pending_frame_or_null()
                if frame is None:
                    raise TimeoutError("Timeout was reached while polling for a frame, program will now exit")

                image_counted += 1

                FILENAME = f"{imgname}_{str(external_count).rjust(3, '0')}_{str(image_counted).rjust(2, '0')}_{str(expo)+'ms'}.tiff"

                # delete image if it exists
                if os.path.exists(OUTPUT_DIRECTORY + os.sep + FILENAME):
                    os.remove(OUTPUT_DIRECTORY + os.sep + FILENAME)

                image_data = frame.image_buffer

                image_data = frame.image_buffer
                pil_image = Image.fromarray(image_data)
                pil_image.save(FILENAME)


                camera.disarm()

    with open(os.path.join(path_image_folder, "counter.txt"), 'r+') as fp:
        fp.write(str(int(external_count) + 1).rjust(2, '0'))
        fp.close()

    #new_external_counter = int(external_count) + 1
    #print(str(new_external_counter).rjust(2, '0'))

    # ovaj kod snima onoliko slika koliko je zadato na pocetku

    # potrebno je promeniti mesto gde ce se snimiti slike kao i regulisati polozaj kodova zbog daljeg razvoja softvera
    # potrebno je snimljenim slikama dati odgovarajuce pozadinske informacije tipa ekpozicija i snimiti tiff file
