from PIL import Image
import os

def img_resize(file_path):
    img = Image.open(file_path)  
    img_resize = img.resize((800,800))
    img_resize.save(file_path)









