"""
@author lferiani
@date Dec 19th, 2019

Single 300ul pipettes

Start from 5 identical 96 WP library plates

Each strain goes into at least one well of a stock 96WP (to freeze)
Each stock plate has 1 column empty for op50 to be added later

Tip rack for single (to change) in 3

Library 96WPs in 1, 4, 7, 10, 6
Stock 96WPs in 2, 5, 8, 11, 9

"""
import pdb
import numpy as np
from opentrons import labware, instruments, robot

####################### user intuitive parameters

# single channel pipette parameters and tipracks
single_pipette_type = 'p300-Single'
single_pipette_mount = 'right'
tiprack_single_slots = ['3']
tiprack_single_type = 'opentrons_96_tiprack_300ul'
tiprack_single_startfrom = 'A1'

# library plates
library_slots = library_slots = ['6','10','7','4','1']
library_type = '96-flat'
bacterial_volume = 75

# stock plates
stock_slots = ['9','11','8','5','2']
stock_type = '96-flat'

# seed for randomness
seed = 20191220
n_columns = 12
np.random.seed(seed)


############### create mapping (just python so far, no robot speech)

# hardcode library wells (they are fixed)
rows = 'ABCDEFGH'
library_wells = ([r+str(col+1) for r in rows for col in range(5)]
                 + ['A6'] + [r+'7' for r in rows] + ['D8'])
library_wells.sort()

# destination wells
# this is a 5 by 88 list of lists, taking out a column every time
all_dst_wells = []
for pc in range(len(stock_slots)):
    col_to_reserve = np.random.randint(1,12)
    print('Reserving col {} in plate in slot {} for OP50'.format(
        col_to_reserve,
        stock_slots[pc]))
    all_dst_wells.append([r+str(col+1)
                          for r in rows for col in range(12)
                          if col != col_to_reserve])

# loop on plates
mapping_dict = {}
for pc, stock_wells in enumerate(all_dst_wells):
    # get the deck slots
    lib_slot = library_slots[pc]
    stock_slot = stock_slots[pc]
    lib_wells = library_wells.copy()
    # first shuffle the copy of library wells and assign it to the stock wells
    np.random.shuffle(lib_wells)
    # now extract a random selection of len(stock)-len(lib) and
    # attach them to shuffled library
    n_remaining_wells = len(stock_wells) - len(lib_wells)
    lib_wells.extend(np.random.choice(library_wells,
                                      n_remaining_wells,
                                      replace=False))
    # now these are not in order of library
    mapping = list(zip(lib_wells, stock_wells))
    mapping.sort(key=lambda x: x[0])
    print(len(mapping))

    for lib_well, stock_well in mapping:
        key = (lib_slot, lib_well)
        value = (stock_slot, stock_well)
        if key not in mapping_dict.keys():
            mapping_dict[key] = [value]
        else:
            mapping_dict[key].append(value)

print(len(mapping_dict))
print(len([v for vv in mapping_dict.values() for v in vv]))

############################# define custom multiwell plates

if '48-well-plate-sarsted' not in labware.list():
    custom_plate = labware.create(
        '48-well-plate-sarsted',        # name of you labware
        grid=(8, 6),                    # specify amount of (columns, rows)
        spacing=(12.4, 12.4),           # distances (mm) between each (column, row)
        diameter=10,                    # diameter (mm) of each well on the plate
        depth=17.05,                    # depth (mm) of each well on the plate
        volume=500
        )                     # Sarsted had a "volume of work"

    print('Wells in 48WP Sarsted:')
    for well in custom_plate.wells():
        print(well)

if '96-well-plate-sqfb-whatman' not in labware.list():
    custom_plate = labware.create(
        '96-well-plate-sqfb-whatman',   # name of you labware
        grid=(12, 8),              # specify amount of (columns, rows)
        spacing=(8.99, 8.99),      # distances (mm) between each (column, row)
        diameter=7.57,             # diameter (mm) of each well on the plate (here width at bottom)
        depth=10.35,               # depth (mm) of each well on the plate
        volume=650
        )                # this is the actual volume as per specs, not a "volume of work"

    print('Wells in 96WP Whatman:')
    for well in custom_plate.wells():
        print(well)

if '96-well-plate-pcr-thermofisher' not in labware.list():
    custom_plate = labware.create(
        '96-well-plate-pcr-thermofisher',   # name of you labware
        grid=(12, 8),              # specify amount of (columns, rows)
        spacing=(9.00, 9.00),      # distances (mm) between each (column, row)
        diameter=5.50,             # diameter (mm) of each well on the plate (here width at top!!)
        depth=15.00,               # depth (mm) of each well on the plate
        volume=200
        )                # as per manufacturer's website

    print('Wells in 96WP PCR Thermo Fisher:')
    for well in custom_plate.wells():
        print(well)

############################ define labware
# i.e. translate user-friendly parameters into opentrons language

# pipette and tiprack

# single channel
if single_pipette_type == 'p300-Single': # this is mostly a type check
    tipracksingle = [
        labware.load(tiprack_single_type, tiprack_slot)
        for tiprack_slot in tiprack_single_slots
        ]
    pipette_single = instruments.P300_Single(
        mount=single_pipette_mount,
        tip_racks=tipracksingle
        )
pipette_single.start_at_tip(tipracksingle[0].well(tiprack_single_startfrom))
pipette_single.plunger_positions['drop_tip'] = -6
# pdb.set_trace()

