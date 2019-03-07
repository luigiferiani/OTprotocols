"""
@author Opentrons
@date April 27th, 2018
@version 1.3

@modified by Luigi Feriani, August 14th 2018
"""
from opentrons import labware, instruments, robot


def run_custom_protocol(pipette_type: 'StringSelection...'='p300-Single',
    pipette_mount:      'StringSelection...'='right',
    dye_labware_type:   'StringSelection...'='trough-12row',
    tip_start_from:     'StringSelection...'='A1'):

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
    pink_wells = ['A3', 'A4', 'A5', 'A7', 'A8', 'A9',
                  'B2', 'B6', 'B10',
                  'C1', 'C11', 'D1', 'D11',
                  'E2', 'E10', 'F3', 'F4', 'F8', 'F9',
                  'G5', 'G7', 'H6']

    light_pink_wells = ['A2', 'A6', 'A10', 'B1', 'B11', 'C12', 'D12',
                        'E1', 'E11', 'F2', 'F10', 'G3', 'G4', 'G8', 'G9',
                        'H5', 'H7']

    blue_wells = ['C3', 'C4', 'C5', 'C8', 'C9',
                  'D5', 'D7', 'D8',
                  'E5', 'E6', 'E7']

    light_blue_wells = ['D3']

    water    = dye_container.wells('A1')
    pink_dye = dye_container.wells('A2')
    blue_dye = dye_container.wells('A3')

    pipette.start_at_tip(tiprack.well(tip_start_from))
    # put water first
    pipette.transfer(
        30,
        water,
        output.wells(light_pink_wells + light_blue_wells),
        new_tip='once'
    )
    # pink
    pipette.pick_up_tip()
    pipette.transfer(
        50,
        pink_dye,
        output.wells(pink_wells),
        new_tip='never',
        trash=False)
    wells_for_lighter_pink = [well.top(-3) for well in output.wells(light_pink_wells)]
    pipette.transfer(
        20,
        pink_dye,
        wells_for_lighter_pink,
        new_tip='never',
        touch_tip=True,
        trash=False)
    print(pipette.current_tip())

    # mixing step
    for well_to_mix in light_pink_wells:
        pipette.mix(
            4,
            10,
            output.wells(well_to_mix))
    pipette.drop_tip()
    print(pipette.current_tip())

    # blue
    pipette.pick_up_tip()
    pipette.transfer(
        50,
        blue_dye,
        output.wells(blue_wells),
        new_tip='never',
        trash='False')
    pipette.transfer(
        20,
        blue_dye,
        output.wells(light_blue_wells).top(-3),
        new_tip='never',
        touch_tip=True,
        trash=False)
    print(pipette.current_tip())

    # mixing step
    pipette.mix(
        4,
        10,
        output.wells(light_blue_wells))

    pipette.drop_tip()
    print(pipette.current_tip())


# end function

run_custom_protocol(**{'pipette_type': 'p10-Single',
                        'pipette_mount': 'left',
                        'dye_labware_type': '6-well-plate',
                        'tip_start_from': 'H1'})
