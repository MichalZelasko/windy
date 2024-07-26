from cloud_history import isolate_cloud_history
from clusters.configuration import *
from utils.converter import convert_raw_images
from screenshoter import get_print_screens

def main():
    get_print_screens(url, \
                      url_map, \
                      do_screenshot=do_screenshot, \
                      delay_1=delay_1, \
                      delay_2=delay_2, \
                      screenshot_number=screenshot_number, \
                      screenshot_time=screenshot_time, \
                      resource=resource)
    convert_raw_images(do_convert = do_convert, rescource=resource, path=path)
    isolate_cloud_history(option_clust=option_clust, option_pos=option_pos, option=option, k=k, func=func, x_a = x_a, x_b = x_b, y_a = y_a, y_b = y_b)

if __name__ == "__main__":
    main()