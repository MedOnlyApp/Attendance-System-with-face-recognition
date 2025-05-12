from customtkinter import CTk, CTkFrame, CTkButton, CTkLabel, CTkComboBox, CTkToplevel, CTkEntry
from tkinter import Scrollbar, StringVar, E, W, CENTER, Y, RIGHT, filedialog, messagebox
from tkinter.ttk import Treeview, Style
from face_recognition import face_locations, face_encodings, compare_faces, load_image_file, face_distance
import cv2
import os, shutil
import re
import database as db
from PIL import Image, ImageTk
import faiss
import numpy as np
# import time
from time import time
import csv

# tk.Frame().place()

class App:
    def __init__(self):
        self.root = CTk()
        self.root.title("Face Recognition")
        self.root.geometry("800x600")

        if 'database.db' not in os.listdir():
            db.database.create_tables()
        # self.root.resizable(True, True)

    def add_side_image(self):
        image = ImageTk.PhotoImage(Image.open("Resources/main1.png"))
        self.image_label = CTkLabel(self.root, text="", image=image, corner_radius=50)
        self.image_label.image = image
        self.image_label.place(relx=0.5, rely=0.5, anchor=E)

        return

    def main_page(self):
        self.add_side_image()

        self.main_frame = CTkFrame(self.root, width=400, height=300, corner_radius=10, border_width=5, border_color="#7a6b68")
        self.main_frame.place(relx=0.5, rely=0.5, anchor=W)
        # self.main_frame.pack(padx=20, pady=20, anchor="center")

        label = CTkLabel(self.main_frame, text="Attendance System", font=("Segoe UI bold", 30), text_color="white")
        label.place(x=70, y=40)

        add_class_button = CTkButton(self.main_frame, text="Add Class", width=200, height=50, font=("Segoe UI", 17), command=self.add_class_page)
        add_class_button.place(x=105, y=110)
        # add_class_button.grid(column=0, row=0)

        mark_absence_button = CTkButton(self.main_frame, text="Mark Absence", width=200, height=50, font=("Segoe UI", 17), command=self.select_class_page)
        mark_absence_button.place(x=105, y=175)
        # mark_absence_button.grid(column=1, row=0)

        return
    
    def return_to_main(self):
        try:
            self.add_class_frame.destroy()
        except:
            pass
        
        try:
            self.absence_frame.destroy()
        except:
            pass

        try:
            self.select_class_frame.destroy()
        except:
            pass

        self.image_label.destroy()
        self.main_page()
        return
    
    def select_class_page(self):
        classes = db.database.fetch_classes()
        self.main_frame.destroy()

        self.select_class_frame = CTkFrame(self.root, width=400, height=300, corner_radius=10, border_width=5, border_color="#7a6b68")
        self.select_class_frame.place(relx=0.5, rely=0.5, anchor=W)

        label = CTkLabel(self.select_class_frame, text="Select Class:", font=("Segoe UI bold", 20))
        label.place(x=20, y=105)

        self.classes_combobox = CTkComboBox(self.select_class_frame, values=[classe for id, classe, nbr in classes], width=200, height=40, font=("Segoe UI", 17), state="readonly")
        self.classes_combobox.place(x=170, y=100)

        cancel_button = CTkButton(self.select_class_frame, text="Cancel", width=150, height=40, font=("Segoe UI", 17), command=self.return_to_main)
        cancel_button.place(x=40, y=200)

        button = CTkButton(self.select_class_frame, text="Select", width=150, height=40, font=("Segoe UI", 17), command=lambda: self.mark_absence_page(self.classes_combobox.get()))
        button.place(x=210, y=200)

        return
    
    def mark_absence_page(self, class_name:str):
        if len(db.database.fetch_classes()) == 0:
            messagebox.showerror("Error", "No classes available, Add a class first")
            return
        elif class_name == "":
            messagebox.showerror("Error", "Select a class first")
            return
        
        self.student_list = db.database.fetch_students(self.classes_combobox.get())
        self.select_class_frame.destroy()
        self.image_label.destroy()

        self.absence_frame = CTkFrame(self.root, width=700, height=600, corner_radius=10, border_width=5, border_color="#7a6b68")
        self.absence_frame.place(relx=0.5, rely=0.5, anchor=CENTER)

        treeview_frame = CTkFrame(self.absence_frame)
        treeview_frame.place(relx=0.5, rely=0.5, y=-80, anchor=CENTER)

        style = Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        # background="silver",
                        forground="white",
                        rowheight=30,
                        fieldbackground="silver"
                        )
        style.map('Treeview', background=[('selected', 'blue')])

        tree_view_scroll_bar = Scrollbar(treeview_frame)
        tree_view_scroll_bar.pack(side=RIGHT, fill=Y)

        self.tree_view = Treeview(treeview_frame, yscrollcommand=tree_view_scroll_bar.set, height=15)
        self.tree_view.pack(expand=0)

        self.tree_view.tag_configure("oddrow", background="white", font=("Segoe UI", 12))
        self.tree_view.tag_configure("evenrow", background="lightblue", font=("Segoe UI", 12))

        ## Configure the columns
        self.tree_view['columns'] = ("#1", "#2")
        self.tree_view.column("#0", anchor=W, width=40, minwidth=40)
        self.tree_view.column("#1", anchor=W, width=400, minwidth=400)
        self.tree_view.column("#2", anchor=W, width=300, minwidth=300)

        ## Name the colomns
        self.tree_view.heading("#0", text="", anchor=W)
        self.tree_view.heading("#1", text='Student Name', anchor=W)
        self.tree_view.heading("#2", text="Attendence", anchor=W)

        for row_iid, student in enumerate(self.student_list, start=1):
            if row_iid % 2 == 0:
                self.tree_view.insert(parent='', index='end', iid=row_iid, values=(student[2].title(), "Absent"), tags=("evenrow",))
            else:
                self.tree_view.insert(parent='', index='end', iid=row_iid, values=(student[2].title(), "Absent"), tags=("oddrow",))

        button = CTkButton(self.absence_frame, text="Mark Attendance", width=200, height=40, font=("Segoe UI", 17), command=lambda: self.start_camera(class_name))
        button.place(x=140, y=420)

        edit_button = CTkButton(self.absence_frame, text="Edit", width=200, height=40, font=("Segoe UI", 17), command=self.Edit_record)
        edit_button.place(x=360, y=420)

        delete_button = CTkButton(self.absence_frame, text="Delete", width=200, height=40, font=("Segoe UI", 17), command=lambda: self.Delete_record(class_name))
        delete_button.place(x=140, y=470)

        export_to_csv_button = CTkButton(self.absence_frame, text="Export (csv)", width=200, height=40, font=("Segoe UI", 17), command=self.Export_to_CSV)
        export_to_csv_button.place(x=360, y=470)

        filter_button = CTkButton(self.absence_frame, text="Cancel", width=420, height=40, font=("Segoe UI", 17), command=self.return_to_main)
        filter_button.place(x=140, y=520)


        self.load_vectors(class_name)
        return
    
    def Edit_record(self):
        selected_item = self.tree_view.selection()
        if len(selected_item) != 1:
            messagebox.showerror("Error", "Please select one student to edit")
            return
        values = self.tree_view.item(selected_item, 'values')

        edit_action_window = CTkToplevel(self.root)
        edit_action_window.title("Edit Record")
        edit_action_window.geometry("400x185")
        edit_action_window.resizable(False, False)
        edit_action_window.attributes('-toolwindow' , 1)
        edit_action_window.grab_set()
        edit_action_window.attributes('-topmost' , 1)
        edit_action_window.focus_set()

        CTkLabel(edit_action_window, text="Edit the student's Attendance.").place(x=10,y=10)
        CTkLabel(edit_action_window, text="Student Name:").place(x=10,y=50)
        
        Label_var = StringVar()
        Label_var.set(values[0])
        CTkEntry(edit_action_window, textvariable=Label_var, state='readonly').place(x=10,y=90)

        CTkLabel(edit_action_window, text="Attendance:").place(x=200,y=50)
        
        attendance_combobox = CTkComboBox(edit_action_window, values=["Present", "Absent"], state='readonly')
        attendance_combobox.place(x=200,y=90)

        edit_button = CTkButton(edit_action_window, text="Edit", width=100, height=28, font=("Segoe UI", 17), command=lambda: self.edit_cammand(edit_action_window, selected_item[0], values[0], attendance_combobox.get()))
        edit_button.place(x=280, y=140)

        cancel_button = CTkButton(edit_action_window, text="Cancel", width=100, height=28, font=("Segoe UI", 17), command=edit_action_window.destroy)
        cancel_button.place(x=160, y=140)


        return

    def edit_cammand(self, window:CTkToplevel, row_iid, student_name:str, attendance:str):
        ## Destroy the window
        window.destroy()

        self.update_treeview_record(row_iid, student_name, attendance)
        return

    def Delete_record(self, class_name:str):
        selected_item = self.tree_view.selection()
        if len(selected_item) != 1:
            messagebox.showerror("Error", "Please select one student to delete.")
            return
        values = self.tree_view.item(selected_item, 'values')

        delete_messagebox = messagebox.askokcancel(title='Delete Student', message=f'This Student will be deleted from this class, Do you want to continue?')

        if delete_messagebox == True:
            self.tree_view.delete(selected_item)
            # db.database.delete_student(class_name, values[0].lower())

        # for i, x in enumerate(self.student_list):
        #     if x[-1] == values[0].lower():
        #         self.student_list.pop(i)
        #         break

        # self.delete_vector(class_name, i)

        return

    def update_treeview_record(self, row_iid, student_name, atendence):
        values = self.tree_view.item(row_iid, values=(student_name.title(), atendence))
        return

    def face_detected(self, image):
        # image = load_image_file(image_path)
        faces_locations = face_locations(image)
        if len(faces_locations) == 0:
            return False, None
        face_encoding = face_encodings(image, faces_locations)
        return True, face_encoding

    def find_student_image(self, class_name:str, student_name:str):
        filepath = f'databases/{class_name}'

        for file in os.listdir(filepath):
            if file.startswith(student_name):
                return filepath + '/' + file
        return

    def start_camera(self, class_name:str):

        # Capture frames
        cap=cv2.VideoCapture(0)
        cap.set(3,640)
        cap.set(4,480)

        # Load background and mode images
        imgBackground = cv2.imread('Resources/background.png')
        folderModesPath = "Resources/Modes"
        imgModes = [cv2.imread(os.path.join(folderModesPath, img)) for img in os.listdir(folderModesPath)]


        detected = False
        while True:
            success, img = cap.read()

            # resize the image :
            imgS = cv2.resize(img,(0,0),None,0.25,0.25)
            imgS= cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)


            if detected == False:
                detected, face_vector = self.face_detected(imgS)
                if detected == True:
                    student_nbr = self.compare_faces(face_vector)
                    if student_nbr != -1:
                        # print(self.student_list)
                        # print(student_nbr)
                        image_path = self.find_student_image(class_name, self.student_list[student_nbr-1][-1])
                        face_image = cv2.imread(image_path)
                        face_image = cv2.resize(face_image,(216,216))

                        mode_copy = imgModes[1]

                        ph, pw = mode_copy.shape[:2]
                        ch, cw = face_image.shape[:2]

                        start_y = (ph - ch) // 2 - 78
                        start_x = (pw - cw) // 2

                        # Insert child into parent
                        mode_copy[start_y:start_y+ch, start_x:start_x+cw] = face_image

                        # print(mode_copy.shape)
                        # print(face_image.shape)
                        # mode_copy[20:20 + 500, 20:20 + 540] = face_image
                        timeout = time() + 5
                        while time() < timeout:
                            success, img = cap.read()
                            
                            imgBackground[162:162 + 480, 55:55 + 640] = img
                            # imgBackground[175:175 + 216, 909:909 + 216] = img
                            
                            cv2.putText(mode_copy, self.student_list[student_nbr-1][-1], (200, 448), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (135, 244, 109), 1)
                            cv2.putText(mode_copy, class_name, (200, 505), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (135, 244, 109), 1)
                            imgBackground[44:44+633,808:808+414] = mode_copy
                            cv2.imshow('Mark Absence', imgBackground)

                            if cv2.waitKey(1) == ord('q'):
                                break
                            if cv2.getWindowProperty('Mark Absence',cv2.WND_PROP_VISIBLE) < 1:
                                break
                        
                        try:
                            if self.tree_view.item(student_nbr, 'values')[1] == 'Absent':
                                self.update_treeview_record(student_nbr, self.student_list[student_nbr-1][-1], "Present")
                                marked = False
                            else:
                                marked = True
                        except:
                            break
                        # print(self.student_list[student_nbr-1])

                        timeout = time() + 3
                        while time() < timeout:
                            success, img = cap.read()
                            
                            imgBackground[162:162 + 480, 55:55 + 640] = img
                            if marked == True:
                                mode_copy = imgModes[3]
                            else:
                                mode_copy = imgModes[2]
                            imgBackground[44:44+633,808:808+414] = mode_copy
                            cv2.imshow('Mark Absence', imgBackground)

                            if cv2.waitKey(1) == ord('q'):
                                break
                            if cv2.getWindowProperty('Mark Absence',cv2.WND_PROP_VISIBLE) < 1:
                                break


                    else:
                        message = messagebox.showinfo("Info", "This student is not in this class")
                    break
            # put the frame in the background
            imgBackground[162:162 + 480, 55:55 + 640] = img
            # imgBackground = img
            imgBackground[44:44+633,808:808+414] = imgModes[0]

            cv2.imshow('Mark Absence', imgBackground)
            if cv2.waitKey(1) == ord('q'):
                break
            if cv2.getWindowProperty('Mark Absence',cv2.WND_PROP_VISIBLE) < 1:        
                break

        cv2.destroyAllWindows()
        # print(face_vector)



        return
    
    def add_class_page(self):
        self.main_frame.destroy()

        self.add_class_frame = CTkFrame(self.root, width=400, height=600, corner_radius=10, border_width=5, border_color="#7a6b68")
        self.add_class_frame.place(relx=0.5, rely=0.5, anchor=W)


        class_name_label = CTkLabel(self.add_class_frame, text="Class Name:", font=("Segoe UI bold", 30))
        class_name_label.place(x=120, y=40)

        self.class_name_var = StringVar()
        class_name_Entry = CTkEntry(self.add_class_frame, width=270, height=50, font=("Segoe UI", 25), textvariable=self.class_name_var)
        class_name_Entry.place(x=70, y=95)
        
        label = CTkLabel(self.add_class_frame, text="Upload Student pictures labeled with\n their name like: 'first_name last_name'", font=("Segoe UI bold", 20))
        label.place(x=20, y=210)

        add_students_button = CTkButton(self.add_class_frame, text="Add Students", width=200, height=50, font=("Segoe UI", 17), command=self.upload_Students_pictures)
        add_students_button.place(x=100, y=295)

        self.student_nbr_uploaded_label = CTkLabel(self.add_class_frame, font=("Segoe UI bold", 20))

        upload_students_button = CTkButton(self.add_class_frame, text="Done", width=150, height=40, font=("Segoe UI", 17), command=lambda:self.add_class_to_database(self.class_name_var.get()))
        upload_students_button.place(x=210, y=500)

        cancel_button = CTkButton(self.add_class_frame, text="Cancel", width=150, height=40, font=("Segoe UI", 17), command=self.return_to_main)
        cancel_button.place(x=40, y=500)

        return
    
    def upload_Students_pictures(self):
        self.files_path = filedialog.askopenfilenames(initialdir=os.getcwd(),
                                    defaultextension='*',
                                    filetypes=[
                                        ("All Images", "*.png;*.jpg;*.jpeg"),
                                        ("PNG", "*.png"),
                                        ("JPG", "*.jpg"),
                                        ("JPEG", "*.jpeg")
                                    ])
        
        # print(self.files_path)


        self.student_nbr_uploaded_label.configure(text=f"{len(self.files_path)} Students uploaded")
        self.student_nbr_uploaded_label.place(x=100, y=360)

        return
    
    def upload_Students_pictures_to_database(self, class_name:str, exist:bool):
        destination_path = f'databases/{class_name}'
        if exist == 0:
            os.makedirs(destination_path)

        for img in self.newfile_paths:
            shutil.copy(img, destination_path+f"/{self.preprocess_name(img[img.rfind('/')+1:img.rfind('.')])}.{img[img.rfind('.')+1:]}")
            # os.popen(f'copy {img} images/{self.preprocess_name(img[img.rfind('/')+1:img.rfind('.')])}.{img[img.rfind('.'):]}')
        
        return
    
    def add_class_to_database(self, class_name:str):
        exist = 0
        if self.class_name_var.get() == "":
            messagebox.showwarning("Warning", "Enter a class name")
            return
        
        elif db.database.check_classe_name(class_name) == True:
            responce = messagebox.askyesno("Classe Name", "Classe Name already exists, do to add students to it ?")
            if responce == False:
                self.class_name_var.set("")
                return
            else:
                exist = 1

        try:
            if self.files_path == None or len(self.files_path) == 0:
                messagebox.showwarning("Warning", "Upload students pictures first")
                return
        except AttributeError:
                messagebox.showwarning("Warning", "Upload students pictures first")
                return
        
        student_names = self.encode_images(class_name, self.files_path)
        self.upload_Students_pictures_to_database(class_name, exist)
        self.store_vectors(class_name, exist)

        if exist == 0:
            db.database.add_class(class_name, len(student_names), student_names)
        elif exist == 1:
            db.database.add_students_to_class(class_name, len(student_names), student_names)

        self.return_to_main()
        return

    def encode_images(self, class_name:str, files_paths:tuple):
        self.encoded_images = []
        student_names = []
        self.newfile_paths = []
        for file_path in files_paths:
            name = self.preprocess_name(file_path[file_path.rfind('/')+1:file_path.rfind('.')])
            image = load_image_file(file_path)
            try:
                self.encoded_images.append(face_encodings(image)[0])
                student_names.append(name)
                self.newfile_paths.append(file_path)
            except:
                pass

        # print(*self.encoded_images, sep='\n====================')
        return student_names
    
    def store_vectors(self, class_name:str, exist:bool):
        if exist == 0:
            index = faiss.IndexFlatL2(128)
        elif exist == 1:
            index = faiss.read_index(f"databases/{class_name}.faiss")

        liste = []
        for vector in self.encoded_images:
            liste.append(np.array(vector, dtype="float32"))
        face_vectors = np.stack(liste)
        # ids = np.array([x for x in range(db.database.get_last_student_id()+1, len(self.encoded_images)+1)], dtype='int64')
        # index.add_with_ids(face_vectors, ids)
        index.add(face_vectors)
        faiss.write_index(index, f"databases/{class_name}.faiss")

        return
    
    def load_vectors(self, class_name:str):
        index = faiss.read_index(f"databases/{class_name}.faiss")

        vectors = index.reconstruct_n(0, index.ntotal)  # returns a list of vectors as a NumPy array
        # print(vectors)
        # Convert to list of lists (optional)
        self.vectors_list = vectors.tolist()

        # print(*self.vectors_list, sep='\n=====================')
        return

    def compare_faces(self, face_vector): 
        # print(len(self.vectors_list))
        # for i, vector in enumerate(self.vectors_list, start=1):
        #     results = compare_faces([np.array(vector, dtype="float32")], np.array(face_vector, dtype="float32"))
        #     # print("=====================================")
        #     # print(results)
        #     if results[0] == True:
        #         return i
        encodings = np.array([np.array(vector, dtype="float32") for vector in self.vectors_list])

        distances = face_distance(encodings, np.array(face_vector, dtype="float32"))

        # Find the index of the smallest distance
        best_match_index = np.argmin(distances)

        print(distances)
        threshold = 0.5
        if distances[best_match_index] < threshold:
            print(f"Best match found at index {best_match_index} with distance {distances[best_match_index]}")
            return best_match_index + 1
        else:
            print("No good match found.")
            return -1
    
    def preprocess_name(self, name:str):
        pattern = r"[\W_0-9]"
        # re.sub(pattern=pattern, repl=' ', string=name)
        name = re.sub(pattern=pattern, repl=' ', string=name).lower()
        name = re.sub(pattern=r"  ", repl=' ', string=name)
        
        return name if name[-1] != ' ' else name[:-1]

    def Export_to_CSV(self):  ## Export to CSV
        row_list = self.tree_view.get_children()     ## Get the idexes of the rows in the treeview
        if len(row_list) == 0:
            return
        
        file = filedialog.asksaveasfile(initialdir="",
                                        defaultextension='.csv',
                                        filetypes=[
                                            ("CSV file",".csv"),
                                            ("All files", ".*"),
                                        ])
        if file is None:
            return

        column_names = ["Student Name",'Presence']
        writer = csv.DictWriter(file, fieldnames=column_names)
        writer.writeheader()

        for i in range(len(row_list)):
            values = self.tree_view.item(row_list[i], 'values')
            writer.writerow({"Student Name": values[0], "Presence": values[1] if values[1] != "" else "A"})
            
        file.close()

        return



    def launch_app(self):
        self.main_page()
        self.root.mainloop()

        return




if __name__ == "__main__":
    app = App()
    app.launch_app()