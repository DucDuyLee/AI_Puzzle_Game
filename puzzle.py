import pygame
import sys
import heapq
import random
from pygame.locals import *

# Các hằng số và biến toàn cục
w_of_board = 3
h_of_board = 3
block_size = 80
win_width = 640
win_height = 480
FPS = 30
BLANK = None
BGCOLOR = (224, 238 ,224)
TILECOLOR = (255, 255, 255)
TEXTCOLOR = (0, 0, 0)
BORDERCOLOR = (0, 0, 0)
BUTTONCOLOR = (202, 225, 255)
GREEN = (0, 128, 0)
TEXT = GREEN
BASICFONTSIZE = 20
BUTTONTEXTCOLOR = (0, 0, 0)
MESSAGECOLOR = (0, 191, 255)
XMARGIN = int((win_width - (block_size * w_of_board + (w_of_board - 1))) / 2)
YMARGIN = int((win_height - (block_size * h_of_board + (h_of_board - 1))) / 2)
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
COST = 1  # Định nghĩa chi phí cho UCS

BFS = 'BFS'
AStar = 'A*'
DFS = 'DFS'
ID =  'ID'
UCS =  'UCS'


# Các hằng số mới
SOLVINGCOLOR = (255, 0, 0)  # Đỏ để chỉ trạng thái giải quyết
solving = False  # Biến để kiểm tra xem puzzle đang được giải quyết hay không
move_count = 0

# Cấu trúc dữ liệu cho trạng thái của bảng
class PuzzleBoard:
    def __init__(self, board, parent=None, move=None, cost=0):
        self.board = board
        self.parent = parent
        self.move = move
        self.blank = self.find_blank()
        self.cost = cost  # Thêm thuộc tính cost

    def find_blank(self):
        for x in range(w_of_board):
            for y in range(h_of_board):
                if self.board[x][y] == BLANK:
                    return (x, y)

    def __eq__(self, other):
        return self.board == other.board

    def __hash__(self):
        return hash(str(self.board))
    
    def __lt__(self, other):
        # So sánh theo chi phí
        return self.cost < other.cost
    
pygame.init()
BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

#Hàm tạo thông số cho text in puzzle
def make_text(text, color, bgcolor, top, left):
    text_rendering = BASICFONT.render(text, True, color, None)
    text_rect = text_rendering.get_rect()
    text_rect.topleft = (top, left)
    return (text_rendering, text_rect)

# Hàm khởi tạo bảng puzzle
def start_playing():
    global move_count
    move_count = 0  # Khởi tạo số bước đi là 0
    counter = 1
    board = []
    for x in range(w_of_board):
        column = []
        for y in range(h_of_board):
            column.append(counter)
            counter += w_of_board
        board.append(column)
        counter -= w_of_board * (h_of_board - 1) + w_of_board - 1
    board[w_of_board-1][h_of_board-1] = BLANK
    return board

# Hàm kiểm tra trạng thái đã giải quyết chưa
def is_solved(board, initial_board):
    return board == initial_board

# Hàm di chuyển một ô trống
def move_blank(board, move):
    global move_count  # Thêm dòng này

    blank_x, blank_y = get_blank_position(board)

    if move == UP:
        if blank_y > 0:
            board[blank_x][blank_y], board[blank_x][blank_y - 1] = board[blank_x][blank_y - 1], board[blank_x][blank_y]
            move_count += 1  # Tăng số bước đi
    elif move == DOWN:
        if blank_y < h_of_board - 1:
            board[blank_x][blank_y], board[blank_x][blank_y + 1] = board[blank_x][blank_y + 1], board[blank_x][blank_y]
            move_count += 1
    elif move == LEFT:
        if blank_x > 0:
            board[blank_x][blank_y], board[blank_x - 1][blank_y] = board[blank_x - 1][blank_y], board[blank_x][blank_y]
            move_count += 1
    elif move == RIGHT:
        if blank_x < w_of_board - 1:
            board[blank_x][blank_y], board[blank_x + 1][blank_y] = board[blank_x + 1][blank_y], board[blank_x][blank_y]
            move_count += 1
    return board

