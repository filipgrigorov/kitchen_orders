import argparse
import numpy as np
import pandas as pd
import re

'''
    A couple of considerations/assumptions:

    (1) The approach taken, the first intuitive one at least, that comes to mind, is to
    sort the orders by preparation time as I would, personnally, prefer to process as
    many as possible orders and undertake the longer ones after, if they even can fit in.

    (2) If the distance to the end destination of the order is known, it, ideally, should 
    be included in the dispatch algorithm. They could be weighted in and used as a ranking 
    mechanism. I would cluster together orders in the same vicinity and factor in the distance.

    (3) If too many orders come in, a rotation mechanism could be implemented, to let through some
    bigger orders along with the smaller ones, from time to time. That is if we have too many big 
    orders in-queue.

    (4) Another consideration might be to factor in the ingredients, in-stock, that go bad faster 
    than others. So, they would be prioritized when the orders come in.

    (5) Many other factors could be added into a more complex cluster of deterministic and learning
    algorithms.
'''

MAX_ALLOWED_TIME = 20 # mins

class Capacity:
    def __init__(self, cooking_capacity, cooking_unit_time, assembling_capacity, assembling_unit_time, \
        packaging_capacity, packaging_unit_time):
        self.cc = int(cooking_capacity[0])
        self.cut = int(cooking_unit_time)

        self.ac = int(assembling_capacity[0])
        self.aut = int(assembling_unit_time)

        self.pc = int(packaging_capacity[0])
        self.put = int(packaging_unit_time)

    def __str__(self):
        return f'Cooking capacity, cooking time, assembly capacity, assembly time, packing capacity, packiging time :\n \
        {self.cc}-{self.cut}, {self.ac}-{self.aut}, {self.pc}-{self.put}'

class Inventory:
    def __init__(self, npatties, nlettuce, ntomatoes, nveggies, nbacon):
        self.npatties = int(npatties)
        self.nlettuce = int(nlettuce)
        self.ntomatoes = int(ntomatoes)
        self.nveggies = int(nveggies)
        self.nbacon = int(nbacon)

    def __str__(self):
        return f'#patties, #lettuce, #tomatoes, #veggies, #bacon :\n \
        {self.npatties}, {self.nlettuce}, {self.ntomatoes}, {self.nveggies}, {self.nbacon}'

class Order:
    def __init__(self, capacity, restaurant_id, date, order_idx, *args):
        self.restaurant_id = restaurant_id
        self.date = date
        self.idx = int(re.search(r'\d+', order_idx).group())
        self.burgers = [*filter(lambda x: isinstance(x, str), [*args])]

        self.num_burgers = len(self.burgers)

        self.num_patties = 0
        self.num_lettuce = 0
        self.num_tomatoes = 0
        self.num_veggies = 0
        self.num_bacon = 0

        self.cooking_time = self.num_burgers * capacity.cut
        self.assembly_time = self.num_burgers * capacity.aut
        self.packaging_time = self.num_burgers * capacity.put
        self.total_time = self.cooking_time + self.assembly_time + self.packaging_time

        for burger in self.burgers:
            self.num_patties += 1
            self.num_lettuce += int(burger.find('L'))
            self.num_bacon += int(burger.find('B'))
            self.num_tomatoes += int(burger.find('T'))
            self.num_veggies += int(burger.find('V'))

    def assign_status(self, status='REJECTED'):
        return f'{self.restaurant_id},O{self.idx},{status},{self.total_time}'

    def __str__(self):
        burgers_str = ''
        for burger in self.burgers:
            burgers_str += burger + ' '
        return f'Order: {self.restaurant_id}:{self.idx} -> {burgers_str} at {self.date}'

def create_inventory(details):
    # Note: The format is assumed to be constant
    capacity_list = details[1:7]
    inventory_list = details[7:]

    capacity = Capacity(*capacity_list)
    inventory = Inventory(*inventory_list)

    return capacity, inventory

def process_order(csv_file):
    # Deserialize the order
    df = pd.read_csv(csv_file, header=None, delimiter=',')

    processed = []

    # Break down orders by restaurant id (by 1st column)
    input_orders = [ df[df.iloc[:, 0] == restaurant_id] for restaurant_id in [*df.iloc[:, 0].unique()] ]
    for input_order in input_orders:
        capacity, inventory = create_inventory([*input_order.iloc[0, :]])
        print(f'\n{capacity}\n{inventory}\n')

        num_orders = len(input_order.index)
        print(f'Number of orders for {input_order.iloc[0, 0]} is {num_orders - 1}')
        # Process the orders by id and assess possibility of processing
        all_orders = []
        for idx in range(1, num_orders):
            order_details = [*input_order.iloc[idx, :]]

            order = Order(capacity, *order_details)
            print(f'Processing {order}\n')
            all_orders.append(order)

        # Process the orders which take least amount of time (quantity) -> sort them by time
        # Note: Ideally, the orders would be processed by the location of the user
        all_orders.sort(key=lambda order: order.total_time)
        [ print(f'{order.total_time}min', end=' ') for order in all_orders ]
        print('')

        for order in all_orders:
            is_inventory_enough = order.num_patties <= inventory.npatties
            is_inventory_enough = is_inventory_enough and order.num_lettuce <= inventory.nlettuce
            is_inventory_enough = is_inventory_enough and order.num_bacon <= inventory.nbacon
            is_inventory_enough = is_inventory_enough and order.num_tomatoes <= inventory.ntomatoes
            is_inventory_enough = is_inventory_enough and order.num_veggies <= inventory.nveggies
            if order.total_time <= MAX_ALLOWED_TIME and is_inventory_enough:
                inventory.npatties -= order.num_patties
                inventory.nlettuce -= order.num_lettuce
                inventory.nbacon -= order.num_bacon
                inventory.ntomatoes -= order.num_tomatoes
                inventory.nveggies -= order.num_veggies
                processed.append(order.assign_status('ACCEPTED'))
            else: processed.append(order.assign_status())
        
    return processed

'''
    Instructions:
    python kitchen.py --csv_file orders.csv
'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv_file', type=str, help='Specify csv order file')

    args = parser.parse_args()

    if not args.csv_file:
        raise('No csv file has been specified!')

    processed_orders = process_order(args.csv_file)
    print('\nOutputs:')
    [ print(order) for order in processed_orders ]
