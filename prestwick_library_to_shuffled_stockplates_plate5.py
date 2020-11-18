"""
@author lferiani
@date Nov 16th, 2020

Only use multichannel

Tip racks for drugs in 4, 7, 10

Source 96WP in 5
Destination 96WPs in 11, 8, 9

Times 3 (number of shufflings)
    - Dispense 10 ul of compound from the source (library) 96 WP to its
        destination (stock) 96 WP (while shuffling columns)

Notation:
    Source = library
    Destination = stock
"""

import numpy as np
from opentrons import labware, instruments, robot

####################### user intuitive parameters

plate_number = 5
date = 20201118

# multichannel pipette parameters and tipracks
multi_pipette_type = 'p10-Multi'
multi_pipette_mount = 'left'

tiprackdrugs_slots = ['4', '7', '10']
tiprackdrugs_type = 'opentrons-tiprack-10ul'
tiprackdrugs_startfrom = '1'

# drugs source
drugs_source_slot = '5'
drugs_source_type = '96-well-plate-pcr-thermofisher'
drugs_volume = 10.0
frombottom_off = +1

# destination plates
destination_slots = ['11', '8', '9']
destination_type = '96-well-plate-pcr-thermofisher'

n_columns = 12

# create mapping from sources to destination.
# it is a dict, with:
# {(source slot, dest slot):(cols in source, cols in dest)}
drugs_mapping = {}
seed = int(str(date) + str(plate_number)) # for reproducibility. Let's use the experimental date for the actual experiment and the plate number, something else for debugging
print(seed)
np.random.seed(seed)
src_cols = np.arange(n_columns) # array of column numbers
for ds in destination_slots:
    # create entry in dict
    dst_cols = src_cols.copy() # array of column numbers to be shuffled
    np.random.shuffle(dst_cols) # shuffle columns in destination. This acts in place!!
    drugs_mapping[(drugs_source_slot, ds)] = (src_cols, dst_cols)

# print out drugs_mapping:
for key, value in drugs_mapping.items():
    _src_slot, _dst_slot = key
    _src_cols, _dst_cols = value
    for _src_col, _dst_col in zip(_src_cols, _dst_cols):
        print('slot {0} col {1} --> slot {2} col {3}'.format(_src_slot, _src_col, _dst_slot, _dst_col))

# print out for humans to do it
plate_name_dict = {
    '5': 'Prestwick_L{:02d}'.format(plate_number),
    '11': 'Prestwick_L{:02d}_SH01'.format(plate_number),
    '8': 'Prestwick_L{:02d}_SH02'.format(plate_number),
    '9': 'Prestwick_L{:02d}_SH03'.format(plate_number),
    }
instructions_list = []
for key, value in drugs_mapping.items():
    _src_slot, _dst_slot = key
    _src_cols, _dst_cols = value
    for _src_col, _dst_col in zip(_src_cols, _dst_cols):
        src_col_number = _src_col+1
        dst_col_number = _dst_col+1
        src_plate_name = plate_name_dict[_src_slot]
        dst_plate_name = plate_name_dict[_dst_slot]
        instruction = f'{src_plate_name} col {src_col_number:02d} --> {dst_plate_name} col {dst_col_number:02d}'
        instructions_list.append(instruction)
# now sort alphabetically (so you do 1 drug => 3 shufflings)
sorted_instructions = sorted(instructions_list)
for instruction in sorted_instructions:
    print(instruction)


############################# define custom multiwell plates

if '96-well-plate-pcr-thermofisher' not in labware.list():
    custom_plate = labware.create(
        '96-well-plate-pcr-thermofisher',   # name of you labware
        grid=(12, 8),              # specify amount of (columns, rows)
        spacing=(9.00, 9.00),      # distances (mm) between each (column, row)
        diameter=5.50,             # diameter (mm) of each well on the plate (here width at top!!)
        depth=15.00,               # depth (mm) of each well on the plate
        volume=200)                # as per manufacturer's website

    print('Wells in 96WP PCR Thermo Fisher:')
    for well in custom_plate.wells():
        print(well)

############################ define labware
# i.e. translate user-friendly parameters into opentrons language

# pipette and tiprack

# multi channel
if multi_pipette_type == 'p10-Multi':
    tiprackdrugs = [labware.load(tiprackdrugs_type, slot) \
                      for slot in tiprackdrugs_slots]
    pipette_multi = instruments.P10_Multi(
        mount=multi_pipette_mount,
        tip_racks=tiprackdrugs)
pipette_multi.start_at_tip(tiprackdrugs[0].well(tiprackdrugs_startfrom))
pipette_multi.plunger_positions['drop_tip'] = -6
# faster dispense
pipette_multi.set_speed(dispense=pipette_multi.speeds['dispense']*4)

# translate the drugs mapping dict in robot language
# load source plate first
src_plate = labware.load(drugs_source_type, drugs_source_slot)
src_wells = [well.bottom(frombottom_off) for well in src_plate.rows('A')]
wells_mapping = {}
for key, value in drugs_mapping.items():
    # unpack slots
    _src_slot, _dst_slot = key
    _src_cols, _dst_cols = value
    # load labware for dst
    dst_plate = labware.load(destination_type,  _dst_slot)
    # create list of wells with the right bottom offset
    # NOT YET FOLLOWING THE ORDER WE WANT
    dst_wells = [well.bottom(frombottom_off) for well in dst_plate.rows('A')]
    # these are normal lists though so should be reshufflable
    src_wells_copy = [src_wells[wi] for wi in _src_cols]
    dst_wells = [dst_wells[wi] for wi in _dst_cols]
    # store in wells_mapping
    wells_mapping[(src_plate, dst_plate)] = (src_wells_copy, dst_wells)

# print(wells_mapping)

################### actions
# safety command
pipette_multi.drop_tip()

# stupid function to measure how many tips got used
def count_used_tips():
    tc=0
    for c in robot.commands():
        if 'Picking up tip wells' in c: # order of checks here matters
            tc+=8
        elif 'Picking up tip well' in c: # note the lack of s in well
            tc+=1
    print('Tips used so far: {}'.format(tc))
    return


count_used_tips() # should be 0

# first put water, then drugs in plates
for plates_tuple, wells_tuple in wells_mapping.items():
    # unpack
    src_plate, dst_plate = plates_tuple
    src_wells, dst_wells = wells_tuple

    # drug transfer
    pipette_multi.transfer(
        drugs_volume,
        src_wells,
        dst_wells,
        new_tip='always',
        mix_before=(3, 10),
        blow_out=True)

    for s,d in zip(src_wells, dst_wells):
        print('{} {} -> {} {}'.format(
            src_plate.parent, s[0], dst_plate.parent, d[0]))

    count_used_tips()
    robot.pause()
    # each time we fill up a 96wp => expecting 96 tips every plate
    # so 96, 192, 288


#write out robot commands
if not robot.is_simulating():
    import datetime
    out_fname = (
        datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        + '_prestwick_library_shuffling'
        + '_plate' + str(plate_number)
        + '_runlog.txt'
        )
    out_fname = '/data/user_storage/opentrons_data/protocols_logs/' + out_fname
    with open(out_fname,'w') as fid:
        for command in robot.commands():
            print(command,file=fid)
