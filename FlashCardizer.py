from pdf2image import convert_from_bytes, convert_from_path
from tkinter import *
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw
from PIL import ImageFilter
from functools import partial
import argparse
import os

import io
import ctypes

from concurrent import futures

os.chdir(os.path.dirname(os.path.abspath(sys.executable)))
try:
    with open("language_preferences.bin", "rb") as inputfile:
        language_length = int.from_bytes(inputfile.read(4), byteorder='big')
        current_language = inputfile.read(language_length).decode('utf-8')
except FileNotFoundError:
    current_language = "english"

user32 = ctypes.windll.user32
width_screen, height_screen = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
border_width, border_height = 200, 300
min_span_algorithm = 5
average_span_algorithm = 10
rating_factor_algorithm = 1
background_color = "gray8"
buttons_color = "gray25"
dark_rating_color = [background_color, "#2d0000", "#2d1d00", "#2c2d00", "#002d03", "#02002d"]
rating_color = ["SystemButtonFace", "red2", "DarkOrange1", "yellow", "green2", "medium blue"]
selected_rectangle = None

menu_bar_text_english = ["Import File", "Load Cards", "Save Cards", "Exit", "File", "Shortcuts", "English", "French", "Language", "About", "Info"]
menu_bar_text_french = ["Importer un PDF", "Charger des cartes", "Sauvegarder mes cartes", "Quitter", "Fichier", "Raccourcis", "Anglais", "Français", "Langues", "À propos", "Info"]
menu_bar_text = {"english": menu_bar_text_english, "french": menu_bar_text_french}

main_screen_text_english = ["Welcome to\nFlash Cardizer!", "Import New PDF ", "Load Existing Cards "]
main_screen_text_french = ["Bienvenue sur\nFlash Cardizer!", "Importer un PDF ", "Charger des cartes "]
main_screen_text = {"english": main_screen_text_english, "french": main_screen_text_french}

loading_screen_text_english = ["Converting PDF", "This might take a while..."]
loading_screen_text_french = ["Conversion du PDF", "Cette opération pourrait prendre quelques minutes..."]
loading_screen_text = {"english": loading_screen_text_english, "french": loading_screen_text_french}

edit_screen_text_english = ["Study!    ", "Current Card: ", "Previous Card", "  Next Card  ", "Blur\nSelection ", "Blur\nCard ", "Color\nSelection ", "Color\nCard ", "Clear \nSelection ", "Clear   \nCard   ", "Link Previous ", "Unlink Previous ", "Delete Card", "Enter Card  \nTitle Here  ", "Enter Card  \nNotes Here  ", "Blur\nLevel", "<No Title For This Card Yet>", "<No Notes For This Card Yet>"]
edit_screen_text_french = ["Étudier!   ", "Carte en cours: ", "  Précédent", "Suivant  ", "Sélection \nfloue", "Carte\nfloue ", "Sélection \nnoircie", "Carte\nnoircie ", "Sélection  \nrétablie  ", "Carte  \nrétablie  ", "Lier au\nprécédent  ", "Delier le\nprécédent  ", "Supprimer  \nla carte", "Titre de\n la carte", "Notes de\n la carte", "Niveau\nde flou", "<Pas de titre donné à cette carte>", "<Pas de notes données à cette carte>"]
edit_screen_text = {"english": edit_screen_text_english, "french": edit_screen_text_french}

study_screen_text_english = ["Edit!    ", "Current Card: ", "Previous Card", "  Next Card  ", "Card Rating: ", "Reset Ratings ", "Completion"]
study_screen_text_french = ["Éditer!    ", "Carte en cours: ", "  Précédent", "Suivant  ", "Cote de la carte: ", "Réinitialiser \nles cotes", "Maîtrise"]
study_screen_text = {"english": study_screen_text_english, "french": study_screen_text_french}

shortcuts_text_english = ["Shortcuts",
                          "Switch Edit/Study Mode\nFlip Card\nPrevious Card\nNext Card\n\nBlur Selection\nBlur Card\nColor Selection\nColor Card\nClear Selection\nClear Card\nLink/Unlink Previous\nDelete Card\n\nSet Card Rating to 1\nSet Card Rating to 2\nSet Card Rating to 3\nSet Card Rating to 4\nSet Card Rating to 5\nReset Ratings",
                          "#\nSPACEBAR\nLEFT ARROW\nRIGHT ARROW\n\nB\nSHIFT+B\nC\nSHIFT+C\nX\nSHIFT+X\nSHIFT+L\nDELETE\n\n1\n2\n3\n4\n5\nDELETE"]
shortcuts_text_french = ["Raccourcis",
                          "Changer mode édition/étude\nRetourner la carte\nCarte précédente\nCarte suivante\n\nBrouiller la sélection\nBrouiller la carte\nNoircir la sélection\nNoircir la carte\nRétablir la sélection\nRétablir la carte\nSupprimer la carte\nVérouiller/dévérouiller\nla carte précédente\n\nFixer la cote à 1\nFixer la cote à 2\nFixer la cote à 3\nFixer la cote à 4\nFixer la cote à 5\nRéinitialiser les cotes",
                          "#\nBARRE D'ESPACE\nFLÈCHE GAUCHE\nFLÈCHE DROITE\n\nB\nSHIFT+B\nC\nSHIFT+C\nX\nSHIFT+X\nSUPPR.\nSHIFT+L\n\n1\n2\n3\n4\n5\nSUPPR."]
shortcuts_text = {"english": shortcuts_text_english, "french": shortcuts_text_french}

about_text_english = ["About", "Flash Cardizer Version 1.0", "Copyright © 2020 Charles-Eric Noel Laflamme\n", "Any bug reports, improvement suggestions, compliments or insults\ncan be directed at charles.eric.noel.laflamme@gmail.com"]
about_text_french = ["À propos", "Flash Cardizer Version 1.0", "Tous droits réservés © 2020 Charles-Éric Noël Laflamme\n", "Tous rapport de bogues, suggestions, compliments ou insultes\npeuvent être adressés au charles.eric.noel.laflamme@gmail.com"]
about_text = {"english": about_text_english, "french": about_text_french}

warning_text_english = ['Delete Card', 'Are you sure you want to delete this card?', 'Reset Ratings', 'Are you sure you want to reset all the card ratings?']
warning_text_french = ['Supprimer la carte', 'Êtes vous sûr de vouloir supprimer cette carte?', 'Réinitialiser les cotes', 'Êtes vous sûr de vouloir réinitialiser les cotes?']
warning_text = {"english": warning_text_english, "french": warning_text_french}

img_text_english = ["media/PageCornerFront.png", "media/PageCornerBack.png"]
img_text_french = ["media/PageCornerFrontFr.png", "media/PageCornerBackFr.png"]
img_text = {"english": img_text_english, "french": img_text_french}

from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)


def slide2card_dimensions(width_slide, height_slide):
    if (width_screen-border_width)/width_slide < (height_screen-border_height)/height_slide:
        return width_screen - border_width, int(((width_screen - border_width) / width_slide) * height_slide)
    else:
        return int(((height_screen - border_height) / height_slide) * width_slide), height_screen - border_height


# Convert pdf2image format to my objects
def createCardList(pdf2image_list):
    return [Card(card_back_image=card_PIL_image, card_number=card_number, score=card_number) for card_number, card_PIL_image in enumerate(pdf2image_list)]


class RectangleOperation:
    def __init__(self, left_corner, upper_corner, right_corner, lower_corner, operation_type, blur_radius=0, blur_card=False):
        self.left_corner = left_corner
        self.upper_corner = upper_corner
        self.right_corner = right_corner
        self.lower_corner = lower_corner
        self.operation_type = operation_type
        self.status = True
        self.blur_card = blur_card
        self.blur_radius = blur_radius

    def get_rectangle_coords(self):
        return self.left_corner, self.upper_corner, self.right_corner, self.lower_corner

    def check_if_in(self, x, y):
        left_corner_screen, upper_corner_screen, right_corner_screen, lower_corner_screen = slide2card_rect_coords(width_card, height_card, self.left_corner, self.upper_corner, self.right_corner, self.lower_corner)
        return ((x>left_corner_screen and x<right_corner_screen) and (y>upper_corner_screen and y<lower_corner_screen))


def card2slide_rect_coords(width_card, height_card, left_pixel, upper_pixel, right_pixel, lower_pixel):
    if width_card == width_screen - border_width:
        ratio = height_card/height_slide
    else:
        ratio = width_card / width_slide
    return int(left_pixel/ratio),  int(upper_pixel/ratio), int(right_pixel/ratio),  int(lower_pixel/ratio)


def slide2card_rect_coords(width_card, height_card, left_pixel, upper_pixel, right_pixel, lower_pixel):
    if width_card == width_screen - border_width:
        ratio = height_card/height_slide
    else:
        ratio = width_card / width_slide
    return int(left_pixel*ratio),  int(upper_pixel*ratio), int(right_pixel*ratio),  int(lower_pixel*ratio)


