"""
@author lferiani
@date June 06th, 2019

Pipette rack in 1
Source 48MWP in 2
Destination 48MWP in 3

First put a droplet of water from A1 (either 5 or 10ul) on each well, then
Take one compound "DMSO" from B1 in Source and distribute it in wells of Destination
Take one compound "OP50" from C1 in Source and distribute it in wells of Destination

In destination 48WP:
Cols 1 to 4 have 5ul H2O
Cols 5 to 8 have 10ul H2O
Rows A to C are DMSO,
Rows D to F are OP50
Rows A,D have 3ul compound
Rows B,E have 5ul compound
Rows C,F have 10ul compound


"""

from opentrons import labware, instruments, robot

####################### user intuitive parameters

pipette_type = 'p10-Single'
pipette_mount = 'left'

tiprack_slot = '1'
tiprack_type = 'opentrons-tiprack-10ul'
tip_start_from = 'A1'   # first nonempty tip in the tip rack

transfer_volume_per_well = 5 # uL

source_slot = '2'
source_type = '48-well-plate-sarsted'
source_H2O_well = 'A1'
source_DMSO_well = 'B1'
source_OP50_well = 'C1'

destination_slot = '3'
destination_type = '48-well-plate-sarsted'

destination_DMSO_rows = ['A','B','C']
destination_OP50_rows = ['D','E','F']
compound_volumes = [3, 5, 10]

water_volumes = [5, 10]
destination_water_cols = [['1','2','3','4'],
                          ['5','6','7','8']]

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

############################ define labware
# pipette and tiprack
if pipette_type == 'p10-Single':
    tiprack = labware.load(tiprack_type, tiprack_slot)
    pipette = instruments.P10_Single(
        mount=pipette_mount,
        tip_racks=[tiprack])
pipette.start_at_tip(tiprack.well(tip_start_from))
pipette.plunger_positions['drop_tip'] = -6

# container for the drugs
src_container = labware.load(source_type, source_slot)
# where water, op50, and dmso are in the source container
src_water = src_container.wells(source_H2O_well)
src_water = src_water.bottom(1)
src_op50 = src_container.wells(source_OP50_well)
src_op50 = src_op50.bottom(1)
src_dmso = src_container.wells(source_DMSO_well)
src_dmso = src_dmso.bottom(1)

# container for the agar-filled 48MWP
dst_container = labware.load(destination_type, destination_slot)


#################### actions

# safety command
pipette.drop_tip()

# first put water
for vol, _cols in zip(water_volumes, destination_water_cols):
    # prepare variables for destination water wells
    dst_water_wells = dst_container.columns(_cols)
    dst_water_wells = [well.bottom(agar_thickness) for column in dst_water_wells for well in column]
    # transfer
    pipette.transfer(vol,
                     src_water,
                     dst_water_wells,
                     new_tip='always',
                     blow_out=True)

# now dmso
for vol, _row in zip(compound_volumes, destination_DMSO_rows):
    # prepare variables for destination dmso dst_water_wells
    dst_dmso_wells = dst_container.rows(_row)
    dst_dmso_wells = [well.bottom(agar_thickness) for well in dst_dmso_wells]
    # transfer
    pipette.transfer(vol,
                     src_dmso,
                     dst_dmso_wells,
                     new_tip='always',
                     blow_out=True)

# now OP50
for vol, _row in zip(compound_volumes, destination_OP50_rows):
    # prepare variables for destination dmso dst_water_wells
    dst_op50_wells = dst_container.rows(_row)
    dst_op50_wells = [well.bottom(agar_thickness) for well in dst_op50_wells]
    # transfer
    pipette.transfer(vol,
                     src_op50,
                     dst_op50_wells,
                     new_tip='always',
                     blow_out=True)


# print
for c in robot.commands():
    print(c)
