"""
@author lferiani
@date Nov 4th, 2020

Both pipettes: a p10 single and a p50 single

Small protocol that deals with one plate at a time
Start with library 96WPs, with drugs in every third well, starting with 45ul

First step is to put control in row H:
Water in H4:H7
DMSO in H8:H12

For each well starting with high concentration drug,
    add solvent to the two wells to its right
    serially dilute


Tip rack for p10 single (to change) in 5
Tip rack for p50 single (to change) in 8
Trough for water and DMSO in 9
Library 96WPs in 6

240 drugs in total, 8 + 7*3 drugs per well, so 8 plates and one extra column

Each protocol shohuld use fewer tips than in two tipracks

"""
import pdb
import numpy as np
from opentrons import labware, instruments, robot

####################### user intuitive parameters

# single channel pipette parameters and tipracks for drugs dilution
drugs_pipette_type = 'p10-Single'
drugs_pipette_mount = 'left'
tiprack_drugs_slots = ['5']
tiprack_drugs_type = 'opentrons-tiprack-10ul'
tiprack_drugs_startfrom = '1'

# single channel pipette parameters and tipracks
solvent_pipette_type = 'p50-Single'
solvent_pipette_mount = 'right'
tiprack_solvent_slots = ['8']
tiprack_solvent_type = 'opentrons-tiprack-300ul'
tiprack_solvent_startfrom = '1'

# trough
trough_slot = '9'
trough_type = 'trough-12row'
H2O_source_well = 'A1'
DMSO_source_well = 'A2'

# library plate
library_slot = '6'
library_type = '96-well-plate-pcr-thermofisher'
library_frombottom_off = +1 # mm from bottom of library wells

# volumes
control_volume = 40  # volume in H4:H12
solvent_volume = 36  # volume of solvent in dilution wells
drugs_volume_for_dilution = 4  # volume of drug (or diluted drug) to transfer

# control wells
control_row = 'A'
DMSO_wells = [control_row + col for col in ['4', '5', '6', '7', '8']]
H2O_wells = [control_row + col for col in ['9', '10', '11', '12']]

# we dilute across 2 times so we always have 3 doses
# wells with the high concentration of drugs are only every 3rd column,
# and then I need to remove those that are used by the control!!!
high_conc_cols = ['1', '4', '7', '10']
drug_wells = [[row + col for col in high_conc_cols] for row in 'ABCDEFGH']
# list comprehension is not very effective way of doing list(set-set),
# but it's small lists AND ORDER MATTERS!!
drug_wells = [[w for w in r if w not in (DMSO_wells + H2O_wells)]
              for r in drug_wells]
assert len([w for r in drug_wells for w in r]) == 8+7*3

############################# define custom multiwell plates

if '48-well-plate-sarsted' not in labware.list():
    custom_plate = labware.create(
        '48-well-plate-sarsted',        # name of you labware
        grid=(8, 6),                    # specify amount of (columns, rows)
        spacing=(12.4, 12.4),           # distances (mm) between each (column, row)
        diameter=10,                    # diameter (mm) of each well on the plate
        depth=17.05,                    # depth (mm) of each well on the plate
        volume=500
        )                     # Sarsted had a "volume of work"

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
        volume=650
        )                # this is the actual volume as per specs, not a "volume of work"

    print('Wells in 96WP Whatman:')
    for well in custom_plate.wells():
        print(well)

if '96-well-plate-pcr-thermofisher' not in labware.list():
    custom_plate = labware.create(
        '96-well-plate-pcr-thermofisher',   # name of you labware
        grid=(12, 8),              # specify amount of (columns, rows)
        spacing=(9.00, 9.00),      # distances (mm) between each (column, row)
        diameter=5.50,             # diameter (mm) of each well on the plate (here width at top!!)
        depth=15.00,               # depth (mm) of each well on the plate
        volume=200
        )                # as per manufacturer's website

    print('Wells in 96WP PCR Thermo Fisher:')
    for well in custom_plate.wells():
        print(well)

############################ define labware
# i.e. translate user-friendly parameters into opentrons language

# pipette and tiprack

# multi channel
if drugs_pipette_type == 'p10-Single': # this is mostly a check
    tiprackdrugs = [
        labware.load(tiprack_drugs_type, tiprack_slot)
        for tiprack_slot in tiprack_drugs_slots
        ]
    pipette_drugs = instruments.P10_Single(
        mount=drugs_pipette_mount,
        tip_racks=tiprackdrugs
        )
pipette_drugs.start_at_tip(tiprackdrugs[0].well(tiprack_drugs_startfrom))
pipette_drugs.plunger_positions['drop_tip'] = -6


# single channel
if solvent_pipette_type == 'p50-Single': # this is mostly a type check
    tipracksolvent = [
        labware.load(tiprack_solvent_type, tiprack_slot)
        for tiprack_slot in tiprack_solvent_slots
        ]
    pipette_solvent = instruments.P50_Single(
        mount=solvent_pipette_mount,
        tip_racks=tipracksolvent
        )
pipette_solvent.start_at_tip(tipracksolvent[0].well(tiprack_solvent_startfrom))
pipette_solvent.plunger_positions['drop_tip'] = -6
# pdb.set_trace()


