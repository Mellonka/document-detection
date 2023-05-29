import cv2


def draw_text(img, text,
              font=cv2.FONT_HERSHEY_PLAIN,
              pos=(0, 0),
              font_scale=2,
              font_thickness=2,
              text_color=(255, 255, 255),
              text_color_bg=(0, 0, 255)
              ):
    x, y = pos
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    text_h += 10
    cv2.rectangle(img, pos, (x + text_w, y + text_h - 5), text_color_bg, -1)
    cv2.putText(img, text, (x, y + text_h + font_scale - 1 - 5), font, font_scale, text_color, font_thickness)

    return text_size
