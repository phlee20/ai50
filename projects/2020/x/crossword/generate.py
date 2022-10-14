import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            for word in self.domains[variable].copy():

                # Check that length of word is equal to length of variable
                if len(word) != variable.length:
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        for word in self.domains[x]:

            # Check if word in domain X is the only word in domain Y (i.e. no corresponding value for y avaialble)
            if word in self.domains[y] and len(self.domains[y]) == 1:
                self.domains[x].remove(word)
                revised = True
        
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = set()

            # Loop over variables and get overlapping neighbours
            for x in self.domains:
                for y in self.crossword.neighbors(x):

                    # Build initial list of all arcs
                    arcs.add((x, y))
        
        while len(arcs) > 0:

            # Dequeue an arc
            x, y = arcs.pop()

            if self.revise(x, y):

                if len(self.domains[x]) == 0:
                    return False
                
                for z in self.crossword.neighbors(x):
                    if z != y:
                        arcs.add(z, x)
        
        return True

            

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == len(self.crossword.variables):
            return True
        
        return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # If length is not correct, then inconsistent
        for key in assignment:
            if key.length != len(assignment[key]):
                return False
        
        # Loop through overlapping cells
        for x, y in self.crossword.overlaps:
            
            overlap = self.crossword.overlaps[x, y]

            # Only consider arcs where both are assigned
            if x not in assignment or y not in assignment:
                continue

            # Only consider where arcs exist
            if overlap is None:
                continue

            # If both words are the same, then not consistent
            if assignment[x] == assignment[y]:
                return False

            # If both do not have the same overlapping character, then not consistent
            if assignment[x][overlap[0]] != assignment[y][overlap[1]]:
                return False
        
        # If nothing inconsistent, then assignment is consistent
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        odv = {}

        # Loop through domain values to compare occurences in neighbouring domains
        for value in self.domains[var]:
            odv[value] = 0
            for neighbor in self.crossword.neighbors(var):
                overlap = self.crossword.overlaps[var, neighbor]
                for y in self.domains[neighbor]:
                    if value[overlap[0]] != y[overlap[1]]:
                        odv[value] += 1

                # Check if test value exists in neighbouring domains and if neighbouring variable is already assigned
                if value in self.domains[neighbor] and neighbor not in assignment:

                    # Count constraining values
                    odv[value] += 1

        # Sort in ascending order
        odv_sorted = sorted(odv.items(), key=lambda item: item[1])
        odv_list = [x[0] for x in odv_sorted]

        return odv_list

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        mrv = []

        # Build list of unassigned variables, length of domain and number of neighbours
        for var in self.domains:
            if var not in assignment:
                mrv.append((var, len(self.domains[var]), len(self.crossword.neighbors(var))))

        if len(mrv) > 0:
        
            # Sort by degree heuristic
            mrv.sort(key=lambda x: x[2], reverse=True)

            # Sort by minimum remaining value heuristic
            mrv.sort(key=lambda x: x[1])

            return mrv[0][0]

        return None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Return assignment if all values have been assigned to variables
        if self.assignment_complete(assignment):
            return assignment

        # Choose an unassigned variable
        var = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(var, assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            del assignment[var]
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
