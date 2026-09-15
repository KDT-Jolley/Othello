#include <QApplication>
#include <QMainWindow>
#include <QLabel>
#include <QPushButton>
#include <QGridLayout>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QMessageBox>
#include <QPixmap>
#include <QTimer>
#include <QPainter>
#include <QCursor>
#include <QImage>
#include <QVector>
#include <QPoint>
#include <QFont>
#include <QCoreApplication>
#include <QStyleSheet>
#include <algorithm>

class OthelloGame : public QMainWindow {
    Q_OBJECT

public:
    OthelloGame(QWidget *parent = nullptr) : QMainWindow(parent) {
        setWindowTitle("オセロ変則版 - ボード回転つき");
        setFixedSize(560, 640);
        
        // ゲーム状態
        for (int i = 0; i < 8; i++)
            for (int j = 0; j < 8; j++)
                board[i][j] = createInitialBoardValue(i, j);
        
        currentPlayer = 'B';
        gameOver = false;
        rotation = 0;
        playerColor = '\0';
        npcColor = '\0';
        difficulty = "medium";
        cursor[0] = 3;
        cursor[1] = 3;
        
        // 画像読み込み
        QString imgDir = QCoreApplication::applicationDirPath();
        blackPixmap = loadImage(imgDir + "/aab4ec96671a3480128142aa0b099350.png", 60, 60);
        whitePixmap = loadImage(imgDir + "/00a9c86c513792f7b8e95df2dadfb190-768x759.png", 60, 60);
        
        // フォールバック
        if (blackPixmap.isNull()) {
            blackPixmap = createFallbackPixmap(60, 60, QColor(0, 0, 0));
        }
        if (whitePixmap.isNull()) {
            whitePixmap = createFallbackPixmap(60, 60, QColor(255, 255, 255));
        }
        
        setupUI();
        drawBoard();
    }

private:
    char board[8][8];
    char currentPlayer;
    bool gameOver;
    int rotation;
    char playerColor;
    char npcColor;
    QString difficulty;
    int cursor[2];
    QPixmap blackPixmap;
    QPixmap whitePixmap;
    
    QWidget *centralWidget;
    QGridLayout *boardLayout;
    QLabel *cells[8][8];
    QLabel *statusLabel;
    QPushButton *rotateBtn;
    QPushButton *restartBtn;
    QLabel *playerLabel;
    QLabel *legendLabel;
    QPushButton *blackBtn;
    QPushButton *whiteBtn;

    QPixmap loadImage(const QString &path, int w, int h) {
        QImage img(path);
        if (img.isNull()) return QPixmap();
        return QPixmap::fromImage(img.scaled(w, h, Qt::KeepAspectRatio, Qt::SmoothTransformation));
    }
    
    QPixmap createFallbackPixmap(int w, int h, const QColor &color) {
        QPixmap pm(w, h);
        pm.fill(color);
        return pm;
    }
    
    char createInitialBoardValue(int i, int j) {
        if (i == 3 && j == 3) return 'W';
        if (i == 3 && j == 4) return 'B';
        if (i == 4 && j == 3) return 'B';
        if (i == 4 && j == 4) return 'W';
        return '.';
    }
    
