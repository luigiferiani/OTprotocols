"""
@author lferiani
@date June 24th, 2019

Pipette rack in 1
Source trough in 2
Destination 96MWP in 3

Dispense 10ul of water from well A1 in trough to a 96 well plate

"""

from opentrons import labware, instruments, robot

####################### user intuitive parameters

pipette_type = 'p10-Multi'
pipette_mount = 'left'

tiprack_slots = ['1']
tiprack_type = 'opentrons-tiprack-10ul'
tip_start_from = '1'   # first nonempty tip column in the first tip rack

source_slot = '2'
source_type = 'trough-12row'
source_H2O_well = 'A1'

destination_slot = '3'
destination_type = '96-well-plate-sqfb-whatman'

water_volume = 10

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
elif pipette_type == 'p10-Multi':
    tipracks = [labware.load(tiprack_type, tiprack_slot) for tiprack_slot in tiprack_slots]
    pipette = instruments.P10_Multi(
        mount=pipette_mount,
        tip_racks=tipracks)
    pipette.start_at_tip(tipracks[0].cols(tip_start_from))
pipette.plunger_positions['drop_tip'] = -6

# container for the drugs
src_container = labware.load(source_type, source_slot)
# where water, op50, and dmso are in the source container
src_water = src_container.wells(source_H2O_well)
src_water = src_water.bottom(0.5)

# container for the agar-filled 96MWP
dst_container = labware.load(destination_type, destination_slot)


################### actions
# safety command
pipette.drop_tip()


# stupid function to measure how many tips got used
def count_used_tips():
    tc=0
    for c in robot.commands():
        if 'Picking up tip wells' in c: # order of checks here matters
            tc+=8
        elif 'Picking up tip well' in c: # note the lack of s in well
            tc+=1
    print(tc)
    return

# put water
pipette.pick_up_tip()
for dst_col in dst_container.cols():
    pipette.transfer(water_volume,
                     src_water,
                     dst_col.bottom(agar_thickness),
                     blow_out=True,
                     new_tip='never')
pipette.drop_tip()

# try this as well, should be same exact thing
pipette.transfer(water_volume,
                     src_water,
                     [dst_well.bottom(3) for dst_well in dst_container.rows('A')],
                     blow_out=True)

count_used_tips() # should be 8


# print
for c in robot.commands():
    print(c)
