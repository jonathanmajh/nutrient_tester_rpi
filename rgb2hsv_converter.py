import colorsys
'''
convert given rgb to hsv opencv format
'''

def rgb_hsv_converter(rgb):
    (r,g,b) = rgb_normalizer(rgb)
    hsv = colorsys.rgb_to_hsv(r,g,b)
    (h,s,v) = hsv_normalizer(hsv)
    upper_band = [h+10, s+40, v+40]
    lower_band = [h-10, s-40, v-40]
    return {
        'upper_band': upper_band,
        'lower_band': lower_band
    }

def rgb_normalizer(rgb):
    (r,g,b) = rgb
    return (r/255, g/255, b/255)

def hsv_normalizer(hsv):
    (h,s,v) = hsv
    return (h*360, s*255, v*255)

rgb_hsv_converter((255, 165, 0))