import pytest
from othello_game import OthelloGame


class TestOthelloGame:
    @pytest.fixture
    def game(self):
        return OthelloGame()
    
    def test_initial_board(self, game):
        assert game.board[3][3] == 'W'
        assert game.board[3][4] == 'B'
        assert game.board[4][3] == 'B'
        assert game.board[4][4] == 'W'
        assert game.current_player == 'B'
        assert game.game_over == False
        assert game.rotation == 0
        assert game.count_stones('B') == 2
        assert game.count_stones('W') == 2
    
    def test_initial_valid_moves(self, game):
        assert game.is_valid_move(2, 3, 'B') == True
        assert game.is_valid_move(3, 2, 'B') == True
        assert game.is_valid_move(4, 5, 'B') == True
        assert game.is_valid_move(5, 4, 'B') == True
        assert game.is_valid_move(3, 3, 'B') == False
        assert game.is_valid_move(3, 4, 'B') == False
        assert game.is_valid_move(4, 3, 'B') == False
        assert game.is_valid_move(4, 4, 'B') == False
    
    def test_make_move_and_flip(self, game):
        assert game.make_move(2, 3) == True
        assert game.board[2][3] == 'B'
        assert game.board[3][3] == 'B'  # 反転
        assert game.current_player == 'W'
    
    def test_invalid_move_occupied(self, game):
        assert game.make_move(3, 3) == False
        assert game.make_move(3, 4) == False
    
    def test_player_switch_after_move(self, game):
        game.make_move(2, 3)
        assert game.current_player == 'W'
        game.make_move(5, 4)
        assert game.current_player == 'W'  # no valid move, player does not switch
    
    def test_rotate_board(self, game):
        original = [row[:] for row in game.board]
        game.rotate()
        assert game.rotation == 1
        for i in range(8):
            for j in range(8):
                assert game.board[i][j] == original[7-j][i]
        assert game.count_stones('B') == 2
        assert game.count_stones('W') == 2
    
    def test_rotate_back_to_original(self, game):
        original = [row[:] for row in game.board]
        for _ in range(4):
            game.rotate()
        assert game.board == original
        assert game.rotation == 0
    
    def test_rotate_and_play(self, game):
        game.rotate()
        assert game.is_valid_move(2, 3, 'B') == True
        assert game.make_move(2, 3) == True
        assert game.board[2][3] == 'B'
        assert game.current_player == 'W'
    
    def test_get_valid_moves(self, game):
        moves = game.get_valid_moves('B')
        assert isinstance(moves, list)
        for row, col in moves:
            assert game.is_valid_move(row, col, 'B')
    
    def test_game_over_no_moves(self, game):
        for i in range(8):
            for j in range(8):
                if game.board[i][j] == '.':
                    game.board[i][j] = 'B'
        game.current_player = 'W'
        assert game.check_game_over() == True
        assert game.game_over == True
    
    def test_winner_black_wins(self, game):
        game.board[0][0] = 'B'
        game.board[0][1] = 'B'
        game.game_over = True
        winner, b_count, w_count = game.get_winner()
        assert winner == 'B'
        assert b_count == 4
        assert w_count == 2
    
    def test_winner_white_wins(self, game):
        game.board[0][0] = 'W'
        game.board[0][1] = 'W'
        game.game_over = True
        winner, b_count, w_count = game.get_winner()
        assert winner == 'W'
        assert w_count == 4
        assert b_count == 2
    
    def test_draw(self, game):
        game.board[0][0] = 'B'
        game.board[0][1] = 'W'
        game.game_over = True
        winner, b_count, w_count = game.get_winner()
        assert winner == 'DRAW'
        assert b_count == 3
        assert w_count == 3
    
    def test_multiple_flips(self, game):
        # 横方向にWが並び、両端にBがある状況を作成
        game.board[2][1] = 'B'  # 左端にB
        game.board[2][2] = 'W'
        game.board[2][3] = '.'
        game.board[2][4] = 'W'
        game.board[2][5] = 'B'  # 右端にB
        game.current_player = 'B'
        assert game.make_move(2, 3) == True
        assert game.board[2][3] == 'B'
        assert game.board[2][2] == 'B'  # 反転
        assert game.board[2][4] == 'B'  # 反転
    
    def test_cursor_bounds(self, game):
        assert 0 <= game.cursor[0] <= 7
        assert 0 <= game.cursor[1] <= 7
    
    def test_no_flips_when_not_enclosed(self, game):
        game.board[2][3] = 'B'
        game.board[3][4] = '.'  # 初期配置のBを無効化
        game.current_player = 'W'
        assert game.make_move(2, 4) == False
    
    def test_pass_when_no_valid_moves(self, game):
        # 白に有効手が無いが、黒には有効手がある状況を作る
        # 初期盤面で、黒の有効手をすべて潰す
        for i in range(8):
            for j in range(8):
                if game.board[i][j] == '.' and (i, j) != (2, 3) and (i, j) != (3, 2) and (i, j) != (4, 5) and (i, j) != (5, 4):
                    game.board[i][j] = 'B'
        game.current_player = 'W'
        game.check_game_over()
        assert game.current_player == 'B'
    
    def test_rotation_preserves_game_state(self, game):
        game.make_move(2, 3)
        assert game.current_player == 'W'
        game.rotate()
        assert game.count_stones('B') == 4
        assert game.count_stones('W') == 1
        game.make_move(3, 4)
        assert game.current_player == 'B'
    
    def test_continuous_play(self, game):
        moves_made = 0
        for _ in range(20):
            moves = game.get_valid_moves(game.current_player)
            if moves:
                row, col = moves[0]
                if game.make_move(row, col):
                    moves_made += 1
                    game.switch_player()
            else:
                game.switch_player()
            if game.check_game_over():
                break
        assert moves_made > 0
    
    def test_board_dimensions(self, game):
        assert len(game.board) == 8
        for row in game.board:
            assert len(row) == 8
    
    def test_all_cells_valid_values(self, game):
        valid_values = {'B', 'W', '.'}
        for row in game.board:
            for cell in row:
                assert cell in valid_values
    
    def test_make_move_updates_board(self, game):
        initial_b = game.count_stones('B')
        initial_w = game.count_stones('W')
        game.make_move(2, 3)
        new_b = game.count_stones('B')
        new_w = game.count_stones('W')
        assert new_b > initial_b
        assert new_w < initial_w
    
    def test_rotated_view(self, game):
        view = game.rotated_view()
        assert len(view) == 8
        for row in view:
            assert len(row) == 8
        assert view == game.board
    
    def test_rotated_view_after_rotation(self, game):
        game.rotate()
        view = game.rotated_view()
        assert view == game.board
    
    def test_rotate_multiple_times(self, game):
        original = [row[:] for row in game.board]
        for i in range(4):
            game.rotate()
            view = game.rotated_view()
            if i == 1:
                for x in range(8):
                    for y in range(8):
                        assert view[x][y] == original[7-x][7-y]
            elif i == 3:
                assert view == original
    
    def test_make_move_board_state_after_rotation(self, game):
        game.rotate()
        game.make_move(2, 3)
        assert game.board[2][3] == 'B'
        game.rotate()
        game.rotate()
        assert game.rotation == 3
    
    def test_game_can_continue_after_rotation(self, game):
        game.make_move(2, 3)
        game.rotate()
        valid_moves = game.get_valid_moves('W')
        assert len(valid_moves) >= 0
        assert isinstance(valid_moves, list)
    
    def test_cursor_moves_within_bounds(self, game):
        game.cursor = [3, 0]
        game.cursor[1] = max(0, game.cursor[1] - 1)
        assert game.cursor[1] == 0
        game.cursor = [3, 7]
        game.cursor[1] = min(7, game.cursor[1] + 1)
        assert game.cursor[1] == 7
    
    def test_display_board_output(self, game, capsys):
        game.display_board()
        captured = capsys.readouterr()
        assert "黒(B): 2個" in captured.out
        assert "白(W): 2個" in captured.out
        assert "手番:" in captured.out
        assert "カーソル:" in captured.out
    
    def test_game_initial_state(self, game):
        assert not game.game_over
        assert game.current_player == 'B'
        assert game.get_valid_moves('B') != []
    
    def test_invalid_coordinates(self, game):
        assert game.is_valid_move(-1, 3, 'B') == False
        assert game.is_valid_move(8, 3, 'B') == False
        assert game.is_valid_move(3, -1, 'B') == False
        assert game.is_valid_move(3, 8, 'B') == False
    
    def test_full_board_scenario(self, game):
        for i in range(8):
            for j in range(8):
                game.board[i][j] = 'B' if (i + j) % 2 == 0 else 'W'
        game.game_over = True
        winner, b, w = game.get_winner()
        assert winner in ['B', 'W', 'DRAW']
        assert b + w == 64
    
    def test_rotation_does_not_change_stone_count(self, game):
        initial_b = game.count_stones('B')
        initial_w = game.count_stones('W')
        for _ in range(3):
            game.rotate()
        assert game.count_stones('B') == initial_b
        assert game.count_stones('W') == initial_w

    # ---------- NPC 関連テスト ----------
    def test_npc_difficulty_default(self, game):
        assert game.difficulty == 'medium'
    
    def test_npc_make_move_easy(self, game):
        game.difficulty = 'easy'
        game.player_color = 'B'
        game.npc_color = 'W'
        game.current_player = 'W'
        
        valid_moves = game.get_valid_moves('W')
        if valid_moves:
            result = game.npc_make_move()
            assert result == True
            # 石が置かれている
            assert game.count_stones('W') > 2
    
    def test_npc_make_move_medium(self, game):
        game.difficulty = 'medium'
        game.player_color = 'B'
        game.npc_color = 'W'
        game.current_player = 'W'
        
        valid_moves = game.get_valid_moves('W')
        if valid_moves:
            initial_w = game.count_stones('W')
            result = game.npc_make_move()
            assert result == True
            assert game.count_stones('W') > initial_w
    
    def test_npc_make_move_no_valid_moves(self, game):
        game.difficulty = 'easy'
        game.player_color = 'B'
        game.npc_color = 'W'
        game.current_player = 'W'
        
        # NPCの有効手をなくす
        for i in range(8):
            for j in range(8):
                if game.board[i][j] == '.':
                    game.board[i][j] = 'B'
        
        result = game.npc_make_move()
        assert result == False
    
    def test_npc_evaluates_corner_high(self, game):
        score = game._evaluate_move(0, 0, 'B')
        assert score >= 30
    
    def test_npc_evaluates_edge_medium(self, game):
        score = game._evaluate_move(0, 3, 'B')
        assert score >= 10
    
    def test_npc_penalizes_x_square(self, game):
        score = game._evaluate_move(1, 1, 'B')
        assert score < 0
    
    def test_player_color_selection_black(self, game):
        game.player_color = 'B'
        game.npc_color = 'W'
        assert game.player_color == 'B'
        assert game.npc_color == 'W'
    
    def test_player_color_selection_white(self, game):
        game.player_color = 'W'
        game.npc_color = 'B'
        assert game.player_color == 'W'
        assert game.npc_color == 'B'
    
    def test_display_board_with_player_color(self, game, capsys):
        game.player_color = 'B'
        game.npc_color = 'W'
        game.display_board()
        captured = capsys.readouterr()
        assert "あなた" in captured.out or "NPC" in captured.out
    
    def test_full_game_initialization(self, game):
        game.player_color = 'B'
        game.npc_color = 'W'
        game.current_player = 'B'
        game.rotation = 0
        assert game.player_color == 'B'
        assert game.npc_color == 'W'
        assert game.current_player == 'B'
        assert game.rotation == 0
        assert not game.game_over