# Hàm kiểm tra xem một bước di chuyển có hợp lệ không
def is_valid_move(board, move):
    blank_x, blank_y = get_blank_position(board)
    if move == UP:
        return blank_y > 0
    elif move == DOWN:
        return blank_y < h_of_board - 1
    elif move == LEFT:
        return blank_x > 0
    elif move == RIGHT:
        return blank_x < w_of_board - 1
    return False

# Hàm sinh ra các trạng thái con từ trạng thái hiện tại
def generate_child_states(parent_state):
    children = []
    for move in [UP, DOWN, LEFT, RIGHT]:
        if is_valid_move(parent_state.board, move):
            child_board = [row[:] for row in parent_state.board]
            move_blank(child_board, move)
            child_state = PuzzleBoard(child_board, parent=parent_state, move=move)
            children.append(child_state)
    return children

#Hàm trượt ô trống giúp có hiệu ứng mượt hơn
def slide_blank(board, move):
    blank_x, blank_y = get_blank_position(board)

    if move == UP:
        if blank_y > 0:
            board[blank_x][blank_y], board[blank_x][blank_y - 1] = board[blank_x][blank_y - 1], board[blank_x][blank_y]
    elif move == DOWN:
        if blank_y < h_of_board - 1:
            board[blank_x][blank_y], board[blank_x][blank_y + 1] = board[blank_x][blank_y + 1], board[blank_x][blank_y]
    elif move == LEFT:
        if blank_x > 0:
            board[blank_x][blank_y], board[blank_x - 1][blank_y] = board[blank_x - 1][blank_y], board[blank_x][blank_y]
    elif move == RIGHT:
        if blank_x < w_of_board - 1:
            board[blank_x][blank_y], board[blank_x + 1][blank_y] = board[blank_x + 1][blank_y], board[blank_x][blank_y]

#Hàm tìm vị trí ô trống và trả về giá trị chỉ vị trí
def get_blank_position(board):
    for x in range(w_of_board):
        for y in range(h_of_board):
            if board[x][y] == BLANK:
                return x, y

#Thực hiện xáo trộn bảng vừa tạo
def shuffle_board(board, num_moves):
    global original_state  # Cập nhật biến global
    last_move = None
    for _ in range(num_moves):
        move = random.choice([UP, DOWN, LEFT, RIGHT])
        if move == UP and last_move != DOWN:
            slide_blank(board, UP)
            last_move = UP
        elif move == DOWN and last_move != UP:
            slide_blank(board, DOWN)
            last_move = DOWN
        elif move == LEFT and last_move != RIGHT:
            slide_blank(board, LEFT)
            last_move = LEFT
        elif move == RIGHT and last_move != LEFT:
            slide_blank(board, RIGHT)

    # Lưu trạng thái ban đầu khi xáo trộn bảng
    original_state = [row[:] for row in board]

# Hàm vẽ khung trò chơi
def draw_board(board, message):
    BUTTON_WIDTH = 150
    BUTTON_HEIGHT = 30
    BUTTON_MARGIN = 10
    global move_count  # Thêm dòng này

    DISPLAYSURF.fill(BGCOLOR)
    if message:
        text_rendering, text_rect = make_text(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(text_rendering, text_rect)

    for tile_x in range(w_of_board):
        for tile_y in range(h_of_board):
            tile_value = board[tile_x][tile_y]
            if tile_value is not None:
                draw_tile(tile_x, tile_y, tile_value)

    left, top = get_left_top_of_tile(0, 0)
    width = w_of_board * block_size
    height = h_of_board * block_size
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

    # Hiển thị số bước đi trên giao diện
    move_text_rendering, move_text_rect = make_text(f'Moves: {move_count}', MESSAGECOLOR, BGCOLOR, 5, win_height - 25)
    DISPLAYSURF.blit(move_text_rendering, move_text_rect)

    # Vẽ khung cho các nút
    pygame.draw.rect(DISPLAYSURF, (205,201,165), (win_width - 160, win_height - 400, 75, 30))
    pygame.draw.rect(DISPLAYSURF, (205,201,165), (win_width - 160, win_height - 350, 125, 30))
    pygame.draw.rect(DISPLAYSURF, (205,201,165), (win_width - 160, win_height - 300, 45, 30))
    pygame.draw.rect(DISPLAYSURF, (205,201,165), (win_width - 160, win_height - 250, 58, 30))
    pygame.draw.rect(DISPLAYSURF, (205,201,165), (win_width - 160, win_height - 200, 58, 30))
    pygame.draw.rect(DISPLAYSURF, (205,201,165), (win_width - 160, win_height - 150, 43, 30))
    pygame.draw.rect(DISPLAYSURF, (205,201,165), (win_width - 160, win_height - 100, 60, 30))

    #vẽ các nút 
    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(AStar_SURF, AStar_RECT)
    DISPLAYSURF.blit(BFS_SURF, BFS_RECT)
    DISPLAYSURF.blit(DFS_SURF, DFS_RECT)
    DISPLAYSURF.blit(ID_SURF, ID_RECT)
    DISPLAYSURF.blit(UCS_SURF, UCS_RECT)

    pygame.display.update()

# Hàm vẽ ô puzzle
def draw_tile(tile_x, tile_y, number, adjx=0, adjy=0):
    left, top = get_left_top_of_tile(tile_x, tile_y)
    
    # Vẽ khung phân cách
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left + adjx, top + adjy, block_size, block_size), 1)
    
    # Vẽ ô số
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx + 1, top + adjy + 1, block_size - 2, block_size - 2))
    
    text_rendering = BASICFONT.render(str(number), True, TEXTCOLOR)
    text_rect = text_rendering.get_rect()
    text_rect.center = left + int(block_size / 2) + adjx, top + int(block_size / 2) + adjy
    DISPLAYSURF.blit(text_rendering, text_rect)

