"""
@author lferiani
@date June 26th, 2019

Tip rack for multichannel in 1
Trough for water in 4
Tip rack for drugs in 3
Source 48WP in 6
Destination 96WPs in 2,5,8

First dispense 10ul of water on all plates, using multichanel pipette_type
Then dispense 3ul of DMSO+drugs from 3 wells of the source 48WP onto wells of the destination 96WPs



"""
import numpy as np
from opentrons import labware, instruments, robot

####################### user intuitive parameters

# multichannel pipette parameters and tipracks
multi_pipette_type = 'p10-Multi'
multi_pipette_mount = 'left'
tiprack_slots_multi = ['1']
tiprack_type_multi = 'opentrons-tiprack-10ul'
tip_start_from_multi = '1'

# single pipette parameters
single_pipette_type = 'p10-Single'
single_pipette_mount = 'right'
tiprack_slots_single = ['3']
tiprack_type_single = 'opentrons-tiprack-10ul'
tip_start_from_single = 'A1'

# water trough
H2O_source_slot = '4'
H2O_source_type = 'trough-12row'
H2O_source_well = 'A1'
H2O_volume = 5

# drugs source
drugs_source_slot = '6'
drugs_source_type = '48-well-plate-sarsted'
drugs_names_source_wells = {'DMSO':'A1', 'Chlorpromazine':'B1', 'Amisulpride':'C1'}
drugs_volume = 3

# destination plates
agar_thickness = +3 # mm from the bottom of the well
destination_slots = ['2','5','8']
destination_type = '96-well-plate-sqfb-whatman'
plate_shape = (8,12)
ntreatments = len(drugs_names_source_wells) + 1 # 2 drugs, dmso, no treatment

def stagger_wells(plate_size, offset, ntreatments):
    nrows,ncols = plate_size
    foo = np.arange(ncols)
    wells = np.array([nrows * foo + (foo + offset) % 8,
                      nrows * foo + (foo + ntreatments + offset) % 8])
    wells = np.sort(wells.flatten())
    return wells

drugs_names_destination_wells = {}
for i, drug in enumerate(drugs_names_source_wells):
    drugs_names_destination_wells[drug] = stagger_wells(plate_shape, i, ntreatments)

# sort by well and print drug
def print_sorted_wellsdrugs(drugswell_dict, nwells):
    """
    Takes a dict with drug : list of wells,
    Prints out well -> drug
    sorted by well"""

    def number_to_name(input, nwells):
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if nwells == 96:
            nrows = 8
            ncols = 12
        row = input%nrows
        col = input//nrows + 1
        return alphabet[row]+str(col)

    drugs_list = []
    wells_list = []
    wellnames_list = []
    for drug in drugswell_dict:
        for well in drugswell_dict[drug]:
            drugs_list.append(drug)
            wells_list.append(well)
            wellnames_list.append(number_to_name(well, nwells))

    sorted_wellsdrugs = [(wellname,well,drug) for well, wellname, drug in sorted(zip(wells_list,wellnames_list,drugs_list))]
    for wn,w,d in sorted_wellsdrugs:
        print('{},{}'.format(wn,d))

# for the plate we fill at random:
def my_random_sample(popset, k):
    """Returns k element at random from popset"""
    k = int(k)
    pop = list(popset)
    sample = []
    for ii in range(k):
        jj = np.random.randint(len(pop)) # random index in remaining pop
        sample.append(pop.pop(jj))       # pop jj entry in pop and append to sample
    return sample

pool = set(np.arange(np.product(plate_shape)))
drugs_names_random_destination_wells = {}
np.random.seed(20190712) # for reproducibility. Let's use 20190712 for the actual experiment, something else for debugging
for i, drug in enumerate(drugs_names_source_wells):
    sample = my_random_sample(pool, np.product(plate_shape)/ntreatments)
    pool -= set(sample)
    drugs_names_random_destination_wells[drug] = sample


# print wells - drugs correspondence
print('Plate 1 and 2:')
print_sorted_wellsdrugs(drugs_names_destination_wells, 96)
print('Plate 3:')
print_sorted_wellsdrugs(drugs_names_random_destination_wells, 96)

############################# define custom multiwell plates

