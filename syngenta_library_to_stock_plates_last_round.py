"""
@author lferiani
@date Nov 19th, 2019

Both pipettes

Start from the library plate, a 96WP, each well is one drug at 100mM or 30mM

Each drug goes into a column of a stock 96WP, which then gets serially diluted
So in total one drug uses 5 or 4 columns
Each stock plate has dmso in col 1 and water in col 12
Drugs span different plates

Tip rack for single (to change) in 9
Tip rack for multichannel (to change) in 3, 6
Trough for water and DMSO in 11

Library 96WPs in 10
Stock 96WPs in 1, 2, 4, 5, 7, 8

Each Stock plate has 10 useful (non control columns), so 6 plates are 60 columns which are 10 drugs
Will need to change stock plates 4 times

"""
import pdb
import numpy as np
from opentrons import labware, instruments, robot

####################### user intuitive parameters

# multichannel pipette parameters and tipracks
multi_pipette_type = 'p10-Multi'
multi_pipette_mount = 'left'
tiprack_multi_slots = ['3','6']
tiprack_multi_type = 'opentrons-tiprack-10ul'
tiprack_multi_startfrom = '1'

# single channel pipette parameters and tipracks
single_pipette_type = 'p50-Single'
single_pipette_mount = 'right'
tiprack_single_slots = ['9']
tiprack_single_type = 'opentrons_96_tiprack_300ul'
tiprack_single_startfrom = 'A1'

# trough
trough_slot = '11'
trough_type = 'trough-12row'
DMSO_source_well = 'A1'
H2O_source_well = 'A2'
control_volume = 10  # volume in the left and rightmost columns of stock

# library plate
library_slot = '10'
library_type = '96-well-plate-pcr-thermofisher'
library_frombottom_off = +0.3 # mm from bottom of library wells
drugs_volume_from_library = 11

# stock plates
stock_slots = ['1', '2', '4', '5', '7', '8']
stock_type = '96-well-plate-pcr-thermofisher'
stock_frombottom_off = +0.5 # mm from bottom of stock wells

# we dilute across n times so we have n+1 doses
drug_groups = []
# drugs with 5 doses:
# this is nice as it is 2 drugs per plate
drug_groups.append(
    {'number_of_drugs' : 41-24-12, # Done 3 rounds of plates before this
     'number_of_doses' : 5,
     'drugs_volumes_for_dilutions' : [3.3, 3.67, 3.3, 3.67]}
    )
# drugs with 4 doses:
# 5 drugs span 2 plates
drug_groups.append(
    {'number_of_drugs' : 6,
     'number_of_doses' : 4,
     'drugs_volumes_for_dilutions' : [3.67, 3.3, 3.67]}
    )

volume_pre_next_dilution = 11

# control columns
DMSO_col = '1'
H2O_col = '12'


n_columns = 12
n_useful_columns = 10


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

# multi channel
if multi_pipette_type == 'p10-Multi': # this is mostly a check as we don't own other multichannel pipettes (and to not have swapped single/multi)
    tiprackmulti = [
        labware.load(tiprack_multi_type, tiprack_slot)
        for tiprack_slot in tiprack_multi_slots
        ]
    pipette_multi = instruments.P10_Multi(
        mount=multi_pipette_mount,
        tip_racks=tiprackmulti
        )
pipette_multi.start_at_tip(tiprackmulti[0].well(tiprack_multi_startfrom))
pipette_multi.plunger_positions['drop_tip'] = -6


# single channel
if single_pipette_type == 'p50-Single': # this is mostly a type check
    tipracksingle = [
        labware.load(tiprack_single_type, tiprack_slot)
        for tiprack_slot in tiprack_single_slots
        ]
    pipette_single = instruments.P50_Single(
        mount=single_pipette_mount,
        tip_racks=tipracksingle
        )
pipette_single.start_at_tip(tipracksingle[0].well(tiprack_single_startfrom))
pipette_single.plunger_positions['drop_tip'] = -6
# pdb.set_trace()


# container for controls
ctrl_src_container = labware.load(trough_type, trough_slot)
dmso_src_well = ctrl_src_container.wells(DMSO_source_well)
water_src_well = ctrl_src_container.wells(H2O_source_well)


# define library plate
lib_plate = labware.load(library_type, library_slot)

# define stock plate
stock_plates = [labware.load(stock_type, slot) for slot in stock_slots]

# define destination for controls:
dmso_dst_cols = [stock_plate.cols(DMSO_col) for stock_plate in stock_plates]
water_dst_cols = [stock_plate.cols(H2O_col) for stock_plate in stock_plates]
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


def is_new_set_stock_plates(counter):
    """
    Return True if the counter points to column '2' of the first stock plate,
    as this means that counter_to_platecolumn has looped around.
    """
    platecol = counter_to_platecolumn(counter)
    slot, _, col = platecol.get_path()
    if slot == stock_slots[0] and col == '2':
        return True
    else:
        return False