# Hàm vẽ khung bảng
def get_left_top_of_tile(tile_x, tile_y):
    left = XMARGIN + (tile_x * block_size) + (tile_x - 1)
    top = YMARGIN + (tile_y * block_size) + (tile_y - 1)
    return left, top

#Tạo hiệu ứng reset
def reset_animation(board):
    global original_state, move_count
    move_count = 0  # Đặt số bước đi về 0
    for i in range(0, 21, 2):
        draw_board(board, 'Resetting...')
        for tile_x in range(w_of_board):
            for tile_y in range(h_of_board):
                tile_value = original_state[tile_x][tile_y]
                draw_tile(tile_x, tile_y, tile_value, 5, 5)
        pygame.display.update()
        pygame.time.wait(100)
    for x in range(w_of_board):
        for y in range(h_of_board):
            board[x][y] = original_state[x][y]
    draw_board(board, 'Reset complete!')
    pygame.display.update()
    pygame.time.wait(1000)

# Xác định ô mà người chơi đã nhấp chuột lên
def get_spot_clicked(board, x, y):
    for tile_x in range(w_of_board):
        for tile_y in range(h_of_board):
            left, top = get_left_top_of_tile(tile_x, tile_y)
            tile_rect = pygame.Rect(left, top, block_size, block_size)
            if tile_rect.collidepoint(x, y):
                return tile_x, tile_y
    return None, None

# Kiểm tra các sự kiện ngắt (quit) hoặc phím thoát (Esc)
def check_for_quit():
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event)
        
#Kết thúc trò chơi
def terminate():
    pygame.quit()
    sys.exit()

#Giải trò chơi bằng thuật toán A*
def solve_animation_a_star(board, solved_board):
    global solving, move_count
    solving = True
    solution_path = find_solution_a_star(PuzzleBoard(board), solved_board)
    move_count = 0
    if solution_path:
        for move in solution_path:
            if not solving:
                return
            slide_blank(board, move)
            move_count += 1
            draw_board(board, 'Solving... ')
            pygame.display.update()
            pygame.time.wait(300)
    solving = False

