from collections import deque
from copy import deepcopy
from datetime import datetime
from typing import Optional
from scr.models.Node import Node
from scr.models.Metrics import Metrics


class AVL:

    def __init__(self, simulation_clock=None, archive_age_hours=72, stress_mode=False):
            self.root = None
            self.list_deleted=[]
            self.list_historic = []
            self.retired_ids = set()
            self.associations = {}
            self.metrics = Metrics()
            self.simulation_clock = simulation_clock or datetime.now()
            self.archive_age_hours = archive_age_hours
            self.stress = stress_mode
    # Estos métodos mantienen en un solo lugar los valores que usa el
    # archivado automático y permiten que Scenario registre sus cambios.
    def set_archive_age_hours(self, archive_age_hours):
        if archive_age_hours <= 0:
            raise ValueError("La antigüedad mínima debe ser positiva.")
        self.archive_age_hours = archive_age_hours

    def set_simulation_clock(self, simulation_clock):
        self.simulation_clock = simulation_clock

    def _get_height(self, node: Optional[Node]) -> int: #We define a helper method that returns the height of a node.
        if node is None: #Is the node missing?
            return 0
        return node.height   #If the node exists, return its stored height.

    def _update_height(self, node: Node) -> None: #This method recalculates a node's height
        node.height = 1 + max(
            self._get_height(node.left),
            self._get_height(node.right)
        ) #It takes the larger height of the two children and adds one.


    def _balance_factor(self, node: Optional[Node]): #We calculate the node's balance factor.
        if node is None:
            return 0

        return (
            self._get_height(node.left)
            - self._get_height(node.right) ) 
    #A positive number means the left subtree is taller. A negative number means the right subtree is taller.

        

    def _rotate_right(self, y: Node) -> Node:  #We define a right rotation. It is used when the tree is too heavy on the left side.

        x = y.left #We take y's left child and store it in x.
        temporary = x.right #We temporarily store x's right child so it is not lost during the rotation.

        x.right = y #y becomes the right child of x.
        y.left = temporary #The temporary subtree becomes y's left child.

        self._update_height(y)
        self._update_height(x)
        #After moving the nodes, their heights have changed. So we recalculate both heights.

        return x

    def _rotate_left(self, x: Node) -> Node: #Left rotation. It is used when the tree is too heavy on the right.

        y = x.right
        temporary = y.left

        y.left = x
        x.right = temporary

        self._update_height(x)
        self._update_height(y)

        return y


    def insert(self, value) -> None:
        for i in range (len(self.list_deleted)):
            if (self.list_deleted[i]== value.get_id()):
                return None  #We iterate through the IDs of deleted events. If the new event's ID is already in the deleted list, we stop and do not insert it again.
        
        for event in self.list_historic:
            if event.get_id() == value.get_id():
                self.same_archive(value, event)  #If the new event's ID is already in the historic list, we stop and do not insert it again.
                return None
            
        self.root = self._insert(self.root, value)#This calls the recursive insertion method. The returned node is assigned to self.root because insertion or balancing can change the root.
        if self.stress is True:
            return Node

    def _insert(self, node: Optional[Node], value) -> Node:

        if node is None:
            return Node(value) #This is the base case. If we reach an empty position, we create a new Node containing the value.
        value_key = value.get_code()
        node_key = node.value.get_code()
        #We get the code of the new event and the code of the event already stored in the current node. The code has three components, which are used for sorting.

        if (value_key[2] != node_key[2]): #first we check if the id is different so we don't insert the same earthquake
            if value_key[0] != node_key[0]: #we compare if the first component of the tuple is different, if they are the same we move on to the second component and so on...
                if value_key[0] < node_key[0]: #if the first number (0) of the earthquake tuple I want to enter is smaller than the earthquake that's already in the tree, then I go to the left
                    node.left = self._insert(node.left, value)

                elif value_key[0] > node_key[0]: #if the first number (0) of the earthquake tuple I want to enter is bigger than the earthquake that's already in the tree, then I go to the right node
                    node.right = self._insert(node.right, value)

            elif value_key[1] != node_key[1]:
                if value_key[1] < node_key[1]:
                    node.left = self._insert(node.left, value)

                elif value_key[1] > node_key[1]:
                    node.right = self._insert(node.right, value)

            elif value_key[2] != node_key[2]:
                if value_key[2] < node_key[2]:
                    node.left = self._insert(node.left, value)

                elif value_key[2] > node_key[2]:
                    node.right = self._insert(node.right, value)

        else:
            self.same_earthquake(value, node) #If the id is the same then it calls another function that checks the new earthquake with the one that’s already there and compares the information

        self._update_height(node)

        # If stress mode is active, do not balance
        if self.stress is True:
            return node

        # Calculate the balance factor
        balance = self._balance_factor(node)

        # Left-Left
        if balance > 1 and self._balance_factor(node.left) >= 0:
            return self._rotate_right(node)

        # Left-Right
        if balance > 1 and self._balance_factor(node.left) < 0:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Right-Right
        if balance < -1 and self._balance_factor(node.right) <= 0:
            return self._rotate_left(node)

        # Right-Left
        if balance < -1 and self._balance_factor(node.right) > 0:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def stress_mode(self, stress):
        self.stress=stress
        if stress is False:
            self.balance()
        #If stress mode is on, nothing moves until they turn off stress mode

    def balance (self) -> None:
        print("BALANCE EJECUTADO. STRESS =", self.stress)
        if self.stress:
            return
        self.root = self._balance(self.root)#I'm going to balance the tree starting from the root.
        #You pass the current root to _balance(). That function may return a different root after rotations. So you assign the result back }
    
    def _balance(self, node: Optional[Node]) -> Optional[Node]:

        if node is None:
            return None

        # Primero balanceamos los hijos
        node.left = self._balance(node.left)
        node.right = self._balance(node.right)

        self._update_height(node)

        balance = self._balance_factor(node)

        # LEFT
        if balance > 1:

            if self._balance_factor(node.left) >= 0:
                node = self._rotate_right(node)

            else:
                node.left = self._rotate_left(node.left)
                node = self._rotate_right(node)

        # RIGHT
        elif balance < -1:

            if self._balance_factor(node.right) <= 0:
                node = self._rotate_left(node)

            else:
                node.right = self._rotate_right(node.right)
                node = self._rotate_left(node)

        # Después de la rotación, los hijos pueden haber cambiado
        node.left = self._balance(node.left)
        node.right = self._balance(node.right)

        self._update_height(node)

        return node


    def pre_order(self) -> None:  #ROOT → LEFT → RIGHT
        if self.root is None:
            return
        items = []
        items = self._pre_order(self.root, items)
        return items

    def _pre_order(self, root: Node, items) -> None:
        if root is None:
            return items
        items.append(root.value) #append the node's value before visiting its children.
        items = self._pre_order(root.left, items) #then visit the left son
        items = self._pre_order(root.right, items) #then visit the right son
        return items


    def in_order(self)->None: #LEFT → ROOT → RIGHT
        if self.root is None:
            return
        items = []
        self._in_order(self.root, items)
        return items

    def _in_order(self, root: Node, items) -> None:
        if root is None:
            return items
        items = self._in_order(root.left, items) #left
        items.append(root.value)  #root
        items = self._in_order(root.right, items) #right

        return items



    def post_order(self) -> None:  #LEFT → RIGHT → ROOT
        if self.root is None:
            return
        items = []
        self._post_order(self.root, items)
        return items

    def _post_order(self, root: Node, items) -> None:
        if root is None:
            return items
        items = self._post_order(root.left, items) #left
        items = self._post_order(root.right, items) #right
        items.append(root.value)  #root
        return items


    def breadth_first(self) -> None:
        if self.root is None:
            return
        items = []
        return self._breadth_first(self.root, items)

    def _breadth_first(self, root: Node, items) -> None:
        queue = deque([root])  #FIRST IN → FIRST OUT
        while queue: #While the queue contains nodes, keep processing them.
            node = queue.popleft() #remove the leftmost element.
            items.append(node.value) #save the node's value
            if node.left is not None:  #If it has a left child, you put it in the queue.
                queue.append(node.left)
            if node.right is not None: #If you have a right child, you put it in the queue.
                queue.append(node.right)
        return items

    def _find_minimum(self, root: Node) -> Node:
            current = root
            while current.left is not None:
                current = current.left
            return current

    def delete(self, id):
        earthquake = self.research(id) #First, you search for the earthquake using its ID.
        if earthquake is None or id in self.list_deleted: # If the earthquake does not exist or has already been deleted, stop the operation.
            return None
        else:
            # Call the recursive deletion method starting from the root.
            # register_deleted=True records this earthquake as deleted.
            self.root = self._delete(self.root, earthquake, self.list_deleted, register_deleted=True)
            return earthquake

    def _delete(self, root: Optional[Node], earthquake, list_deleted, register_deleted: bool) -> Optional[Node]:

        if root is None: # If there is no node, the earthquake cannot be found in this tree.
            return None

        root_key = root.value.get_code() # Get the code of the current node.
        value_key = earthquake.value.get_code() # Get the code of the earthquake that needs to be deleted.
        
        if value_key[0] != root_key[0]: # Compare the first component of the codes to determine the search direction
            if value_key[0] < root_key[0]: ## If the target code is smaller, continue searching in the left tree.
                root.left = self._delete(root.left, earthquake, list_deleted, register_deleted)
            elif value_key[0] > root_key[0]: # If the target code is larger, continue searching in the right subtree.
                root.right = self._delete(root.right, earthquake, list_deleted, register_deleted)

        elif value_key[1] != root_key[1]:
            if value_key[1] < root_key[1]:
                root.left = self._delete(root.left,earthquake, list_deleted, register_deleted)
            elif value_key[1] > root_key[1]:
                root.right = self._delete(root.right, earthquake, list_deleted, register_deleted)

        elif value_key[2] != root_key[2]:
            if value_key[2] < root_key[2]:
                root.left = self._delete(root.left, earthquake, list_deleted, register_deleted)
            elif value_key[2] > root_key[2]:
                root.right = self._delete(root.right, earthquake, list_deleted, register_deleted)

        else: # All code components match, so the target earthquake has been found.
            if register_deleted: #It serves to remember which earthquakes were deleted.
                list_deleted.append(earthquake.value.get_id())
            if root.is_leaf(): # If the node is a leaf, remove it by returning None.
                return None
            if root.left is None: # If there is no left child, replace the node with its right child.
                return root.right
            if root.right is None: # If there is no right child, replace the node with its left child.
                return root.left

            successor = self._find_minimum(root.right) # Find the smallest node in the right subtree to replace the deleted node.
            root.value = successor.value # Replace the current node's value with the successor's value.
            root.right = self._delete(root.right, successor, list_deleted, False)# Remove the successor from its original position. # False prevents the successor from being registered as a second deletion.

        self._update_height(root) # Update the height because the subtree structure has changed.
        if self.stress: # If stress mode is enabled, skip the rebalancing process.
            return root

        balance = self._balance_factor(root) # Calculate the balance factor after the deletion.
        if balance > 1: # If the node is too heavy on the left, a right rotation may be required.
            if self._balance_factor(root.left) < 0:
                root.left = self._rotate_left(root.left)
            return self._rotate_right(root)
        if balance < -1: # If the node is too heavy on the right, a left rotation may be required.
            if self._balance_factor(root.right) > 0:
                root.right = self._rotate_right(root.right)
            return self._rotate_left(root)
        return root
        
    def height(self) -> int:
        if self.root is None: # An empty tree has a height of -1.
            return -1

        return self._height(self.root)

    def _height(
        self,
        node: Optional[Node]
    ) -> int: 
        if node is None:
            return -1
        return 1 + max(
            self._height(node.left),
            self._height(node.right)
        ) #The height of the node is 1 plus the greater height between the left and right child.


    def size(self) -> int:
        if self.root is None:
            return 0
        return self._size(self.root)  # Count all nodes starting from the root.

    def _size(
        self,
        node: Optional[Node]
    ) -> int:
        if node is None:
            return 0
        
        return (
            1
            + self._size(node.left)
            + self._size(node.right)
        )   # Count the current node and recursively count both subtrees.


    def node_level(self, id):
        
        earthquake= self.research(id) # Search for the earthquake using its ID.

        if earthquake is None:
            return -1

        result= self._node_level(self.root, earthquake.value.get_code(), 0) # Start searching from the root at level 0.
        return result

    def _node_level(self, node: Optional[Node], value, current_level: int) -> int:

        if node is None: # Return -1 if the node is not found.
            return -1

        if node.value.get_code() == value: # If the current node contains the target value, return its level.
            return current_level
    
        if value < node.value.get_code(): # If the target value is smaller, search in the left subtree.

            return self._node_level(
                node.left,
                value,
                current_level + 1
            )

        else: # Otherwise, search in the right subtree.

            return self._node_level(
                node.right,
                value,
                current_level + 1
            )

    def budget(self, L, id) -> str:
        cost=self.node_level(id) # Calculate the level of the earthquake in the tree.
        if cost>L:  # If the node level is greater than L, classify it as high budget.
            bugett="presupuesto alto"
        else: # Otherwise, classify it as low budget.
            bugett="presupuesto bajo"
        return bugett
    
   
    
    def research(self, id,) -> None: # Start searching for the earthquake from the root of the tree.
        return  self._research(self.root, id)
    
    def _research(self, node: Optional[Node], id) -> Node:

        if node is None: # Stop searching when there is no node.
            return None

        value_key = id # Store the ID that we are looking for.
        node_key = node.value.get_code() # Get the code of the current node.

        if value_key == node_key[2]:  # If the ID matches the third component of the code, return the node.
            return node

        else:
            result = self._research(node.left, id)  #Search the left subtree first.

            if result is not None: # If the earthquake is found on the left, return it.
                return result

            return self._research(node.right, id) # Otherwise, search the right subtree.

    def compare(self, id) -> None:
    
        list_similitude=[] # Create a list to store earthquakes that meet the similarity conditions.
        value_key = self.research(id) # Search for the reference earthquake.

        if value_key is None:
            return list_similitude
        
        self._compare(self.root, value_key, list_similitude) # Compare the earthquake with all nodes.
        return list_similitude

    
    def _compare(self, node: Optional[Node], value_key, list_similitude) -> Node:

        if node is None:
            return None

        # Get the epicenter, time, and magnitude of the current node.
        node_key_epicenter = node.value.get_epicenter()
        node_key_time = node.value.get_datetime()
        node_key_magnitude= node.value.get_magnitude()

        # Get the epicenter, time, and magnitude of the earthquake.
        value_key_epicenter=value_key.value.get_epicenter()
        value_key_time = value_key.value.get_datetime()
        value_key_magnitude=value_key.value.get_magnitude()

        if (value_key_magnitude> node_key_magnitude): #El sismo de referencia debe tener una magnitud mayor.
            if ( 0< (((node_key_time)-(value_key_time)).total_seconds() / 3600) <= 48): # Check whether the current earthquake occurred within the required 48-hour time range.
                if (( ((((value_key_epicenter[0])-(node_key_epicenter[0]))**2) + (((value_key_epicenter[1])-(node_key_epicenter[1]))**2))**(1/2)) <= 40): # Check whether the distance between the two epicenters is at most 40 units.

                    list_similitude.append(node) # Add the current earthquake to the list of similar earthquakes.

        self._compare(node.left, value_key, list_similitude) # Continue checking the left subtree.  
        self._compare(node.right, value_key, list_similitude) # Continue checking the right subtree.

        return list_similitude

    def data_correction(self, id, new_info):
        earthquake=self.research(id) # Search for the earthquake using its ID.
        if earthquake is None: # Stop if the earthquake does not exist.
            return None
        return self._data_correction(earthquake, new_info)
    
    def _data_correction (self, earthquake, new_info):
        event = earthquake.value
        old_key = event.get_code()

        if "magnitud" in new_info: # Update the magnitude and recalculate the earthquake priority.
            event.set_magnitude(new_info["magnitud"])
            event.set_priority()

        elif "profundidad" in new_info:
            event.set_depth(new_info["profundidad"])
            event.set_priority()

        elif "epicentro" in new_info: # Update the epicenter, recalculate the zone, and update the priority.
            event.set_epicenter(new_info["epicentro"][0], new_info["epicentro"][1])
            event.set_zone()
            event.set_priority()

        elif "fecha y hora" in new_info: # Update the date and time of the earthquake.
            event.set_datetime(new_info["fecha y hora"])

        elif "estacion" in new_info: # Update the station information.
            event.set_stations(new_info["estacion"])

        new_key=event.get_code()

        if (old_key == new_key): #Changing the data didn't change the key that determines the earthquake's position.
            return "Datos corregidos. El sismo esta en el mismo lugar."
        else:
            event.set_review(0)  # Mark the corrected earthquake as not reviewed.
            self.delete(event.get_id()) # Remove the earthquake from its old position in the AVL tree.
            if self.list_deleted: # Remove earthquake the list_deleted because it will be inserted again.
                self.list_deleted.pop(-1)
            self.insert(event) # Reinsert the corrected earthquake so it can be placed according to its new key. 
            return("datos corregidos. se reubico el sismo")



    def review(self, id):
        earthquake = self.research(id) # Search for the earthquake using its ID.
        if earthquake is None:  # Stop if the earthquake does not exist.
            return None

        earthquake.value.set_review(1) # Mark the earthquake as reviewed.
        earthquake.value.set_revisions(earthquake.value.get_revisions() + 1)# Increase the revision counter by one.
        return True
        
    def same_earthquake(self, event, existing_node):
        return self._same_earthquake(event, existing_node)

    def _same_earthquake(self, event, existing_node):
        existing_event = existing_node.value
        new_event = event
        old_key = existing_event.get_code()

        # Check whether the new event contains exactly the same information as the earthquake already stored in the tree.
        if (new_event.get_id() == existing_event.get_id() and
            new_event.get_magnitude() == existing_event.get_magnitude() and
            new_event.get_depth() == existing_event.get_depth() and
            new_event.get_epicenter() == existing_event.get_epicenter() and
            new_event.get_datetime() == existing_event.get_datetime() and
            new_event.get_station() == existing_event.get_station()):

            existing_event.set_review(1) # Mark the existing earthquake as reviewed.
            existing_event.set_revisions(existing_event.get_revisions() + 1) # Increase the number of revisions because the event was confirmed.
            return True

        # If the new event has more revisions, use its information to update the existing event
        elif new_event.get_revisions() > existing_event.get_revisions():
            existing_event.set_magnitude(new_event.get_magnitude())
            existing_event.set_depth(new_event.get_depth())
            epicenter=new_event.get_epicenter()
            existing_event.set_epicenter(epicenter[0], epicenter[1])
            existing_event.set_zone()
            existing_event.datetime = new_event.get_datetime()
            existing_event.set_station(new_event.get_station())
            existing_event.set_priority()
            existing_event.set_review(0)
            existing_event.set_revisions(new_event.get_revisions())

            # If the code did not change, the earthquake can remain in its current position.
            if (existing_event.get_code() == old_key):
                return True
            else: #if the key changed, then the earthquake is deleted, removed from the list, and inserted again
                self.delete(existing_event.get_id())
                if self.list_deleted:
                    self.list_deleted.pop(-1)
                self.insert(existing_event)
                return True
        
        else:
            return False


    def same_archive(self, value, event):
        return self._same_archive(value, event)

    def _same_archive(self, value, event):
        existing_event = event
        new_event = value

        if (new_event.get_id() == existing_event.get_id() and
            new_event.get_magnitude() == existing_event.get_magnitude() and
            new_event.get_depth() == existing_event.get_depth() and
            new_event.get_epicenter() == existing_event.get_epicenter() and
            new_event.get_datetime() == existing_event.get_datetime() and
            new_event.get_station() == existing_event.get_station()):

            existing_event.set_review(1) # Mark the existing earthquake as reviewed.
            existing_event.set_revisions(existing_event.get_revisions() + 1) # Increase the number of revisions because the event was confirmed.
            
            self.list_historic.remove(existing_event)
            self.root = self._insert(self.root, existing_event)
            return True

        # If the new event has more revisions, use its information to update the existing event
        elif new_event.get_revisions() > existing_event.get_revisions():
            existing_event.set_magnitude(new_event.get_magnitude())
            existing_event.set_depth(new_event.get_depth())
            epicenter=new_event.get_epicenter()
            existing_event.set_epicenter(epicenter[0], epicenter[1])
            existing_event.set_zone()
            existing_event.datetime = new_event.get_datetime()
            existing_event.set_station(new_event.get_station())
            existing_event.set_priority()
            existing_event.set_review(0)
            existing_event.set_revisions(new_event.get_revisions())

            
            self.list_historic.remove(existing_event)
            self.root = self._insert(self.root, existing_event)

            return True

        else:
            return False