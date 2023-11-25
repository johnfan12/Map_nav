from Map import Map, Node, Road, Highway, InvisibleCity
import tkinter as tk
import os
import random
from PIL import ImageGrab

root = tk.Tk()
canvas = tk.Canvas(root, width=1200, height=700)
canvas.pack()
current_map = None
current_file = None
all_x, all_y = 0, 0
mode = 0
start = None
end = None


def draw_node(node):
    x = node.x
    y = node.y
    if not node.invisible:
        canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='grey', tags=node.name)
        canvas.create_text(x, y + 7, text=node.name, tags=node.name)
    else:
        canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='orange', tags=node.name)


def remove_node(tag):
    canvas.delete(tag)


def draw_road(road):
    x1, y1 = road.start.x, road.start.y
    x2, y2 = road.end.x, road.end.y
    if road.is_accident:
        canvas.create_line(x1 + all_x, y1 + all_y, x2 + all_x, y2 + all_y, width=2, fill='red', dash=(4, 4),
                           tags=road.name)
    elif road.is_narrow:
        canvas.create_line(x1 + all_x, y1 + all_y, x2 + all_x, y2 + all_y, width=2, fill='brown', dash=(4, 4),
                           tags=road.name)
    elif road.highway:
        canvas.create_line(x1 + all_x, y1 + all_y, x2 + all_x, y2 + all_y, width=2, fill='green', tags=road.name)
    else:
        canvas.create_line(x1 + all_x, y1 + all_y, x2 + all_x, y2 + all_y, width=2, fill='blue', tags=road.name)
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    canvas.create_text(mid_x + all_x, mid_y + all_y, text=road.name, tags='road' + road.name)


def implement_map(self):
    for node in self.node:
        draw_node(node)
    for road in self.road:
        draw_road(road)


def clear_map():
    global current_map
    canvas.delete("all")
    current_map = None


def clear_node_and_road():
    global current_map
    if current_map is not None:
        for node in current_map.node:
            remove_node(node.name)
        for road in current_map.road:
            remove_node(road.name)


class Editor:
    def __init__(self, file):
        self.file = file
        self.map = Map()
        self.map.load_map(file)

    def add_city(self, name, x, y):
        with open(self.file, 'a', encoding='UTF-8') as f:
            f.write('\nn ' + name + ' ' + str(x) + ' ' + str(y))

    def add_invisible(self, name, x, y):
        with open(self.file, 'a', encoding='UTF-8') as f:
            f.write('\ni ' + str(name) + ' ' + str(x) + ' ' + str(y))

    def add_road(self, name, start, end):
        with open(self.file, 'a', encoding='UTF-8') as f:
            f.write('\nr ' + name + ' ' + start + ' ' + end)

    def add_highway(self, name, start, end):
        with open(self.file, 'a', encoding='UTF-8') as f:
            f.write('\nh ' + name + ' ' + start + ' ' + end)

    def del_city(self, name):
        with open(self.file, 'r', encoding='UTF-8') as f:
            lines = f.readlines()
        with open(self.file, 'w', encoding='UTF-8') as f:
            for line in lines:
                if (line[0] == 'n' or line[0] == 'i') and line.split(' ')[1] == name:
                    f.write('#' + line)
                    continue
                else:
                    f.write(line)

    def del_road_and_highway(self, name):
        with open(self.file, 'r', encoding='UTF-8') as f:
            lines = f.readlines()
        with open(self.file, 'w', encoding='UTF-8') as f:
            for line in lines:
                if (line[0] == 'r' or line[0] == 'h') and line.split(' ')[1] == name:
                    f.write('#' + line)
                    continue
                else:
                    f.write(line)


def set_background(image_file):
    file = image_file + ".png"
    background_image = tk.PhotoImage(file=file)
    canvas.create_image(0, 0, anchor=tk.NW, image=background_image)
    canvas.image = background_image

def choose_map(file, window=None):
    global current_map
    global current_file
    clear_map()
    set_background(file)
    current_map = Map()
    current_file = file + '.txt'
    current_map.load_map(file + '.txt')
    implement_map(current_map)
    if window is not None:
        window.destroy()
    return True


def on_key_press(event):
    global all_x, all_y
    move_x, move_y = 0, 0
    if event.keysym == "s":
        move_y -= 10
        all_y -= 10
    elif event.keysym == "w":
        move_y += 10
        all_y += 10
    elif event.keysym == "d":
        move_x -= 10
        all_x -= 10
    elif event.keysym == "a":
        move_x += 10
        all_x += 10

    canvas.move('all', move_x, move_y)


canvas.bind("<KeyPress>", on_key_press)
canvas.focus_set()


def choose_menu():
    choice_window = tk.Toplevel(root)
    choice_window.title('选择地图')
    tk.Label(choice_window, text='选择地图文件').pack()
    files = os.listdir('Map')
    for afile in files:
        if 'txt' in afile:
            tk.Button(choice_window, text=afile[:-4],
                      command=lambda file=afile: choose_map('Map/' + file[:-4], choice_window)).pack()


def change_mode(mode_number):
    global mode
    global start, end
    start, end = None, None
    canvas.delete('highlight')
    mode = mode_number
    if mode == 1:
        mode_label.config(text='mode: city')
    elif mode == 2:
        mode_label.config(text='mode: road')
    elif mode == 3:
        mode_label.config(text='mode: highway')
    elif mode == 4:
        mode_label.config(text='mode: delete')
    elif mode == 5:
        mode_label.config(text='mode: invisible')


