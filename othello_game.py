import sys
import msvcrt
import random

class OthelloGame:
    def __init__(self):
        self.board = self.create_initial_board()
        self.current_player = 'B'   # B: Black(黒), W: White(白)
        self.game_over = False
        self.cursor = [3, 3]        # カーソル位置 [row, col]
        self.rotation = 0           # ボード回転回数（0:通常,1:90°,2:180°,3:270°）
        self.player_color = None    # プレイヤーの色
        self.npc_color = None       # NPCの色
        self.difficulty = 'medium'  # NPCの難易度（easy, medium, hard）
    
    # ---------- 盤面作成 ----------
    def create_initial_board(self):
        board = [['.' for _ in range(8)] for _ in range(8)]
        board[3][3] = 'W'
        board[3][4] = 'B'
        board[4][3] = 'B'
        board[4][4] = 'W'
        return board

    # ---------- 回転 ----------
    def rotate(self):
        """ボードを時計回りに90°回転（1回） - 物理的に盤面を回転"""
        self.board = [[self.board[7 - j][i] for j in range(8)] for i in range(8)]
        self.rotation = (self.rotation + 1) % 4

    def rotated_view(self):
        """現在の盤面をそのまま返す（回転は物理的にすでに適用済み）"""
        return [row[:] for row in self.board]

    # ---------- 石の数 ----------
    def count_stones(self, color):
        return sum(row.count(color) for row in self.board)

    # ---------- 有効手判定 ----------
    def is_valid_move(self, row, col, player):
        if not (0 <= row < 8 and 0 <= col < 8):
            return False
        if self.board[row][col] != '.':
            return False

        opponent = 'W' if player == 'B' else 'B'
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            found_opponent = False
            while 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent:
                found_opponent = True
                r += dr
                c += dc
            if found_opponent and 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == player:
                return True
        return False

    def get_valid_moves(self, player):
        moves = []
        for i in range(8):
            for j in range(8):
                if self.is_valid_move(i, j, player):
                    moves.append((i, j))
        return moves

    # ---------- 手を置く ----------
    def make_move(self, row, col, player=None):
        if player is None:
            player = self.current_player
        if not self.is_valid_move(row, col, player):
            return False

        self.board[row][col] = player

        opponent = 'W' if player == 'B' else 'B'
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            to_flip = []
            while 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent:
                to_flip.append((r, c))
                r += dr
                c += dc
            if to_flip and 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == player:
                for fr, fc in to_flip:
                    self.board[fr][fc] = player

        # 手番を切り替える
        self.current_player = 'W' if self.current_player == 'B' else 'B'
        return True

    # ---------- 手番交代 / ゲーム終了 ----------
    def switch_player(self):
        self.current_player = 'W' if self.current_player == 'B' else 'B'

    def check_game_over(self):
        b_moves = self.get_valid_moves('B')
        w_moves = self.get_valid_moves('W')
        if not b_moves and not w_moves:
            self.game_over = True
            return True
        if not self.get_valid_moves(self.current_player):
            print("  有効な手がありません。パスします。")
            self.switch_player()
        return False

    def get_winner(self):
        b = self.count_stones('B')
        w = self.count_stones('W')
        if b > w:
            return 'B', b, w
        elif w > b:
            return 'W', b, w
        else:
            return 'DRAW', b, w

    # ---------- 表示 ----------
    def display_board(self):
        view = self.rotated_view()
        print("\n    " + " ".join(f"{i:^3}" for i in range(8)))
        print("    " + "─" * 25)
        for i, row in enumerate(view):
            row_str = f"{i} |"
            for j, cell in enumerate(row):
                if cell == 'B':
                    if self.player_color == 'B':
                        row_str += " 私|"  # プレイヤーが黒の場合
                    elif self.npc_color == 'B':
                        row_str += " NPC|"  # NPCが黒の場合
                    else:
                        row_str += " ●|"
                elif cell == 'W':
                    if self.player_color == 'W':
                        row_str += " 私|"  # プレイヤーが白の場合
                    elif self.npc_color == 'W':
                        row_str += " NPC|"  # NPCが白の場合
                    else:
                        row_str += " ○|"
                else:
                    if self.cursor[0] == i and self.cursor[1] == j:
                        row_str += " ＿|"
                    else:
                        row_str += " ・|"
            print(row_str)
        b = self.count_stones('B')
        w = self.count_stones('W')
        print(f"\n  黒(B): {b}個  白(W): {w}個")
        if not self.game_over:
            player_name = "あなた" if self.current_player == self.player_color else "NPC"
            print(f"  手番: {player_name} ({'黒(B)' if self.current_player == 'B' else '白(W)'})")
            print(f"  カーソル: ({self.cursor[0]}, {self.cursor[1]})")

    # ---------- 改造の難易度別AI ----------
    def npc_make_move(self):
        """NPCが石を置く（難易度によって戦略が変わる）"""
        valid_moves = self.get_valid_moves(self.npc_color)
        if not valid_moves:
            print(f"  NPC({'黒' if self.npc_color == 'B' else '白'})に有効な手がありません。パスします。")
            return False
        
        if self.difficulty == 'easy':
            # ランダムに選ぶ
            row, col = random.choice(valid_moves)
        elif self.difficulty == 'medium':
            # 石の多い場所を優先（端やコーナーに近いところ）
            scored_moves = []
            for row, col in valid_moves:
                score = self._evaluate_move(row, col, self.npc_color)
                scored_moves.append((score, row, col))
            scored_moves.sort(reverse=True)
            _, row, col = scored_moves[0]
        else:  # hard
            # 最適手をより深く評価
            scored_moves = []
            for row, col in valid_moves:
                score = self._evaluate_move(row, col, self.npc_color, depth=1)
                scored_moves.append((score, row, col))
            scored_moves.sort(reverse=True)
            _, row, col = scored_moves[0]
        
        success = self.make_move(row, col)
        if success:
            print(f"  NPC({'黒' if self.npc_color == 'B' else '白'})が({row}, {col})に置きました！")
        return success
    
    def _evaluate_move(self, row, col, player, depth=0):
        """手の評価スコア（大きいほど良い手）"""
        score = 0
        # コーナーはとても良い（30点）
        if (row, col) in [(0, 0), (0, 7), (7, 0), (7, 7)]:
            score += 30
        # 端も良い（10点）
        elif row == 0 or row == 7 or col == 0 or col == 7:
            score += 10
        # 相手の石を多く反転できるほど良い
        opponent = 'W' if player == 'B' else 'B'
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]
        for dr, dc in directions:
            r, c = row + dr, col + dc
            count = 0
            while 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent:
                count += 1
                r += dr
                c += dc
            if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == player:
                score += count * 2
        # 隅っこの次のマス（Xマス）は悪いのでペナルティ
        if (row, col) in [(0, 1), (1, 0), (1, 1), (0, 6), (1, 7), (1, 6),
                           (6, 0), (7, 1), (6, 1), (6, 7), (7, 6), (6, 6)]:
            score -= 15
        return score

    # ---------- ゲーム実行 ----------
    def run(self):
        # プレイヤーが黒か白かを選択
        print("╔" + "═" * 48 + "╗")
        print("║" + "   オセロ変則版 - ボード回転つき".center(48) + "║")
        print("╚" + "═" * 48 + "╝")
        print()
        print("  対戦モード: あなた vs NPC（1VS1）")
        print()
        print("  あなたが先攻（黒）か後攻（白）かを選んでください。")
        print()
        
        while True:
            print("  あなたの色を選んでください:")
            print("    [B] 黒(Black) - 先攻")
            print("    [W] 白(White) - 後攻")
            print()
            choice = input("  選択 > ").strip().upper()
            if choice in ('B', 'BLACK'):
                self.player_color = 'B'
                self.npc_color = 'W'
                self.current_player = 'B'  # 黒が先攻
                break
            elif choice in ('W', 'WHITE'):
                self.player_color = 'W'
                self.npc_color = 'B'
                self.current_player = 'B'  # 黒（NPC）が先攻
                break
            else:
                print("  B または W を入力してください。")
        
        print()
        print(f"  あなた: {'黒(B)' if self.player_color == 'B' else '白(W)'}")
        print(f"  NPC: {'黒(B)' if self.npc_color == 'B' else '白(W)'}")
        print()
        
        print("  操作方法（あなたのターン時のみ）")
        print("    ← ↑ ↓ → または H/J/K/L : カーソル移動")
        print("    Enter                  : 石を置く")
        print("    R                      : ボードを90°時計回りに回転（回転ターン）")
        print("    Q                      : ゲーム終了")
        print()
        print("  ※ NPCのターンは自動で進みます。")
        print("  ※ ボード回転はあなたしか使えません。")
        print()
        
        while not self.game_over:
            self.display_board()
            
            if self.current_player == self.player_color:
                # プレイヤーのターン
                valid_moves = self.get_valid_moves(self.current_player)
                if valid_moves:
                    print(f"\n  置ける場所: {len(valid_moves)}箇所")
                else:
                    print("\n  あなたに有効な手がありません。パスします。")
                    self.switch_player()
                    continue
                
                print("  コマンド > ", end="", flush=True)
                key = self._get_key()
                if key is None:
                    continue
                key = key.upper()
                
                if key in ('Q', 'QUIT', 'EXIT'):
                    print("  ゲームを終了します。")
                    break
                
                if key == 'R':
                    self.rotate()
                    print("  ボードを90°時計回りに回転しました！")
                    # 回転後もプレイヤーのターン（石は置かない）
                    continue
                
                dr, dc = 0, 0
                if key in ('W', '上', 'K'):      dr = -1
                elif key in ('S', '下', 'J'):   dr = 1
                elif key in ('A', '左', 'H'):   dc = -1
                elif key in ('D', '右', 'L'):   dc = 1
                elif key in ('↑',):             dr = -1
                elif key in ('↓',):             dr = 1
                elif key in ('←',):             dc = -1
                elif key in ('→',):             dc = 1
                
                if dr != 0 or dc != 0:
                    self.cursor[0] = max(0, min(7, self.cursor[0] + dr))
                    self.cursor[1] = max(0, min(7, self.cursor[1] + dc))
                    print(f"  カーソル: ({self.cursor[0]}, {self.cursor[1]})")
                    continue
                
                if key in ('', '\r', '\n', 'ENTER'):
                    row, col = self.cursor
                    if self.make_move(row, col):
                        print(f"  ({row}, {col}) に stoneを置きました！")
                        self.switch_player()
                        if self.check_game_over():
                            break
                    else:
                        print("  そこには置けません！")
                        continue
            else:
                # NPCのターン
                print(f"\n  ▼ NPC({'黒' if self.npc_color == 'B' else '白'})のターン ▼")
                self.npc_make_move()
                self.switch_player()
                if self.check_game_over():
                    break
        
        if self.game_over:
            winner, b, w = self.get_winner()
            self.display_board()
            print("\n" + "╔" + "═" * 48 + "╗")
            print("║" + "   ゲーム終了！".center(48) + "║")
            print("╚" + "═" * 48 + "╝")
            print(f"\n  黒(Black): {b}個")
            print(f"  白(White): {w}個")
            
            if winner == 'DRAW':
                print("\n  ★ 結果: 引き分け！ ★")
            elif winner == self.player_color:
                print(f"\n  ★ あなたの勝ちです！ ★ （{'黒' if self.player_color == 'B' else '白'} {b if self.player_color == 'B' else w}個 vs {'白' if self.player_color == 'B' else '黒'} {w if self.player_color == 'B' else b}個）")
            else:
                print(f"\n  ★ NPCの勝ちです... ★ （{'黒' if self.npc_color == 'B' else '白'} {b if self.npc_color == 'B' else w}個 vs {'白' if self.npc_color == 'B' else '黒'} {w if self.npc_color == 'B' else b}個）")
            print()

    def _get_key(self):
        """単一キー入力（Windows用 msvcrt）"""
        if sys.platform != 'win32':
            try:
                return input()
            except EOFError:
                return None
        try:
            ch = msvcrt.getch()
            if ch == b'\x00' or ch == b'\xe0':  # 拡張キー
                ch2 = msvcrt.getch()
                if ch2 == b'H':   return '上'
                if ch2 == b'P':   return '下'
                if ch2 == b'K':   return '左'
                if ch2 == b'M':   return '右'
                return None
            if ch in (b'\r', b'\n'):
                return ''
            if ch >= b'\x81' and ch <= b'\xfe':
                ch2 = msvcrt.getch()
                try:
                    return (ch + ch2).decode('cp932')
                except:
                    return None
            return ch.decode('ascii', errors='ignore')
        except:
            return None


def main():
    game = OthelloGame()
    game.run()


if __name__ == '__main__':
    main()