    void setupUI() {
        centralWidget = new QWidget(this);
        setCentralWidget(centralWidget);
        
        QVBoxLayout *mainLayout = new QVBoxLayout(centralWidget);
        mainLayout->setSpacing(10);
        mainLayout->setContentsMargins(15, 15, 15, 15);
        
        // タイトル
        QLabel *title = new QLabel("🎮 オセロ変則版");
        title->setFont(QFont("Arial", 16, QFont::Bold));
        title->setStyleSheet("color: #e94560;");
        mainLayout->addWidget(title);
        
        // 色選択表示
        playerLabel = new QLabel("★ あなたの色を選択してください ★");
        playerLabel->setFont(QFont("Arial", 12, QFont::Bold));
        playerLabel->setStyleSheet("background-color: #0f3460; color: white; padding: 8px;");
        mainLayout->addWidget(playerLabel);
        
        // 色選択ボタン
        QHBoxLayout *colorBtnLayout = new QHBoxLayout();
        
        blackBtn = new QPushButton("⬛ 黒(Black) - 先攻");
        blackBtn->setFont(QFont("Arial", 11, QFont::Bold));
        blackBtn->setFixedSize(180, 40);
        blackBtn->setStyleSheet("background-color: black; color: white; border: 2px solid #333;");
        connect(blackBtn, &QPushButton::clicked, this, [this]() { selectColor('B'); });
        colorBtnLayout->addWidget(blackBtn);
        
        whiteBtn = new QPushButton("⬜ 白(White) - 後攻");
        whiteBtn->setFont(QFont("Arial", 11, QFont::Bold));
        whiteBtn->setFixedSize(180, 40);
        whiteBtn->setStyleSheet("background-color: white; color: black; border: 2px solid #999;");
        connect(whiteBtn, &QPushButton::clicked, this, [this]() { selectColor('W'); });
        colorBtnLayout->addWidget(whiteBtn);
        
        mainLayout->addLayout(colorBtnLayout);
        
        // 盤面
        boardLayout = new QGridLayout();
        boardLayout->setSpacing(2);
        boardLayout->setContentsMargins(0, 0, 0, 0);
        
        for (int i = 0; i < 8; i++) {
            for (int j = 0; j < 8; j++) {
                cells[i][j] = new QLabel();
                cells[i][j]->setFixedSize(65, 65);
                cells[i][j]->setAlignment(Qt::AlignCenter);
                
                QString style = ((i + j) % 2 == 0) ? 
                    "background-color: #2d5a2d;" : "background-color: #3d7a3d;";
                cells[i][j]->setStyleSheet(style + "border: 1px solid #1a3a1a;");
                
                cells[i][j]->setCursor(Qt::PointingHandCursor);
                cells[i][j]->setScaledContents(true);
                
                // クリックイベント
                int row = i, col = j;
                connect(cells[i][j], &QLabel::clicked, this, [this, row, col]() {
                    if (playerColor && currentPlayer == playerColor) {
                        cursor[0] = row;
                        cursor[1] = col;
                        makePlayerMove();
                    }
                });
                
                boardLayout->addWidget(cells[i][j], i, j);
            }
        }
        
        QFrame *boardFrame = new QFrame();
        boardFrame->setFixedSize(520 + 10, 520 + 10);
        boardFrame->setStyleSheet("background-color: #006400; border: 3px solid #2d5a2d; border-radius: 5px;");
        boardFrame->setLayout(boardLayout);
        
        mainLayout->addWidget(boardFrame, 0, Qt::AlignCenter);
        
        // ステータス
        statusLabel = new QLabel("");
        statusLabel->setFont(QFont("Arial", 11));
        statusLabel->setStyleSheet("background-color: #533483; color: white; padding: 8px; min-height: 40px;");
        mainLayout->addWidget(statusLabel);
        
        // 凡例
        legendLabel = new QLabel("※ 黒=あなた / 白=NPC  （選択時に変動）");
        legendLabel->setFont(QFont("Arial", 9));
        legendLabel->setStyleSheet("color: #aaa;");
        mainLayout->addWidget(legendLabel);
        
        // ボタン
        QHBoxLayout *btnLayout = new QHBoxLayout();
        
        rotateBtn = new QPushButton("🔄 ボードを90°回転");
        rotateBtn->setFont(QFont("Arial", 10, QFont::Bold));
        rotateBtn->setFixedSize(160, 35);
        rotateBtn->setStyleSheet("background-color: #e94560; color: white;");
        rotateBtn->setEnabled(false);
        connect(rotateBtn, &QPushButton::clicked, this, &OthelloGame::rotateBoard);
        btnLayout->addWidget(rotateBtn);
        
        restartBtn = new QPushButton("🔄 最初から");
        restartBtn->setFont(QFont("Arial", 10));
        restartBtn->setFixedSize(100, 35);
        restartBtn->setStyleSheet("background-color: #533483; color: white;");
        connect(restartBtn, &QPushButton::clicked, this, &OthelloGame::restartGame);
        btnLayout->addWidget(restartBtn);
        
        mainLayout->addLayout(btnLayout);
    }
    
