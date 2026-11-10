"""
オセロ GUI ゲーム（pygame による画像表示版）
ボード回転機能付き。
tkinter/PIL が使えない場合にこちらを使います。

操作：
  ← ↑ ↓ →    : カーソル移動
  Enter      : 石を置く
  R          : ボードを 90° 回転
  Q          : ゲーム終了
"""

import pygame


def main():
    """メイン関数"""
    # pygame 初期化
    pygame.init()
    screen = pygame.display.set_mode((640, 720))
    pygame.display.set_caption("オセロ GUI - ボード回転つき版")
    clock = pygame.time.Clock()

    # オセロゲームのロジック
    board: list[list[str]] = [['.' for _ in range(8)] for _ in range(8)]
    board[3][3] = 'W'
    board[3][4] = 'B'
    board[4][3] = 'B'
    board[4][4] = 'W'

    current_player: str = 'B'   # B: Black, W: White
    cursor: list[int] = [3, 3]  # カーソル位置 [row, col]
    rotation: int = 0           # 回転回数（0:通常，1:90°，2:180°，3:270°）

    colors = {
        'black': (50, 50, 50),
        'white': (240, 240, 240),
        'board_bg': (34, 176, 98),     # オセロの緑色
        'grid_line': (255, 255, 255),   # 盤面の白線
        'cursor': (255, 204, 0),         # カーソルの黄色
        'highlight': (100, 180, 140),    # 有効手の青色
        'bg_dark': (30, 30, 30),
        'text_light': (240, 240, 240),
        'text_dim': (150, 150, 150),
    }

    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    status_label: list[pygame.Surface] | None = [None] * 8

    def is_valid_move(row: int, col: int, player: str) -> bool:
        """有効手の判定"""
        if not (0 <= row < 8 and 0 <= col < 8):
            return False
        if board[row][col] != '.':
            return False

        opponent = 'W' if player == 'B' else 'B'
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]

        for dr, dc in directions:
            r, c = row + dr, col + dc
            found_opponent = False
            while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == opponent:
                found_opponent = True
                r += dr
                c += dc
            if found_opponent and 0 <= r < 8 and 0 <= c < 8 and board[r][c] == player:
                return True
        return False

    def get_valid_moves(player: str):
        """有効手の座標リストを取得"""
        moves = []
        for i in range(8):
            for j in range(8):
                if is_valid_move(i, j, player):
                    moves.append((i, j))
        return moves

    def make_move(row: int, col: int) -> bool:
        """石を置く"""
        if not (0 <= row < 8 and 0 <= col < 8):
            return False
        if board[row][col] != '.':
            return False

        player = current_player
        opponent = 'W' if player == 'B' else 'B'
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),           (0, 1),
                      (1, -1),  (1, 0),  (1, 1)]

        board[row][col] = player

        for dr, dc in directions:
            r, c = row + dr, col + dc
            to_flip = []
            while 0 <= r < 8 and 0 <= c < 8 and board[r][c] == opponent:
                to_flip.append((r, c))
                r += dr
                c += dc
            if to_flip and 0 <= r < 8 and 0 <= c < 8 and board[r][c] == player:
                for fr, fc in to_flip:
                    board[fr][fc] = player

        current_player = 'W' if current_player == 'B' else 'B'
        return True

    def rotate_board():
        """ボードを 90° 回転"""
        new_board = [[board[7 - j][i] for j in range(8)] for i in range(8)]
        board[:] = new_board[:]
        rotation = (rotation + 1) % 4

    def count_stones(player: str) -> int:
        return sum(row.count(player) for row in board)

    # ゲームループ
    running = True
    while running:
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                key = event.key
                dr, dc = 0, 0

                if key == pygame.K_UP:
                    cursor[0] = max(0, min(7, cursor[0] - 1))
                elif key == pygame.K_DOWN:
                    cursor[0] = max(0, min(7, cursor[0] + 1))
                elif key == pygame.K_LEFT:
                    cursor[1] = max(0, min(7, cursor[1] - 1))
                elif key == pygame.K_RIGHT:
                    cursor[1] = max(0, min(7, cursor[1] + 1))
                elif key == pygame.K_RETURN:
                    row, col = cursor
                    if make_move(row, col):
                        print(f"\n{row},{col} に石を置きました！")

        # 有効手のハイライト
        valid_moves = get_valid_moves(current_player)
        cell_size = 64
        margin_x, margin_y = 52, 16

        for row, col in valid_moves:
            x = margin_x + col * cell_size
            y = margin_y + row * cell_size
            pygame.draw.rect(screen, colors['highlight'], (x, y, cell_size, cell_size), 1)

        # タイトル・盤面の描画
        screen.fill(colors['bg_dark'])

        title = font.render("オセロ", center=True, size=(640 - 20, None))
        subtitle = small_font.render("ボード回転つき版", center=True)
        screen.blit(title, (310, 10))
        screen.blit(subtitle, (290, 58))

        # 盤面描画（画像として）
        for row in board:
            for col_idx, cell in enumerate(row):
                x = margin_x + col_idx * cell_size
                y = margin_y + row * cell_size
                pygame.draw.rect(screen, colors['board_bg'], (x, y, cell_size, cell_size))

                if cell == 'B':
                    pygame.draw.circle(screen, colors['black'], (x + 32, y + 32), 28)
                    # 光の表現
                    pygame.draw.circle(screen, (40, 40, 40), (x + 32, y + 32), 15)
                elif cell == 'W':
                    pygame.draw.circle(screen, colors['white'], (x + 32, y + 32), 28)

        # カーソル
        cx = margin_x + cursor[1] * cell_size
        cy = margin_y + cursor[0] * cell_size
        pygame.draw.rect(
            screen, colors['cursor'],
            (cx - 2, cy - 2, 68, 68),
            width=3
        )

        # プレイヤー情報・石の数
        player_name = "あなた" if current_player == 'B' else "NPC"
        color_str = "黒" if current_player == 'B' else "白"
        info_text = font.render(
            f"{player_name}: {color_str} | 残手：{len(valid_moves)}",
            center=True, size=(580, None)
        )
        screen.blit(info_text, (310, 680))

        b_count = count_stones('B')
        w_count = count_stones('W')
        score_text = font.render(
            f"黒：{b_count}個   |   白：{w_count}個",
            center=True, size=(580, None)
        )
        screen.blit(score_text, (310, 720))

        pygame.display.flip()
        clock.tick(60)

    print("\nゲーム終了")
    pygame.quit()


if __name__ == '__main__':
    main()

