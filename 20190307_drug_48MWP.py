"""
@author lferiani
@date March 07th, 2019

Pipette rack in 1
Source 48MWP in 2
Destination 48MWP in 3

Take diluted drug from A1 in Source and distribute it in staggered wells of Destination
Take water + DMSO from B1 in Source and distribute it in the remaining wells of Destination


"""

from opentrons import labware, instruments, robot

####################### user intuitive parameters

pipette_type = 'p10-Single'
pipette_mount = 'left'

tiprack_slot = '1'
tip_start_from = 'D2'   # first nonempty tip in the tip rack

transfer_volume_per_well = 2 # uL

source_slot = '2'
source_type = '48-well-plate'
source_drug_well = 'A1'
source_dmso_well = 'B1'

destination_slot = '3'
destination_type = '48-well-plate'
destination_drug_wells = ['A1', 'A3', 'A5', 'A7',
                          'B2', 'B4', 'B6', 'B8',
                          'C1', 'C3', 'C5', 'C7',
                          'D2', 'D4', 'D6', 'D8',
                          'E1', 'E3', 'E5', 'E7',
                          'F2', 'F4', 'F6', 'F8']
destination_dmso_wells = ['A2', 'A4', 'A6', 'A8',
                          'B1', 'B3', 'B5', 'B7',
                          'C2', 'C4', 'C6', 'C8',
                          'D1', 'D3', 'D5', 'D7',
                          'E2', 'E4', 'E6', 'E8',
                          'F1', 'F3', 'F5', 'F7']
agar_thickness = +3 # mm from the bottom of the well



############################ define labware
# pipette and tiprack
if pipette_type == 'p10-Single':
    tiprack = labware.load('tiprack-10ul', tiprack_slot)
    pipette = instruments.P10_Single(
        mount=pipette_mount,
        tip_racks=[tiprack])
pipette.start_at_tip(tiprack.well(tip_start_from))

# container for the drugs
src_container = labware.load(source_type, source_slot)
# where drug and dmso are in the container
src_drug = src_container.wells(source_drug_well)
src_dmso = src_container.wells(source_dmso_well)

# container for the agar-filled 48MWP
dst_container = labware.load(destination_type, destination_slot)
# where drug and dmso need to go in the destination container
dst_drug = dst_container.wells(destination_drug_wells)
dst_drug = [well.bottom(agar_thickness) for well in dst_drug]
dst_dmso = dst_container.wells(destination_dmso_wells)
dst_dmso = [well.bottom(agar_thickness) for well in dst_dmso]


#################### actions
# transfer drugs
pipette.transfer(transfer_volume_per_well,
                 src_drug,
                 dst_drug,
                 blow_out=True)

# transfer dmso
pipette.transfer(transfer_volume_per_well,
                 src_dmso,
                 dst_dmso,
                 blow_out=True)

# print
for c in robot.commands():
    print(c)