# Card Class
class Card:
    def __init__(self, card_back_image, card_front_image=None, card_number=0, current_side=True, rating=0, score=0, title="", notes="", linked_to_previous=False, linked_to_next=False):
        self.card_back_image = card_back_image
        if card_front_image is None:
            self.card_front_image = self.card_back_image.copy()
        else:
            self.card_front_image = card_front_image
        self.card_number = card_number
        self.current_side = current_side  # Always starts on the front side
        self.rating = rating
        self.score = score
        self.title = title
        self.notes = notes
        self.rectangle_operations = []
        self.linked_to_previous = linked_to_previous
        self.linked_to_next = linked_to_next
        self.draw = ImageDraw.Draw(self.card_front_image)

    def set_rectangle_operation(self, rectangle_operations):
        self.rectangle_operations = rectangle_operations

    def set_title(self, title):
        self.title = title

    def set_notes(self, notes):
        self.notes = notes

    def set_rating(self, rating):
        self.rating = rating

    def set_new_score(self, new_rating):
        self.score = self.score + min_span_algorithm + average_span_algorithm * max(0, (new_rating-self.rating)) + new_rating**2*rating_factor_algorithm

    def flip_card(self):
        self.current_side = not self.current_side

    def set_front_card(self):
        self.current_side = True

    def set_back_card(self):
        self.current_side = False

    def get_card(self):
        if self.current_side:
            return self.card_front_image
        else:
            return self.card_back_image

    def blur_selection(self):
        # Convert coords
        left_corner, upper_corner, right_corner, lower_corner = card2slide_rect_coords(width_card, height_card, rectangle_left_coord, rectangle_upper_coord, rectangle_right_coord, rectangle_lower_coord)
        self.rectangle_operations.append(RectangleOperation(left_corner, upper_corner, right_corner, lower_corner, operation_type=False, blur_radius=blur_radius.get()))

    def blur_card(self):
        self.clear_operations()
        left_corner, upper_corner, right_corner, lower_corner = card2slide_rect_coords(width_card, height_card, 0, 0, width_slide, height_slide)
        self.rectangle_operations.append(RectangleOperation(left_corner, upper_corner, right_corner, lower_corner, operation_type=False, blur_radius=blur_radius.get(), blur_card=True))

        # self.card_front_image.paste(self.card_back_image.filter(ImageFilter.GaussianBlur(radius=blur_radius.get())))

    def clear_selection(self):
        # Convert coords
        if selected_rectangle is not None:
            self.rectangle_operations.pop(selected_rectangle)

    def clear_card(self):
        self.card_front_image = self.card_back_image.copy()
        self.draw = ImageDraw.Draw(self.card_front_image)

    def clear_operations(self):
        self.rectangle_operations = []

    def color_selection(self):
        left_corner, upper_corner, right_corner, lower_corner = card2slide_rect_coords(width_card, height_card,
                                                             rectangle_left_coord, rectangle_upper_coord,
                                                             rectangle_right_coord, rectangle_lower_coord)
        self.rectangle_operations.append(RectangleOperation(left_corner, upper_corner, right_corner, lower_corner, operation_type=True))

    def color_card(self):
        self.clear_operations()
        left_corner, upper_corner, right_corner, lower_corner = card2slide_rect_coords(width_card, height_card, 0, 0,width_slide, height_slide)
        self.rectangle_operations.append(RectangleOperation(left_corner, upper_corner, right_corner, lower_corner, operation_type=True))

    def update_rectangle_operations(self):
        self.clear_card()
        for rectangle_operation in self.rectangle_operations:
            if rectangle_operation.status:
                if rectangle_operation.operation_type:
                    self.draw.rectangle(rectangle_operation.get_rectangle_coords(), fill="black")
                else:
                    if rectangle_operation.blur_card:
                        self.card_front_image.paste(self.card_back_image.filter(ImageFilter.GaussianBlur(radius=rectangle_operation.blur_radius)))
                    else:
                        crop_img = self.card_back_image.crop(rectangle_operation.get_rectangle_coords())
                        blur_image = crop_img.filter(ImageFilter.GaussianBlur(radius=rectangle_operation.blur_radius))  # To blur
                        self.card_front_image.paste(blur_image, rectangle_operation.get_rectangle_coords())
            else:
                self.draw.rectangle(rectangle_operation.get_rectangle_coords(), outline='yellow', width=3)

# TkInter Events
def raise_frame(frame, event=None):
    global study_edit_state
    global current_card_number_edit

    if study_edit_state:  # Update Window if was modified
        current_card_number_edit = current_card_number_study
        update_card_edit()
    else:
        update_card_study()

    frame.tkraise()
    study_edit_state = not study_edit_state


def show_card_study():
    global image_tk_study
    pilImage = card_list[current_card_number_study].get_card()
    image_tk_study = ImageTk.PhotoImage(pilImage.resize((width_card, height_card)))
    canvas_study.itemconfigure(card_displayed_study, image=image_tk_study)


def show_card_edit():
    global image_tk_edit
    pilImage = card_list[current_card_number_edit].get_card()
    image_tk_edit = ImageTk.PhotoImage(pilImage.resize((width_card, height_card)))
    canvas_edit.itemconfigure(card_displayed_edit, image=image_tk_edit)


def update_card_study(flip_to_front=True):
    study_frame.focus_set()
    # Reset rectangles status
    for rectangle_operation in card_list[current_card_number_study].rectangle_operations:
        rectangle_operation.status = True
    card_list[current_card_number_study].update_rectangle_operations()

    if flip_to_front:
        card_list[current_card_number_study].set_front_card()
        canvas_study.itemconfig(page_corner_image_study, image=page_corner_image_tk_back)
        # Update Card Notes
        if card_list[current_card_number_study].notes != "":
            card_notes_study_lbl.configure(text="Notes: ")
            card_notes_study_lbl.configure(image=notes_alert_img, compound="right")
        else:
            card_notes_study_lbl.configure(text="")
            card_notes_study_lbl.configure(image="")
    else:
        card_list[current_card_number_study].set_back_card()
        canvas_study.itemconfig(page_corner_image_study, image=page_corner_image_tk_front)
        # Update Card Notes
        card_notes_study_lbl.configure(text="Notes: " + card_list[current_card_number_study].notes)
    # Show Card
    show_card_study()
    # Update Current Card Label
    btn_current_card_study.configure(text=study_screen_text[current_language][1] + str(1+current_card_number_study) + "/" + str(len(card_list)))
    # Update Rating
    rating_lbl.configure(text=study_screen_text[current_language][4] + str(card_list[current_card_number_study].rating))
    # Update Backgrounds
    new_background_color = dark_rating_color[card_list[current_card_number_study].rating]
    rating_lbl.configure(background=new_background_color)
    study_frame.configure(background=new_background_color)
    card_title_study_lbl.configure(bg=new_background_color)
    card_notes_study_lbl.configure(bg=new_background_color)
    canvas_study.configure(bg=new_background_color, highlightbackground=new_background_color)
    progress_bar_canvas.configure(bg=new_background_color, highlightbackground=new_background_color)

    # Update Completion
    completion_pct, one_pct, two_pct, three_pct, four_pct, five_pct = find_completion(card_list)
    progress_bar.update(completion_pct, one_pct, two_pct, three_pct, four_pct, five_pct)
    # Update Card Title
    card_title_study_lbl.configure(text=card_list[current_card_number_study].title)
    # Update Card Notes
    if card_list[current_card_number_study].title != "":
        card_title_study_lbl.configure(image=title_question_img, compound="right")
    else:
        card_title_study_lbl.configure(image="")
    # Update Focus
    study_frame.focus_set()


def update_card_edit(flip_to_front=True):
    # Reset rectangles status
    for rectangle_operation in card_list[current_card_number_edit].rectangle_operations:
        rectangle_operation.status = True
    card_list[current_card_number_edit].update_rectangle_operations()

    if flip_to_front:
        card_list[current_card_number_edit].set_front_card()
        canvas_edit.itemconfig(page_corner_image_edit, image=page_corner_image_tk_back)
    else:
        card_list[current_card_number_edit].set_back_card()
        canvas_edit.itemconfig(page_corner_image_edit, image=page_corner_image_tk_front)
    # Show Card
    show_card_edit()
    # Update Current Card Label
    btn_current_card_edit.configure(text=edit_screen_text[current_language][1] + str(1+current_card_number_edit) + "/" + str(len(card_list)))
    # Update title entry
    card_title_entry.delete('1.0', END)
    card_title_entry.insert('1.0', card_list[current_card_number_edit].title)

    # Update notes entry
    card_notes_entry.delete('1.0', END)
    card_notes_entry.insert('1.0', card_list[current_card_number_edit].notes)

    # Update link button
    if card_list[current_card_number_edit].linked_to_previous:
        btn_link_card.config(text=edit_screen_text[current_language][11], image=unlock_image, command=clicked_unlink_card)
        edit_frame.bind("L", clicked_unlink_card)

    else:
        btn_link_card.config(text=edit_screen_text[current_language][10], image=lock_image, command=clicked_link_card)
        edit_frame.bind("L", clicked_link_card)

    # Update Card Title
    if card_list[current_card_number_edit].title != "":
        card_title_edit_lbl.configure(text=card_list[current_card_number_edit].title)
    else:
        card_title_edit_lbl.configure(text=edit_screen_text[current_language][16])

    # Update Notes
    if card_list[current_card_number_edit].notes != "":
        card_notes_edit_lbl.configure(text="Notes: " + card_list[current_card_number_edit].notes)
    else:
        card_notes_edit_lbl.configure(text="Notes: "+edit_screen_text[current_language][17])


    # Update focus
    edit_frame.focus_set()  # Prevent focus from staying in entry box
    selection_obj.hide()  # Hide/reset selection

    # Update selection coordinates
    global rectangle_left_coord, rectangle_upper_coord, rectangle_right_coord, rectangle_lower_coord
    rectangle_left_coord = 0
    rectangle_upper_coord = 0
    rectangle_right_coord = 0
    rectangle_lower_coord = 0


