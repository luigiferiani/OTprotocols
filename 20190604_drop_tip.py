"""
@author lferiani
@date June 04th, 2019

OpenTrons Pipette rack in 1

Pick up tip, return tip

"""

from opentrons import labware, instruments, robot

####################### user intuitive parameters

tiprack_slot = '1'
tip_start_from = 'A1'   # first nonempty tip in the tip rack
tips_left = 96 # full tiprack

############################ define labware
# pipette and tiprack
tiprack = labware.load('opentrons-tiprack-10ul', tiprack_slot)
# tiprack = labware.load('opentrons_96_tiprack_10ul', tiprack_slot)
pipette = instruments.P10_Single(
    mount='left',
    tip_racks=[tiprack])
pipette.start_at_tip(tiprack.well(tip_start_from))

#################### actions

# safety command
# pipette.drop_tip() # actually maybe it hurts the robot to try to drop a tip when there's none

for _ in range(tips_left):
    pipette.pick_up_tip()
    pipette.delay(seconds=1)
    pipette.return_tip()

# print
for c in robot.commands():
    print(c)
