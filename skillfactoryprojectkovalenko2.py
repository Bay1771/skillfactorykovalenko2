import random


class BoardWrongShipException(Exception):
    pass


class BoardWrongDotException(Exception):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, length, direction):
        self.bow = bow
        self.length = length
        self.direction = direction
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            if self.direction == 0:
                ship_dots.append(Dot(self.bow.x + i, self.bow.y))
            else:
                ship_dots.append(Dot(self.bow.x, self.bow.y + i))
        return ship_dots


class Board:
    def __init__(self, size=6, hid=False):
        self.size = size
        self.hid = hid
        self.field = [["О"] * size for _ in range(size)]
        self.busy = []
        self.ships = []
        self.count = 0

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not self.out(cur):
                    if cur not in self.busy:
                        if verb:
                            self.field[cur.x][cur.y] = "T"
                        self.busy.append(cur)

    def out(self, d):
        return not (0 <= d.x < self.size and 0 <= d.y < self.size)

    def shot(self, d):
        if self.out(d):
            raise BoardWrongDotException()
        if d in self.busy:
            raise BoardWrongDotException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль подбит!")
                    return False

        self.field[d.x][d.y] = "T"
        print("Промах!")
        return True

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardWrongDotException as e:
                print("Неверный ход! Повторите.")
            except Exception as e:
                print(f"Ошибка: {e}")


class AI(Player):
    def ask(self):
        while True:
            d = Dot(random.randint(0, 5), random.randint(0, 5))
            if d not in self.enemy.busy:
                print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
                return d


class User(Player):
    def ask(self):
        while True:
            coords = input("Ваш ход (строка столбец): ").split()
            if len(coords) != 2:
                print("Введите 2 координаты!")
                continue

            x, y = coords
            if not (x.isdigit() and y.isdigit()):
                print("Введите числа!")
                continue

            x, y = int(x) - 1, int(y) - 1
            if not (0 <= x < 6 and 0 <= y < 6):
                print("Координаты вне диапазона!")
                continue

            return Dot(x, y)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return self.random_board()
                ship = Ship(
                    Dot(random.randint(0, self.size - 1), random.randint(0, self.size - 1)),
                    l,
                    random.randint(0, 1)
                )
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.busy = []
        return board

    def greet(self):
        print("-------------------")
        print("  Приветствуем вас ")
        print("      в игре       ")
        print("    Морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def print_board(self, board, hidden=False):
        print("  | 1 | 2 | 3 | 4 | 5 | 6 |")
        for i, row in enumerate(board.field):
            if hidden and not board.hid:
                visible_row = ["■" if cell == "■" else "О" for cell in row]
                print(f"{i+1} | " + " | ".join(visible_row) + " |")
            else:
                print(f"{i+1} | " + " | ".join(row) + " |")

    def loop(self):
        num = 0
        while True:
            print("-" * 30)
            print("Доска пользователя:")
            self.print_board(self.us.board)
            print("-" * 30)
            print("Доска компьютера:")
            self.print_board(self.ai.board, hidden=True)

            if num % 2 == 0:
                print("-" * 30)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 30)
                print("Ходит компьютер!")
                repeat = self.ai.move()

            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 30)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 30)
                print("Компьютер выиграл!")
                break

            num += 1

    def start(self):
        self.greet()
        self.loop()


if __name__ == "__main__":
    g = Game()
    g.start()