def update_rectangle_operations(event=None):
    card_list[current_card_number_edit].update_rectangle_operations()

def clicked_previous_card(event=None):
    if study_edit_state:
        global current_card_number_study
        if current_card_number_study != 0:
            current_card_number_study = current_card_number_study - 1
            update_card_study()
    else:
        global current_card_number_edit
        if current_card_number_edit != 0:
            current_card_number_edit = current_card_number_edit - 1
            update_card_edit()


def clicked_next_card(event=None):
    if study_edit_state:
        global current_card_number_study
        if current_card_number_study != len(card_list) - 1:
            current_card_number_study = current_card_number_study + 1
            update_card_study()
    else:
        global current_card_number_edit
        if current_card_number_edit != len(card_list) - 1:
            current_card_number_edit = current_card_number_edit + 1
            update_card_edit()


def clicked_flip_card(event=None):

    global image_tk_edit
    global image_tk_study

    if study_edit_state:
        card_list[current_card_number_study].flip_card()
        pilImage = card_list[current_card_number_study].get_card()
        image_tk_study = ImageTk.PhotoImage(pilImage.resize((width_card, height_card)))
        canvas_study.itemconfigure(card_displayed_study, image=image_tk_study)
        study_frame.focus_set()
        if card_list[current_card_number_study].current_side:
            canvas_study.itemconfig(page_corner_image_study, image=page_corner_image_tk_back)
            if card_list[current_card_number_study].notes != "":
                card_notes_study_lbl.configure(text="Notes: ")
                card_notes_study_lbl.configure(image=notes_alert_img, compound="right")
            else:
                card_notes_study_lbl.configure(text="")
                card_notes_study_lbl.configure(image="")
        else:
            canvas_study.itemconfig(page_corner_image_study, image=page_corner_image_tk_front)
            if card_list[current_card_number_study].notes != "":
                card_notes_study_lbl.configure(text="Notes: " + card_list[current_card_number_study].notes)
                card_notes_study_lbl.configure(image="")
            else:
                card_notes_study_lbl.configure(text="")
                card_notes_study_lbl.configure(image="")
    else:
        card_list[current_card_number_edit].flip_card()
        pilImage = card_list[current_card_number_edit].get_card()
        image_tk_edit = ImageTk.PhotoImage(pilImage.resize((width_card, height_card)))
        canvas_edit.itemconfigure(card_displayed_edit, image=image_tk_edit)
        edit_frame.focus_set()
        if card_list[current_card_number_edit].current_side:
            canvas_edit.itemconfig(page_corner_image_edit, image=page_corner_image_tk_back)
        else:
            canvas_edit.itemconfig(page_corner_image_edit, image=page_corner_image_tk_front)


def clicked_blur_selection(event=None):
    card_list[current_card_number_edit].blur_selection()
    update_card_edit(flip_to_front=True)


def clicked_blur_card(event=None):
    card_list[current_card_number_edit].blur_card()
    update_card_edit(flip_to_front=True)


def clicked_color_card(event=None):
    card_list[current_card_number_edit].color_card()
    update_card_edit(flip_to_front=True)


def clicked_color_selection(event=None):
    card_list[current_card_number_edit].color_selection()
    update_card_edit(flip_to_front=True)


def clicked_clear_selection(event=None):
    card_list[current_card_number_edit].clear_selection()
    update_card_edit(flip_to_front=True)


def clicked_clear_card(event=None):
    card_list[current_card_number_edit].clear_operations()
    card_list[current_card_number_edit].clear_card()
    update_card_edit(flip_to_front=True)


def clicked_link_card(event=None):
    # Check if first card
    if current_card_number_edit != 0:
        card_list[current_card_number_edit].linked_to_previous = True
        card_list[current_card_number_edit - 1].linked_to_next = True
        card_list[current_card_number_edit].score = 4294967295
        update_card_edit()


def clicked_unlink_card(event=None):
    card_list[current_card_number_edit].linked_to_previous = False
    card_list[current_card_number_edit - 1].linked_to_next = False
    previous_card_idx = 1
    while card_list[current_card_number_edit - previous_card_idx].linked_to_previous:
        previous_card_idx = previous_card_idx + 1
    card_list[current_card_number_edit].score = card_list[current_card_number_edit - previous_card_idx].score
    update_card_edit()


def clicked_delete_card(event=None):
    global current_card_number_edit
    warning_delete = messagebox.askquestion(warning_text[current_language][0], warning_text[current_language][1],
                                       icon='warning')
    if warning_delete == "yes":
        card_list.pop(current_card_number_edit)
        if current_card_number_edit != len(card_list):  # Not -1 because of the pop
            # Update card number and score
            for card in card_list[current_card_number_edit:]:
                card.card_number = card.card_number - 1
                card.score = card.score - 1
        else:  # If at the end, go back
            current_card_number_edit = current_card_number_edit - 1

        update_card_edit()


def clicked_reset_blur_slider():
    blur_slider.set(30)
    edit_frame.focus_set()


def clicked_reset_ratings(event=None):
    global current_card_number_edit
    warning_reset = messagebox.askquestion(warning_text[current_language][2], warning_text[current_language][3],
                                       icon='warning')
    if warning_reset == "yes":
        for card in card_list:
            card.rating = 0
            card.score = card.card_number

        update_card_study()


def clickled_rating(rating=0, event=None):
    global current_card_number_study
    card_list[current_card_number_study].set_rating(rating=rating)
    if not card_list[current_card_number_study].linked_to_previous:
        card_list[current_card_number_study].set_new_score(new_rating=rating)
    if card_list[current_card_number_study].linked_to_next:
        current_card_number_study = current_card_number_study + 1
    else:
        current_card_number_study = find_min_score_card(card_list)
    update_card_study()


def convert_pdf_to_card_list():
    global card_list
    pdf2image_list = convert_from_path(window.filename, thread_count=1, fmt='jpg')  # Create image list from path
    card_list = createCardList(pdf2image_list)  # Convert pdf2image_list to a Card list


def done_import(future=None):
    global study_edit_state
    stop_loading()
    initialize_canvas()  # Initialize canvas
    study_edit_state = True  # Needs to be True because gets reversed in raise_frame
    raise_frame(edit_frame)


def clicked_import_file():
    window.filename = filedialog.askopenfilename(initialdir="./", title="Select file",
                                               filetypes=(("PDF files", "*.pdf"), ("all files", "*.*")))
    if window.filename != '':
        thread_pool_executor = futures.ThreadPoolExecutor(max_workers=1)
        loading_frame.tkraise()
        start_loading()
        loading_frame.update()
        executor = thread_pool_executor.submit(convert_pdf_to_card_list)
        executor.add_done_callback(done_import)

        window.filename = (window.filename.split("/")[-1]).split(".")[0]  # Fix for MACs


def clicked_load_cards():
    window.load_cards_filename = filedialog.askopenfilename(initialfile=window.filename, initialdir="./", title="Select file",
                                               filetypes=(("Flashcardizer file", "*.fcz"), ("all files", "*.*")))
    if window.load_cards_filename != '':
        load_cards(window.load_cards_filename)


