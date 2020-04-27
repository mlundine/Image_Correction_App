# Image_Correction_App
Corrects underwater images by bringing out reds and bringing down blues and greens
**Underwater Photo Correction in Python (Windows)**

**Mark Lundine**

**Rationale:** Underwater photos become enriched in blues and greens while losing most of their red color.

**Solution:** Shift the pixels around to heighten the reds and bring down the blues and greens. Make this automated instead of using expensive and time-intensive software like Photoshop.

**Credits:** The basis of this algorithm was adapted into Python from some Javascript code available at [https://github.com/nikolajbech/underwater-image-color-correction](https://github.com/nikolajbech/underwater-image-color-correction)

**How-To-Use (with GUI):**

1. Download Anaconda and Spyder from [https://www.anaconda.com/distribution/#download-section](https://www.anaconda.com/distribution/#download-section) Make sure you choose Python 3.x.

2. Download this github repository, and then unzip it to a location of your choice on your machine.

Make sure the name of the downloaded folder is &quot;Image\_Correction\_App&quot;

2. Open up Anaconda Prompt and type the following commands to make a new virtual environment and to download necessary libraries:

conda create –n underwaterImage python = 3.5

activate underwaterImage

pip install sk-video

pip install pillow

pip install pyqt5

3. Go to the &#39;Image\_Correction\_App&#39; directory, basically just use the cd command and then type the file path to where you placed the Image\_Correction\_App folder.

cd C:\yourname\image\_correction\_app

4. In this directory, type in the terminal:

idle

This will bring up a Python console. Go to File  Open and then open up &#39;main.py&#39;.

5. This will open up the GUI python script. To run, go to Run  Run Module

This will bring up the GUI.

![gui image](read_me_images\gui_image.jpg)

There are four parameters that can be changed:

MIN\_AVG\_RED, MAX\_HUE\_SHIFT, BLUE\_MAGIC\_VALUE, SHARPEN

Base values:

MIN\_AVG\_RED = 60

MAX\_HUE\_SHIFT = 120

BLUE\_MAGIC\_VALUE = 1.2

SHARPEN = 2

Right now, to change the parameters, you have to change them before you select an image/folder/video.

To select an image, you just hit &#39;Single Image&#39; and navigate to the image you want to run the algorithm on. When an image is selected, it will display in the GUI. Then you hit the &#39;Run&#39; button, and it will run the algorithm, save the image as a jpeg with &#39;cc&#39; at the end, and then display the result in the GUI.

To select a folder of images, hit &#39;Batch of Images&#39; and then navigate to the folder. Hit &#39;Run&#39; and it will run the algorithm on every image in that folder. This function does not display anything to the GUI. You will know it&#39;s done once the &#39;Run&#39; button is no longer highlighted.

To select a single video, hit &#39;Single Video&#39;, navigate to the video (only mp4s work), and then hit &#39;Run&#39;. This will take a long time, particularly for videos longer than a few minutes. This option does not display anything. It is finished once the &#39;Run&#39; button is no longer highlighted.
