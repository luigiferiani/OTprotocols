"""
@author lferiani
@date June 18th, 2019

Pipette rack in 4 and 1
Source 48MWP in 2
Destination 96MWP in 3

First take some water from A2 and put it in C2, take some DMSO from B2 and mix it with the water in C2,
Take 1.5 ul DMSO from B2 and distribute it in destination
Take 3 ul of DMSO+H2O from C2 and distribute it in destination


In destination 96WP:
Rows A to D have 5 ul water
Rows E to H have 10 ul water

Cols 1 to 6 have 1.5ul DMSO
Cols 6 to 12 have 3ul of DMSO+H2O mix

"""

from opentrons import labware, instruments, robot

####################### user intuitive parameters

pipette_type = 'p10-Single'
pipette_mount = 'left'

tiprack_slots = ['4','1']
tiprack_type = 'opentrons-tiprack-10ul'
tip_start_from = 'A10'   # first nonempty tip in the first tip rack

source_slot = '2'
source_type = '48-well-plate-sarsted'
source_H2O_well = 'A2'
source_DMSO_well = 'B2'
source_dilDMSO_well = 'C2'

destination_slot = '3'
destination_type = '96-well-plate-sqfb-whatman'

destination_DMSO_cols = [str(x+1) for x in range(0,6)]
destination_dilDMSO_cols = [str(x+1 + 6) for x in range(0,6)]
DMSO_volume = 1.5
dilDMSO_volume = 3

mixing_volume = 100 # how much of DMSO and water will be mixed so we can take 3 ul x 48 wells of it?

water_volumes = [5, 10]
destination_water_rows = [['A','B','C','D'],
                          ['E','F','G','H']]

agar_thickness = +3 # mm from the bottom of the well

############################# define custom multiwell plates

if '48-well-plate-sarsted' not in labware.list():
    custom_plate = labware.create(
        '48-well-plate-sarsted',        # name of you labware
        grid=(8, 6),                    # specify amount of (columns, rows)
        spacing=(12.4, 12.4),           # distances (mm) between each (column, row)
        diameter=10,                    # diameter (mm) of each well on the plate
        depth=17.05,                    # depth (mm) of each well on the plate
        volume=500)                     # Sarsted had a "volume of work"

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

    for well in custom_plate.wells():
        print(well)

############################ define labware
# pipette and tiprack
if pipette_type == 'p10-Single':
    tipracks = [labware.load(tiprack_type, tiprack_slot) for tiprack_slot in tiprack_slots]
    pipette = instruments.P10_Single(
        mount=pipette_mount,
        tip_racks=tipracks)
pipette.start_at_tip(tipracks[0].well(tip_start_from))
pipette.plunger_positions['drop_tip'] = -6

# container for the drugs
src_container = labware.load(source_type, source_slot)
# where water, op50, and dmso are in the source container
src_water = src_container.wells(source_H2O_well)
src_water = src_water.bottom(0.5)
src_dmso = src_container.wells(source_DMSO_well)
src_dmso = src_dmso.bottom(0.5)
src_dildmso = src_container.wells(source_dilDMSO_well)
src_dildmso = src_dildmso.bottom(0.5)

# container for the agar-filled 96MWP
dst_container = labware.load(destination_type, destination_slot)


################### actions
# safety command
pipette.drop_tip()

# stupid function to measure how many tips got used
def count_used_tips():
    tc=0
    for c in robot.commands():
        if 'Picking up tip' in c:
            tc+=1
    print(tc)
    return

# first mix:
pipette.transfer(mixing_volume,
                 src_water,
                 src_dildmso,
                 blow_out=True)
count_used_tips() # should be 1

pipette.transfer(mixing_volume,
                 src_dmso,
                 src_dildmso,
                 new_tip='always',
                 blow_out=True,
                 mix_after=(1,10))
count_used_tips() # should be 11

# then put water
for vol, _rows in zip(water_volumes, destination_water_rows):
    # prepare variables for destination water wells
    dst_water_wells = dst_container.rows(_rows)
    # note here list of lists so we can change tip every row
    dst_water_wells = [[well.bottom(agar_thickness) for well in row] for row in dst_water_wells]
    # transfer
    # divide by row to use fewer tips
    for dst_row in dst_water_wells:
        pipette.transfer(vol,
                         src_water,
                         dst_row,
                         blow_out=True)

count_used_tips() # should be 19

# now dmso
# prepare variables for destination dmso dst_water_wells
dst_dmso_wells = dst_container.columns(destination_DMSO_cols)
dst_dmso_wells = [well.bottom(agar_thickness) for col in dst_dmso_wells for well in col]
# transfer
pipette.transfer(DMSO_volume,
                 src_dmso,
                 dst_dmso_wells,
                 new_tip='always',
                 blow_out=True)
count_used_tips() # should be 19 + 48 = 67


# now diluted dmso
# prepare variables for destination dmso dst_water_wells
dst_dildmso_wells = dst_container.columns(destination_dilDMSO_cols)
dst_dildmso_wells = [well.bottom(agar_thickness) for col in dst_dildmso_wells for well in col]
# transfer
pipette.transfer(dilDMSO_volume,
                 src_dildmso,
                 dst_dildmso_wells,
                 new_tip='always',
                 blow_out=True)
count_used_tips() # should be 67 + 48 = 115


# print
for c in robot.commands():
    print(c)