def load_cards(load_filename):
    global card_list
    global study_edit_state
    global current_card_number_study, current_card_number_edit
    if 'card_list' in globals():
        del card_list
    card_list = []
    with open(window.load_cards_filename, "rb") as inputfile:
        number_of_cards = int.from_bytes(inputfile.read(4), byteorder='big')
        current_card_number_study = int.from_bytes(inputfile.read(4), byteorder='big')
        current_card_number_edit = current_card_number_study
        for card_number in range(number_of_cards):
            back_image_length = int.from_bytes(inputfile.read(4), byteorder='big')
            back_image = inputfile.read(back_image_length)
            card_number_card = int.from_bytes(inputfile.read(4), byteorder='big')
            current_side_card = bool.from_bytes(inputfile.read(1), byteorder='big')
            rating_card = int.from_bytes(inputfile.read(4), byteorder='big')
            score_card = int.from_bytes(inputfile.read(4), byteorder='big')
            title_length = int.from_bytes(inputfile.read(4), byteorder='big')
            title_card = inputfile.read(title_length).decode('utf-8')
            notes_length = int.from_bytes(inputfile.read(4), byteorder='big')
            notes_card = inputfile.read(notes_length).decode('utf-8')
            linked_to_previous_card = bool.from_bytes(inputfile.read(1), byteorder='big')
            linked_to_next_card = bool.from_bytes(inputfile.read(1), byteorder='big')

            rectangle_operations = []
            number_of_rectangle_operations = int.from_bytes(inputfile.read(4), byteorder='big')
            for rectangle_operation_number in range(number_of_rectangle_operations):
                rectangle_operation_left_corner = int.from_bytes(inputfile.read(4), byteorder='big')
                rectangle_operation_upper_corner = int.from_bytes(inputfile.read(4), byteorder='big')
                rectangle_operation_right_corner = int.from_bytes(inputfile.read(4), byteorder='big')
                rectangle_operation_lower_corner = int.from_bytes(inputfile.read(4), byteorder='big')
                rectangle_operation_operation_type = bool.from_bytes(inputfile.read(1), byteorder='big')
                rectangle_operation_status = bool.from_bytes(inputfile.read(1), byteorder='big')
                rectangle_operation_blur_card = bool.from_bytes(inputfile.read(1), byteorder='big')
                rectangle_operation_blur_radius = int.from_bytes(inputfile.read(4), byteorder='big')

                rectangle_operation = RectangleOperation(rectangle_operation_left_corner, rectangle_operation_upper_corner, rectangle_operation_right_corner, rectangle_operation_lower_corner, rectangle_operation_operation_type, blur_radius=rectangle_operation_blur_radius, blur_card=rectangle_operation_blur_card)
                rectangle_operations.append(rectangle_operation)

            # Create Card List Here
            card_list.append(Card(card_back_image=Image.open(io.BytesIO(back_image)),
                                  card_number=card_number_card,
                                  current_side=current_side_card,
                                  rating=rating_card,
                                  score=score_card,
                                  title=title_card,
                                  notes=notes_card,
                                  linked_to_previous=linked_to_previous_card,
                                  linked_to_next=linked_to_next_card
                                  ))
            card_list[card_number].set_rectangle_operation(rectangle_operations)


    # Destroy Previous Canvas
    if 'canvas_study' in globals():
        canvas_study.destroy()
        canvas_edit.destroy()
        card_notes_study_lbl.destroy()
        card_notes_edit_lbl.destroy()

    initialize_canvas()
    study_edit_state = True  # Needs to be True because gets reversed in raise_frame
    raise_frame(edit_frame)

    window.filename = (window.load_cards_filename.split("/")[-1]).split(".")[0]  # Fix for MACs


def clicked_save_cards():
    window.save_cards_filename = filedialog.asksaveasfilename(initialfile=window.filename, initialdir="./", title="Select file",
                                                filetypes=(("Flashcardizer file", "*.fcz"), ("all files", "*.*")),
                                                defaultextension="*.*")
    if window.save_cards_filename != '':
        with open(window.save_cards_filename, "wb") as outfile:
            outfile.write((len(card_list)).to_bytes(4, byteorder='big', signed=False))  # Write Card List Length card
            outfile.write((current_card_number_study).to_bytes(4, byteorder='big', signed=False))  # Write current study card
            for card_number, card in enumerate(card_list):
                binary_stream_back = io.BytesIO()  # Create a binary reader for back card
                card_list[card_number].card_back_image.save(binary_stream_back, format='JPEG')  # Save into binary reader
                byte_im_back = binary_stream_back.getvalue()  # Save byte image
                outfile.write((len(byte_im_back)).to_bytes(4, byteorder='big', signed=False))  # Write back image length
                outfile.write(byte_im_back)  # Write back image
                outfile.write(card_list[card_number].card_number.to_bytes(4, byteorder='big', signed=False)) # Write Card Number
                outfile.write(card_list[card_number].current_side.to_bytes(1, byteorder='big', signed=False))  # Write Current Side
                outfile.write(card_list[card_number].rating.to_bytes(4, byteorder='big', signed=False))  # Write Rating
                outfile.write(card_list[card_number].score.to_bytes(4, byteorder='big', signed=False))  # Write Score
                outfile.write(len(card_list[card_number].title.encode('utf-8')).to_bytes(4, byteorder='big', signed=False))  # Write Title length
                outfile.write(card_list[card_number].title.encode('utf-8'))  # Write Title
                outfile.write(len(card_list[card_number].notes.encode('utf-8')).to_bytes(4, byteorder='big', signed=False))  # Write Notes Length
                outfile.write(card_list[card_number].notes.encode('utf-8'))  # Write Notes
                outfile.write(card_list[card_number].linked_to_previous.to_bytes(1, byteorder='big', signed=False))  # Write Linked_Previous
                outfile.write(card_list[card_number].linked_to_next.to_bytes(1, byteorder='big', signed=False))  # Write Linked Next

                outfile.write((len(card_list[card_number].rectangle_operations)).to_bytes(4, byteorder='big', signed=False))  # Write Rectangle Operations Number
                for rectangle_operation in card_list[card_number].rectangle_operations:
                    outfile.write(rectangle_operation.left_corner.to_bytes(4, byteorder='big', signed=False))  # Write Rectangle Operation Left Corner
                    outfile.write(rectangle_operation.upper_corner.to_bytes(4, byteorder='big', signed=False))  # Write Rectangle Operation Upper Corner
                    outfile.write(rectangle_operation.right_corner.to_bytes(4, byteorder='big', signed=False))  # Write Rectangle Operation Right Corner
                    outfile.write(rectangle_operation.lower_corner.to_bytes(4, byteorder='big', signed=False))  # Write Rectangle Operation Lower Corner
                    outfile.write(rectangle_operation.operation_type.to_bytes(1, byteorder='big', signed=False))  # Write Rectangle Operation Operation Type
                    outfile.write(rectangle_operation.status.to_bytes(1, byteorder='big', signed=False))  # Write Rectangle Operation Status
                    outfile.write(rectangle_operation.blur_card.to_bytes(1, byteorder='big', signed=False))  # Write Rectangle Blur Card
                    outfile.write(rectangle_operation.blur_radius.to_bytes(4, byteorder='big', signed=False))  # Write Rectangle Blur Radius

def clicked_exit():
    window.destroy()


def find_min_score_card(card_list):
    score_list = [card.score for card in card_list]
    return score_list.index(min(score_list))


def find_completion(card_list):
    rating_list = [card.rating for card in card_list]

    return (sum(rating_list)/(len(rating_list)*5))*100, 100*rating_list.count(1)/len(rating_list), 100*rating_list.count(2)/len(rating_list), 100*rating_list.count(3)/len(rating_list), 100*rating_list.count(4)/len(rating_list), 100*rating_list.count(5)/len(rating_list)


def add_title_card(event=None):
    card_list[current_card_number_edit].set_title(title=card_title_entry.get('1.0', 'end-1c'))
    update_card_edit()


def add_notes_card(event=None):
    card_list[current_card_number_edit].set_notes(notes=card_notes_entry.get('1.0', 'end-1c'))
    update_card_edit()


def add_line_notes(event=None):
    pass


class MouseStudyTracker(Frame):
    def __init__(self, canvas):
        self.canvas = canvas
        self.canv_width = self.canvas.cget('width')
        self.canv_height = self.canvas.cget('height')
        self.reset()

    def reset(self):
        self.start = self.end = None

    def begin(self, event):
        self.start = (event.x, event.y)

    def quit(self, event):
        self.end = (event.x, event.y)
        # Check if clicked on existing rectangle
        for rectangle_operation in card_list[current_card_number_study].rectangle_operations:
            if rectangle_operation.check_if_in(self.start[0], self.start[1]) and rectangle_operation.check_if_in(self.end[0], self.end[1]):
                rectangle_operation.status = not rectangle_operation.status
                card_list[current_card_number_study].draw.rectangle(rectangle_operation.get_rectangle_coords(), outline='yellow', width=3)
                card_list[current_card_number_study].update_rectangle_operations()
                show_card_study()  # Show current yellow lines
                break
        if page_corner_button.contains(self.start[0], self.start[1]) and page_corner_button.contains(self.end[0], self.end[1]):
            clicked_flip_card()
        self.reset()

    def autodraw(self, command=lambda *args: None):
        """Setup automatic drawing; supports command option"""
        self.reset()
        self._command = command
        self.canvas.bind("<Button-1>", self.begin)
        self.canvas.bind("<ButtonRelease-1>", self.quit)


