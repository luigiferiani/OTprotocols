"""
@author lferiani
@date June 24th, 2019

OpenTrons Pipette rack in 3

Using the multichannel P10,
pick up tips, pause, return tips

"""

from opentrons import labware, instruments, robot

####################### user intuitive parameters

tiprack_slot = '3'
tip_start_from = '1'   # first nonempty tip in the tip rack
cols_left = 12 # full tiprack

############################ define labware
# pipette and tiprack
tiprack = labware.load('opentrons-tiprack-10ul', tiprack_slot)
# tiprack = labware.load('opentrons_96_tiprack_10ul', tiprack_slot)
pipette = instruments.P10_Multi(
    mount='left',
    tip_racks=[tiprack])
pipette.start_at_tip(tiprack.cols(tip_start_from))
pipette.plunger_positions['drop_tip'] = -6

#################### actions

# safety command
# pipette.drop_tip() # actually maybe it hurts the robot to try to drop a tip when there's none

for _ in range(cols_left):
    pipette.pick_up_tip()
    pipette.delay(seconds=5)
    pipette.return_tip()

# print
for c in robot.commands():
    print(c)
