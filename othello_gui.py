import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sys
import os

# 画像パス
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BLACK_IMAGE_PATH = os.path.join(SCRIPT_DIR, 'aab4ec96671a3480128142aa0b099350.png')
WHITE_IMAGE_PATH = os.path.join(SCRIPT_DIR, '00a9c86c513792f7b8e95df2dadfb190-768x759.png')


class OthelloGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("オセロ変則版 - ボード回転つき")
        self.root.resizable(False, False)
        
        # ゲーム状態
        self.board = self.create_initial_board()
        self.current_player = 'B'
        self.game_over = False
        self.rotation = 0
        self.player_color = None
        self.npc_color = None
        self.difficulty = 'medium'
        self.cursor = [3, 3]
        
        # 画像読み込み
        self.black_img = self.load_image(BLACK_IMAGE_PATH, (60, 60))
        self.white_img = self.load_image(WHITE_IMAGE_PATH, (60, 60))
        
        # キャンバス設定
        self.cell_size = 65
        self.board_size = 8 * self.cell_size
        self.padding = 40
        
        # キャンバス作成
        self.canvas = tk.Canvas(
            root,
            width=self.board_size + self.padding * 2,
            height=self.board_size + self.padding * 2 + 60,
            bg='#1a1a2e',
            highlightthickness=0
        )
        self.canvas.pack(pady=10)
        
        # 画像をキャンバスに登録
        self.black_photo = ImageTk.PhotoImage(self.black_img)
        self.white_photo = ImageTk.PhotoImage(self.white_img)
        
        # セル格納用
        self.cell_items = {}
        
        # UI作成
        self.create_ui()
        
        # 初回描画
        self.draw_board()
    
    def load_image(self, path, size):
        """画像を読み込んでサイズ変更"""
        try:
            img = Image.open(path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            return img
        except Exception as e:
            print(f"画像読み込みエラー: {path} - {e}")
            # フォールバック：白黒の四角形
            img = Image.new('RGB', size, 'black' if 'black' in path.lower() else 'white')
            return img
    
    def create_initial_board(self):
        board = [['.' for _ in range(8)] for _ in range(8)]
        board[3][3] = 'W'
        board[3][4] = 'B'
        board[4][3] = 'B'
        board[4][4] = 'W'
        return board
    
    def create_ui(self):
        """UIコンポーネント作成"""
        
        # タイトルフレーム
        title_frame = tk.Frame(self.root, bg='#16213e')
        title_frame.pack(fill='x', padx=20)
        
        title_label = tk.Label(
            title_frame,
            text="🎮 オセロ変則版",
            font=('Arial', 16, 'bold'),
            bg='#16213e',
            fg='#e94560'
        )
        title_label.pack()
        
        # 情報フレーム
        info_frame = tk.Frame(self.root, bg='#0f3460')
        info_frame.pack(fill='x', padx=20, pady=5)
        
        self.player_label = tk.Label(
            info_frame,
            text="あなたの色を選択してください",
            font=('Arial', 11),
            bg='#0f3460',
            fg='#fff'
        )
        self.player_label.pack(pady=5)
        
        color_frame = tk.Frame(info_frame, bg='#0f3460')
        color_frame.pack()
        
        self.black_btn = tk.Button(
            color_frame,
            text="⬛ 黒(Black) - 先攻",
            font=('Arial', 10, 'bold'),
            bg='#000',
            fg='#fff',
            width=20,
            command=lambda: self.select_color('B')
        )
        self.black_btn.pack(side='left', padx=10)
        
        self.white_btn = tk.Button(
            color_frame,
            text="⬜ 白(White) - 後攻",
            font=('Arial', 10, 'bold'),
            bg='#fff',
            fg='#000',
            width=20,
            command=lambda: self.select_color('W')
        )
        self.white_btn.pack(side='left', padx=10)
        
        # ステータスフレーム
        self.status_frame = tk.Frame(self.root, bg='#533483')
        self.status_frame.pack(fill='x', padx=20, pady=5)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="",
            font=('Arial', 11),
            bg='#533483',
            fg='#fff'
        )
        self.status_label.pack()
        
        # ボタンフレーム
        btn_frame = tk.Frame(self.root, bg='#1a1a2e')
        btn_frame.pack(pady=5)
        
        self.rotate_btn = tk.Button(
            btn_frame,
            text="🔄 ボードを90°回転",
            font=('Arial', 10, 'bold'),
            bg='#e94560',
            fg='#fff',
            width=18,
            command=self.rotate_board
        )
        self.rotate_btn.pack(side='left', padx=10)
        self.rotate_btn.config(state='disabled')  # 色選択するまで無効
        
        self.restart_btn = tk.Button(
            btn_frame,
            text="🔄 最初から",
            font=('Arial', 10),
            bg='#533483',
            fg='#fff',
            width=10,
            command=self.restart_game
        )
        self.restart_btn.pack(side='right', padx=10)
        
        # ヘルプテキスト
        self.help_label = tk.Label(
            self.root,
            text="操作: クリックで石を置く | Rキーで回転",
            font=('Arial', 9),
            bg='#1a1a2e',
            fg='#aaa'
        )
        self.help_label.pack(pady=5)
        
        # キーボードバインド
        self.root.bind('<Key>', self.on_key_press)
    
    def select_color(self, color):
        """プレイヤーが色を選択"""
        self.player_color = color
        self.npc_color = 'W' if color == 'B' else 'B'
        self.current_player = 'B'  # 黒が先攻

        self.player_label.config(text=f"あなた: {'黒' if color == 'B' else '白'} | NPC: {'白' if color == 'B' else '黒'}")
        self.black_btn.config(state='disabled')
        self.white_btn.config(state='disabled')
        self.rotate_btn.config(state='normal')
        self.status_label.config(text=f"ゲームスタート！ 黒が先攻です")

        self.draw_board()

        # NPCが先攻の場合、最初のNPCターンを予約
        if self.current_player == self.npc_color:
            self.root.after(500, self.npc_turn)
    
    def draw_board(self):
        """盤面を描画"""
        self.canvas.delete('all')
        
        # 盤面背景
        self.canvas.create_rectangle(
            self.padding - 5, self.padding - 5,
            self.padding + self.board_size + 5, self.padding + self.board_size + 5,
            fill='#006400',
            outline='#2d5a2d',
            width=2
        )
        
        # マス目
        for i in range(8):
            for j in range(8):
                x1 = self.padding + j * self.cell_size
                y1 = self.padding + i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                # 緑のマス
                if (i + j) % 2 == 0:
                    color = '#2d5a2d'
                else:
                    color = '#3d7a3d'
                
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline='#1a3a1a',
                    width=1
                )
                
                # 石の描画（回転表示を考慮）
                display_row = (i + self.rotation) % 8
                display_col = (j - self.rotation) % 8
                if 0 <= display_row < 8 and 0 <= display_col < 8:
                    cell_value = self.board[display_row][display_col]
                    
                    if cell_value == 'B':
                        self.canvas.create_image(
                            x1 + self.cell_size // 2,
                            y1 + self.cell_size // 2,
                            image=self.black_photo
                        )
                    elif cell_value == 'W':
                        self.canvas.create_image(
                            x1 + self.cell_size // 2,
                            y1 + self.cell_size // 2,
                            image=self.white_photo
                        )
        
        # カーソル表示
        cursor_x = self.padding + self.cursor[1] * self.cell_size
        cursor_y = self.padding + self.cursor[0] * self.cell_size
        self.canvas.create_rectangle(
            cursor_x, cursor_y,
            cursor_x + self.cell_size, cursor_y + self.cell_size,
            outline='#e94560',
            width=3
        )
        
        # 石の数表示
        b_count = sum(row.count('B') for row in self.board)
        w_count = sum(row.count('W') for row in self.board)
        
        info_text = f"黒(B): {b_count}個  |  白(W): {w_count}個"
        if not self.game_over and self.player_color:
            player_name = "あなた" if self.current_player == self.player_color else "NPC"
            info_text += f"  |  手番: {player_name}"
        
        self.status_label.config(text=info_text)
    
    def on_key_press(self, event):
        """キーボード操作"""
        if not self.player_color:
            return
        
        if self.current_player != self.player_color:
            return
        
        key = event.keysym
        
        if key == 'r' or key == 'R':
            self.rotate_board()
        elif key in ['Up', 'w', 'W', 'k', 'K']:
            self.cursor[0] = max(0, self.cursor[0] - 1)
            self.draw_board()
        elif key in ['Down', 's', 'S', 'j', 'J']:
            self.cursor[0] = min(7, self.cursor[0] + 1)
            self.draw_board()
        elif key in ['Left', 'a', 'A', 'h', 'H']:
            self.cursor[1] = max(0, self.cursor[1] - 1)
            self.draw_board()
        elif key in ['Right', 'd', 'D', 'l', 'L']:
            self.cursor[1] = min(7, self.cursor[1] + 1)
            self.draw_board()
        elif key in ['Return', 'KP_Enter']:
            self.make_player_move()
    
    def rotate_board(self):
        """ボードを90°時計回りに回転"""
        if not self.player_color:
            return
        
        if self.current_player != self.player_color:
            return
        
        self.board = [[self.board[7 - j][i] for j in range(8)] for i in range(8)]
        self.rotation = (self.rotation + 1) % 4
        self.status_label.config(text="ボードを90°時計回りに回転しました！")
        self.draw_board()
    
    def make_player_move(self):
        """プレイヤーの石を置く"""
        if not self.player_color or self.current_player != self.player_color:
            return
        
        row, col = self.cursor
        if self.is_valid_move(row, col, self.current_player):
            self.make_move(row, col)
            self.status_label.config(text=f"({row}, {col}) に石を置きました！")
            self.current_player = 'W' if self.current_player == 'B' else 'B'
            
            if self.check_game_over():
                self.end_game()
            else:
                self.draw_board()
                if self.current_player == self.npc_color:
                    self.root.after(500, self.npc_turn)
        else:
            self.status_label.config(text="そこには置けません！")
    
    def npc_turn(self):
        """NPCのターン（自動）"""
        if self.game_over:
            return
        if self.current_player != self.npc_color:
            return
        
        self.status_label.config(text=f"▼ NPC({'黒' if self.npc_color == 'B' else '白'})のターン ▼")
        
        valid_moves = self.get_valid_moves(self.npc_color)
        if not valid_moves:
            self.status_label.config(text=f"NPCに有効な手がありません。パスします。")
            self.current_player = 'B' if self.current_player == 'W' else 'W'
            self.draw_board()
            if not self.check_game_over():
                self.root.after(300, self.npc_turn)
            return
        
        # 評価して最善手を選ぶ
        scored_moves = []
        for row, col in valid_moves:
            score = self._evaluate_move(row, col, self.npc_color)
            scored_moves.append((score, row, col))
        scored_moves.sort(reverse=True)
        _, row, col = scored_moves[0]
        
        self.make_move(row, col)
        self.status_label.config(text=f"NPCが({row}, {col})に置きました！")
        self.current_player = 'B' if self.current_player == 'W' else 'W'
        
        if self.check_game_over():
            self.end_game()
        else:
            self.draw_board()
    
    def make_move(self, row, col, player=None):
        """石を置いて反転"""
        if player is None:
            player = self.current_player
        
        opponent = 'W' if player == 'B' else 'B'
        self.board[row][col] = player
        
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            to_flip = []
            while (0 <= r < 8 and 0 <= c < 8 and 
                   self.board[r][c] == opponent):
                to_flip.append((r, c))
                r += dr
                c += dc
            if to_flip and (0 <= r < 8 and 0 <= c < 8 and 
                           self.board[r][c] == player):
                for fr, fc in to_flip:
                    self.board[fr][fc] = player
    
    def is_valid_move(self, row, col, player):
        """有効手判定"""
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
            while (0 <= r < 8 and 0 <= c < 8 and 
                   self.board[r][c] == opponent):
                found_opponent = True
                r += dr
                c += dc
            if found_opponent and (0 <= r < 8 and 0 <= c < 8 and 
                                 self.board[r][c] == player):
                return True
        return False
    
    def get_valid_moves(self, player):
        """有効な手のリスト"""
        moves = []
        for i in range(8):
            for j in range(8):
                if self.is_valid_move(i, j, player):
                    moves.append((i, j))
        return moves
    
    def _evaluate_move(self, row, col, player):
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

    def check_game_over(self):
        """ゲーム終了判定"""
        b_moves = self.get_valid_moves('B')
        w_moves = self.get_valid_moves('W')
        
        if not b_moves and not w_moves:
            self.game_over = True
            return True
        
        if not self.get_valid_moves(self.current_player):
            self.status_label.config(text=f"{'あなた' if self.current_player == self.player_color else 'NPC'}に有効な手がありません。パスします。")
            self.current_player = 'W' if self.current_player == 'B' else 'B'
        
        return False
    
    def end_game(self):
        """ゲーム終了"""
        b_count = sum(row.count('B') for row in self.board)
        w_count = sum(row.count('W') for row in self.board)
        
        if b_count > w_count:
            winner = 'B'
        elif w_count > b_count:
            winner = 'W'
        else:
            winner = 'DRAW'
        
        if winner == 'DRAW':
            msg = "★ 引き分け！ ★"
        elif winner == self.player_color:
            msg = f"★ あなたの勝ちです！ ★\n黒: {b_count}個 vs 白: {w_count}個"
        else:
            msg = f"★ NPCの勝ちです... ★\n黒: {b_count}個 vs 白: {w_count}個"
        
        messagebox.showinfo("ゲーム終了", msg)
        self.game_over = True
        self.rotate_btn.config(state='disabled')
    
    def restart_game(self):
        """ゲームを最初から"""
        self.board = self.create_initial_board()
        self.current_player = 'B'
        self.game_over = False
        self.rotation = 0
        self.cursor = [3, 3]
        self.player_color = None
        self.npc_color = None
        
        self.black_btn.config(state='normal')
        self.white_btn.config(state='normal')
        self.rotate_btn.config(state='disabled')
        self.player_label.config(text="あなたの色を選択してください")
        self.status_label.config(text="")
        
        self.draw_board()


def main():
    root = tk.Tk()
    app = OthelloGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
