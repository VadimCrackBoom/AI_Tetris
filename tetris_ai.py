import pygame
import random
import sys

# Константы
SCREEN_WIDTH = 400  # Увеличиваем ширину экрана
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
BOARD_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
BOARD_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # Циан
    (255, 165, 0),  # Оранжевый
    (0, 0, 255),    # Синий
    (255, 0, 0),    # Красный
    (0, 255, 0),    # Зеленый
    (128, 0, 128),  # Пурпурный
    (255, 255, 0),  # Желтый
]

# Фигуры
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # L
    [[0, 0, 1], [1, 1, 1]],  # J
]

class Tetris:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.current_piece = self.new_piece()
        self.score = 0
        self.generation = 0
        self.ai = AI(self)

    def new_piece(self):
        shape = random.choice(SHAPES)
        return {'shape': shape, 'x': BOARD_WIDTH // 2 - len(shape[0]) // 2, 'y': 0, 'color': random.choice(COLORS)}

    def draw_board(self):
        self.screen.fill(BLACK)
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.board[y][x]:
                    pygame.draw.rect(self.screen, self.board[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        self.draw_piece(self.current_piece)
        self.draw_generation()
        pygame.display.flip()

    def draw_piece(self, piece):
        shape = piece['shape']
        color = piece['color']
        for y, row in enumerate(shape):
            for x, block in enumerate(row):
                if block:
                    pygame.draw.rect(self.screen, color, ((piece['x'] + x) * BLOCK_SIZE, (piece['y'] + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

    def draw_generation(self):
        font = pygame.font.Font(None, 36)
        text = font.render(f'GEN: {self.generation}', True, WHITE)
        self.screen.blit(text, (SCREEN_WIDTH - 100, 10))

    def collide(self):
        for y in range(len(self.current_piece['shape'])):
            for x in range(len(self.current_piece['shape'][y])):
                if self.current_piece['shape'][y][x]:
                    board_x = self.current_piece['x'] + x
                    board_y = self.current_piece['y'] + y
                    if board_x < 0 or board_x >= BOARD_WIDTH or board_y >= BOARD_HEIGHT:
                        return True
                    if board_y >= 0 and self.board[board_y][board_x]:
                        return True
        return False

    def lock_piece(self):
        shape = self.current_piece['shape']
        color = self.current_piece['color']
        for y, row in enumerate(shape):
            for x, block in enumerate(row):
                if block:
                    board_x = self.current_piece['x'] + x
                    board_y = self.current_piece['y'] + y
                    # Проверяем, что board_x и board_y находятся в пределах допустимого диапазона
                    if 0 <= board_x < BOARD_WIDTH and 0 <= board_y < BOARD_HEIGHT:
                        self.board[board_y][board_x] = color
        lines_cleared = self.clear_lines()
        self.current_piece = self.new_piece()
        if self.collide():
            self.restart_game()  # Перезапуск игры при проигрыше
        # AI получает вознаграждение за очищенные линии
        self.ai.update_score(lines_cleared)

    def clear_lines(self):
        lines_to_clear = [i for i in range(BOARD_HEIGHT) if all(self.board[i])]
        for i in lines_to_clear:
            del self.board[i]
            self.board.insert(0, [0] * BOARD_WIDTH)
        return len(lines_to_clear)

    def restart_game(self):
        self.board = [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.current_piece = self.new_piece()
        self.score = 0
        self.generation += 1  # Увеличиваем счетчик поколения
        self.ai = AI(self)  # Перезапускаем ИИ

    def run(self):
        while True:
            self.handle_input()
            self.current_piece['y'] += 1
            if self.collide():
                self.current_piece['y'] -= 1
                self.lock_piece()
            self.ai.make_move()  # ИИ делает ход
            self.draw_board()
            self.clock.tick(10)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.current_piece['x'] -= 1
                    if self.collide():
                        self.current_piece['x'] += 1
                elif event.key == pygame.K_RIGHT:
                    self.current_piece['x'] += 1
                    if self.collide():
                        self.current_piece['x'] -= 1
                elif event.key == pygame.K_DOWN:
                    self.current_piece['y'] += 1
                    if self.collide():
                        self.current_piece['y'] -= 1
                elif event.key == pygame.K_UP:
                    self.current_piece['shape'] = self.rotate_piece(self.current_piece['shape'])
                    if self.collide():
                        self.current_piece['shape'] = self.rotate_piece(self.current_piece['shape'], -1)

    def rotate_piece(self, shape, times=1):
        for _ in range(times % 4):
            shape = [list(row) for row in zip(*shape[::-1])]
        return shape

class AI:
    def __init__(self, game):
        self.game = game
        self.score = 0

    def make_move(self):
        # Логика для ИИ, чтобы сделать оптимальный ход
        if random.random() < 0.5:  # Пример случайного хода
            self.game.current_piece['x'] += random.choice([-1, 1])  # Случайное движение влево или вправо
            if self.game.collide():
                self.game.current_piece['x'] -= random.choice([-1, 1])  # Отмена движения, если произошло столкновение

    def update_score(self, lines_cleared):
        if lines_cleared > 0:
            self.score += lines_cleared  # Вознаграждение за очищенные линии
        else:
            self.score -= 1  # Штраф за неудачный ход

if __name__ == "__main__":
    game = Tetris()
    game.run()