# tìm điểm tiếp theo dựa trên chi phí từ hàm heuristic_cost và đánh giá xem các đỉnh xung quanh đỉnh nào chi phí tốt nhất
# Hàm tìm kiếm giải pháp sử dụng thuật toán A* với hàm heuristic
def find_solution_a_star(initial_state, solved_board):
    visited = set()  # Tạo một tập hợp để theo dõi các trạng thái đã được duyệt qua
    heap = [(heuristic_cost(initial_state.board, solved_board), initial_state, 0)]  # Tạo một hàng đợi ưu tiên (heap) 
                                                                #với giá trị ưu tiên ban đầu được tính bằng hàm heuristic

    while heap:
        _, current_state, current_moves = heapq.heappop(heap)  # Lấy trạng thái có giá trị ưu tiên thấp nhất từ hàng đợi ưu tiên
        visited.add(hash(current_state))  # Đánh dấu trạng thái hiện tại là đã duyệt

        if is_solved(current_state.board, solved_board):  # Kiểm tra xem trạng thái hiện tại có phải là trạng thái đích không
            solution_path = []
            while current_state.parent:
                solution_path.insert(0, current_state.move)  # Tái tạo đường dẫn giải quyết bằng cách duyệt ngược từ trạng thái hiện tại 
                                                                                        #đến trạng thái ban đầu
                current_state = current_state.parent
            return solution_path  # Trả về đường dẫn giải quyết nếu trạng thái đích được tìm thấy

        children = generate_child_states(current_state)  # Tạo danh sách các trạng thái con từ trạng thái hiện tại
        for child in children:
            if hash(child) not in visited:  # Kiểm tra xem trạng thái con đã được duyệt qua chưa
                # Tính toán giá trị ưu tiên cho trạng thái con bằng cách cộng thêm chi phí hiện tại (số bước đi) và giá trị heuristic
                cost = current_moves + 1 + heuristic_cost(child.board, solved_board)
                heapq.heappush(heap, (cost, child, current_moves + 1))  # Thêm trạng thái con vào hàng đợi ưu tiên với giá trị ưu tiên mới

    return None  # Trả về None nếu không tìm thấy giải pháp


#Tính chi phí để đánh giá
def heuristic_cost(state, solved_board):
    # Hàm đánh giá chi phí heuristics (ví dụ: số ô không đúng vị trí)
    cost = 0
    for i in range(len(state)):
        for j in range(len(state[i])):
            if state[i][j] != solved_board[i][j]:
                cost += 1
    return cost

#Giải trò chơi bằng thuật toán UCS tìm kiếm với chi phí tối ưu
def solve_animation_ucs(board, solved_board):
    global solving, move_count
    solving = True
    solution_path = find_solution_ucs(PuzzleBoard(board), solved_board)
    move_count = 0  # Reset số bước đi khi bắt đầu giải quyết
    if solution_path:
        for move in solution_path:
            if not solving:  # Kiểm tra xem có nên dừng không
                return
            slide_blank(board, move)
            move_count += 1
            draw_board(board, 'Solving...')
            pygame.display.update()
            pygame.time.wait(300)
    solving = False

# timnf kiếm mù với chi phí thấp nhất, ở đây không có cost nên mặc định mỗi bước đi cost sẽ tăng 1
# Hàm tìm kiếm giải pháp sử dụng thuật toán Uniform Cost Search (UCS)
def find_solution_ucs(initial_state, solved_board):
    heap = [(0, initial_state)]  # Tạo một hàng đợi ưu tiên (heap) với giá trị ưu tiên ban đầu là 0, sử dụng nó để quản lý các trạng thái

    visited = set()  # Tạo một tập hợp để theo dõi các trạng thái đã được duyệt qua

    while heap:
        cost, current_state = heapq.heappop(heap)  # Lấy trạng thái có giá trị ưu tiên thấp nhất từ hàng đợi ưu tiên
        visited.add(hash(current_state))  # Đánh dấu trạng thái hiện tại là đã duyệt

        if is_solved(current_state.board, solved_board):
            solution_path = []
            while current_state.parent:
                solution_path.insert(0, current_state.move)  # Tái tạo đường dẫn giải quyết bằng cách duyệt ngược từ trạng thái 
                                                                                    #hiện tại đến trạng thái ban đầu
                current_state = current_state.parent
            return solution_path  # Trả về đường dẫn giải quyết nếu trạng thái đích được tìm thấy

        children = generate_child_states(current_state)  # Tạo danh sách các trạng thái con từ trạng thái hiện tại
        for child in children:
            if hash(child) not in visited:  # Kiểm tra xem trạng thái con đã được duyệt qua chưa
                heapq.heappush(heap, (cost + 1, child))  # Thêm trạng thái con vào hàng đợi ưu tiên với giá trị ưu tiên tăng lên 1 
                                                                                            #(chi phí tăng lên 1 cho mỗi bước đi)

    return None  # Trả về None nếu không tìm thấy giải pháp


