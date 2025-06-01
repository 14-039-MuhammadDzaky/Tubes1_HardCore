from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
import math
from game.util import get_direction, position_equals


class HcBot(BaseLogic):
    def __init__(self):
        self.goal_position = None
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # Arah dasar: Timur, Selatan, Barat, Utara (untuk roaming fallback)
        self.current_direction_index = 0

    def manhattan_distance(self, pos1: Position, pos2: Position) -> int:
        """Menghitung jarak Manhattan antara dua posisi."""
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)

    def get_diamonds_in_radius(self, center_pos: Position, radius: int, diamonds_on_board: list[GameObject]) -> list[GameObject]:
        """Mengembalikan daftar diamond dalam radius Manhattan tertentu dari posisi bot."""
        diamonds_in_range = []
        for diamond in diamonds_on_board:
            if self.manhattan_distance(center_pos, diamond.position) <= radius:
                diamonds_in_range.append(diamond)
        return diamonds_in_range

    def update_goal_position(self, board_bot: GameObject, board: Board):
        """
        Menentukan posisi tujuan (goal_position) bot berdasarkan prioritas.
        Strategi Greedy digunakan untuk memilih opsi terbaik pada saat itu:
        1. Pulang ke base jika inventaris penuh
        2. Menekan tombol merah jika tidak ada diamond di radius tertentu
        3. Ambil diamond dengan nilai terbaik per jarak
        4. Roaming (fallback jika tidak ada target)
        """
        current_position = board_bot.position
        inventory_size = board_bot.properties.inventory_size if board_bot.properties.inventory_size is not None else 5
        
        # Kumpulan objek di papan permainan
        diamonds_on_board = [obj for obj in board.game_objects if obj.type == "DiamondGameObject"]
        red_button_on_board = next((obj for obj in board.game_objects if obj.type == "RedButtonGameObject"), None)

        # Reset tujuan dan skor terbaik
        self.goal_position = None
        best_overall_score = -1.0

        # (1) Strategi Greedy Prioritas Tinggi: Pulang ke base jika inventaris penuh
        if board_bot.properties.diamonds >= inventory_size:
            base_position = board_bot.properties.base
            self.goal_position = base_position

            # Jika sudah di base, tidak perlu gerak lagi
            if position_equals(current_position, self.goal_position):
                return 
        
        # (2) Strategi Heuristik Greedy: Evaluasi tombol merah atau diamond terbaik
        if self.goal_position is None: 
            DIAMOND_CHECK_RADIUS_FOR_BUTTON = 15  # Radius untuk mengecek apakah ada diamond di sekitar

            diamonds_in_current_radius = self.get_diamonds_in_radius(current_position, DIAMOND_CHECK_RADIUS_FOR_BUTTON, diamonds_on_board)
            
            # (2a) Tombol Merah diprioritaskan jika tidak ada diamond di radius (Greedy Conditional)
            if red_button_on_board and not diamonds_in_current_radius:
                self.goal_position = red_button_on_board.position
                best_overall_score = float('inf')  # Skor tertinggi untuk memastikan tombol dipilih
                print(f"Menggunakan Tombol Merah: Tidak ada diamond dalam radius {DIAMOND_CHECK_RADIUS_FOR_BUTTON}.")
                return 

            # (2b) Evaluasi semua diamond berdasarkan nilai / jarak (Greedy Heuristic)
            for diamond in diamonds_on_board:
                diamond_value = diamond.properties.points if diamond.properties and diamond.properties.points is not None else 1
                
                # Prioritaskan diamond bernilai 1 jika hanya satu slot tersisa
                if board_bot.properties.diamonds == (inventory_size - 1) and diamond_value != 1:
                    continue 

                distance = self.manhattan_distance(current_position, diamond.position)
                
                if distance == 0: 
                    current_score = float('inf')  # Sudah berada di atas diamond
                else:
                    # Skor berbasis rasio nilai terhadap jarak (Greedy Value/Cost Ratio)
                    current_score = diamond_value / distance 
                
                # Simpan diamond dengan skor terbaik
                if current_score > best_overall_score:
                    best_overall_score = current_score
                    self.goal_position = diamond.position 

        # Jika tidak ada tujuan ditemukan, self.goal_position akan tetap None => mode roaming

    def next_move(self, board_bot: GameObject, board: Board):
        """
        Menghitung langkah bot selanjutnya.
        Menggunakan hasil goal_position dari update_goal_position dan memilih arah terbaik.
        """
        current_position = board_bot.position
        
        # Perbarui posisi tujuan berdasarkan strategi greedy
        self.update_goal_position(board_bot, board)

        delta_x, delta_y = 0, 0

        # (3) Pergerakan menuju goal_position (Greedy Direct Move)
        if self.goal_position:
            # Jika sudah sampai tujuan, reset agar evaluasi ulang di giliran berikutnya
            if position_equals(current_position, self.goal_position):
                # Berhenti jika sudah di base dan inventaris penuh
                if board_bot.properties.diamonds >= (board_bot.properties.inventory_size if board_bot.properties.inventory_size is not None else 5) and position_equals(current_position, board_bot.properties.base):
                    return (0, 0)
                self.goal_position = None
                return (0, 0)

            # Hitung arah ke goal
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
            )
            
            # (4) Fallback Greedy: Validasi langkah, coba alternatif jika terhalang
            if not board.is_valid_move(current_position, delta_x, delta_y):
                # Coba bergerak hanya ke arah X atau Y
                if delta_x != 0 and board.is_valid_move(current_position, delta_x, 0):
                    delta_y = 0 
                elif delta_y != 0 and board.is_valid_move(current_position, 0, delta_y):
                    delta_x = 0 
                else:
                    # Roaming fallback: coba arah berdasarkan rotasi default
                    temp_delta_x, temp_delta_y = self.directions[self.current_direction_index]
                    if board.is_valid_move(current_position, temp_delta_x, temp_delta_y):
                        delta_x, delta_y = temp_delta_x, temp_delta_y
                        self.current_direction_index = (self.current_direction_index + 1) % len(self.directions)
                    else:
                        return (0, 0)  # Semua arah buntu
        
        # (5) Roaming fallback jika tidak ada goal_position (Greedy Random Roaming)
        if not self.goal_position:
            temp_delta_x, temp_delta_y = self.directions[self.current_direction_index]
            if board.is_valid_move(current_position, temp_delta_x, temp_delta_y):
                delta_x, delta_y = temp_delta_x, temp_delta_y
                self.current_direction_index = (self.current_direction_index + 1) % len(self.directions)
            else:
                # Coba arah lain secara rotasi jika arah saat ini buntu
                for _ in range(len(self.directions)):
                    self.current_direction_index = (self.current_direction_index + 1) % len(self.directions)
                    temp_delta_x, temp_delta_y = self.directions[self.current_direction_index]
                    if board.is_valid_move(current_position, temp_delta_x, temp_delta_y):
                        delta_x, delta_y = temp_delta_x, temp_delta_y
                        break
                else:
                    return (0, 0)  # Semua arah buntu

        return delta_x, delta_y
