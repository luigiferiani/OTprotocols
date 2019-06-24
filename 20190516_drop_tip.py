"""
@author lferiani
@date May 15th, 2019

Pipette rack in 1

Pick up tip, return tip

"""

from opentrons import labware, instruments, robot

####################### user intuitive parameters

pipette_type = 'p10-Single'
pipette_mount = 'left'

tiprack_slot = '1'
tip_start_from = 'A3'   # first nonempty tip in the tip rack
tips_left = 56 # 7 columns of 8 rows each


############################ define labware
# pipette and tiprack
if pipette_type == 'p10-Single':
    tiprack = labware.load('tiprack-10ul', tiprack_slot)
    pipette = instruments.P10_Single(
        mount=pipette_mount,
        tip_racks=[tiprack])
pipette.start_at_tip(tiprack.well(tip_start_from))
# pipette._drop_tip_speed=30
#################### actions

# safety command
# pipette.drop_tip()

for _ in range(tips_left):
    pipette.pick_up_tip()
    pipette.delay(seconds=1)
    pipette.return_tip()

# print
for c in robot.commands():
    print(c)