class MousePositionTracker(Frame):
    """ Tkinter Canvas mouse position widget. """

    def __init__(self, canvas):
        self.canvas = canvas
        self.canv_width = self.canvas.cget('width')
        self.canv_height = self.canvas.cget('height')
        self.reset()

        # Create canvas cross-hair lines.
        xhair_opts = dict(dash=(3, 2), fill='white', state=HIDDEN)
        self.lines = (self.canvas.create_line(0, 0, 0, self.canv_height, **xhair_opts),
                      self.canvas.create_line(0, 0, self.canv_width,  0, **xhair_opts))

    def cur_selection(self):
        return (self.start, self.end)

    def begin(self, event):
        global selected_rectangle
        self.start = (event.x, event.y)  # Remember position (no drawing).
        # Check if clicked on existing rectangle
        for rectangle_operation_idx, rectangle_operation in enumerate(card_list[current_card_number_edit].rectangle_operations):
            if rectangle_operation.check_if_in(self.start[0], self.start[1]):
                selected_rectangle = rectangle_operation_idx
                card_list[current_card_number_edit].update_rectangle_operations()
                show_card_edit()  # Clear previous yellow lines
                card_list[current_card_number_edit].draw.rectangle(rectangle_operation.get_rectangle_coords(), outline='yellow', width=3)
                show_card_edit()  # Show current  yellow lines
                self.reset()
                selection_obj.hide()
                return

        card_list[current_card_number_edit].update_rectangle_operations()
        show_card_edit()  # Clear previous yellow lines
        selected_rectangle = None

        if page_corner_button.contains(self.start[0], self.start[1]):
            clicked_flip_card()

    def update(self, event):
        if self.start is not None:
            self.end = (event.x, event.y)
            self._update(event)
            self._command(self.start, (event.x, event.y))  # User callback.

    def _update(self, event):
        # Update cross-hair lines.
        self.canvas.coords(self.lines[0], event.x, 0, event.x, self.canv_height)
        self.canvas.coords(self.lines[1], 0, event.y, self.canv_width, event.y)
        self.show()

    def reset(self):
        self.start = self.end = None

    def hide(self):
        self.canvas.itemconfigure(self.lines[0], state=HIDDEN)
        self.canvas.itemconfigure(self.lines[1], state=HIDDEN)

    def show(self):
        self.canvas.itemconfigure(self.lines[0], state=NORMAL)
        self.canvas.itemconfigure(self.lines[1], state=NORMAL)

    def autodraw(self, command=lambda *args: None):
        """Setup automatic drawing; supports command option"""
        self.reset()
        self._command = command
        self.canvas.bind("<Button-1>", self.begin)
        self.canvas.bind("<B1-Motion>", self.update)
        self.canvas.bind("<ButtonRelease-1>", self.quit)

    def quit(self, event):
        self.hide()  # Hide cross-hairs.
        self.reset()


class SelectionObject:
    """ Widget to display a rectangular area on given canvas defined by two points
        representing its diagonal.
    """
    def __init__(self, canvas, select_opts):
        # Create a selection objects for updating.
        self.canvas = canvas
        self.select_opts1 = select_opts
        self.width = self.canvas.cget('width')
        self.height = self.canvas.cget('height')

        # Options for areas outside rectanglar selection.
        select_opts1 = self.select_opts1.copy()
        select_opts1.update({'state': HIDDEN})  # Hide initially.
        # Separate options for area inside rectanglar selection.
        select_opts2 = dict(dash=(2, 2), fill='', outline='white', state=HIDDEN)

        # Initial extrema of inner and outer rectangles.
        imin_x, imin_y,  imax_x, imax_y = 0, 0,  1, 1
        omin_x, omin_y,  omax_x, omax_y = 0, 0,  self.width, self.height

        self.rects = (
            # Area *outside* selection (inner) rectangle.
            self.canvas.create_rectangle(omin_x, omin_y,  omax_x, imin_y, **select_opts2),
            self.canvas.create_rectangle(omin_x, imin_y,  imin_x, imax_y, **select_opts2),
            self.canvas.create_rectangle(imax_x, imin_y,  omax_x, imax_y, **select_opts2),
            self.canvas.create_rectangle(omin_x, imax_y,  omax_x, omax_y, **select_opts2),
            # Inner rectangle.
            self.canvas.create_rectangle(imin_x, imin_y,  imax_x, imax_y, **select_opts1)
        )

    def update(self, start, end):
        # Current extrema of inner and outer rectangles.
        imin_x, imin_y,  imax_x, imax_y = self._get_coords(start, end)
        omin_x, omin_y,  omax_x, omax_y = 0, 0,  self.width, self.height

        # Update coords of all rectangles based on these extrema.
        self.canvas.coords(self.rects[0], omin_x, omin_y,  omax_x, imin_y),
        self.canvas.coords(self.rects[1], omin_x, imin_y,  imin_x, imax_y),
        self.canvas.coords(self.rects[2], imax_x, imin_y,  omax_x, imax_y),
        self.canvas.coords(self.rects[3], omin_x, imax_y,  omax_x, omax_y),
        self.canvas.coords(self.rects[4], imin_x, imin_y,  imax_x, imax_y),

        for rect in self.rects:  # Make sure all are now visible.
            self.canvas.itemconfigure(rect, state=NORMAL)

    def _get_coords(self, start, end):
        """ Determine coords of a polygon defined by the start and
            end points one of the diagonals of a rectangular area.
        """
        return (min((start[0], end[0])), min((start[1], end[1])),
                max((start[0], end[0])), max((start[1], end[1])))

    def hide(self):
        for rect in self.rects:
            self.canvas.itemconfigure(rect, state=HIDDEN)


class RectangleButton:
    def __init__(self, x1, y1, x2, y2):
        # (x1, y1) is the upper left point of the rectangle
        # (x2, y2) is the lower right point of the rectangle
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        return

    def contains(self, newx, newy):
        # Will return true if the point (newx, newy) lies within the rectangle.
        # False otherwise.
        return (self.x1 <= newx <= self.x2) and (self.y1 <= newy <= self.y2)


def clicked_flip_corner(event=None):
    if page_corner_button.contains(event.x, event.y):
        clicked_flip_card()


class CircularProgressbar:
    def __init__(self, canvas, radius, thickness):
        self.canvas = canvas
        self.start_ang = 0
        self.radius = radius
        self.thickness = thickness
        self.completion_lbl = self.canvas.create_text(radius/2, radius/2, text=study_screen_text[current_language][6] + "\n0%", fill="white", justify="center", font=("Arial Bold", 16))
        self.arc_id_bg = self.canvas.create_arc(0 + self.thickness, 0 + self.thickness, self.radius - self.thickness,
                                             self.radius - self.thickness,
                                             start=0, extent=360-0.00000001,
                                             width=self.thickness, style='arc', outline="gray25")

        self.arc_id_1 = self.canvas.create_arc(0 + self.thickness, 0 + self.thickness, self.radius - self.thickness,
                                               self.radius - self.thickness,
                                               start=0, extent=0,
                                               width=self.thickness, style='arc', outline=rating_color[1])
        self.arc_id_2 = self.canvas.create_arc(0 + self.thickness, 0 + self.thickness, self.radius - self.thickness,
                                               self.radius - self.thickness,
                                               start=0, extent=0,
                                               width=self.thickness, style='arc', outline=rating_color[2])
        self.arc_id_3 = self.canvas.create_arc(0 + self.thickness, 0 + self.thickness, self.radius - self.thickness,
                                               self.radius - self.thickness,
                                               start=0, extent=0,
                                               width=self.thickness, style='arc', outline=rating_color[3])
        self.arc_id_4 = self.canvas.create_arc(0 + self.thickness, 0 + self.thickness, self.radius - self.thickness,
                                               self.radius - self.thickness,
                                               start=0, extent=0,
                                               width=self.thickness, style='arc', outline=rating_color[4])
        self.arc_id_5 = self.canvas.create_arc(0 + self.thickness, 0 + self.thickness, self.radius - self.thickness,
                                               self.radius - self.thickness,
                                               start=0, extent=0,
                                               width=self.thickness, style='arc', outline=rating_color[5])

    def update(self, completion_pct, one_pct, two_pct, three_pct, four_pct, five_pct):
        self.canvas.itemconfigure(self.arc_id_1, extent=one_pct*360/100-0.00000001)
        self.canvas.itemconfigure(self.arc_id_2, start=one_pct*360/100, extent=two_pct * 360 / 100 - 0.00000001)
        self.canvas.itemconfigure(self.arc_id_3, start=(one_pct+two_pct)*360/100, extent=three_pct * 360 / 100 - 0.00000001)
        self.canvas.itemconfigure(self.arc_id_4, start=(one_pct+two_pct+three_pct)*360/100, extent=four_pct * 360 / 100 - 0.00000001)
        self.canvas.itemconfigure(self.arc_id_5, start=(one_pct+two_pct+three_pct+four_pct)*360/100, extent=five_pct * 360 / 100 - 0.00000001)
        self.canvas.itemconfigure(self.completion_lbl, text=study_screen_text[current_language][6]+"\n{:.0f}%".format(completion_pct))