def combined_function(del_window, editor, name, x, y):
    del_window.destroy()
    if name in current_map.list_cities():
        name = name + random_name()
    editor.add_city(name, x, y)
    current_map.add_node(Node(name, x, y))
    draw_node(Node(name, x + all_x, y + all_y))
    remove_node('temp')


def road_combined_function(del_window, editor, name):
    global start
    global end
    del_window.destroy()
    if name == '':
        name = str(start.name) + str(end.name)
    editor.add_road(name, start.name, end.name)
    draw_road(Road(name, start, end))
    remove_node('highlight')
    start = None
    end = None


def highway_combined_function(del_window, editor, name):
    global start
    global end
    del_window.destroy()
    if name == '':
        name = str(start.name) + str(end.name)
    editor.add_highway(name, start.name, end.name)
    draw_road(Highway(name, start, end))
    remove_node('highlight')
    start = None
    end = None


def put_on_map(event):
    global mode
    global current_file
    global all_x, all_y
    global start, end
    edit = Editor(current_file)
    if mode == 1:
        x = event.x
        y = event.y
        draw_node(Node('temp', x, y))
        name_window = tk.Toplevel(root)
        name_window.title('Enter name')
        entry = tk.Entry(name_window, width=30)
        entry.pack(pady=10)  # 设置垂直间距
        tk.Button(name_window, text='add',
                  command=lambda: combined_function(name_window, edit, entry.get(), x - all_x, y - all_y)).pack()
    if mode == 2:
        if start is None:
            for node in current_map.node:
                if abs(node.x - event.x + all_x) < 10 and abs(node.y - event.y + all_y) < 10:
                    start = node
                    highlight_node(node)
                    break
        elif end is None:
            available_node = current_map.node.copy()
            available_node = [node for node in available_node if node != start]
            for node in available_node:
                if abs(node.x - event.x + all_x) < 10 and abs(node.y - event.y + all_y) < 10:
                    end = node
                    break
            if end is not None:
                name_window = tk.Toplevel(root)
                name_window.title('Enter name')
                entry = tk.Entry(name_window, width=30)
                entry.pack(pady=10)  # 设置垂直间距
                tk.Button(name_window, text='add',
                          command=lambda: road_combined_function(name_window, edit, entry.get())).pack()
        else:
            return
    if mode == 3:
        if start is None:
            for node in current_map.node:
                if abs(node.x - event.x + all_x) < 10 and abs(node.y - event.y + all_y) < 10:
                    start = node
                    highlight_node(node)
                    break
        elif end is None:
            available_node = current_map.node.copy()
            available_node = [node for node in available_node if node != start]
            for node in available_node:
                if abs(node.x - event.x + all_x) < 10 and abs(node.y - event.y + all_y) < 10:
                    end = node
                    break
            if end is not None:
                name_window = tk.Toplevel(root)
                name_window.title('Enter name')
                entry = tk.Entry(name_window, width=30)
                entry.pack(pady=10)  # 设置垂直间距
                tk.Button(name_window, text='add',
                          command=lambda: highway_combined_function(name_window, edit, entry.get())).pack()
        else:
            return
    if mode == 4:
        for node in current_map.node:
            if abs(node.x - event.x + all_x) < 10 and abs(node.y - event.y + all_y) < 10:
                edit.del_city(node.name)
                for road in node.road:
                    remove_node(road.name)
                    edit.del_road_and_highway(road.name)
                remove_node(node.name)
                break
    if mode == 5:
        x = event.x - all_x
        y = event.y - all_y
        draw_node(Node('temp', x, y))
        name = random_name()
        edit.add_invisible(name, x, y)
        current_map.add_node(InvisibleCity(name, x, y))
        draw_node(InvisibleCity(name, x + all_x, y + all_y))
        remove_node('temp')


def highlight_node(node):
    x = node.x
    y = node.y
    canvas.create_oval(x - 5 + all_x, y - 5 + all_y, x + 5 + all_x, y + 5 + all_y, fill='red', tags='highlight')


def get_refer_picture():
    background_image = tk.PhotoImage(file="Map/CN.png")
    canvas.create_image(0, 0, anchor=tk.NW, image=background_image)
    canvas.image = background_image


# def save_image():
#    ImageGrab.grab().save("canvas_image.png")

def hide_road_name():
    for road in current_map.road:
        remove_node('road' + road.name)


def random_name():
    return ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 4))


city = tk.Button(root, text='city', command=lambda: change_mode(1))
city.place(x=20, y=20)
road = tk.Button(root, text='road', command=lambda: change_mode(2))
road.place(x=20, y=50)
highway = tk.Button(root, text='highway', command=lambda: change_mode(3))
highway.place(x=20, y=80)
delete = tk.Button(root, text='delete', command=lambda: change_mode(4))
delete.place(x=20, y=110)
invisible = tk.Button(root, text='invisible', command=lambda: change_mode(5))
invisible.place(x=20, y=140)
mode_label = tk.Label(root, text='mode:')
mode_label.place(x=20, y=170)
refer_picture = tk.Button(root, text='refer picture', command=lambda: get_refer_picture())
refer_picture.place(x=20, y=200)
# save = tk.Button(root, text='save', command=lambda: save_image())
# save.place(x=20, y=230)
hide = tk.Button(root, text='hide road name', command=lambda: hide_road_name())
hide.place(x=20, y=260)
canvas.bind("<Button-1>", put_on_map)

choose_menu()
root.mainloop()
