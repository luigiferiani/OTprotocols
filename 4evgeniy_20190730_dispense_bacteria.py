"""
@author lferiani
@date July 30th, 2019

Materials (what: where):
96WP flat, source of bacterial strains: 2
96WP square wells, destination of bacterial wells: 3
Tip rack for multichannel in 1

Protocol:
Dispense 10 ul from source to destination, keeping order (just a copy)

"""

import numpy as np
from opentrons import labware, instruments, robot

####################### user intuitive parameters

# multichannel pipette parameters and tipracks
multi_pipette_type = 'p10-Multi'
multi_pipette_mount = 'left'
tiprack_slots_multi = ['1','8']
tiprack_type_multi = 'opentrons-tiprack-10ul'
tip_start_from_multi = '1'

# bugs source
source_slot = '2'
source_type = '96-flat'

dispensing_volume = 10

# M9 trough
M9_source_slot = '7'
M9_source_type = 'trough-12row'
M9_source_well = 'A2'
M9_volume = 10


# destination plates
agar_thickness = +5 # mm from the bottom of the well
destination_slots = ['3']
destination_type = '96-well-plate-sqfb-whatman'

############################# define custom multiwell plates

if '48-well-plate-sarsted' not in labware.list():
    custom_plate = labware.create(
        '48-well-plate-sarsted',        # name of you labware
        grid=(8, 6),                    # specify amount of (columns, rows)
        spacing=(12.4, 12.4),           # distances (mm) between each (column, row)
        diameter=10,                    # diameter (mm) of each well on the plate
        depth=17.05,                    # depth (mm) of each well on the plate
        volume=500)                     # Sarsted had a "volume of work"

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
        volume=650)                # this is the actual volume as per specs, not a "volume of work"

    print('Wells in 96WP Whatman:')
    for well in custom_plate.wells():
        print(well)

############################ define labware

# pipette and tiprack

# multi channel
if multi_pipette_type == 'p10-Multi':
    tipracks_multi = [labware.load(tiprack_type_multi, tiprack_slot) \
                      for tiprack_slot in tiprack_slots_multi]
    pipette_multi = instruments.P10_Multi(
        mount=multi_pipette_mount,
        tip_racks=tipracks_multi)
pipette_multi.start_at_tip(tipracks_multi[0].well(tip_start_from_multi))
pipette_multi.plunger_positions['drop_tip'] = -6


# cource container
src_plate = labware.load(source_type, source_slot)

# container for M9
M9_src_container = labware.load(M9_source_type, M9_source_slot)
M9_src_well = M9_src_container.wells(M9_source_well)

# destination containers
dst_plates = [labware.load(destination_type, slot) for slot in destination_slots]


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

# first put water, then drugs in plates where position of drugs is "known"
for dst_plate in dst_plates:

    # pretend you're filling the top row, but this is 8channel so whole plate will be filled
    for src_well, dst_well in zip(src_plate.rows('A'), dst_plate.rows('A')):

        dst_well = dst_well.bottom(agar_thickness)

        pipette_multi.transfer(M9_volume,
                               M9_src_well,
                               dst_well,
                               rate=4.0,
                               blow_out=True)

        # try this as well, should be same exact thing
        pipette_multi.transfer(dispensing_volume,
                               src_well,
                               dst_well,
                               rate=4.0,
                               blow_out=True)


    count_used_tips()
    # should just be 96
