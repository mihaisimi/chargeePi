## Prepare Raspberry Pi
1. Create + rw for ```images_cars``` folder and a ```upload_image_code``` folder on the Raspberry Pi.
2. Add + make executable the ```camera_feed.py``` file into the ```upload_image_code```
3. Install s3cmd on the Raspberry Pi: ```sudo apt-get install s3cmd```
4. Run the upload every 5 seconds ```$ nohup ./every-5-seconds.sh &```

Recognition steps:
1. Identification of color
2. Cropping and identification for licence plate numbers
3. Recognize the licence place and extract the number