def initialize_canvas(loading_current_study_number=0):
    global current_card_number_edit
    global current_card_number_study
    global width_card, height_card, width_slide, height_slide
    global rectangle_left_coor, rectangle_upper_coord, rectangle_right_coord, rectangle_lower_coord
    global card_displayed_edit, card_displayed_study
    global selection_obj
    global canvas_edit, canvas_study

    canvas_edit = Canvas(edit_frame, width=0, height=0, bg=background_color, highlightbackground=background_color)
    canvas_edit.grid(column=1, row=2, rowspan=13)

    canvas_study = Canvas(study_frame, width=0, height=0, bg=background_color, highlightbackground=background_color)
    canvas_study.grid(column=1, row=2, rowspan=12)

    rectangle_left_coord, rectangle_upper_coord, rectangle_right_coord, rectangle_lower_coord = 0, 0, 0, 0
    card_list[current_card_number_edit].set_back_card()  # Flip First Card
    pilImage = card_list[current_card_number_edit].get_card()  # Get First Card
    width_slide, height_slide = pilImage.size  # Get Card size

    width_card, height_card = slide2card_dimensions(width_slide, height_slide)  # Ascertain Canvas Size
    canvas_edit.config(width=width_card, height=height_card)
    image_tk_edit = ImageTk.PhotoImage(pilImage.resize((width_card, height_card)))
    card_displayed_edit = canvas_edit.create_image(width_card, height_card, image=image_tk_edit, anchor="se")

    canvas_study.config(width=width_card, height=height_card)
    card_list[current_card_number_study].set_front_card()  # Flip First Card
    pilImage = card_list[current_card_number_study].get_card()  # Get First Card
    image_tk_study = ImageTk.PhotoImage(pilImage.resize((width_card, height_card)))
    card_displayed_study = canvas_study.create_image(width_card, height_card, image=image_tk_study, anchor="se")

    SELECT_OPTS = dict(dash=(2, 2), stipple='gray25', fill='red', outline='')
    selection_obj = SelectionObject(canvas_edit, SELECT_OPTS)

    # Callback function to update it given two points of its diagonal.
    def on_drag(start, end, **kwarg):  # Must accept these arguments.
        global rectangle_left_coord, rectangle_upper_coord, rectangle_right_coord, rectangle_lower_coord

        selection_obj.update(start, end)
        rectangle_left_coord = min(start[0], end[0])
        rectangle_right_coord = max(start[0], end[0])
        rectangle_upper_coord = min(start[1], end[1])
        rectangle_lower_coord = max(start[1], end[1])

    # Create mouse position tracker that uses the function.
    posn_tracker = MousePositionTracker(canvas_edit)
    posn_tracker.autodraw(command=on_drag)  # Enable callbacks.
    posn_tracker_study = MouseStudyTracker(canvas_study)
    posn_tracker_study.autodraw(command=on_drag)  # Enable callbacks.

    # Card Title
    global card_title_edit_lbl, card_title_study_lbl
    global title_question_img

    title_question_img = PhotoImage(file="media/Question.png")
    card_title_edit_lbl = Label(edit_frame, text="<No Text For This Card Yet>", wraplength=width_card, justify='center',
                                bg=background_color, fg="white", font=("Arial Bold", 20))
    card_title_edit_lbl.grid(column=1, row=0, rowspan=2)
    card_title_study_lbl = Label(study_frame, text="", wraplength=width_card, justify='center', bg=background_color,
                                 fg="white", font=("Arial Bold", 20))
    card_title_study_lbl.grid(column=1, row=0, rowspan=2)

    # Card Notes
    global card_notes_study_lbl
    global notes_alert_img

    notes_alert_img = PhotoImage(file="media/NotesAlert.png")
    card_notes_study_lbl = Label(study_frame,
                                 text="Notes: ",
                                 wraplength=width_card, bg=background_color, fg="white", font=("Arial Bold", 14),
                                 justify="left")
    card_notes_study_lbl.grid(column=1, row=15, sticky="W")
    global card_notes_edit_lbl
    card_notes_edit_lbl = Label(edit_frame,
                                text="Notes: ",
                                wraplength=width_card, bg=background_color, fg="white", font=("Arial Bold", 14),
                                justify="left")
    card_notes_edit_lbl.grid(column=1, row=17, sticky="W")

    # Put Images and Buttons in corner
    global page_corner_image_tk_front, page_corner_image_tk_back
    global page_corner_image_edit, page_corner_image_study
    global page_corner_button
    page_corner_image_front = Image.open(img_text[current_language][0])
    page_corner_image_front = page_corner_image_front.resize((int(width_card / 20), int(width_card / 20)))
    page_corner_image_tk_front = ImageTk.PhotoImage(page_corner_image_front)

    page_corner_image_back = Image.open(img_text[current_language][1])
    page_corner_image_back = page_corner_image_back.resize((int(width_card / 20), int(width_card / 20)))
    page_corner_image_tk_back = ImageTk.PhotoImage(page_corner_image_back)

    page_corner_image_edit = canvas_edit.create_image((width_card, 0), image=page_corner_image_tk_back, anchor='ne')
    page_corner_image_study = canvas_study.create_image((width_card, 0), image=page_corner_image_tk_front,
                                                        anchor='ne')

    page_corner_button = RectangleButton(width_card - int(width_card / 20), 0, width_card, int(width_card / 20))
    # Bind left mouse click to corner
    # canvas_study.bind("<Button-1>", clicked_flip_corner) # TO DELETE


def clicked_shortcuts():
    shortcuts_window = Toplevel()
    shortcuts_window.configure(background=background_color)
    label1 = Label(shortcuts_window, bg=background_color, text=shortcuts_text[current_language][0], fg="white", font=("Arial Bold", 54))
    label1.grid(row=1, column=1, columnspan=2, padx=(100, 100), pady=(50, 25))
    label2 = Label(shortcuts_window, bg=background_color, justify="left",
                   text=shortcuts_text[current_language][1],
                   fg="gray95", font=("Arial Bold", 12))
    label2.grid(row=2, column=1, padx=(100, 25), pady=(0, 100))
    label3 = Label(shortcuts_window, bg=background_color, justify="right",
                   text=shortcuts_text[current_language][2],
                   fg="gray95", font=("Arial Bold", 12))
    label3.grid(row=2, column=2, padx=(25, 100), pady=(0, 100))


def clicked_language_french():
    global current_language
    current_language = "french"
    clicked_language()


def clicked_language_english():
    global current_language
    current_language = "english"
    clicked_language()

def clicked_language():
    # Change Menu Bar
    file_menu.entryconfig(0, label=menu_bar_text[current_language][0])
    file_menu.entryconfig(1, label=menu_bar_text[current_language][1])
    file_menu.entryconfig(2, label=menu_bar_text[current_language][2])
    file_menu.entryconfig(4, label=menu_bar_text[current_language][3])
    menu_bar.entryconfig(0, label=menu_bar_text[current_language][4])

    info_menu.entryconfig(0, label=menu_bar_text[current_language][5])

    language_menu.entryconfig(0, label=menu_bar_text[current_language][6])
    language_menu.entryconfig(1, label=menu_bar_text[current_language][7])

    info_menu.entryconfig(1, label=menu_bar_text[current_language][8])
    info_menu.entryconfig(2, label=menu_bar_text[current_language][9])

    menu_bar.entryconfig(1, label=menu_bar_text[current_language][10])

    # Change Main Screen
    lbl_welcome.configure(text=main_screen_text[current_language][0])
    btn_import.configure(text=main_screen_text[current_language][1])
    btn_load.configure(text=main_screen_text[current_language][2])

    # Change Loading Screen
    lbl_loading.configure(text=loading_screen_text[current_language][0])
    lbl_loading_small.configure(text=loading_screen_text[current_language][1])

    # Change Edit Screen
    btn_study.configure(text=edit_screen_text[current_language][0])
    btn_current_card_edit.configure(text=edit_screen_text[current_language][1])  # NECESSARY???
    btn_previous_edit.configure(text=edit_screen_text[current_language][2])
    btn_next_edit.configure(text=edit_screen_text[current_language][3])
    btn_blur_selection.configure(text=edit_screen_text[current_language][4])
    btn_blur_card.configure(text=edit_screen_text[current_language][5])
    btn_color_selection.configure(text=edit_screen_text[current_language][6])
    btn_color_card.configure(text=edit_screen_text[current_language][7])
    btn_clear_selection.configure(text=edit_screen_text[current_language][8])
    btn_clear_card.configure(text=edit_screen_text[current_language][9])
    btn_link_card.configure(text=edit_screen_text[current_language][10])  # NECESSARY???
    btn_delete_card.configure(text=edit_screen_text[current_language][12])
    btn_card_title_entry.configure(text=edit_screen_text[current_language][13])
    btn_card_notes_entry.configure(text=edit_screen_text[current_language][14])
    btn_blur_slider.configure(text=edit_screen_text[current_language][15])

    # Change Study Screen
    btn_edit.configure(text=study_screen_text[current_language][0])
    btn_current_card_study.configure(text=study_screen_text[current_language][1])  # NECESSARY???
    btn_previous_study.configure(text=study_screen_text[current_language][2])
    btn_next_study.configure(text=study_screen_text[current_language][3])
    rating_lbl.configure(text=study_screen_text[current_language][4])
    btn_reset_ratings.configure(text=study_screen_text[current_language][5])

    if 'study_edit_state' in globals():
        # Change images
        global page_corner_image_tk_front, page_corner_image_tk_back
        page_corner_image_front = Image.open(img_text[current_language][0])
        page_corner_image_front = page_corner_image_front.resize((int(width_card / 20), int(width_card / 20)))
        page_corner_image_tk_front = ImageTk.PhotoImage(page_corner_image_front)

        page_corner_image_back = Image.open(img_text[current_language][1])
        page_corner_image_back = page_corner_image_back.resize((int(width_card / 20), int(width_card / 20)))
        page_corner_image_tk_back = ImageTk.PhotoImage(page_corner_image_back)

        if study_edit_state:
            update_card_study()
        else:
            update_card_edit()

    # Save Settings
    with open("language_preferences.bin", "wb") as language_file:
        language_file.write(len(current_language.encode('utf-8')).to_bytes(4, byteorder='big', signed=False))  # Write Language Length
        language_file.write(current_language.encode('utf-8'))  # Write Language