    void selectColor(char color) {
        playerColor = color;
        npcColor = (color == 'B') ? 'W' : 'B';
        currentPlayer = 'B';
        
        if (color == 'B') {
            playerLabel->setText("★ あなた：黒(Black) ★  |  NPC：白(White) ★");
            legendLabel->setText("※ あなたの石 = 黒  /  NPCの石 = 白");
        } else {
            playerLabel->setText("★ あなた：白(White) ★  |  NPC：黒(Black) ★");
            legendLabel->setText("※ あなたの石 = 白  /  NPCの石 = 黒");
        }
        
        blackBtn->setEnabled(false);
        whiteBtn->setEnabled(false);
        rotateBtn->setEnabled(true);
        statusLabel->setText(QString("ゲームスタート！ %1が先攻です").arg(color == 'B' ? "黒" : "白"));
        
        drawBoard();
    }
    
    void drawBoard() {
        for (int i = 0; i < 8; i++) {
            for (int j = 0; j < 8; j++) {
                int displayRow = (i + rotation) % 8;
                int displayCol = (j - rotation + 8) % 8;
                
                char cell = board[displayRow][displayCol];
                
                if (cell == 'B') {
                    cells[i][j]->setPixmap(blackPixmap);
                    if (playerColor == 'B') {
                        cells[i][j]->setToolTip("あなたの石");
                    } else if (npcColor == 'B') {
                        cells[i][j]->setToolTip("NPCの石");
                    }
                } else if (cell == 'W') {
                    cells[i][j]->setPixmap(whitePixmap);
                    if (playerColor == 'W') {
                        cells[i][j]->setToolTip("あなたの石");
                    } else if (npcColor == 'W') {
                        cells[i][j]->setToolTip("NPCの石");
                    }
                } else {
                    cells[i][j]->clear();
                    cells[i][j]->setToolTip("");
                }
                
                // カーソル位置
                if (i == cursor[0] && j == cursor[1] && playerColor && currentPlayer == playerColor) {
                    cells[i][j]->setStyleSheet(
                        QString((i + j) % 2 == 0 ? "background-color: #2d5a2d;" : "background-color: #3d7a3d;") +
                        "border: 3px solid #e94560;");
                } else {
                    cells[i][j]->setStyleSheet(
                        QString((i + j) % 2 == 0 ? "background-color: #2d5a2d;" : "background-color: #3d7a3d;") +
                        "border: 1px solid #1a3a1a;");
                }
            }
        }
        
        int bCount = 0, wCount = 0;
        for (int i = 0; i < 8; i++)
            for (int j = 0; j < 8; j++) {
                if (board[i][j] == 'B') bCount++;
                else if (board[i][j] == 'W') wCount++;
            }
        
        QString info = QString("黒(B): %1個  |  白(W): %2個").arg(bCount).arg(wCount);
        if (!gameOver && playerColor) {
            QString turn = (currentPlayer == playerColor) ? "あなた" : "NPC";
            info += QString("  |  手番：%1 (%2)").arg(turn).arg(currentPlayer == 'B' ? "黒" : "白");
        }
        statusLabel->setText(info);
    }
    
    void rotateBoard() {
        if (!playerColor || currentPlayer != playerColor) return;
        
        char newBoard[8][8];
        for (int i = 0; i < 8; i++)
            for (int j = 0; j < 8; j++)
                newBoard[i][j] = board[7 - j][i];
        
        for (int i = 0; i < 8; i++)
            for (int j = 0; j < 8; j++)
                board[i][j] = newBoard[i][j];
        
        rotation = (rotation + 1) % 4;
        statusLabel->setText("ボードを90°時計回りに回転しました！");
        drawBoard();
    }
    