# container for controls
ctrl_src_container = labware.load(trough_type, trough_slot)
dmso_src_well = ctrl_src_container.wells(DMSO_source_well)
water_src_well = ctrl_src_container.wells(H2O_source_well)

# define library plate
lib_plate = labware.load(library_type, library_slot)

# define destination for controls:
dmso_dst_wells = lib_plate.wells(*[DMSO_wells])
water_dst_wells = lib_plate.wells(*[H2O_wells])

# wells where the highest concentration drugs go
all_high_conc_drugs_wells = [lib_plate.wells(*[drug_wells_in_row])
                             for drug_wells_in_row in drug_wells]

# pdb.set_trace()
################### functions

# stupid function to measure how many tips got used
def count_used_tips(is_print=True):
    """
    Count how many tips have been used and print it (can be silenced).
    Return a tuple with the number of used tips from single and multichannel
    pipettes.
    """
    stc = 0
    mtc = 0
    for c in robot.commands():
        if 'Picking up tip wells' in c: # order of checks here matters
            mtc+=8
        elif 'Picking up tip well' in c: # note the lack of s in well
            stc+=1
    if is_print:
        print('TIP COUNT: Single = {}, Multi = {}'.format(stc, mtc))
    return stc, mtc

def get_well_to_the_right_of(well):
    """
    Return the well (object) to the right of the input well (object)
    """
    plate = well.get_parent()
    well_name = well.get_name()
    # create name for next well, checking for out of bounds
    row_name = well_name[0]
    col_number = int(well_name[1:])
    next_col_number = col_number + 1
    assert next_col_number <= len(plate.cols()), (
        "Next well's column would be out of bounds"
    )
    next_well_name = row_name + str(col_number + 1)
    # make the well object
    next_well = plate.wells(next_well_name)
    return next_well

def my_get_path(well_or_wellseries):
    """
    Return slot on the robot deck, and position in the plate, of an input object
    """
    slot, _, pos = well_or_wellseries.get_path()
    return (slot, pos)


def dispense_controls():

    pipette_solvent.transfer(
        control_volume,
        dmso_src_well,
        dmso_dst_wells,
        blow_out=True,
        new_tip='once'
        )
    pipette_solvent.transfer(
        control_volume,
        water_src_well,
        water_dst_wells,
        blow_out=True,
        new_tip='once'
        )

    return

def put_solvent_in_row(high_wells):
    wells_for_solvent = []
    for high_well in high_wells:
        # get the two wells we need to dilute in
        middle_well = get_well_to_the_right_of(high_well)
        low_well = get_well_to_the_right_of(middle_well)
        wells_for_solvent.append(middle_well)
        wells_for_solvent.append(low_well)
    # now dispense
    pipette_solvent.transfer(
        solvent_volume,
        dmso_src_well,
        wells_for_solvent,
        blow_out=True,
        new_tip='once'
        )
    return

def serially_dilute_well_drugonly(high_well):
    # get the two wells we need to dilute in
    middle_well = get_well_to_the_right_of(high_well)
    low_well = get_well_to_the_right_of(middle_well)

    # and do the dilution
    pipette_drugs.transfer(
        drugs_volume_for_dilution,
        [high_well, middle_well],
        [middle_well, low_well],
        blow_out=True,
        mix_before=(2, 10), # mix 2x with 10 uL before
        mix_after=(2, 10), # mix 2x with 10 uL after
        touch=True,
        new_tip='always'
    )


def serially_dilute_well(high_well):
    # get the two wells we need to dilute in
    middle_well = get_well_to_the_right_of(high_well)
    low_well = get_well_to_the_right_of(middle_well)

    # now dispense all the dmso first
    pipette_solvent.transfer(
        solvent_volume,
        dmso_src_well,
        [middle_well, low_well],
        blow_out=True,
        new_tip='once'
        )

    # and do the dilution
    pipette_drugs.transfer(
        drugs_volume_for_dilution,
        [high_well, middle_well],
        [middle_well, low_well],
        blow_out=True,
        mix_before=(2, 10), # mix 2x with 10 uL before
        mix_after=(2, 10), # mix 2x with 10 uL after
        touch=True,
        new_tip='always'
    )

    return



################### actions

# safety command
pipette_solvent.drop_tip()
pipette_drugs.drop_tip()

# controls
dispense_controls()
count_used_tips()

# dilute
for high_conc_drugs_wells in all_high_conc_drugs_wells:
    # deal with one row being a well and not a wellseries
    if len(high_conc_drugs_wells) == 0:
        high_conc_drugs_wells = [high_conc_drugs_wells]
    put_solvent_in_row(high_conc_drugs_wells)
    for well in high_conc_drugs_wells:
        serially_dilute_well_drugonly(well)

# tips used:
# 2 tips for controls
# 1 tip for each row to put solvent => 28 tips
# 2 tips per drug to dilute => 58 tips
# total is 68 tips (58 10ul tips and 10 200ul tips)
count_used_tips()

#write out robot commands
if not robot.is_simulating():
    import datetime
    out_fname = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")+'_runlog.txt'
    out_fname = '/data/user_storage/opentrons_data/protocols_logs/' + out_fname
    with open(out_fname,'w') as fid:
        for command in robot.commands():
            print(command,file=fid)
