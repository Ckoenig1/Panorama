If you want to run my code with other images you only need to run panorama_creator.py
it will handle running the other scripts so you dont have to run each one individually.
This code is only made to handle two pictures that have quite a bit of overlap so if
you give it two pictures that only share their edges it likely wont work without some 
slight modifications. Also PIL strips EXIF data causing orientation problems to avoid this
resave images before using them if necessary.