def clicked_about():
    about_window = Toplevel()
    about_window.configure(background=background_color)
    label1 = Label(about_window, bg=background_color, text=about_text[current_language][0], fg="white", font=("Arial Bold", 76))
    label1.pack(padx=(100, 100), pady=(50, 0))
    lbl_logo_about = Label(about_window, image=logo_image, bg=background_color)
    lbl_logo_about.pack(padx=(100, 100), pady=(0, 0))
    label2 = Label(about_window, bg=background_color, text=about_text[current_language][1], fg="white",
                   font=("Arial Bold", 32))
    label2.pack(padx=(100, 100))
    label3 = Label(about_window, bg=background_color, text=about_text[current_language][2],
                   fg="white", font=("Arial Bold", 24))
    label3.pack(padx=(100, 100))
    label4 = Label(about_window, bg=background_color,
                   text=about_text[current_language][3],
                   fg="gray95", font=("Arial Bold", 16))
    label4.pack(padx=(100, 100), pady=(0, 100))


timer_id = None


def start_loading(n=0, stop_flag=False):
    global timer_id
    gif = loading_animation[n % len(loading_animation)]
    lbl_loading_animation.configure(image=gif)
    timer_id = window.after(40, start_loading, n + 1)  # call this function every 100ms


def stop_loading():
    window.after_cancel(timer_id)

