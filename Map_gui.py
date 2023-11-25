import time
import tkinter as tk
from Map import Node, Road, Car, Map
import threading
from plan import get_plan, get_from_spark
import sys
import os
import random

root = tk.Tk()
width = 1000
height = 700
canvas = tk.Canvas(root, width=width, height=height)
canvas.pack()
current_node = None
current_map = None
current_car = None
all_x, all_y = 0, 0
search_window = None
mode = sys.argv[1]
current_file = None
path_strategies = 'distance'
running_flag = True


def clear_map():
    global current_map
    global current_node
    global current_car
    global search_window
    global current_file
    set_original_view()
    current_node = None
    current_map = None
    current_car = None
    search_window = None
    current_file = None
    canvas.delete("all")


def set_original_view():
    global all_x, all_y
    canvas.move('all', -all_x, -all_y)
    all_x, all_y = 0, 0


def draw_node(node):
    x = node.x
    y = node.y
    if not node.invisible:
        canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='grey', tags=node.name)
        canvas.create_text(x, y + 7, text=node.name, tags=node.name)


def draw_road(road, move_x=0, move_y=0):
    x1, y1 = road.start.x + move_x, road.start.y + move_y
    x2, y2 = road.end.x + move_x, road.end.y + move_y
    if road.is_accident:
        canvas.create_line(x1, y1, x2, y2, width=2, fill='red')
    elif road.is_narrow:
        canvas.create_line(x1, y1, x2, y2, width=2, fill='brown')
        canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text='narrow', fill='brown', tags=road.name)
    elif road.highway:
        canvas.create_line(x1, y1, x2, y2, width=2, fill='green')
    else:
        canvas.create_line(x1, y1, x2, y2, width=2, fill='blue')


def draw_car(car, tag="car"):
    canvas.delete(tag)  # 清除之前的小车
    canvas.create_oval(car.x - 5 + all_x, car.y - 5 + all_y, car.x + 5 + all_x, car.y + 5 + all_y, fill="orange",
                       tags=tag)


def move_car(car, city_now, city_next, tag="car"):
    length = int(city_now.distant(city_next))
    road = city_now.go_city(city_next)
    if road.add_car(car):
        draw_road(road, all_x, all_y)
    if road.is_narrow:
        step = 2
    elif road.highway:
        step = 5
    else:
        step = 3
    for i in range(int(length / step)):
        car.x = city_now.x + (city_next.x - city_now.x) * step * i / length
        car.y = city_now.y + (city_next.y - city_now.y) * step * i / length
        draw_car(car, tag)
        time.sleep(0.05)

    car.x = city_next.x
    car.y = city_next.y
    if road.exit_car(car):
        canvas.delete(road.name)
        draw_road(road, all_x, all_y)
    car.position = city_next
    draw_car(car, tag)
    return city_next


def move_car_async(car, city_now, city_next, tag="car"):
    move_thread = threading.Thread(target=move_car, args=(car, city_now, city_next, tag))
    move_thread.start()


def move_by_path(car):
    global current_node
    draw_car(car)
    city_now = car.path[0]
    car.path = car.path[1:]
    if len(car.path) == 0:
        current_node = city_now
        return
    if path_strategies == 'time' and city_now.go_city(car.path[0]).is_narrow:
        got_city(city_now, car.path[-1])
        car.path = car.path[1:]
    city_next = car.path[0]
    if city_now.go_city(city_next) is None:
        return
    else:
        move_car(car, city_now, city_next)
        move_by_path(car)


def move_by_path_async(car):
    move_thread = threading.Thread(target=move_by_path, args=(car,))
    move_thread.start()


def implement_map(self):
    for node in self.node:
        draw_node(node)
    for road in self.road:
        draw_road(road)


def get_current_node(node):
    global current_map
    global current_node
    global current_car
    global search_window
    if current_node is not None:
        return
    current_node = node
    current_car = Car("car", current_node, 60)
    draw_car(current_car)
    search_window.destroy()
    get_ready(mode)


