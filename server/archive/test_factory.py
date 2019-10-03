class TreeFactory:
    class Oak:
        def get_message(self):
            return "This is an Oak Tree"
    class Pine:
        def get_message(self):
            return "This is a Pine Tree"
    class Maple:
        def get_message(self):
            return "This is a Maple Tree"
    @staticmethod
    def create_tree(tree):
        if tree=="Oak":
            return TreeFactory.Oak()
        elif tree=="Pine":
            return TreeFactory.Pine()
        elif tree=="Maple":
            return TreeFactory.Maple()



def print_trees(tree_list):
    for current in tree_list:
        tree=TreeFactory.create_tree(current)
        print(tree.get_message())

tree_list=["Oak","Pine","Maple"]
print_trees(tree_list)