import pygame
import sys
import copy
from typing import List, Tuple, Set, Dict, Optional

class TrianglePegSolitaire:
    def __init__(self, initial_board: List[int]):
        """
        Initialize the peg solitaire solver
        initial_board: list of 15 positions (0 = empty, 1 = peg)
        Position mapping (1-15):
             1
            2 3
           4 5 6
          7 8 9 10
        11 12 13 14 15
        """
        self.root = initial_board[:]
        self.stree = {0: [set(), initial_board[:], -1]}
        self.nnodes = 1
        self.gnode = -100
        
        # Define valid moves: (from, over, to) for each position
        # Based on triangular peg solitaire rules
        self.valid_moves = self._generate_move_patterns()
    
    def _generate_move_patterns(self) -> List[Tuple[int, int, int]]:
        """Generate all possible move patterns for triangular peg solitaire"""
        moves = []
        
        # Horizontal moves (left-right within rows)
        # Row 3: positions 4,5,6
        moves.extend([(4,5,6), (6,5,4)])  # 4->6 jumping over 5, 6->4 jumping over 5
        
        # Row 4: positions 7,8,9,10
        moves.extend([(7,8,9), (9,8,7)])    # 7->9, 9->7
        moves.extend([(8,9,10), (10,9,8)])  # 8->10, 10->8
        
        # Row 5: positions 11,12,13,14,15
        moves.extend([(11,12,13), (13,12,11)])  # 11->13, 13->11
        moves.extend([(12,13,14), (14,13,12)])  # 12->14, 14->12
        moves.extend([(13,14,15), (15,14,13)])  # 13->15, 15->13
        
        # Diagonal moves (left diagonal)
        moves.extend([(1,2,4), (4,2,1)])    # 1->4, 4->1
        moves.extend([(2,5,8), (8,5,2)])    # 2->8, 8->2
        moves.extend([(3,6,10), (10,6,3)])  # 3->10, 10->3
        moves.extend([(4,7,11), (11,7,4)])  # 4->11, 11->4
        moves.extend([(5,8,12), (12,8,5)])  # 5->12, 12->5
        moves.extend([(6,9,13), (13,9,6)])  # 6->13, 13->6
        moves.extend([(7,12,14), (14,12,7)]) # 7->14, 14->7 (special diagonal)
        moves.extend([(8,13,15), (15,13,8)]) # 8->15, 15->8 (special diagonal)
        
        # Diagonal moves (right diagonal)
        moves.extend([(1,3,6), (6,3,1)])    # 1->6, 6->1
        moves.extend([(2,5,9), (9,5,2)])    # 2->9, 9->2
        moves.extend([(4,8,13), (13,8,4)])  # 4->13, 13->4
        moves.extend([(5,9,14), (14,9,5)])  # 5->14, 14->5
        moves.extend([(7,8,9), (9,8,7)])    # Already added above
        moves.extend([(11,12,13), (13,12,11)]) # Already added above
        
        # Remove duplicates and convert to 0-based indexing
        unique_moves = list(set(moves))
        return [(f-1, o-1, t-1) for f, o, t in unique_moves]
    
    def genmoves(self, board: List[int]) -> List[List[int]]:
        """Generate all valid moves from current board position"""
        valid_moves = []
        
        for from_pos, over_pos, to_pos in self.valid_moves:
            # Check if move is valid: from has peg, over has peg, to is empty
            if (board[from_pos] == 1 and 
                board[over_pos] == 1 and 
                board[to_pos] == 0):
                
                # Create new board state after move
                new_board = board[:]
                new_board[from_pos] = 0  # Remove peg from start
                new_board[over_pos] = 0  # Remove jumped peg
                new_board[to_pos] = 1    # Place peg at destination
                
                valid_moves.append(new_board)
        
        return valid_moves
    
    def is_goal_state(self, board: List[int]) -> bool:
        """Check if board has exactly one peg (winning condition)"""
        return sum(board) == 1
    
    def gentree(self, max_depth: int = 20) -> int:
        """Generate search tree to find solution"""
        depth = 0
        self.gnode = -100
        goal_found = False
        
        while depth < max_depth and not goal_found:
            print(f'Searching at depth {depth}')
            ntree = {}
            
            for node_id in self.stree:
                # Only expand nodes at current depth that haven't been expanded
                if len(self.stree[node_id][0]) < 1 and not goal_found:
                    current_board = self.stree[node_id][1]
                    
                    # Check if current state is goal
                    if self.is_goal_state(current_board):
                        print(f'Goal found at depth {depth}')
                        self.gnode = node_id
                        goal_found = True
                        break
                    
                    # Generate possible moves
                    possible_moves = self.genmoves(current_board)
                    
                    for new_board in possible_moves:
                        # Avoid cycles (don't go back to parent state)
                        if depth > 0:
                            parent_id = self.stree[node_id][2]
                            if parent_id >= 0 and new_board == self.stree[parent_id][1]:
                                continue
                        
                        # Add new node to tree
                        self.stree[node_id][0].add(self.nnodes)
                        ntree[self.nnodes] = [set(), new_board, node_id]
                        
                        # Check if this is goal state
                        if self.is_goal_state(new_board):
                            print(f'Goal found at depth {depth + 1}')
                            self.gnode = self.nnodes
                            goal_found = True
                            break
                        
                        self.nnodes += 1
            
            # Add new nodes to main tree
            for key in ntree:
                self.stree[key] = ntree[key]
            
            depth += 1
        
        return self.gnode
    
    def print_solution(self):
        """Print the solution path if found"""
        if self.gnode < 0:
            print('No solution found')
            return
        
        # Reconstruct solution path
        solution = []
        current_node = self.gnode
        
        while current_node != -1:
            solution.append(self.stree[current_node][1][:])
            current_node = self.stree[current_node][2]
        
        solution.reverse()
        
        print(f'\nSolution found with {len(solution)-1} moves:')
        print('=' * 40)
        
        for i, board in enumerate(solution):
            print(f'Step {i}:')
            self.print_board(board)
            print()
    
    def print_board(self, board: List[int]):
        """Print triangular board representation"""
        positions = [
            [0],           # Row 1: position 1
            [1, 2],        # Row 2: positions 2,3
            [3, 4, 5],     # Row 3: positions 4,5,6
            [6, 7, 8, 9],  # Row 4: positions 7,8,9,10
            [10, 11, 12, 13, 14]  # Row 5: positions 11,12,13,14,15
        ]
        
        for row_idx, row in enumerate(positions):
            # Add spacing for triangular shape
            spaces = ' ' * (4 - row_idx)
            print(spaces, end='')
            
            for pos_idx in row:
                symbol = '●' if board[pos_idx] == 1 else '○'
                print(symbol, end=' ')
            print()