if __name__ == "__main__":
    # TkInter
    window = Tk()  # Initialize Window
    window.iconbitmap("media/Icon.ico")
    window.configure(background=background_color)
    window.filename = ''
    window.title("Flash Cardizer")  # Add Title
    window.columnconfigure(0, weight=1)
    window.rowconfigure(0, weight=1)

    # Create Menu
    menu_bar = Menu(window, tearoff=False)
    file_menu = Menu(menu_bar, tearoff=False)
    file_menu.add_command(label=menu_bar_text[current_language][0], command=clicked_import_file)
    file_menu.add_command(label=menu_bar_text[current_language][1], command=clicked_load_cards)
    file_menu.add_command(label=menu_bar_text[current_language][2], command=clicked_save_cards)
    file_menu.add_separator()
    file_menu.add_command(label=menu_bar_text[current_language][3], command=clicked_exit)
    menu_bar.add_cascade(label=menu_bar_text[current_language][4], menu=file_menu)

    info_menu = Menu(menu_bar, tearoff=False)
    info_menu.add_command(label=menu_bar_text[current_language][5], command=clicked_shortcuts)
    language_menu = Menu(info_menu, tearoff=False)
    language_menu.add_command(label=menu_bar_text[current_language][6], command=clicked_language_english)
    language_menu.add_command(label=menu_bar_text[current_language][7], command=clicked_language_french)
    info_menu.add_cascade(label=menu_bar_text[current_language][8], menu=language_menu)
    info_menu.add_command(label=menu_bar_text[current_language][9], command=clicked_about)
    menu_bar.add_cascade(label=menu_bar_text[current_language][10], menu=info_menu)

    window.config(menu=menu_bar)

    # Create Welcome frame
    welcome_frame = Frame(window, bg=background_color)
    welcome_frame.grid(row=0, column=0)
    welcome_frame.columnconfigure(0, weight=1)
    welcome_frame.rowconfigure(0, weight=1)
    welcome_frame.rowconfigure(6, weight=1)

    logo_image = PhotoImage(file="media/Logo.png")
    lbl_logo = Label(welcome_frame, image=logo_image, bg=background_color)
    lbl_logo.grid(column=0, row=1)

    lbl_welcome = Label(welcome_frame, text=main_screen_text[current_language][0], bg=background_color, fg="white", font=("Arial Bold", 64))
    lbl_welcome.grid(column=0, row=2)

    # Import Button
    import_pdf_image = PhotoImage(file="media/ImportPdf.png")
    btn_import = Button(welcome_frame, width=500, height=90, text=main_screen_text[current_language][1], image=import_pdf_image, compound="right", bg="white", fg="red2", font=('Arial', '30', 'bold'), borderwidth=0, command=clicked_import_file)
    btn_import.grid(column=0, row=3)

    lbl_welcome_load = Label(welcome_frame, text=" ", bg=background_color, font=("Arial Bold", 16))
    lbl_welcome_load.grid(column=0, row=4)
    # Load Button
    load_cards_image = PhotoImage(file="media/LoadCards.png")
    btn_load = Button(welcome_frame, width=500, height=90, text=main_screen_text[current_language][2], image=load_cards_image, compound="right", bg="midnight blue", fg="white", font=('Arial', '28', 'bold'), borderwidth=0, command=clicked_load_cards)
    btn_load.grid(column=0, row=5, pady=(0, 100))

    # Create Loading screen
    loading_frame = Frame(window)
    loading_frame.configure(background=background_color)
    loading_frame.columnconfigure(0, weight=1)
    loading_frame.rowconfigure(0, weight=1)
    loading_frame.rowconfigure(4, weight=1)
    lbl_loading = Label(loading_frame, text=loading_screen_text[current_language][0], fg="white", bg=background_color, font=("Arial Bold", 64))
    lbl_loading.grid(column=0, row=1)
    lbl_loading_small = Label(loading_frame, text=loading_screen_text[current_language][1], fg="white", bg=background_color, font=("Arial Bold", 16))
    lbl_loading_small.grid(column=0, row=2)
    loading_animation = [PhotoImage(file='media/Loading.gif', format='gif -index %i' %(i)) for i in range(30)]

    lbl_loading_animation = Label(loading_frame, image=loading_animation[0], bg=background_color)
    lbl_loading_animation.grid(column=0, row=3, pady=(0, 100))

    # Create Frames
    edit_frame = Frame(window)
    edit_frame.configure(background=background_color)
    edit_frame.focus_set()  # Initialize Focus
    edit_frame.columnconfigure(0, weight=1)
    edit_frame.columnconfigure(4, weight=1)
    edit_frame.bind("<1>", lambda event: edit_frame.focus_set())  # Make Frame be able to receive keyboard focus
    study_frame = Frame(window)
    study_frame.focus_set()  # Initialize Focus
    study_frame.columnconfigure(0, weight=1)
    study_frame.columnconfigure(12, weight=1)
    study_frame.bind("<1>", lambda event: study_frame.focus_set())  # Make Frame be able to receive keyboard focus
    study_frame.configure(background=background_color)  # Default Background Color
    for frame in (edit_frame, study_frame, welcome_frame, loading_frame):
        frame.grid(row=0, column=0, sticky='news')

    # # Text label
    # edit_msg_lbl = Label(edit_frame, text="Edit your cards!", bg=background_color, fg="white", font=("Arial Bold", 32))
    # edit_msg_lbl.grid(column=1, row=0)
    # study_msg_lbl = Label(study_frame, text="Study your cards!", bg=background_color, fg="white", font=("Arial Bold", 32))
    # study_msg_lbl.grid(column=1, row=0)

    # Study Button
    study_image = PhotoImage(file="media/Study.png")
    btn_study = Button(edit_frame, width=450, height=90, text=edit_screen_text[current_language][0], image=study_image, compound="right", bg="green4", fg="black", font=('Arial', '32', 'bold'), borderwidth=0, command=lambda: raise_frame(study_frame))
    btn_study.grid(column=2, row=0, rowspan=2, columnspan=2,  pady=(10, 0))
    edit_frame.bind("#", partial(raise_frame, study_frame))

    # Edit Button
    edit_image = PhotoImage(file="media/Edit.png")
    btn_edit = Button(study_frame, width=450, height=90, text=study_screen_text[current_language][0], image=edit_image, compound="right", bg="gold3", fg="black", font=('Arial', '32', 'bold'), borderwidth=0, command=lambda: raise_frame(edit_frame))
    btn_edit.grid(column=2, row=0, rowspan=2, columnspan=10,  pady=(10, 0))
    study_frame.bind("#", partial(raise_frame, edit_frame))

    # Current Card Label
    void_image = PhotoImage(file="media/Void.png")
    btn_current_card_edit = Button(edit_frame, width=350, height=45, text=edit_screen_text[current_language][1], image=void_image, compound="left", bg=buttons_color, fg="white", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_flip_card)
    btn_current_card_edit.grid(column=2, row=3, columnspan=2)
    btn_current_card_study = Button(study_frame, width=350, height=45, text=study_screen_text[current_language][1], image=void_image, compound="left", bg=buttons_color, fg="white", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_flip_card)
    btn_current_card_study.grid(column=2, row=3, columnspan=10)

    # Previous and Next Button
    previous_img = PhotoImage(file="media/Previous.png")
    btn_previous_edit = Button(edit_frame, width=150, height=45, text=edit_screen_text[current_language][2], image=previous_img, compound="left", bg=buttons_color, fg="white", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_previous_card)
    btn_previous_edit.grid(column=2, row=4)
    btn_previous_study = Button(study_frame, width=150, height=45, text=study_screen_text[current_language][2], image=previous_img, compound="left", bg=buttons_color, fg="white", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_previous_card)
    btn_previous_study.grid(column=2, row=4, columnspan=5)
    edit_frame.bind("<Left>", clicked_previous_card)
    study_frame.bind("<Left>", clicked_previous_card)

    next_img = PhotoImage(file="media/Next.png")
    btn_next_edit = Button(edit_frame, width=150, height=45, text=edit_screen_text[current_language][3], image=next_img, compound="right", bg=buttons_color, fg="white", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_next_card)
    btn_next_edit.grid(column=3, row=4)
    btn_next_study = Button(study_frame, width=150, height=45, text=study_screen_text[current_language][3], image=next_img, compound="right", bg=buttons_color, fg="white", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_next_card)
    btn_next_study.grid(column=7, row=4, columnspan=5)
    edit_frame.bind("<Right>", clicked_next_card)
    study_frame.bind("<Right>", clicked_next_card)

    # Flip Button
    edit_frame.bind("<space>", clicked_flip_card)
    study_frame.bind("<space>", clicked_flip_card)

    # Blur Selection Button
    blur_selection_image = PhotoImage(file="media/BlurSelection.png")
    btn_blur_selection = Button(edit_frame, width=150, height=45, text=edit_screen_text[current_language][4], image=blur_selection_image, compound="right", bg=buttons_color, fg="white", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_blur_selection)
    btn_blur_selection.grid(column=2, row=5)
    edit_frame.bind("b", clicked_blur_selection)

    # Blur Card Button
    blur_card_image = PhotoImage(file="media/BlurCard.png")
    btn_blur_card = Button(edit_frame, width=150, height=45, text=edit_screen_text[current_language][5], image=blur_card_image, compound="right", bg=buttons_color, fg="white", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_blur_card)
    btn_blur_card.grid(column=3, row=5)
    edit_frame.bind("B", clicked_blur_card)

    # Color Selection Button
    color_selection_image = PhotoImage(file="media/ColorSelection.png")
    btn_color_selection = Button(edit_frame, width=150, height=45, text=edit_screen_text[current_language][6], image=color_selection_image, compound="right", bg=buttons_color, fg="white", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_color_selection)
    btn_color_selection.grid(column=2, row=6)
    edit_frame.bind("c", clicked_color_selection)

    # Color Card Button
    color_card_image = PhotoImage(file="media/ColorCard.png")
    btn_color_card = Button(edit_frame, width=150, height=45, text=edit_screen_text[current_language][7], image=color_card_image, compound="right", bg=buttons_color, fg="white", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_color_card)
    btn_color_card.grid(column=3, row=6)
    edit_frame.bind("C", clicked_color_card)

    # Clear Selection Button
    clear_selection_image = PhotoImage(file="media/ClearSelection.png")
    btn_clear_selection = Button(edit_frame, width=150, height=45, text=edit_screen_text[current_language][8], image=clear_selection_image, compound="right", bg=buttons_color, fg="white", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_clear_selection)
    btn_clear_selection.grid(column=2, row=7)
    edit_frame.bind("x", clicked_clear_selection)

    # Clear Card Button
    clear_card_image = PhotoImage(file="media/ClearCard.png")
    btn_clear_card = Button(edit_frame, width=150, height=45, text=edit_screen_text[current_language][9], image=clear_card_image, compound="right", bg=buttons_color, fg="white", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_clear_card)
    btn_clear_card.grid(column=3, row=7)
    edit_frame.bind("X", clicked_clear_card)

    # Link Card Button
    lock_image = PhotoImage(file="media/Lock.png")
    unlock_image = PhotoImage(file="media/Unlock.png")
    btn_link_card = Button(edit_frame, width=150, height=45, text=edit_screen_text[current_language][10], image=lock_image, compound="right", bg=buttons_color, fg="orange3", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_link_card)
    btn_link_card.grid(column=2, row=8)
    edit_frame.bind("L", clicked_link_card)

    # Delete Card Button
    delete_image = PhotoImage(file="media/Delete.png")
    btn_delete_card = Button(edit_frame, width=150, height=45, text=edit_screen_text[current_language][12], image=delete_image, compound="right", bg=buttons_color, fg="red3", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_delete_card)
    btn_delete_card.grid(column=3, row=8)
    edit_frame.bind("<Delete>", clicked_delete_card)

    # Card Title Entry
    btn_card_title_entry = Button(edit_frame, width=150, height=45, text=edit_screen_text[current_language][13], image=next_img, compound="right", bg=buttons_color, fg="white", font=('Arial', '12', 'bold'), borderwidth=0, command=add_title_card)
    btn_card_title_entry.grid(column=2, row=9)

    card_title_entry = Text(edit_frame, height=1, width=22, bg=buttons_color, fg="white", font=('Arial', '9'))
    card_title_entry.grid(column=3, row=9, ipady=15)
    card_title_entry.bind('<Return>', add_title_card)
    card_title_entry.bind('<Shift-Return>', add_line_notes)

    # Card Notes Entry
    btn_card_notes_entry = Button(edit_frame, width=150, height=45, text=edit_screen_text[current_language][14], image=next_img, compound="right", bg=buttons_color, fg="white", font=('Arial', '12', 'bold'), borderwidth=0, command=add_notes_card)
    btn_card_notes_entry.grid(column=2, row=10)

    card_notes_entry = Text(edit_frame, height=1, width=22, bg=buttons_color, fg="white", font=('Arial', '9'))
    card_notes_entry.grid(column=3, row=10, ipady=15)
    card_notes_entry.bind('<Return>', add_notes_card)
    card_notes_entry.bind('<Shift-Return>', add_line_notes)

    # Blur Slider
    blur_slider_img = PhotoImage(file="media/BlurSlider.png")
    btn_blur_slider = Button(edit_frame, width=150, height=45, text=edit_screen_text[current_language][15], image=blur_slider_img, compound="right", bg=buttons_color, fg="white", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_reset_blur_slider)
    btn_blur_slider.grid(column=2, row=11)
    blur_radius = IntVar()
    blur_slider = Scale(edit_frame, length=150, width=45, variable=blur_radius, bd=0, sliderlength=45, sliderrelief="flat", showvalue=0, bg="white", fg="white", highlightcolor="white", troughcolor=buttons_color, highlightbackground=buttons_color, border=0, orient=HORIZONTAL, activebackground="white", font=('Arial', '16', 'bold'))
    blur_slider.grid(column=3, row=11)
    blur_slider.set(30)

    # TEST UPDATE OPERATION
    edit_frame.bind("Q", update_rectangle_operations)

    # Add Appreciation Buttons
    for i in range(5):
        rating_button = Button(study_frame, width=6, height=2, text=str(i+1), bg=rating_color[i+1], fg="white", font=('Arial', '16', 'bold'), borderwidth=0, command=partial(clickled_rating, i+1))
        rating_button.grid(column=2+2*i, row=6, columnspan=2)
        study_frame.bind(str(i+1), partial(clickled_rating, i+1))

    # Current Rating Label
    rating_lbl = Label(study_frame, text=study_screen_text[current_language][4], bg=background_color, fg="white", font=("Arial Bold", 16))
    rating_lbl.grid(column=2, row=11, columnspan=10)

    # Progress Bar
    progress_bar_canvas = Canvas(study_frame, width=200, height=200, bg=background_color, highlightbackground=background_color)
    progress_bar_canvas.grid(column=2, row=5, columnspan=10)
    progress_bar = CircularProgressbar(progress_bar_canvas, 200, 20)

    # Rest Ratings Button
    btn_reset_ratings = Button(study_frame, width=150, height=45, text=study_screen_text[current_language][5]+"0", image=delete_image, compound="right", bg=buttons_color, fg="red3", font=('Arial', '12', 'bold'), borderwidth=0, command=clicked_reset_ratings)
    btn_reset_ratings.grid(column=2, row=13, columnspan=10)
    study_frame.bind("<Delete>", clicked_reset_ratings)

    current_card_number_edit = 0
    current_card_number_study = 0

    # Raise welcome frame by default
    welcome_frame.tkraise()

    # Set window geometry
    window.geometry(str(width_screen)+'x'+str(height_screen)+'+0+0')

    # If icon clicked directly
    parser = argparse.ArgumentParser()
    parser.add_argument("fczfile", nargs="?", default=False)  # 'nargs="?"' makes the argument optional
    args = parser.parse_args()
    if args.fczfile:
        print(args.fczfile)
        print("LOADING DIRECTLY FROM FCZ FILE")
        window.load_cards_filename = args.fczfile
        load_cards(window.load_cards_filename)

    # Mainloop
    window.mainloop()


# ############################## TO DO ##############################
# FIX FOR APPLE (SCREENSIZE?)
# CHECK SAVED? (MAYBE ALWAYS ON EXIT???)
# CLICK ON NOTES?
# CTRL Z???
# NOT NECESSARY TO SAVE FRONT IMAGE?

# FIX FOCUS!!!!! (MOSTLY DONE, MAYBE BETTER FLIP CARD?)
# BETTER PROGRAMMING FOR EDIT/STUDY??
# PERFECT ALGORITHM FOR STUDY ORDER
# LINK WITH PREVIOUS -> ASK YOURSELF ABOUT WHAT DO DO WITH DUAL SCORES??
# CONVERT TO OBJECTS FOR BLACK/BLUR?

# EXPORT
