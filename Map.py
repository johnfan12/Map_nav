import random
from pypinyin import lazy_pinyin
from strategy import dijkstra, autocorrect, shifty_shifts, combine_string, get_first_pinyin


class Node:
    def __init__(self, name, x, y):
        self.name = name
        self.road = []
        self.x = x
        self.y = y
        self.invisible = False

    def distant(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def go_next(self, road):
        if road.start == self:
            return road.end
        elif road.end == self and road.isDuplex:
            return road.start
        else:
            return None

    def go_city(self, city):
        if city == self:
            return None
        for road in self.road:
            if road.start == city or road.end == city:
                return road
        return None

    def list_near_cities(self):
        cities = []
        for road in self.road:
            if road.start == self:
                cities.append(road.end)
            elif road.end == self and road.isDuplex:
                cities.append(road.start)
        return cities


class InvisibleCity(Node):
    def __init__(self, name, x, y):
        super().__init__(name, x, y)
        self.invisible = True


class Road:
    def __init__(self, name, start, end, speedlimit=60, duplex=True):
        self.name = name
        self.length = start.distant(end)
        self.start = start
        self.end = end
        self.speedLimit = speedlimit
        self.isDuplex = duplex
        self.is_accident = False
        self.is_narrow = False
        self.cost = 0.7
        self.highway = False
        self.cars = []
        start.road.append(self)
        end.road.append(self)

    def add_car(self, car):
        self.cars.append(car)
        if len(self.cars) > 1 and self.is_narrow == False:
            self.is_narrow = True
            return True
        else:
            return False

    def exit_car(self, car):
        self.cars.remove(car)
        if len(self.cars) <= 1 and self.is_narrow == True:
            self.is_narrow = False
            return True
        else:
            return False


class Highway(Road):
    def __init__(self, name, start, end, speedlimit=120, duplex=True):
        super().__init__(name, start, end, speedlimit, duplex)
        self.highway = True
        self.cost = 1.3


class Car:
    def __init__(self, name, position, target_speed):
        self.name = name
        self.position = position
        self.x = position.x
        self.y = position.y
        self.speed = 0
        self.target_speed = target_speed
        self.path = [position]
        self.rect = None
        self.location = position
        self.user = True

    def add_path(self, path):
        self.path = path

    def move_randomly(self):
        city_now = self.location
        available_city = city_now.list_near_cities()
        if len(available_city) == 1:
            next_city = available_city[0]
            self.path = [city_now, next_city]
            self.location = next_city
            return
        if not self.user:
            available_city.remove(self.path[0])
        next_city = available_city[random.randint(0, len(available_city) - 1)]
        self.location = next_city
        self.path = [city_now, next_city]
        if self.user:
            self.user = False


class Map:

    def __init__(self):
        self.node = []
        self.road = []

    def add_node(self, node):
        self.node.append(node)

    def add_road(self, road):
        self.road.append(road)

    def get_node(self, name):
        for node in self.node:
            if node.name == name:
                return node
        return None

    def load_map(self, file):  # example format: n node1 100 100 r road1 node1 node2
        with open(file, 'r', encoding='UTF-8') as f:
            for line in f.readlines():
                line = line.strip()
                if line == '' or line[0] == '#':
                    continue
                elif line[0] == 'n':
                    name, x, y = line.split(' ')[1:]
                    self.add_node(Node(name, int(x), int(y)))
                elif line[0] == 'r':
                    name, start, end = line.split(' ')[1:]
                    self.add_road(
                        Road(name, self.get_node(start), self.get_node(end)))
                elif line[0] == 'h':
                    name, start, end = line.split(' ')[1:]
                    self.add_road(
                        Highway(name, self.get_node(start), self.get_node(end)))
                elif line[0] == 'i':
                    name, x, y = line.split(' ')[1:]
                    self.add_node(InvisibleCity(name, int(x), int(y)))
                else:
                    print('Error: Wrong Map Format')
                    return False
        return True

    def get_path(self, start, end, mode='distance'):
        if len(end) == 1:
            path = []
            path_name = self.get_path_by_dijkstra(start, end[0], mode)
            for name in path_name:
                path.append(self.get_node(name))
            return path

        else:
            return

    # create distance graph
    def create_distance_graph(self):
        distance_graph = {}
        for node in self.node:
            distance_graph[node.name] = {}
            for road in node.road:
                if road.start == node:
                    distance_graph[node.name][road.end.name] = road.length
                elif road.isDuplex:
                    distance_graph[node.name][road.start.name] = road.length
        return distance_graph

    def create_price_graph(self):
        price_graph = {}
        for node in self.node:
            price_graph[node.name] = {}
            for road in node.road:
                if road.start == node:
                    price_graph[node.name][road.end.name] = road.length * road.cost
                elif road.isDuplex:
                    price_graph[node.name][road.start.name] = road.length * road.cost
        return price_graph

    def create_time_graph(self):
        time_graph = {}
        for node in self.node:
            time_graph[node.name] = {}
            for road in node.road:
                if road.start == node:
                    time_graph[node.name][road.end.name] = road.length / road.speedLimit
                elif road.isDuplex:
                    time_graph[node.name][road.start.name] = road.length / road.speedLimit
        return time_graph

    def get_path_by_dijkstra(self, start, end, mode='distance'):
        if mode == 'distance':
            distance_graph = self.create_distance_graph()
            distances, paths = dijkstra(distance_graph, start, end)
            return paths
        elif mode == 'price':
            price_graph = self.create_price_graph()
            distances, paths = dijkstra(price_graph, start, end)
            return paths
        elif mode == 'time':
            time_graph = self.create_time_graph()
            distances, paths = dijkstra(time_graph, start, end)
            return paths

    def list_cities(self):
        cities = []
        for node in self.node:
            if not node.invisible:
                cities.append(node.name)
        return cities

    def search_city(self, city='', removed=None):  # return a list of city names containing the keyword
        cities = []
        available_cities = self.list_cities()
        if removed is not None:
            available_cities.remove(removed)
        if city == '':
            return available_cities
        for node in available_cities:
            if city in node or city in get_first_pinyin(node) or city in combine_string(
                    lazy_pinyin(node)):
                cities.append(node)
        if len(cities) < 3:
            # all cities minus the cities in cities
            rest_cities = [city for city in available_cities if city not in cities]
            cities.append(autocorrect(city, rest_cities, shifty_shifts, 13))
        return cities

    def random_narrow(self):
        for road in self.road:
            if random.randint(0, 100) < 5:
                road.is_narrow = True
                road.speedLimit = 30