# define library plates and stock plates
lib_plates = [labware.load(library_type, slot) for slot in library_slots]
stk_plates = [labware.load(stock_type, slot) for slot in stock_slots]


# translate mapping dictionary into robot terms
robot_mapping = {}
for k, v in mapping_dict.items():
    lib_slot, lib_well = k
    src_well = lib_plates[library_slots.index(lib_slot)].well(lib_well)
    stk_slot = v[0][0]
    if len(v) > 1:
        stk_wells = [w for _,w in v]
        dst_wells = stk_plates[stock_slots.index(stk_slot)].wells(stk_wells)
    else:
        dst_wells = stk_plates[stock_slots.index(stk_slot)].wells(v[0][1])
    robot_mapping[src_well] = dst_wells

print(len(robot_mapping))



# print to check
cc=0
for k, v in robot_mapping.items():
    if v.get_type()=='Well':
        cc+=1
    else:
        cc+=len(v)
print(cc)

# pdb.set_trace()
################### functions

# stupid function to measure how many tips got used
def count_used_tips(is_print=True):
    """
    Count how many tips have been used and print it (can be silenced).
    Return a tuple with the number of used tips from single and multichannel
    pipettes.
    """
    stc = 0
    mtc = 0
    for c in robot.commands():
        if 'Picking up tip wells' in c: # order of checks here matters
            mtc+=8
        elif 'Picking up tip well' in c: # note the lack of s in well
            stc+=1
    if is_print:
        print('TIP COUNT: Single = {}, Multi = {}'.format(stc, mtc))
    return stc, mtc


def is_tiprack_empty(pipette):
    """
    Count the number of tips by pipettes of the same type as in input,
    return True if the number of used tips is a multiple of
    (96 * the number of racks assigned to the pipette in input)
    """
    stc, mtc = count_used_tips(is_print=True)
    n_racks = len(pipette.tip_racks)
    n_tips_touse = 96 * n_racks
    message = '------------------- Out of tips -------------------'
    if pipette.type == 'single':
        if (stc % n_tips_touse == 0) and (stc != 0):
            print(message)
            return True
        else:
            return False
    elif pipette.type == 'multi':
        if (mtc % n_tips_touse == 0) and (mtc != 0):
            print(message)
            return True
        else:
            return False
    else:
        raise Exception('Unknown pipette type')


def counter_to_platecolumn(counter):
    """
    Take a counter 0...Inf, return a WellSeries object (a column).
    Loop between columns '2' to '11' across the plates listed in stock_plates.
    After stock_plates[-1].cols('11') restart from stock_plates[0].cols('2')
    """
    # get column name
    col_name = str(counter % n_useful_columns + 2)
    # get plate index
    plate_ind = (counter // n_useful_columns) % len(stock_plates)
    # get plate and column
    out = stock_plates[plate_ind].cols(col_name)
    # print(out)
    return out


def my_get_path(well_or_wellseries):
    """
    Return slot on the robot deck, and position in the plate, of an input object
    """
    slot, _, pos = well_or_wellseries.get_path()
    return (slot, pos)


def print_change_tiprack(pipette):
    print('###################################################')
    if pipette.type == 'multi':
        print('#               CHANGE MULTI TIPRACK              #')
    elif pipette.type == 'single':
        print('#              CHANGE SINGLE TIPRACK              #')
    else:
        raise Exception('unknown pipette type')
    print('###################################################')
    robot.pause()


def print_action(what, from_where, to_where):
    message = 'TRANSFER: '
    message += (what.strip(' ') + ' ')
    message += 'from slot {}, pos {} '.format(*my_get_path(from_where))
    message += 'into slot {}, pos {}'.format(*my_get_path(to_where))
    print(message)


def safely_pick_up_tip(pipette):
    """
    Wrapper for pipette.pick_up_tip():
        - Check if tips are available
        - Prompt user action if needed
        - Reset robot's internal tipcounting
        - Pick up tip(s)
    """
    # check if tips available
    if is_tiprack_empty(pipette):
        # prompt user action
        print_change_tiprack(pipette)
        # tell robot that we changed the tipracks
        pipette_multi.reset_tip_tracking()
    # proceed to pick up the tips as intended
    return pipette.pick_up_tip()


def safely_transfer(pipette, volume, source, destination, **kwargs):

    if is_tiprack_empty(pipette):
        print_change_tiprack(pipette)
        pipette.reset_tip_tracking()

    # and move drug from previous column
    return pipette.transfer(
        volume,
        source,
        destination,
        **kwargs
        )


################### actions

# safety command
pipette_single.drop_tip()
is_always_change = True

for src_well, dst in robot_mapping.items():
    if is_always_change:
        # deal with wells not being iterable while wellseries are
        if dst.get_type() == 'Well':
            dst_wells = [dst]
        else:
            dst_wells = dst

        for dst_well in dst_wells:
            safely_transfer(pipette_single,
                            bacterial_volume,
                            src_well,
                            dst_well,
                            blow_out=True,
                            )
    else:
        safely_transfer(pipette_single,
                        bacterial_volume,
                        src_well,
                        dst,
                        blow_out=True,
                        )

count_used_tips()

# each time we add water and fill up a 96wp => expecting 104 tips every plate
# so 104, 208, 312, 416

#write out robot commands
if not robot.is_simulating():
    import datetime
    out_fname = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+'_runlog.txt'
    out_fname = '/data/user_storage/opentrons_data/protocols_logs/' + out_fname
    with open(out_fname,'w') as fid:
        for command in robot.commands():
            print(command,file=fid)