def print_new_round_splash():
    print('###################################################')
    print('#             NEW SET OF STOCK PLATES             #')
    print('#             DISPENSE WATER AND DMSO             #')
    print('#             AFTER RESUMING PROTOCOL             #')
    print('###################################################')
    robot.pause()


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


def dispense_controls(pipette):

    # safe tip pick up
    safely_pick_up_tip(pipette)
    # now dispense all the dmso
    for dmso_dst_col in dmso_dst_cols:
        print_action('DMSO', dmso_src_well, dmso_dst_col)
        pipette.transfer(
            control_volume,
            dmso_src_well,
            dmso_dst_col,
            blow_out=True,
            new_tip='never'
            )
    pipette.drop_tip()

    # safe tip pick up
    safely_pick_up_tip(pipette)
    # now dispense all the water
    for water_dst_col in water_dst_cols:
        print_action('WATER', water_src_well, water_dst_col)
        pipette.transfer(
            control_volume,
            water_src_well,
            water_dst_col,
            blow_out=True,
            new_tip='never'
            )
    pipette.drop_tip()

    return

def new_round_actions(pipette):
    print_new_round_splash()
    dispense_controls(pipette)


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
        pipette.reset_tip_tracking()
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
pipette_multi.drop_tip()
pipette_single.drop_tip()

# get a list, by row, of all the drugs
lib_wells_list = [well
                  for row in lib_plate.rows()
                  for well in row.wells()]

# counters
start_druglib_well = 36 # because we have already dispensed 3 rows of drugs
column_counter = 180  # needed to keep track of which column as drugs span multiple plates
# robot has already done 3 rounds
# 3 rounds are 10 columns * 6 plates * 3 rounds

if is_new_set_stock_plates(column_counter):
    new_round_actions(pipette_multi)

for dgc, drug_group in enumerate(drug_groups):

    # extract the drug wells we're going to use now
    stop_druglib_well = start_druglib_well + drug_group['number_of_drugs']
    group_lib_wells_list = lib_wells_list[start_druglib_well:stop_druglib_well]
    assert len(group_lib_wells_list) == drug_group['number_of_drugs']

    # retrieve dilutions array
    drugs_volumes_for_dilutions = drug_group['drugs_volumes_for_dilutions']

    # for loop on library drugs of this group
    for drug_well in group_lib_wells_list:

        # first we put drug in every well of a new column
        stock_column = counter_to_platecolumn(column_counter)
        print_action('drug', drug_well, stock_column)
        safely_transfer(
            pipette_single,
            drugs_volume_from_library,
            drug_well.bottom(library_frombottom_off),
            stock_column,
            mix_before=(3,11),
            )
        column_counter += 1
        if is_new_set_stock_plates(column_counter):
            new_round_actions(pipette_multi)

        # now we do the serial dilution:
        # use multichannel to dispense all the dmso first, to save on tips
        dmso_column_counter = column_counter

        # pick up tip here
        safely_pick_up_tip(pipette_multi)

        # now dispense DMSO
        for vc, dil_vol in enumerate(drugs_volumes_for_dilutions):
            current_column = counter_to_platecolumn(dmso_column_counter)
            # add dmso to this column first
            dmso_dil_vol = volume_pre_next_dilution - dil_vol
            print_action('DMSO', dmso_src_well, current_column)
            pipette_multi.transfer(
                dmso_dil_vol,
                dmso_src_well,
                current_column,
                new_tip='never'
                )
            # prepare variables for next column
            dmso_column_counter += 1
            # problem if next column of dmso is in new set of stock plates
            if is_new_set_stock_plates(dmso_column_counter):
                # doesn't matter if we finished the doses as then dmso column
                # counter will be overwritten
                if vc < len(drugs_volumes_for_dilutions)-1:
                    print('DILUTION IS SPLIT ACROSS ROUNDS OF STOCK PLATES!!!')

        # done, drop tip
        pipette_multi.drop_tip()

        # continue serial dilution:
        # use multichannel to dispense from one col to the next
        previous_column = stock_column
        for dil_vol in drugs_volumes_for_dilutions:

            current_column = counter_to_platecolumn(column_counter)
            if previous_column.get_path()[0] != current_column.get_path()[0]:
                print('PREVIOUS AND CURRENT ON TWO DIFFERENT PLATES')
            print_action('drug', previous_column, current_column)
            safely_transfer(
                pipette_multi,
                dil_vol,
                previous_column.bottom(stock_frombottom_off),
                current_column,
                mix_before=(2, 5), # mix 2x with 5 uL before
                mix_after=(2, 5), # mix 2x with 5 uL after
                )

            # update columns
            previous_column = current_column
            column_counter += 1
            if is_new_set_stock_plates(column_counter):
                new_round_actions(pipette_multi)

    # update start_druglib_well
    start_druglib_well = stop_druglib_well


count_used_tips()
robot.pause(60)
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
