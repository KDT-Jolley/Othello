"""
オセロ GUI ゲーム (tkinter + Pillow) - osero-illust1.png / osero-illust2.png

必要な画像ファイル:
  C:\Users\koyo\Documents\Othello\osero-illust1.png   ← 黒の石
  C:\Users\koyo\Documents\Othello\osero-illust2.png    ← 白の石

操作:
  ← ↑ ↓ →    : カーソル移動
  Enter      : 石を置く
  R          : ボードを 90°回転
  Q          : ゲーム終了
"""

import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image


class OthelloGUI:
    """オセロ GUI ゲーム (tkinter + Pillow)"""

    def __init__(self, root):
        self.root = root
        self.root.title("オセロ GUI - ボード回転つき版")
        self.root.resizable(False, False)

        # ゲーム状態
        board: list[list[str]] = [['.' for _ in range(8)] for _ in range(8)]
        board[3][3] = 'W'
        board[3][4] = 'B'
        board[4][3] = 'B'
        board[4][4] = 'W'

        self.current_player: str = 'B'   # B: Black, W: White
        self.cursor: list[int] = [3, 3]  # カーソル位置 [row, col]
        self.rotation: int = 0           # 回転回数 (0:通常，1:90°,2:180°,3:270°)

        # 画像パス
        BLACK_IMAGE_PATH = "osero-illust1.png"   # 黒の石
        WHITE_IMAGE_PATH = "osero-illust2.png"    # 白の石

        self.cell_size = 65
        self.board_size = 8 * self.cell_size
        self.padding = 40

        # キャンバス作成
        canvas_width = self.board_size + self.padding * 2
        canvas_height = self.board_size + self.padding * 2 + 70
        self.canvas = tk.Canvas(
            self.root,
            width=canvas_width,
            height=canvas_height,
            bg='#1a1a2e',
            highlightthickness=0
        )
        self.canvas.pack(pady=5)

        # 画像読み込み (Pillow を使って)
        self.black_img = self.load_image(BLACK_IMAGE_PATH, (64, 64))
        self.white_img = self.load_image(WHITE_IMAGE_PATH, (64, 64))

        # UI コンポーネント作成
        self._create_ui()
        self.draw_board()

    def load_image(self, path: str, size: tuple[int, int]) -> Image.Image | None:
        """画像を読み込んでサイズ変更"""
        try:
            img = Image.open(path)
            if 'P' in img.getbands():  # RGBA など
                img = img.convert('RGBA')
            img = img.resize(size, Image.Resampling.LANCZOS)
            return img
        except FileNotFoundError:
            print(f"⚠️ 画像が見つかりません：{path}")
            return None
        except Exception as e:
            print(f"⚠️ 画像読み込みエラー：{path} - {e}")
            return None

    def _create_ui(self):
        """UI コンポーネント作成"""

        # タイトルフレーム
        title_frame = tk.Frame(self.root, bg='#16213e')
        title_frame.pack(fill='x', padx=20)

        title_label = ttk.Label(
            title_frame, text="🎮 オセロ変則版", font=('MS PGothic', 18, 'bold'),
            bg='#16213e', fg='#e94560'
        )
        title_label.pack(pady=(10, 0))

        # 情報フレーム
        info_frame = tk.Frame(self.root, bg='#0f3460')
        info_frame.pack(fill='x', padx=20, pady=5)

        self.player_label = ttk.Label(
            info_frame, text="あなたの色を選択してください", font=('MS PGothic', 12),
            bg='#0f3460', fg='#fff'
        )
        self.player_label.pack(pady=5)

        color_frame = tk.Frame(info_frame, bg='#0f3460')
        color_frame.pack()

        self.black_btn = ttk.Button(
            color_frame, text="⬛ 黒 (Black) - 先攻", font=('MS PGothic', 10),
            command=lambda: self.select_color('B'), state='disabled'
        )
        self.black_btn.pack(side='left', padx=5)

        self.white_btn = ttk.Button(
            color_frame, text="⬜ 白 (White) - 後攻", font=('MS PGothic', 10),
            command=lambda: self.select_color('W'), state='disabled'
        )
        self.white_btn.pack(side='left', padx=5)

        # ステータスフレーム
        self.status_frame = tk.Frame(self.root, bg='#533483')
        self.status_frame.pack(fill='x', padx=20, pady=5)

        self.status_label = ttk.Label(
            self.status_frame, text="", font=('MS PGothic', 11), bg='#533483', fg='#fff'
        )
        self.status_label.pack()

        # ボタンフレーム
        btn_frame = tk.Frame(self.root, bg='#1a1a2e')
        btn_frame.pack(pady=5)

        self.rotate_btn = ttk.Button(
            btn_frame, text="🔄 ボードを 90°回転", command=lambda: self.rotate_board(), state='disabled'
        )
        self.rotate_btn.pack(side='left', padx=10)

        self.restart_btn = ttk.Button(btn_frame, text="🔄 最初から", command=self.restart_game)
        self.restart_btn.pack(side='right', padx=10)

        # ヘルプテキスト
        self.help_label = tk.Label(
            self.root, text="操作：クリックで石を置く | R キーで回転 | Q で終了",
            font=('MS PGothic', 9), fg='#aaa'
        )
        self.help_label.pack(pady=5)

    def select_color(self, color: str):
        """プレイヤーが色を選択"""
        self.player_color = color
        self.npc_color = 'W' if color == 'B' else 'B'
        self.current_player = 'B'  # 黒が先攻

        text_black = "黒" if color == 'B' else "白"
        text_npc = "白" if color == 'B' else "黒"
        self.player_label.config(text=f"あなた：{text_black} | NPC: {text_npc}")
        self.black_btn.config(state='disabled')
        self.white_btn.config(state='disabled')
        self.rotate_btn.config(state='normal')
        self.status_label.config(text="ゲームスタート！")

    def draw_board(self):
        """盤面を描画"""
        self.canvas.delete("all")

        # タイトル・サブタイトル
        self.canvas.create_text(310, 10, text="🎮 オセロ", font=('MS PGothic', 36, 'bold'), fill='#e94560')
        self.canvas.create_text(260, 38, text="ボード回転つき版", font=('MS PGothic', 12), fill='#aaa')

        # 盤面背景（緑）
        x1 = self.padding - 5
        y1 = self.padding - 5
        x2 = self.padding + self.board_size + 5
        y2 = self.padding + self.board_size + 5
        self.canvas.create_rectangle(x1, y1, x2, y2, fill='#006400', outline='#2d5a2d', width=2)

        # マス目描画（画像用）
        for i in range(8):
            for j in range(8):
                cell_x = self.padding + j * self.cell_size
                cell_y = self.padding + i * self.cell_size
                cell_w = self.cell_size
                cell_h = self.cell_size

                # チェスボード風チェック柄
                if (i + j) % 2 == 0:
                    fill_color = '#2d5a2d'
                else:
                    fill_color = '#3d7a3d'

                self.canvas.create_rectangle(
                    cell_x, cell_y,
                    cell_x + cell_w, cell_y + cell_h,
                    fill=fill_color, outline='#1a3a1a', width=0.5
                )

        # 石の描画（回転表示を考慮）
        for i in range(8):
            for j in range(8):
                display_row = (i + self.rotation) % 8
                display_col = (j - self.rotation) % 8
                if 0 <= display_row < 8 and 0 <= display_col < 8:
                    cell_value = board[display_row][display_col]

                    cell_x = self.padding + display_col * self.cell_size
                    cell_y = self.padding + display_row * self.cell_size
                    cx, cy = cell_x + self.cell_size // 2, cell_y + self.cell_size // 2

                    if cell_value == 'B':
                        # 黒の石：画像を使用（回転）またはフォールバック
                        if self.black_img is not None:
                            angle = self.rotation * 90
                            rotated_black = Image.new('RGBA', (64, 64), (50, 50, 50))
                            # 実際の画像は描画しない（簡易版）
                        else:
                            # フォールバック：黒円
                            self.canvas.create_oval(
                                cx - 28, cy - 28, cx + 28, cy + 28,
                                fill='#333333', outline='', width=0
                            )
                    elif cell_value == 'W':
                        # 白の石：画像を使用（回転）またはフォールバック
                        if self.white_img is not None:
                            angle = self.rotation * 90
                            rotated_white = Image.new('RGBA', (64, 64), (255, 255, 255))
                        else:
                            # フォールバック：白円
                            self.canvas.create_oval(
                                cx - 28, cy - 28, cx + 28, cy + 28,
                                fill='#dddddd', outline='', width=0
                            )

        # カーソル表示（点線）
        cursor_x = self.padding + self.cursor[1] * self.cell_size
        cursor_y = self.padding + self.cursor[0] * self.cell_size
        self.canvas.create_rectangle(
            cursor_x, cursor_y,
            cursor_x + self.cell_size, cursor_y + self.cell_size,
            outline='#e94560', width=3, dash=(4, 2)
        )

        # 石の数表示
        b_count = sum(row.count('B') for row in board)
        w_count = sum(row.count('W') for row in board)

        info_text = (f"黒 (B): {b_count}個 | 白 (W): {w_count}個\n"
                     f"残手：{len(self.get_valid_moves(self.current_player))}")
        if not self.game_over and self.player_color:
            player_name = "あなた" if self.current_player == self.player_color else "NPC"
            info_text += f"\n手番：{player_name}"

        info_label = tk.Label(
            self.root, text=info_text, font=('MS PGothic', 9), fg='#aaa', bg='#1a1a2e'
        )
        info_label.place(x=self.padding + self.board_size // 2 - 50, y=cursor_y + self.cell_size + 40)

    def on_key_press(self, event):
        """キーボード操作"""
        if not self.player_color:
            return

        key = event.keysym
        if key in ('q', 'Q'):
            self.root.quit()
            return

        if key == 'r' or key == 'R':
            self.rotate_board()
        elif key == 'Up' or key == 'w' or key == 'W' or key == 'K':
            self.cursor[0] = max(0, min(7, self.cursor[0] - 1))
            self.draw_board()
        elif key == 'Down' or key == 's' or key == 'S' or key == 'J':
            self.cursor[0] = min(7, self.cursor[0] + 1)
            self.draw_board()
        elif key == 'Left' or key == 'a' or key == 'A' or key == 'H':
            self.cursor[1] = max(0, min(7, self.cursor[1] - 1))
            self.draw_board()
        elif key == 'Right' or key == 'd' or key == 'D' or key == 'L':
            self.cursor[1] = min(7, self.cursor[1] + 1)
            self.draw_board()

    def rotate_board(self):
        """ボードを 90°回転（非破壊的）"""
        if not self.player_color:
            return
        if self.current_player != 'B':
            return

        # 物理的に盤面を変換しない（表示用の rotation のみ）
        self.rotation = (self.rotation + 1) % 4
        print(f"  ボードを {self.rotation * 90}°回転しました！")
        self.draw_board()

    def make_player_move(self):
        """プレイヤーの石を置く"""
        if not self.player_color or self.current_player != self.player_color:
            return

        row, col = self.cursor
        if self.is_valid_move(row, col, self.current_player):
            # 石を置く（回転考慮なし - ゲームロジックは常に論理的座標）
            board[row][col] = self.current_player
            directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

            for dr, dc in directions:
                r, c = row + dr, col + dc
                to_flip = []
                while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == 'W' if self.current_player == 'B' else 'B':
                    to_flip.append((r, c))
                    r += dr
                    c += dc

                if to_flip and (0 <= r < 8 and 0 <= c < 8 and board[r][c] == self.current_player):
                    for fr, fc in to_flip:
                        board[fr][fc] = self.current_player

            # 手番交代
            self.current_player = 'W' if self.current_player == 'B' else 'B'
        else:
            self.status_label.config(text="そこには置けません！")

        self.draw_board()

    def is_valid_move(self, row: int, col: int, player: str) -> bool:
        """有効手の判定（常に論理的座標）"""
        if not (0 <= row < 8 and 0 <= col < 8):
            return False
        if board[row][col] != '.':
            return False

        opponent = 'W' if player == 'B' else 'B'
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            found = False
            while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == opponent:
                found = True
                r += dr
                c += dc

            if found and (0 <= r < 8 and 0 <= c < 8 and board[r][c] == player):
                return True
        return False

    def get_valid_moves(self, player: str) -> list[tuple[int, int]]:
        """有効な手のリスト"""
        moves = []
        for i in range(8):
            for j in range(8):
                if self.is_valid_move(i, j, player):
                    moves.append((i, j))
        return moves

    def check_game_over(self) -> bool:
        """ゲーム終了判定"""
        b_moves = self.get_valid_moves('B')
        w_moves = self.get_valid_moves('W')

        if not b_moves and not w_moves:
            self.game_over = True
            return True

        if not self.get_valid_moves(self.current_player):
            opponent_name = "あなた" if self.current_player != self.player_color else "NPC"
            self.status_label.config(text=f"{opponent_name} に有効な手がありません。パスします。")
            self.current_player = 'W' if self.current_player == 'B' else 'B'
        return False

    def end_game(self):
        """ゲーム終了"""
        b_count = sum(row.count('B') for row in board)
        w_count = sum(row.count('W') for row in board)

        if b_count > w_count:
            winner = '黒 (Black)'
        elif w_count > b_count:
            winner = '白 (White)'
        else:
            winner = '引き分け'

        msg = f"★ ゲーム終了 ★\n\n{winner} の勝ち！\n黒：{b_count}個 | 白：{w_count}個"
        messagebox.showinfo("ゲーム終了", msg)
        self.game_over = True

    def restart_game(self):
        """ゲームをリセット"""
        board[3][3] = 'W'
        board[3][4] = 'B'
        board[4][3] = 'B'
        board[4][4] = 'W'

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
    """メイン関数"""
    root = tk.Tk()
    app = OthelloGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
