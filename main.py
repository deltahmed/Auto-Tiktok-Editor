import customtkinter as ctk
import tkinter as tk
from moviepy.editor import *
from moviepy.video.fx.all import crop
from PIL import Image, ImageDraw, ImageFont
import os
from random import choice
from pathvalidate import sanitize_filename
from pytube import YouTube
from tkinter.messagebox import showerror
from tkinter import filedialog as fd


def create_tiktok_text(size: tuple, message: str, fontColor, fnt = ImageFont.truetype('ressources\Futura.otf', 70)):
    espacement = 13
    W, H = size
    image = Image.new('RGBA', size, (0,0,0,0))
    draw = ImageDraw.Draw(image)
    _, _, w, h = draw.textbbox((0, 0), message, font=fnt)
    draw.rounded_rectangle(((W-w)/2 - espacement, (H-h)/2 - espacement, (W-w)/2 + w + espacement , (H-h)/2 + h + espacement), fill="white", radius=7)
    draw.text(((W-w)/2, (H-h)/2), message, font=fnt, fill=fontColor)
    return image

def one_tiktok(text: str, frontclip: VideoClip, backclip: VideoClip):
    filename = sanitize_filename(f"temp_img_{text}_{id(text)}.png")
    myImage = create_tiktok_text(frontclip.size, text, 'black')
    myImage.save(filename)

    (w, h) = backclip.size
    backclip = crop(backclip, width=720, height=650, x_center=w/2, y_center=h/2).resize(width=1280)

    final_clip = clips_array([[frontclip],[backclip]])
    (w2, h2) = frontclip.size
    title = ImageClip(filename).set_start(0).set_duration(frontclip.duration).set_pos(("center",h2/2)) #h2+10

    final = CompositeVideoClip([final_clip, title])
    final.write_videofile(sanitize_filename(f"{text}.mp4"))

    os.remove(filename)


def video_to_tiktoks(title, path,cuttime):
    video = VideoFileClip(path)
    duration = video.duration
    n = duration/cuttime
    deb = 0
    fin = cuttime
    if cuttime > duration :
        duration = video.duration
        n = 0
        fin = duration
    listnums = [f'back_videos/{i}.mp4' for i in range(1,len(os.listdir('back_videos'))+1)]
    current = choice(listnums)
    listnums.remove(current)
    backvideo = VideoFileClip(current)
    backduration = backvideo.duration 
    while backduration != duration :
        if backduration > duration :
            backvideo = backvideo.subclip(0,duration)
        else :
            if listnums == [] :
                listnums = [f'back_videos/{i}.mp4' for i in range(1,len(os.listdir('back_videos'))+1)]
            current = choice(listnums)
            listnums.remove(current)
            backvideo = concatenate_videoclips([backvideo,VideoFileClip(current)])

        backduration = backvideo.duration


    for i in range(int(n) + 1):
        one_tiktok(f'{title} - p.{i+1}',video.subclip(deb, fin), backvideo.subclip(deb, fin))
        deb += cuttime
        fin += cuttime
        if fin > duration :
            fin = duration


class Button(ctk.CTkButton):
    def __init__(self,master,text: str,command, side: str = tk.TOP, taille=18):
        super().__init__(master=master, text=text, command=command,font=('Arial', taille))
        self.pack(side=side, padx=5,pady=10,) #pack avec 10 de marge y et 20 de marge x

class ButtonPlage(ctk.CTkFrame) :
    def __init__(self,master,num: int, listtexts, listcmd):
        super().__init__(master, fg_color="transparent")
        self.l = []
        for i in range(num): #pour chaque element de la liste creer des bouttons a gauche de frame
            x = Button(self,text=listtexts[i],command=listcmd[i], side=tk.LEFT)
            self.l.append(x)
        self.pack()

class Text(ctk.CTkLabel):
    def __init__(self, master, text: str, taille=18):
        self.text_var = tk.StringVar(value=text)
        super().__init__(master,textvariable= self.text_var,font=('Arial', taille))
        self.pack(padx=20,pady=10)

class Champs(ctk.CTkEntry):
    def __init__(self, master):
        super().__init__(master, width= 350)
        self.pack()


def fromytb(win, link, title):
        win.quit()
        link = "".join([c for c in link if c != ' '])
        try: 
            yt = YouTube(link) 
        except: 
            showerror('Link Error', 'Link Error : Erreur de lien')

        try : 
            videoset = yt.streams.filter(file_extension='mp4',progressive=True).order_by('resolution').desc()
            fname = f"temp_video_{id(yt)}.mp4"
            if title == "" :
                title = yt.streams[0].title
            videoset.get_by_resolution("720p").download('youtube_videos',filename=fname)
        except:
            showerror('Youtube Error', 'Youtube Error : Erreur Youtube')
        
        try : video_to_tiktoks(title, f"youtube_videos/{fname}", 30)
        except: showerror('Error', 'Video Error : Erreur Video')

        try : os.remove(f"youtube_videos/{fname}")
        except: pass



def fromfile(win, title):
        win.quit()
        filetypes = (('mp4 files', '*.mp4'),)
        name = fd.askopenfilename(title='Choisir une video',filetypes=filetypes,defaultextension="*.mp4")
        if name == '':
            return
        try : video_to_tiktoks(title, name, 30)
        except: showerror('Error', 'Video Error : Erreur Video')
        

class Window(ctk.CTk):
    def __init__(self):
        """ fenètre de base de l'application """
        super().__init__()
        self.geometry('1000x300')
        self.title('Video to Tiktok') 
        self.wm_title("Video to Tiktok") 
        try:
            self.iconbitmap('ressources\\icone.ico')
        except:
            pass
        label2 = Text(self, 'Video to Tiktok', 30)
        label = Text(self, 'Lien youtube :')
        self.entry = Champs(self)
        label = Text(self, 'Titre a afficher : (automatique si vide)')
        self.entry2 = Champs(self)
        self.btn = ButtonPlage(self, 2, ['Choisir un fichier', 'Utiliser le lien youtube'], [lambda: fromfile(self,self.entry2.get()), lambda: fromytb(self,self.entry.get(),self.entry2.get())])

        
    


if __name__=='__main__':
    win = Window()
    win.mainloop()


