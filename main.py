from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np
import cv2
from collections import Counter
from skimage.color import rgb2lab, deltaE_cie76
import os

clustered_images = {}

def RGB2HEX(color):
    return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

def get_image(image_path):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


def get_colors(image, number_of_colors, show_chart):
    
    modified_image = cv2.resize(image, (200, 300), interpolation = cv2.INTER_AREA)
    modified_image = modified_image.reshape(modified_image.shape[0]*modified_image.shape[1], 3)
    
    clf = KMeans(n_clusters = number_of_colors)
    labels = clf.fit_predict(modified_image)
    
    counts = Counter(labels)
    
    center_colors = clf.cluster_centers_
    # We get ordered colors by iterating through the keys
    ordered_colors = [center_colors[i]/255 for i in counts.keys()]
    hex_colors = [RGB2HEX(ordered_colors[i]*255) for i in counts.keys()]
    rgb_colors = [ordered_colors[i]*255 for i in counts.keys()]
    
    if (show_chart):
        plt.figure(figsize = (8, 6))
        plt.pie(counts.values(), labels = hex_colors, colors = ordered_colors)
    
    return rgb_colors

def match_image_by_color(image, color, threshold = 60, number_of_colors = 5): 
    
    image_colors = get_colors(image, number_of_colors, False)
    selected_color = rgb2lab(np.uint8(np.asarray([[color]])))

    select_image = False
    # palette_counter = 0
    for i in range(number_of_colors):
        curr_color = rgb2lab(np.uint8(np.asarray([[image_colors[i]]])))
        diff = deltaE_cie76(selected_color, curr_color)
        if (diff < threshold):
            select_image = True
    return select_image

def show_selected_images(images, label, color, threshold, colors_to_match):
    index = 1
    for key in images:
        selected = match_image_by_color(images[key],
                                        color,
                                        threshold,
                                        colors_to_match)
        if selected:
            if label in clustered_images:
                clustered_images[label].append(key)
            else:
                clustered_images[label] = []
                clustered_images[label].append(key)

IMAGE_DIRECTORY = 'data/'
COLORS = {
    'GREEN': [0, 128, 0],
    'BLUE': [0, 0, 128],
    'YELLOW': [255, 255, 0],
    'RED': [255,0,0],
    'WHITE': [255,255,255]
}
images = {}

for file in os.listdir(IMAGE_DIRECTORY):
    if not file.startswith('.'):
        images[file] = get_image(os.path.join(IMAGE_DIRECTORY, file))



# Search for GREEN
for key in COLORS:
    show_selected_images(images, key, COLORS[key], 60, 5)
print(clustered_images)
