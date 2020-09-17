# Last updated 8.31.20

import PIL.Image
import PIL.ImageTk  # will need to install image or pillow library
import os
import sys
from tkinter import Label, TOP, LEFT, Tk
from tkinter import ttk

# from tkinter import tk
from tkinter import filedialog, messagebox, Message, Toplevel, BOTTOM


class ImageOpener:
    """
    ImageOpener class.
    Container for all the GUI parts.
    """
    def __init__(self, master, *args, **kwargs):
        # set self.master to root
        self.master = master
        master.title("Basic Image Opener")
        # btn.pack()

        # settings
        master.configure(background="#73afa7")
        self.framewidth, self.frameheight = (600, 600)
        self.windowwidth, self.windowheight = (1000, 800)
        root.geometry("%dx%d" % (self.windowwidth, self.windowheight))
        self.ext = ("jpg", "png")
        self.debug = False  # kwargs.get('debug', False)
        self.permanent_delete = False
        self.show_info = False
        self.buttonWidth = 10

        # find a folder of images and generate a list of the images in them
        self.set_dir_name()
        self.generate_img_list()

        # image goes on label
        self.image_label = Label(compound=TOP, bg="#eee", borderwidth=2)
        self.image_label.pack()
        self.image_label.place(x=90, y=90)
        self.current = 0

        # ll = info, lr = page #
        self.ll = ttk.Label(self.master, text="lower left")
        self.ll.place(relx=0.0, rely=1.0, anchor="sw")
        self.lr = ttk.Label(self.master, text="lower right")
        self.lr.place(relx=1.0, rely=1.0, anchor="se")

        # nav bar goes on frame
        # , width=600, height=600, borderwidth = 1)
        self.frame = ttk.Frame(master)
        self.frame.pack()

        # generate the nav bar
        self.create_nav_bar()

        self.move(0)

    # allows you to navigate through the image list forwards or backwards
    def move(self, delta):
        # from: https://stackoverflow.com/questions/46359590/tkinter-update-image-list
        if self.debug:
            print(
                (
                    0 <= self.current + delta < len(self.sorted_imagelist),
                    self.current,
                    delta,
                    len(self.sorted_imagelist),
                )
            )
        if not (0 <= self.current + delta < len(self.sorted_imagelist)):
            #
            # top = Toplevel(root)
            # top.title('End')
            # Message(top, text='No more images.', padx=20, pady=20).pack(BOTTOM)
            # top.after(2000, top.destroy)
            # self.show_info = 'No more images.'
            # body = 'No more images'a
            if sys.platform == "darwin":
                messagebox.showerror(title="End", message="No more images.")
                # messagebox.showerror(title="Invalid Steam folder!",
                #                  message="{0} is not a valid Steam folder.".format("nuddin"))
                # os.system("osascript -e 'Tell application \"System Events\" to display dialog \""+body+"\"'")
            else:
                messagebox.showerror(title="End", message="No more images.")
                # messagebox.showinfo("End", "No more images.")
            self.master.update()
            return
        self.current += delta

        # set page number
        self.lr.configure(text=str(self.current))

        # open image and  find width+height
        image = PIL.Image.open(self.sorted_imagelist[self.current])
        width, height = image.size

        # resize image to fit in frame
        neww, newh = self.resizer(width, height, self.framewidth, self.frameheight)
        # The (250, 250) is (height, width)
        image = image.resize((neww, newh), PIL.Image.ANTIALIAS)

        # convert to photo image and set label to it
        photo = PIL.ImageTk.PhotoImage(image)
        self.image_label["image"] = photo
        self.image_label.photo = photo

        # clear (previous) image info
        self.toggle_info(False)

        # center the image
        self.image_label.pack()

    # resizes the image to fit within the framewidth
    def resizer(self, imgWidth, imgHeight, wWidth, wHeight):
        # get the ratio to find the factor
        relWidth = imgWidth / wWidth
        relHeight = imgHeight / wHeight

        newWidth, newHeight = 0, 0
        if relWidth > relHeight:
            newHeight = round(imgHeight / relWidth)
            newWidth = wWidth
        else:
            newWidth = round(imgWidth / relHeight)
            newHeight = wHeight
        if self.debug:
            print(imgWidth, imgHeight, relWidth, relHeight, newWidth, newHeight)
        return newWidth, newHeight

    def create_nav_bar(self):
        # super outside lambda: super().reload(), inside lambda: lambda:super(navigationBar, self).reload())
        buttons = [  # txt, h, w, callback
            ("Reload", self.buttonWidth, self.reload),
            ("Info", self.buttonWidth, lambda: self.toggle_info(True)),
            ("Open Containing Folder", self.buttonWidth * 1.5, self.open_current_folder),
            ("Keep", self.buttonWidth, self.keep_file),
            ("Delete", self.buttonWidth, self.delete_image),
            ("Previous", self.buttonWidth, lambda: self.move(-1)),
            ("Next", self.buttonWidth, lambda: self.move(+1)),
            ("Quit", self.buttonWidth, self.master.quit),
        ]
        # go through button list and make each button in order
        for button in buttons:
            self.create_button(*button)

    def create_button(self, txt, w, callback):
        btn = ttk.Button(self.frame, text=f"\n{txt}\n", width=w, command=callback)
        btn.pack(side=LEFT)

    # returns the filename for the current image being shown
    def get_curr_img_name(self):
        return str(self.sorted_imagelist[self.current])

    # select the folder to browse
    # this code gives an error, text input context does not correspond
    def set_dir_name(self):
        self.dir_name = filedialog.askdirectory()
        # parent=self.master, initialdir="~", title='Please select a directory')
        if len(self.dir_name) > 0:
            print("You chose %s" % self.dir_name)
        else:
            self.master.quit()

    def generate_img_list(self):
        # walk generates 3 iterables: [0] is name of folder, [1] is names of sub folder, [2] is name of files
        self.image_list = [
            os.path.join(self.dir_name, img).replace("\\", "/")
            for img in next(os.walk(self.dir_name))[2]
            if img.endswith(self.ext)
        ]
        if self.debug:
            print("imagelist:", self.image_list)

        self.sorted_imagelist = sorted(self.image_list, key=str.lower, reverse=False)
        if self.debug:
            print("sorted imagelist:", self.sorted_imagelist)

    # choose a different folder to reload into
    def reload(self):
        # hide the imageOpener
        self.master.withdraw()

        # choose a new folder and generate the appropriate image list
        self.set_dir_name()
        self.generate_img_list()

        # unhide the imageOpener
        self.master.deiconify()

        # move to the first picture of the newly loaded image list
        self.move(0)

    # moves the current image to a new folder, makes a folder if it doesn't exist
    def move_file(self, file, new_folder):
        from shutil import move

        dir_path = self.dir_name + "/" + new_folder
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        if os.path.exists(dir_path):
            move(file, dir_path)

    def delete_image(self):
        # soft delete
        file = self.get_curr_img_name()
        if not self.permanent_delete:
            self.move_file(file, "delete")
            self.sorted_imagelist.remove(file)

            if 0 <= self.current == len(self.sorted_imagelist):  # if end of list
                self.move(-1)
            else:
                self.move(0)  # update the shown image

        # real delete
        else:
            os.remove(file)

    def keep_file(self):
        file = self.get_curr_img_name()
        self.move_file(file, "keep")
        self.sorted_imagelist.remove(file)
        self.move(0)  # update the shown image

    def open_current_folder(self):
        if sys.platform == "darwin":
            os.system("open " + self.dir_name)
        else:
            os.system(f"explorer {self.dir_name}")
            # os.startfile(self.dir_name)

    # flips the show_info flag if user desires, toggles the info label on/off

    def toggle_info(self, flip):
        # flip the flag if you want it to be
        if flip:
            self.show_info = not self.show_info

        # fill = self.get_curr_img_name() if self.show_info else ""s
        if self.show_info:
            self.ll.configure(text=self.get_curr_img_name())
        else:
            self.ll.configure(text="")


if __name__ == "__main__":
    root = Tk()
    ImageOpener(root)
    root.mainloop()