if '48-well-plate-sarsted' not in labware.list():
    custom_plate = labware.create(
        '48-well-plate-sarsted',        # name of you labware
        grid=(8, 6),                    # specify amount of (columns, rows)
        spacing=(12.4, 12.4),           # distances (mm) between each (column, row)
        diameter=10,                    # diameter (mm) of each well on the plate
        depth=17.05,                    # depth (mm) of each well on the plate
        volume=500)                     # Sarsted had a "volume of work"

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
        volume=650)                # this is the actual volume as per specs, not a "volume of work"

    print('Wells in 96WP Whatman:')
    for well in custom_plate.wells():
        print(well)

############################ define labware

# pipette and tiprack

# single channel
if single_pipette_type == 'p10-Single':
    tipracks_single = [labware.load(tiprack_type_single, tiprack_slot) \
                       for tiprack_slot in tiprack_slots_single]
    pipette_single = instruments.P10_Single(
        mount=single_pipette_mount,
        tip_racks=tipracks_single)
pipette_single.start_at_tip(tipracks_single[0].well(tip_start_from_single))
pipette_single.plunger_positions['drop_tip'] = -6

# multi channel
if multi_pipette_type == 'p10-Multi':
    tipracks_multi = [labware.load(tiprack_type_multi, tiprack_slot) \
                      for tiprack_slot in tiprack_slots_multi]
    pipette_multi = instruments.P10_Multi(
        mount=multi_pipette_mount,
        tip_racks=tipracks_multi)
pipette_multi.start_at_tip(tipracks_multi[0].well(tip_start_from_multi))
pipette_multi.plunger_positions['drop_tip'] = -6


# container for water
water_src_container = labware.load(H2O_source_type, H2O_source_slot)
water_src_well = water_src_container.wells(H2O_source_well)

# container for drugs
drugs_src_container = labware.load(drugs_source_type, drugs_source_slot)
# make a dict drugs -> wells
drugs_src_wells = {}
for drug, well in drugs_names_source_wells.items():
    drugs_src_wells[drug] = drugs_src_container.wells(well).bottom(0.3)

# destination containers
dst_plates = [labware.load(destination_type, slot) for slot in destination_slots]
dst_plate_random = dst_plates.pop(-1) # select the last plate to be the one filled "at random"



################### actions
# safety command
pipette_multi.drop_tip()
pipette_single.drop_tip()

# stupid function to measure how many tips got used
def count_used_tips():
    tc=0
    for c in robot.commands():
        if 'Picking up tip wells' in c: # order of checks here matters
            tc+=8
        elif 'Picking up tip well' in c: # note the lack of s in well
            tc+=1
    print('Tips used so far: {}'.format(tc))
    return


count_used_tips() # should be 0

# first put water
for dst_plate in (dst_plates + [dst_plate_random]):
    # pretend you're filling the top row, but this is 8channel so whole plate will be filled
    dst_wells = [dst_well.bottom(agar_thickness) for dst_well in dst_plate.rows('A')]
    # try this as well, should be same exact thing
    pipette_multi.transfer(H2O_volume,
                           water_src_well,
                           dst_wells,
                           blow_out=True)
    count_used_tips() # 8, 16, 24


# now put drugs in plates where position of drugs is "known"
for dst_plate in dst_plates:
    # one drug at a time:
    for drug in drugs_src_wells:
        # create list of destination wells in the selected plate for the selected drug
        dst_wells = [dst_plate.wells(wi).bottom(agar_thickness) \
                     for wi in drugs_names_destination_wells[drug]]

        # actual transfer
        # print(drugs_src_wells[drug])
        # for w in dst_wells: print(w)
        pipette_single.transfer(drugs_volume,
                                drugs_src_wells[drug],
                                dst_wells,
                                new_tip='always',
                                blow_out=True)

    count_used_tips() # each time we fill up 3/4 of a 96wp = 72 => expecting 96, 168
    robot.pause(60)
    pipette_single.reset_tip_tracking()


# now put drug on the "random" plate dst_plate_random
for drug in drugs_src_wells:
    # create list of destination wells in the selected plate for the selected drug
    dst_wells = [dst_plate_random.wells(wi).bottom(agar_thickness) \
                 for wi in drugs_names_random_destination_wells[drug]]
    # actual transfer
    pipette_single.transfer(drugs_volume,
                            drugs_src_wells[drug],
                            dst_wells,
                            new_tip='always',
                            blow_out=True)

count_used_tips() # 168+72 = 240


# print
# for c in robot.commands():
#     print(c)