def on_left_click_up(event):
    global current_map
    if current_map is None:
        return
    for node in current_map.node:
        if abs(node.x - event.x + all_x) < 5 and abs(node.y - event.y + all_y) < 5:
            get_current_node(node)


canvas.bind("<Button-1>", on_left_click_up)


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


def choose_map(file, window=None):
    global current_map
    clear_map()
    set_background(file)
    current_map = Map()
    current_map.load_map(file + '.txt')
    implement_map(current_map)
    if window is not None:
        window.destroy()
        search_menu()
    return True


# pop a window to choose map
def choose_window():
    choice_window = tk.Toplevel(root)
    choice_window.title('选择地图')
    tk.Label(choice_window, text='选择地图文件').pack()
    files = os.listdir('Map')
    for afile in files:
        if 'txt' in afile:
            tk.Button(choice_window, text=afile[:-4],
                      command=lambda file=afile: choose_map('Map/' + file[:-4], choice_window)).pack()


def combined_function(del_window):
    del_window.destroy()
    choose_window()


def choose_button(window):
    tk.Button(window, text='choose map', command=lambda: combined_function(window)).pack()


def search_menu():
    global current_node
    global current_car
    global current_map
    global search_window

    def filter_list():
        global current_map
        filtered_list = [item for item in current_map.search_city(entry.get())]  # 根据搜索规则过滤列表
        listbox.delete(0, tk.END)  # 清空列表框中的内容
        for item in filtered_list:
            listbox.insert(tk.END, item)

    def got_city():
        global current_node
        global current_map
        global current_car
        if listbox.get(listbox.curselection()) == '':
            return
        city = listbox.get(listbox.curselection())
        the_node = current_map.get_node(city)
        get_current_node(the_node)
        set_view_to_center(the_node.x, the_node.y)

    search_window = tk.Tk()
    search_window.title('choose start city')
    choose_button(search_window)
    entry = tk.Entry(search_window, width=30)
    entry.pack(pady=10)  # 设置垂直间距
    entry.bind("<KeyRelease>", lambda event: filter_list())
    tk.Button(search_window, text='ok', command=lambda: got_city()).pack()
    listbox = tk.Listbox(search_window, width=40)
    listbox.pack()
    for city in current_map.search_city():
        listbox.insert(tk.END, city)


def destination_menu():
    global current_node
    global current_car
    global current_map
    global search_window

    def filter_list():
        global current_map
        filtered_list = [item for item in current_map.search_city(entry.get())]  # 根据搜索规则过滤列表
        listbox.delete(0, tk.END)  # 清空列表框中的内容
        for item in filtered_list:
            listbox.insert(tk.END, item)

    def got_path():
        global current_node
        global current_map
        global current_car
        if listbox.curselection():
            city = listbox.get(listbox.curselection())
            if city == current_node.name:
                canvas.delete("highlight")
                return
            got_city(current_node, current_map.get_node(city))
            move_by_path_async(current_car)
        else:
            return

    search_window = tk.Tk()
    search_window.title('choose destination city')
    entry = tk.Entry(search_window, width=30)
    entry.pack(pady=10)  # 设置垂直间距
    entry.bind("<KeyRelease>", lambda event: filter_list())
    tk.Button(search_window, text='ok', command=lambda: got_path()).pack()
    listbox = tk.Listbox(search_window, width=40)
    listbox.pack()
    for city in current_map.search_city():
        listbox.insert(tk.END, city)


def get_user_prompt():
    user_prompt = input("user prompt:")
    return user_prompt


def NPC_car(tag):
    available_cities = []
    for city in current_map.node:
        if not city.invisible and len(city.road) != 0:
            available_cities.append(city)
    node = available_cities[random.randint(0, len(available_cities) - 1)]
    npc_car = Car(tag, node, 60)
    while running_flag:
        npc_car.move_randomly()
        move_car(npc_car, npc_car.path[0], npc_car.path[1], tag)
    canvas.delete(tag)


def NPC_car_async(tag):
    move_thread = threading.Thread(target=NPC_car, args=(tag,))
    move_thread.start()