    void makePlayerMove() {
        if (!playerColor || currentPlayer != playerColor) return;
        
        int row = cursor[0], col = cursor[1];
        if (isValidMove(row, col, currentPlayer)) {
            makeMove(row, col);
            statusLabel->setText(QString("(%1, %2) に石を置きました！").arg(row).arg(col));
            currentPlayer = (currentPlayer == 'B') ? 'W' : 'B';
            
            if (checkGameOver()) {
                endGame();
            } else {
                drawBoard();
                if (currentPlayer == npcColor) {
                    QTimer::singleShot(600, this, &OthelloGame::npcTurn);
                }
            }
        } else {
            statusLabel->setText("そこには置けません！");
        }
    }
    
    void npcTurn() {
        if (gameOver || currentPlayer != npcColor) return;
        
        statusLabel->setText(QString("▼ NPC (%1)のターン ▼").arg(npcColor == 'B' ? "黒" : "白"));
        
        auto validMoves = getValidMoves(npcColor);
        if (validMoves.isEmpty()) {
            statusLabel->setText("NPCに有効な手がありません。パスします。");
            currentPlayer = (currentPlayer == 'B') ? 'W' : 'B';
            drawBoard();
            if (!checkGameOver()) {
                QTimer::singleShot(300, this, &OthelloGame::npcTurn);
            }
            return;
        }
        
        // 評価
        struct ScoredMove { int score; int row; int col; };
        QVector<ScoredMove> scored;
        for (auto &m : validMoves) {
            int score = evaluateMove(m.x(), m.y(), npcColor);
            scored.push_back({score, m.x(), m.y()});
        }
        
        std::sort(scored.begin(), scored.end(), [](const ScoredMove &a, const ScoredMove &b) {
            return a.score > b.score;
        });
        
        int row = scored[0].row;
        int col = scored[0].col;
        
        makeMove(row, col);
        statusLabel->setText(QString("NPCが(%1, %2)に置きました！").arg(row).arg(col));
        currentPlayer = (currentPlayer == 'B') ? 'W' : 'B';
        
        if (checkGameOver()) {
            endGame();
        } else {
            drawBoard();
        }
    }
    
    void makeMove(int row, int col, char player = 0) {
        if (player == 0) player = currentPlayer;
        char opponent = (player == 'B') ? 'W' : 'B';
        board[row][col] = player;
        
        int dr[] = {-1, -1, -1, 0, 0, 1, 1, 1};
        int dc[] = {-1, 0, 1, -1, 1, -1, 0, 1};
        
        for (int d = 0; d < 8; d++) {
            int r = row + dr[d], c = col + dc[d];
            QVector<QPoint> toFlip;
            while (r >= 0 && r < 8 && c >= 0 && c < 8 && board[r][c] == opponent) {
                toFlip.push_back(QPoint(r, c));
                r += dr[d];
                c += dc[d];
            }
            if (!toFlip.isEmpty() && r >= 0 && r < 8 && c >= 0 && c < 8 && board[r][c] == player) {
                for (auto &p : toFlip) {
                    board[p.x()][p.y()] = player;
                }
            }
        }
    }
    
    bool isValidMove(int row, int col, char player) {
        if (row < 0 || row > 7 || col < 0 || col > 7) return false;
        if (board[row][col] != '.') return false;
        
        char opponent = (player == 'B') ? 'W' : 'B';
        int dr[] = {-1, -1, -1, 0, 0, 1, 1, 1};
        int dc[] = {-1, 0, 1, -1, 1, -1, 0, 1};
        
        for (int d = 0; d < 8; d++) {
            int r = row + dr[d], c = col + dc[d];
            bool foundOpponent = false;
            while (r >= 0 && r < 8 && c >= 0 && c < 8 && board[r][c] == opponent) {
                foundOpponent = true;
                r += dr[d];
                c += dc[d];
            }
            if (foundOpponent && r >= 0 && r < 8 && c >= 0 && c < 8 && board[r][c] == player) {
                return true;
            }
        }
        return false;
    }
    
    QVector<QPoint> getValidMoves(char player) {
        QVector<QPoint> moves;
        for (int i = 0; i < 8; i++)
            for (int j = 0; j < 8; j++)
                if (isValidMove(i, j, player))
                    moves.push_back(QPoint(i, j));
        return moves;
    }
    
