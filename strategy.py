import heapq
from pypinyin import lazy_pinyin


def dijkstra(graph, start, end):
    distances = {node: float('infinity') for node in graph}
    distances[start] = 0
    predecessors = {node: None for node in graph}
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

        path_to_end = []
        node = end
        while node is not None:
            path_to_end.insert(0, node)
            node = predecessors[node]

    return distances, path_to_end


def autocorrect(user_word, valid_words, diff_function, limit):
    """Returns the element of VALID_WORDS that has the smallest difference
    from USER_WORD. Instead returns USER_WORD if that difference is greater
    than LIMIT.
    """
    possible_word = min(valid_words, key=lambda words: diff_function(user_word, combine_string(lazy_pinyin(words)),
                                                                     limit))  # it gives the first of all quralified to pw
    if diff_function(user_word, possible_word, limit) <= limit:
        return possible_word
    else:
        return None


def shifty_shifts(start, goal, limit):
    """A diff function for autocorrect that determines how many letters
    in START need to be substituted to create GOAL, then adds the difference in
    their lengths.
    """
    # BEGIN PROBLEM 6
    if limit == -1:
        return 0
    elif len(start) == 0 or len(goal) == 0:
        return abs(len(goal) - len(start))
    else:
        if start[0] == goal[0]:
            return shifty_shifts(start[1:], goal[1:], limit)
        if goal[0] == '_':
            return shifty_shifts(start, goal[1:], limit)
        else:
            return 1 + shifty_shifts(start[1:], goal[1:], limit - 1)


def combine_string(strings):
    result = ''
    for string in strings:
        result += string
    return result


def get_first_pinyin(strings):
    encoded_string = lazy_pinyin(strings)
    result = ''
    for string in encoded_string:
        result += string[0]
    return result
