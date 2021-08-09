If you want to run my code with other images you only need to run panorama_creator.py
it will handle running the other scripts so you dont have to run each one individually.
This code is only made to handle two pictures that have quite a bit of overlap so if
you give it two pictures that only share their edges it likely wont work without some 
slight modifications. Also PIL strips EXIF data causing orientation problems to avoid this
resave images before using them if necessary.


![visualized_corners](visualized_corners.png)


![visualized_corners2](https://user-images.githubusercontent.com/65579262/128753626-9f7a4f9f-e8bd-4b30-98d1-e31ccc97a20b.png)
![paired_matches](https://user-images.githubusercontent.com/65579262/128753609-d58c10ad-61f6-4224-813c-89243406cac2.png)
![final_panorama](https://user-images.githubusercontent.com/65579262/128753611-9fdb409f-b433-4041-acc8-6ac80ab09311.png)