    int evaluateMove(int row, int col, char player) {
        int score = 0;
        if ((row == 0 || row == 7) && (col == 0 || col == 7)) {
            score += 30; // コーナー
        } else if (row == 0 || row == 7 || col == 0 || col == 7) {
            score += 10; // 端
        }
        
        char opponent = (player == 'B') ? 'W' : 'B';
        int dr[] = {-1, -1, -1, 0, 0, 1, 1, 1};
        int dc[] = {-1, 0, 1, -1, 1, -1, 0, 1};
        
        for (int d = 0; d < 8; d++) {
            int r = row + dr[d], c = col + dc[d], count = 0;
            while (r >= 0 && r < 8 && c >= 0 && c < 8 && board[r][c] == opponent) {
                count++;
                r += dr[d];
                c += dc[d];
            }
            if (r >= 0 && r < 8 && c >= 0 && c < 8 && board[r][c] == player) {
                score += count * 2;
            }
        }
        
        // Xマスペナルティ
        if ((row == 0 || row == 7) && (col >= 1 && col <= 6)) score -= 15;
        if ((col == 0 || col == 7) && (row >= 1 && row <= 6)) score -= 15;
        
        return score;
    }
    
    bool checkGameOver() {
        auto bMoves = getValidMoves('B');
        auto wMoves = getValidMoves('W');
        
        if (bMoves.isEmpty() && wMoves.isEmpty()) {
            gameOver = true;
            return true;
        }
        
        if (getValidMoves(currentPlayer).isEmpty()) {
            QString name = (currentPlayer == playerColor) ? "あなた" : "NPC";
            statusLabel->setText(QString("%1に有効な手がありません。パスします。").arg(name));
            currentPlayer = (currentPlayer == 'B') ? 'W' : 'B';
        }
        
        return false;
    }
    
    void endGame() {
        int bCount = 0, wCount = 0;
        for (int i = 0; i < 8; i++)
            for (int j = 0; j < 8; j++) {
                if (board[i][j] == 'B') bCount++;
                else if (board[i][j] == 'W') wCount++;
            }
        
        char winner;
        if (bCount > wCount) winner = 'B';
        else if (wCount > bCount) winner = 'W';
        else winner = 'D';
        
        QString msg;
        if (winner == 'D') {
            msg = "★ 引き分け！ ★";
        } else if (winner == playerColor) {
            msg = QString("★ あなたの勝ちです！ ★\n%1: %2個 vs %3: %4個")
                .arg(winner == 'B' ? "黒" : "白")
                .arg(winner == 'B' ? bCount : wCount)
                .arg(winner == 'B' ? "白" : "黒")
                .arg(winner == 'B' ? wCount : bCount);
        } else {
            msg = QString("★ NPCの勝ちです... ★\n%1: %2個 vs %3: %4個")
                .arg(winner == 'B' ? "黒" : "白")
                .arg(winner == 'B' ? bCount : wCount)
                .arg(winner == 'B' ? "白" : "黒")
                .arg(winner == 'B' ? wCount : bCount);
        }
        
        QMessageBox::information(this, "ゲーム終了", msg);
        gameOver = true;
        rotateBtn->setEnabled(false);
    }
    
    void restartGame() {
        for (int i = 0; i < 8; i++)
            for (int j = 0; j < 8; j++)
                board[i][j] = createInitialBoardValue(i, j);
        
        currentPlayer = 'B';
        gameOver = false;
        rotation = 0;
        cursor[0] = 3;
        cursor[1] = 3;
        playerColor = '\0';
        npcColor = '\0';
        
        blackBtn->setEnabled(true);
        whiteBtn->setEnabled(true);
        playerLabel->setText("★ あなたの色を選択してください ★");
        legendLabel->setText("※ 黒=あなた / 白=NPC  （選択時に変動）");
        statusLabel->clear();
        rotateBtn->setEnabled(false);
        
        drawBoard();
    }
};

#include "main.moc"

int main(int argc, char *argv[]) {
    QApplication app(argc, argv);
    OthelloGame game;
    game.show();
    return app.exec();
}