class PegSolitaireGUI:
    def __init__(self, solver: TrianglePegSolitaire):
        pygame.init()
        self.solver = solver
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Triangle Peg Solitaire Solver")
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.GRAY = (128, 128, 128)
        
        # Font
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Board positions (pixel coordinates)
        self.positions = self._calculate_positions()
        self.peg_radius = 20
        
        # Animation
        self.current_step = 0
        self.solution_steps = []
        self.animating = False
        self.animation_speed = 60  # FPS
        
    def _calculate_positions(self) -> List[Tuple[int, int]]:
        """Calculate pixel positions for each peg position"""
        positions = []
        center_x = self.width // 2
        start_y = 100
        row_spacing = 60
        peg_spacing = 50
        
        # Position mapping for triangular layout
        rows = [
            [0],                    # Row 1: position 1
            [1, 2],                 # Row 2: positions 2,3  
            [3, 4, 5],              # Row 3: positions 4,5,6
            [6, 7, 8, 9],           # Row 4: positions 7,8,9,10
            [10, 11, 12, 13, 14]    # Row 5: positions 11,12,13,14,15
        ]
        
        for row_idx, row in enumerate(rows):
            y = start_y + row_idx * row_spacing
            row_width = (len(row) - 1) * peg_spacing
            start_x = center_x - row_width // 2
            
            for col_idx, pos_idx in enumerate(row):
                x = start_x + col_idx * peg_spacing
                positions.append((x, y))
        
        return positions
    
    def draw_board(self, board: List[int], step_num: int = 0):
        """Draw the current board state"""
        self.screen.fill(self.WHITE)
        
        # Draw title
        title = self.font.render("Triangle Peg Solitaire", True, self.BLACK)
        title_rect = title.get_rect(center=(self.width//2, 30))
        self.screen.blit(title, title_rect)
        
        # Draw step number
        step_text = self.small_font.render(f"Step: {step_num}", True, self.BLACK)
        self.screen.blit(step_text, (10, 10))
        
        # Draw pegs count
        pegs_count = sum(board)
        count_text = self.small_font.render(f"Pegs: {pegs_count}", True, self.BLACK)
        self.screen.blit(count_text, (10, 35))
        
        # Draw board positions
        for i, (x, y) in enumerate(self.positions):
            # Draw position number
            num_text = self.small_font.render(str(i+1), True, self.GRAY)
            num_rect = num_text.get_rect(center=(x, y-35))
            self.screen.blit(num_text, num_rect)
            
            # Draw hole
            pygame.draw.circle(self.screen, self.GRAY, (x, y), self.peg_radius + 2)
            
            # Draw peg if present
            if board[i] == 1:
                pygame.draw.circle(self.screen, self.BLUE, (x, y), self.peg_radius)
            else:
                pygame.draw.circle(self.screen, self.WHITE, (x, y), self.peg_radius - 2)
        
        # Draw controls
        controls = [
            "SPACE: Next step",
            "R: Reset",
            "S: Solve automatically",
            "Q: Quit"
        ]
        
        y_offset = self.height - 120
        for control in controls:
            control_text = self.small_font.render(control, True, self.BLACK)
            self.screen.blit(control_text, (10, y_offset))
            y_offset += 25
        
        pygame.display.flip()
    
    def run_visualization(self):
        """Run the GUI visualization"""
        clock = pygame.time.Clock()
        running = True
        
        # Check if solution exists
        if self.solver.gnode >= 0:
            # Get solution steps
            current_node = self.solver.gnode
            while current_node != -1:
                self.solution_steps.append(self.solver.stree[current_node][1][:])
                current_node = self.solver.stree[current_node][2]
            self.solution_steps.reverse()
        else:
            self.solution_steps = [self.solver.root]
        
        auto_play = False
        auto_timer = 0
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.current_step < len(self.solution_steps) - 1:
                            self.current_step += 1
                    elif event.key == pygame.K_r:
                        self.current_step = 0
                        auto_play = False
                    elif event.key == pygame.K_s:
                        auto_play = True
                        auto_timer = 0
                    elif event.key == pygame.K_q:
                        running = False
            
            # Auto play
            if auto_play:
                auto_timer += 1
                if auto_timer >= 60:  # 1 second at 60 FPS
                    if self.current_step < len(self.solution_steps) - 1:
                        self.current_step += 1
                    else:
                        auto_play = False
                    auto_timer = 0
            
            # Draw current state
            if self.solution_steps:
                current_board = self.solution_steps[self.current_step]
                self.draw_board(current_board, self.current_step)
            
            clock.tick(60)
        
        pygame.quit()


def create_initial_board(empty_position: int) -> List[int]:
    """Create initial board with one empty position (1-15)"""
    board = [1] * 15  # All positions filled
    board[empty_position - 1] = 0  # Make specified position empty (convert to 0-based)
    return board


def main():
    print("Triangle Peg Solitaire Solver")
    print("=============================")
    
    # Get initial empty position from user
    if len(sys.argv) > 1:
        try:
            empty_pos = int(sys.argv[1])
            if not (1 <= empty_pos <= 15):
                raise ValueError("Position must be between 1 and 15")
        except ValueError:
            print("Error: Please provide a valid position number (1-15)")
            print("Usage: python peg_solitaire.py <empty_position>")
            return
    else:
        try:
            empty_pos = int(input("Enter the position that starts empty (1-15): "))
            if not (1 <= empty_pos <= 15):
                raise ValueError("Position must be between 1 and 15")
        except ValueError:
            print("Error: Please enter a valid position number (1-15)")
            return
    
    # Create initial board
    initial_board = create_initial_board(empty_pos)
    print(f"\nInitial board (position {empty_pos} is empty):")
    
    # Create solver
    solver = TrianglePegSolitaire(initial_board)
    solver.print_board(initial_board)
    
    # Solve the puzzle
    print(f"\nSolving puzzle with initial empty position: {empty_pos}")
    print("This may take a while...")
    
    result = solver.gentree(max_depth=15)
    
    if result >= 0:
        print("\n*** SOLUTION FOUND! ***")
        solver.print_solution()
        
        # Ask if user wants to see visualization
        try:
            show_gui = input("\nShow visualization? (y/n): ").lower().strip()
            if show_gui in ['y', 'yes']:
                gui = PegSolitaireGUI(solver)
                gui.run_visualization()
        except KeyboardInterrupt:
            print("\nExiting...")
    else:
        print(f"\nNo solution found for initial empty position: {empty_pos}")
        print("This configuration may not be solvable.")


if __name__ == "__main__":
    main()