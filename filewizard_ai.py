#from Image_search.image_classifier import classify_image

# Try to import image classifier, but skip if unavailable
try:
    from image_classifier import classify_image
except ImportError:
    classify_image = None

def sort_and_tag_file(local_path):
    return classify_image(local_path)
