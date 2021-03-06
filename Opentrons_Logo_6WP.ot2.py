"""
@author Opentrons
@date April 27th, 2018
@version 1.3

@modified by Luigi Feriani, July 27th 2018
"""
from opentrons import labware, instruments


def run_custom_protocol(pipette_type: 'StringSelection...'='p300-Single',
    pipette_mount: 'StringSelection...'='right',
    dye_labware_type: 'StringSelection...'='trough-12row'):

    if pipette_mount == 'left' or pipette_mount == 'l':
        mount_position = 'left'
    elif pipette_mount == 'right' or pipette_mount == 'r':
        mount_position = 'right'
    else:
        raise Exception(
        "You can only mount the pipette on the 'left' or 'right' mount")

    if pipette_type == 'p300-Single':
        tiprack = labware.load('tiprack-200ul', '1')
        pipette = instruments.P300_Single(
            mount=mount_position,
            tip_racks=[tiprack])
    elif pipette_type == 'p50-Single':
        tiprack = labware.load('tiprack-200ul', '1')
        pipette = instruments.P50_Single(
            mount=mount_position,
            tip_racks=[tiprack])
    elif pipette_type == 'p10-Single':
        tiprack = labware.load('tiprack-10ul', '1')
        pipette = instruments.P10_Single(
            mount=mount_position,
            tip_racks=[tiprack])

    if dye_labware_type == 'trough-12row':
        dye_container = labware.load('trough-12row', '2')
    elif dye_labware_type == '6-well-plate':
        dye_container = labware.load('6-well-plate', '2')
    else:
        dye_container = labware.load('tube-rack-2ml', '2')

    output = labware.load('96-flat', '3')
    # Well Location set-up
    dye1_wells = ['A5', 'A6', 'A8', 'A9', 'B4', 'B10', 'C3', 'C11', 'D3',
                  'D11', 'E3', 'E11', 'F3', 'F11', 'G4', 'G10',
                  'H5', 'H6', 'H7', 'H8', 'H9']

    dye2_wells = ['C7', 'D6', 'D7', 'D8', 'E5', 'E6', 'E7', 'E8',
                  'E9', 'F5', 'F6', 'F7', 'F8', 'F9', 'G6', 'G7', 'G8']

    dye2 = dye_container.wells('A1')
    dye1 = dye_container.wells('A2')

    pipette.distribute(
        50,
        dye1,
        output.wells(dye1_wells),
        new_tip='once')
    pipette.distribute(
        50,
        dye2,
        output.wells(dye2_wells),
        new_tip='once')


run_custom_protocol(**{'pipette_type': 'p10-Single',
                        'pipette_mount': 'left',
                        'dye_labware_type': 'trough-12row'})