#Giải trò chơi bằng thuật toán ID (BFS với chiều sâu bằng 5)
def solve_animation_id(board, solved_board, max_depth):
    global solving, move_count
    solving = True
    solution_path = find_solution_id(PuzzleBoard(board), solved_board, max_depth)
    move_count = 0  # Reset số bước đi khi bắt đầu giải quyết
    if solution_path:
        for move in solution_path:
            if not solving:  # Kiểm tra xem có nên dừng không
                return
            slide_blank(board, move)
            move_count += 1
            draw_board(board, 'Solving...')
            pygame.display.update()
            pygame.time.wait(300)
    solving = False

#Tìm kiếm theo độ sâu được giới hạn trước
# Hàm tìm kiếm giải pháp sử dụng thuật toán Iterative Deepening (ID) Depth-First Search (DFS)
def find_solution_id(initial_state, solved_board, depth_limit):
    visited = set()  # Tạo một tập hợp để theo dõi các trạng thái đã được duyệt qua

    def dfs(current_state, depth):
        visited.add(hash(current_state))

        if is_solved(current_state.board, solved_board):
            solution_path = []
            while current_state.parent:
                solution_path.insert(0, current_state.move)  # Tái tạo đường dẫn giải quyết bằng cách duyệt ngược từ trạng thái 
                                                                                                #hiện tại đến trạng thái ban đầu
                current_state = current_state.parent
            return solution_path  # Trả về đường dẫn giải quyết nếu trạng thái đích được tìm thấy

        if depth < depth_limit:
            children = generate_child_states(current_state)  # Tạo danh sách các trạng thái con từ trạng thái hiện tại
            for child in children:
                if hash(child) not in visited:
                    result = dfs(child, depth + 1)  # Gọi đệ quy với trạng thái con và tăng độ sâu lên 1
                    if result:
                        return result  # Trả về kết quả nếu tìm thấy giải pháp

        return None  # Trả về None nếu không tìm thấy giải pháp trong giới hạn độ sâu

    return dfs(initial_state, 0)  # Gọi hàm DFS ban đầu với độ sâu ban đầu là 0


#Giải trò chơi bằng thuật toán BFS tìm kiếm theo chiều rộng
def solve_animation_bfs(board, solved_board):
    global solving, move_count
    solving = True
    
    solution_path = find_solution_bfs(PuzzleBoard(board), solved_board)
    move_count = 0  # Reset số bước đi khi bắt đầu giải quyết
    if solution_path:
        for move in solution_path:
            if not solving:
                return
            slide_blank(board, move)
            move_count += 1  # Tăng số bước đi
            draw_board(board, 'Solving...')
            pygame.display.update()
            pygame.time.wait(300)
    solving = False
    
# Thăm tất cả các điểm bắt đầu từ điểm xuất phát, thăm theo chiều rộng nên quét tất cả các đỉnh gần kề đỉnh gốc mới sang đỉnh con tiếp theo
# Hàm tìm kiếm giải pháp sử dụng thuật toán Breadth-First Search (BFS)
def find_solution_bfs(initial_state, solved_board):
    visited = set()  # Tạo một tập hợp để theo dõi các trạng thái đã được duyệt qua
    queue = [(initial_state, 0)]  # Sử dụng hàng đợi để lưu trữ trạng thái và số bước đi từ trạng thái ban đầu

    while queue:  # Tiếp tục cho đến khi hàng đợi không còn trống
        current_state, current_moves = queue.pop(0)  # Lấy trạng thái đầu tiên ra khỏi hàng đợi
        visited.add(hash(current_state))  # Đánh dấu trạng thái hiện tại đã được duyệt qua bằng cách thêm vào tập hợp visited

        # Kiểm tra nếu trạng thái hiện tại là trạng thái đích
        if is_solved(current_state.board, solved_board):
            solution_path = []
            while current_state.parent:
                solution_path.insert(0, current_state.move)  # Tái tạo đường dẫn giải quyết bằng cách duyệt ngược từ trạng thái 
                                                                                    #hiện tại đến trạng thái ban đầu
                current_state = current_state.parent
            return solution_path  # Trả về đường dẫn giải quyết

        children = generate_child_states(current_state)  # Tạo danh sách các trạng thái con từ trạng thái hiện tại

        # Duyệt qua từng trạng thái con và kiểm tra xem chúng đã được duyệt qua chưa
        for child in children:
            if hash(child) not in visited:
                queue.append((child, current_moves + 1))  # Thêm trạng thái con và số bước đi mới vào hàng đợi

    return None  # Trả về None nếu không tìm thấy giải pháp


