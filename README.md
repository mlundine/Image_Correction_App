# Image_Correction_App
Corrects underwater images by bringing out reds and bringing down blues and greens <br />
**Underwater Photo Correction in Python (Windows)**

**Mark Lundine**

**Rationale:** Underwater photos become enriched in blues and greens while losing most of their red color.

![fishies](/read_me_images/fishies_original.JPG)

**Solution:** Shift the pixels around to heighten the reds and bring down the blues and greens. Make this automated instead of using expensive and time-intensive software like Photoshop.

![fishies corrected](/read_me_images/fishies_corrected.JPG)

**Credits:** The basis of this algorithm was adapted into Python from some Javascript code available at [https://github.com/nikolajbech/underwater-image-color-correction](https://github.com/nikolajbech/underwater-image-color-correction)

**How-To-Use (with GUI):**

Download this github repo to your computer and unzip it into your C-Drive, with the first folder named Image_Correction_App.

**Only Read this section if you are using a mac**

The repo here will work with Windows, but it can be made to work with Macs by first downloading ffmpeg from: 
https://ffmpeg.zeranoe.com/builds/

You would want the top version, macOS 64-bit, static.  Replace the ffmpeg folder residing in /Image_Correction_App with this folder.  Make sure it is unzipped and named ffmpeg, without all of the extra characters it puts in the name when downloaded.

You also need to build a static version of the main.py script.  To do so, open up terminal.

Type this command and then hit enter:

pip install pyinstaller

Wait for that to finish, then type this command, filling in the blank line with the directory you saved the github repo to:

cd _____/Image_Correction_App

The final command you must type is the following:

pyinstaller --noconsole --onefile main.py

This will make make a build and dist folder in the Image_Correction_App folder.  

The executable to run the GUI is in dist, named main.exe.  Double click it to run.

**How-To-Use Continued**

In the folder C:\Image_Correction_App\dist, there is an executable called "main.exe".  Double click it to run the GUI.

This will bring up the GUI.

![gui image](/read_me_images/gui_image.jpg)

There are four parameters that can be changed:

MIN\_AVG\_RED, MAX\_HUE\_SHIFT, BLUE\_MAGIC\_VALUE, SHARPEN

Base values:

MIN\_AVG\_RED = 60

MAX\_HUE\_SHIFT = 120

BLUE\_MAGIC\_VALUE = 1.2

SHARPEN = 1

Each option will save the result in a new folder called 'correction_results', which can be found in /Image_Correction_App/dist, the folder that main.exe resides in.

To select an image, you just hit &#39;Single Image&#39; and navigate to the image you want to run the algorithm on. When an image is selected, it will display in the GUI. Then you hit the &#39;Run&#39; button, and it will run the algorithm, save the image as a jpeg with &#39;cc&#39; at the end, and then display the result in the GUI.

To select a folder of images, hit &#39;Batch of Images&#39; and then navigate to the folder. This will display the filepaths of all of the images seen in the selected folder.  If there are more than 30 images, it will just say Working on: 'your/folder/name'. Hit &#39;Run&#39; and it will run the algorithm on every image in that folder. You will know it&#39;s done once the &#39;Run&#39; button is no longer highlighted.

To select a single video, hit &#39;Single Video&#39;, navigate to the video (only mp4s work), and then hit &#39;Run&#39;. This will take a long time, particularly for videos longer than a few minutes. This will display the file path to that video. It is finished once the &#39;Run&#39; button is no longer highlighted.

There are some sample images to play with in /Image_Correction_App/test_images.