def model_action(prompt):
    global current_map
    global current_node
    global current_car
    canvas.delete("highlight")
    available_cities = current_map.list_cities().copy()
    available_cities.remove(current_node.name)
    plan = get_from_spark(available_cities, prompt)
    path = current_map.get_path(current_node.name, plan)
    highlight(path)
    current_car.add_path(path)
    move_by_path_async(current_car)


def get_ready(mode='auto'):
    global current_map
    global current_node
    global current_car
    if mode == 'auto':
        prompt_window = tk.Tk()
        prompt_window.title('互动式导航')
        tk.Label(prompt_window, text='输入你的想法:').pack()
        prompt = tk.Entry(prompt_window, width=40)
        prompt.pack(pady=20)  # 设置垂直间距
        tk.Button(prompt_window, text='发送', command=lambda: model_action(prompt.get())).pack()
    else:
        destination_menu()


def highlight(path):
    node = path[0]
    canvas.create_oval(node.x - 5 + all_x, node.y - 5 + all_y, node.x + 5 + all_x, node.y + 5 + all_y, fill='red',
                       tags="highlight")
    road = node.go_city(path[1])
    canvas.create_line(road.start.x + all_x, road.start.y + all_y, road.end.x + all_x, road.end.y + all_y, width=2,
                       fill='red', tags="highlight")
    if len(path) <= 2:
        node = path[1]
        canvas.create_oval(node.x - 5 + all_x, node.y - 5 + all_y, node.x + 5 + all_x, node.y + 5 + all_y, fill='red',
                           tags="highlight")
        return
    highlight(path[1:])


def set_view_to_center(x, y):
    global all_x, all_y
    former_x, former_y = all_x, all_y
    all_x = -x + width / 2
    all_y = -y + height / 2
    canvas.move('all', all_x - former_x, all_y - former_y)


def change_strategy(strategy):
    global path_strategies
    path_strategies = strategy
    if strategy == 'distance':
        strategy_label.config(text='策略:距离最短')
    elif strategy == 'price':
        strategy_label.config(text='策略:价格最低')
    elif strategy == 'time':
        strategy_label.config(text='策略:耗时最少')


def narrow_road():
    canvas.delete('all')
    set_original_view()
    current_map.random_narrow()
    implement_map(current_map)
    if current_car is not None and len(current_car.path) >= 2:
        highlight(current_car.path)


def narrow_reset():
    canvas.delete('all')
    set_original_view()
    for road in current_map.road:
        road.is_narrow = False
    implement_map(current_map)
    if current_car is not None and len(current_car.path) >= 2:
        highlight(current_car.path)


def random_name():
    return ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 4))


def NPC_button():
    name = random_name()
    NPC_car_async(name)


def destroy_NPC():
    global running_flag
    if running_flag:
        running_flag = False
    else:
        running_flag = True


def got_city(city_now, city_final):
    global current_map
    global current_car
    current_car.path = current_map.get_path(city_now.name, [city_final.name], path_strategies)
    canvas.delete("highlight")
    highlight(current_car.path)


def set_background(image_file):
    file = image_file + ".png"
    background_image = tk.PhotoImage(file=file)
    canvas.create_image(0, 0, anchor=tk.NW, image=background_image)
    canvas.image = background_image


distance_button = tk.Button(root, text='距离最短', command=lambda: change_strategy('distance'), bg='pink')
distance_button.place(x=20, y=20)
price_button = tk.Button(root, text='价格最低', command=lambda: change_strategy('price'), bg='lightblue')
price_button.place(x=20, y=50)
time_button = tk.Button(root, text='耗时最少', command=lambda: change_strategy('time'), bg='lightgreen')
time_button.place(x=20, y=80)
strategy_label = tk.Label(root, text='策略:距离最短')
strategy_label.place(x=20, y=110)
npc_button = tk.Button(root, text='NPC', command=lambda: NPC_button())
npc_button.place(x=20, y=350)
stop_button = tk.Button(root, text='停止/开始NPC', command=lambda: destroy_NPC())
stop_button.place(x=20, y=400)

choose_window()

root.config(bg='lightyellow')
root.mainloop()