#Giải trò chơi bằng thuật toán DFS tìm kiếm theo chiều sâu
def solve_animation_dfs(board, solved_board):
    global solving, move_count
    solving = True
    solution_path = find_solution_dfs(PuzzleBoard(board), solved_board)
    move_count = 0  # Reset số bước đi khi bắt đầu giải quyết
    if solution_path:
        for move in solution_path:
            if not solving:
                return
            slide_blank(board, move)
            move_count += 1  # Tăng số bước đi
            draw_board(board, 'Solving...')
            pygame.display.update()
            pygame.time.wait(300)
    solving = False
    
# Hàm tìm đường đi từ trạng thái hiện tại đến đích
# thăm các đỉnh sao cho sâu nhất trước thi back lại đỉnh gốc
def find_solution_dfs(initial_state, solved_board):
    visited = set()  # Tạo một tập hợp để theo dõi các trạng thái đã được duyệt qua

    # Định nghĩa hàm đệ quy dfs để thực hiện tìm kiếm
    def dfs(current_state):
        visited.add(hash(current_state))  # Đánh dấu trạng thái hiện tại đã được duyệt qua bằng cách thêm vào tập hợp visited

        # Kiểm tra nếu trạng thái hiện tại là trạng thái đích
        if is_solved(current_state.board, solved_board):
            solution_path = []
            while current_state.parent:
                solution_path.insert(0, current_state.move)  # Tái tạo đường dẫn giải quyết bằng cách duyệt ngược từ trạng thái 
                                                                #hiện tại đến trạng thái ban đầu
                current_state = current_state.parent
            return solution_path  # Trả về đường dẫn giải quyết

        children = generate_child_states(current_state)  # Tạo danh sách các trạng thái con từ trạng thái hiện tại

        # Duyệt qua từng trạng thái con và kiểm tra xem chúng đã được duyệt qua chưa
        for child in children:
            if hash(child) not in visited:
                result = dfs(child)  # Gọi đệ quy cho trạng thái con
                if result:
                    return result  # Trả về đường dẫn giải quyết nếu nó tồn tại

        return None  # Trả về None nếu không tìm thấy giải pháp từ trạng thái hiện tại

    return dfs(initial_state)  # Gọi hàm dfs bắt đầu từ trạng thái ban đầu

