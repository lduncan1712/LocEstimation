
from detection_step import detection_step

if __name__ == "__main__":
    
    ######detection_step()

    import cv2,os
    from PIL import Image
    import numpy as np

    # Get all image files from the folder
    image_files = [f for f in os.listdir("NEW_IMAGES") if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    #image_files.sort()  # Ensure the files are in the correct order

    image_files = sorted(image_files, key=lambda x: int(x[19:-4]))
    
    # Define the video codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4
    video_writer = cv2.VideoWriter("shortened_output.MP4", fourcc, 5, (1600,1240))

    count = 0
    
    for image_file in image_files:
        count += 1

        if image_file == "sample_det_photoNEW708.jpg":
            break

        if count % 7 != 0:
            continue


        print(image_file)
        image_path = os.path.join("NEW_IMAGES", image_file)
        
        # Open the image using PIL
        img = Image.open(image_path)
        
        # Resize or pad the image to the target size
        img = img.convert("RGB")  # Ensure 3 channels
        img = img.resize((1600,1240), Image.Resampling.LANCZOS)  # Resize the image to target size
        
        # Convert the image to a NumPy array (compatible with OpenCV)
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Write the frame to the video
        video_writer.write(frame)
    
    # Release the video writer
    video_writer.release()






    # import cv2
    # import os

    # # Directory containing PNG images
    # image_folder = 'images_folder'
    # output_video = 'output_video.mp4'

    # # Get list of image files in the directory and sort them
    # images = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
    # images.sort()  # Ensure the images are in order

    # # Read the first image to determine the frame size
    # first_image_path = os.path.join(image_folder, images[0])
    # frame = cv2.imread(first_image_path)
    # height, width, layers = frame.shape

    # # Define the codec and create VideoWriter object
    # fps = 30  # Frames per second
    # fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 format
    # video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    # # Write each image to the video
    # for image in images:
    #     img_path = os.path.join(image_folder, image)
    #     frame = cv2.imread(img_path)
    #     video.write(frame)

    # # Release the VideoWriter
    # video.release()