#Hàm main
def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, AStar_SURF, AStar_RECT
    global BFS_SURF, BFS_RECT, DFS_SURF, DFS_RECT, ID_SURF, ID_RECT, UCS_SURF, UCS_RECT
    global original_state  # Thêm biến global

    pygame.init()
    # Đường dẫn đến tệp âm nhạc nền
    music_file = "background_music.mp3"
    # Đường dẫn đến tệp âm thanh khi di chuyển
    move_sound = pygame.mixer.Sound("move_sound.wav")


    # Phát âm nhạc nền vô hạn lặp
    pygame.mixer.music.load(music_file)
    pygame.mixer.music.play(-1)

    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption('Slide Puzzle')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    RESET_SURF, RESET_RECT = make_text('Reset', (255, 106, 106), BGCOLOR, win_width - 150, win_height - 395)
    NEW_SURF, NEW_RECT = make_text('New Game', (255, 106, 106), BGCOLOR, win_width - 150, win_height - 345)
    AStar_SURF, AStar_RECT = make_text('A*', (255, 106, 106), BGCOLOR, win_width - 150, win_height - 295)
    BFS_SURF, BFS_RECT = make_text('BFS', (255, 106, 106), BGCOLOR, win_width - 150, win_height - 245)
    DFS_SURF, DFS_RECT = make_text('DFS', (255, 106, 106), BGCOLOR, win_width - 150, win_height - 195)
    ID_SURF, ID_RECT = make_text('ID', (255, 106, 106), BGCOLOR, win_width - 150, win_height - 145)
    UCS_SURF, UCS_RECT = make_text('UCS', (255, 106, 106), BGCOLOR, win_width - 150, win_height - 95)

    main_board = start_playing()
    solved_board = start_playing()

    # Xáo trộn bảng ban đầu để tạo trạng thái khởi đầu cho game
    shuffle_board(main_board, 1000)

    while True:
        msg = 'Welcome to my game! 8-Puzzle making by Duy '
        if main_board == solved_board:
            msg = 'Congratulations!!!'

        draw_board(main_board, msg)


        check_for_quit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                spot_x, spot_y = get_spot_clicked(main_board, event.pos[0], event.pos[1])

                if (spot_x, spot_y) == (None, None):
                    if RESET_RECT.collidepoint(event.pos):
                        pygame.mixer.Sound.play(move_sound)
                        reset_animation(main_board)
                    elif NEW_RECT.collidepoint(event.pos):
                        pygame.mixer.Sound.play(move_sound)
                        main_board = start_playing()
                        shuffle_board(main_board, 1000)
                    elif AStar_RECT.collidepoint(event.pos):
                        pygame.mixer.Sound.play(move_sound)
                        solve_animation_a_star(main_board, solved_board)
                    elif BFS_RECT.collidepoint(event.pos):
                        pygame.mixer.Sound.play(move_sound)
                        solving = True
                        solve_animation_bfs(main_board, solved_board)
                        solving = False
                    elif DFS_RECT.collidepoint(event.pos):
                        pygame.mixer.Sound.play(move_sound)
                        solving = True
                        solve_animation_dfs(main_board, solved_board)
                        solving = False
                    elif ID_RECT.collidepoint(event.pos):
                        pygame.mixer.Sound.play(move_sound)
                        solving = True
                        solve_animation_id(main_board, solved_board, max_depth=50)
                        solving = False
                    elif UCS_RECT.collidepoint(event.pos):
                        pygame.mixer.Sound.play(move_sound)
                        solving = True
                        solve_animation_ucs(main_board, solved_board)
                        solving = False
                else:
                    blank_x, blank_y = get_blank_position(main_board)
                    if spot_x == blank_x + 1 and spot_y == blank_y:
                        pygame.mixer.Sound.play(move_sound)
                        main_board = move_blank(main_board, RIGHT)
                    elif spot_x == blank_x - 1 and spot_y == blank_y:
                        pygame.mixer.Sound.play(move_sound)
                        main_board = move_blank(main_board, LEFT)
                    elif spot_x == blank_x and spot_y == blank_y + 1:
                        pygame.mixer.Sound.play(move_sound)
                        main_board = move_blank(main_board, DOWN)
                    elif spot_x == blank_x and spot_y == blank_y - 1:
                        pygame.mixer.Sound.play(move_sound)
                        main_board = move_blank(main_board, UP)

            elif event.type == KEYUP:
                if event.key in (K_LEFT, K_a) and is_valid_move(main_board, LEFT):
                    pygame.mixer.Sound.play(move_sound)
                    main_board = move_blank(main_board, LEFT)
                elif event.key in (K_RIGHT, K_d) and is_valid_move(main_board, RIGHT):
                    pygame.mixer.Sound.play(move_sound)
                    main_board = move_blank(main_board, RIGHT)
                elif event.key in (K_UP, K_w) and is_valid_move(main_board, UP):
                    pygame.mixer.Sound.play(move_sound)
                    main_board = move_blank(main_board, UP)
                elif event.key in (K_DOWN, K_s) and is_valid_move(main_board, DOWN):
                    pygame.mixer.Sound.play(move_sound)
                    main_board = move_blank(main_board, DOWN)

        move_text_rendering, move_text_rect = make_text(f'Moves: {move_count}', MESSAGECOLOR, BGCOLOR, 5, win_height - 25)
        DISPLAYSURF.blit(move_text_rendering, move_text_rect)

        pygame.display.update()
        FPSCLOCK.tick(FPS)
        
#Dòng này thay đổi giới hạn đệ quy trong Python lên 1 triệu.
#Điều này có thể cần thiết nếu sử dụng đệ quy sâu để tránh lỗi "RecursionError" khi đệ quy quá nhiều.
sys.setrecursionlimit(10**6)  # Tăng giới hạn đệ quy

if __name__ == '__main__':
    main()