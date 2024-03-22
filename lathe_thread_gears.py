# Program for working out gear ratios to hit specific pitches
# on my Vevor mini lathe.
# Matthias Wandel Dec 30 2023 - Mar 19 2024
#
# The way I use this is:
#
# Targets are shown with a dashed line, combination above and below that are
# either side of the target MM pitch or TPI
import sys

do_inches = True    # Use TPI instead of mm pitch, different targets for imperial screws.
ShowTargetsOnly = True # Show only entries either side of a target
KeepDuplicates = False # Show all combinations, even ones with the same ratio

gears_have = [80,80,72,66,60,52,50,      40,33,24,20] # Gears included with vevor lathe
#gears_have =  [80,80,72,66,60,52,50,49,44,40,33,24,20]  # With extra gears that I made.

# Gears included with vevor lathe plus unique ones from the 27 pc Vevor metal gear set
#gears_have = [80,80,72,66,65,60,57,55,54,52,50,48,45,40,35,33,30,25,24,20] 

if do_inches:
    targets = [10,11,12,13,14,16,18,20,24,27,28,32,40,44] # From tap and die set
    label = "tpi"
else:
    targets = [0.5,0.7,0.8,1,1.5,1.75,2,2.5,3] # Target MM pitches
    label = "mm"

leadscrew_pitch = 2

# My Vevor lathe has five gears that can be swapped.
# For many lathes, the inermediate post 2 has fixed gearing to the spindle, so
# only gears 0-3 can be changed, but on this one I can swap five gears (0 to 4)
#
#  +--+------+
#  |SS|      | 
#  |SS|      |
# =|SS|      |==Spindle with 54 tooth gear.
#  |SS|      |
#  |SS|      |
#  +==+------+
#  |44+--+
#  |44|33|
# =|44|33|==Intermediate Post 2
#  |44|33|
#  |44+==+
#  +--+22|
#     |22|
#  +--+22|
#  |11|22|
# =|11|22|==Intermediate Post 1
#  |11|22|
#  +==+22|
#  |00|22|
#  |00|22|
#  |00+--+
#  |00|
# =|00|==Lead screw
#  |00|
#  |00|
#  |00|
#  |00|
#  +==+
#
#  Lead screw gear 0 can be in left or right position
#  Gears on post 1 (gear 1 and 2) be replaced with one single gear
#  Gears on post 2 (gear 3 and 4) be replaced with one single gear
#
#  To avoid interference:
#  Teeth2-Teeth1 < Teeth1-20 or gear 2 hits lead screw shaft.
#  Teeth2-Teeth1+6 > Teeth4-Teeth3 to avoid gear 1 hitting gear 4,
#             Unless a signle gear is used on post 1 or post 2
#  Teeth3 <= Teeth4 to avoid gear 3 hitting the spindle shaft.


#--------------------------------------------------------------------
# Check if gear combination will lead to any sort of interference between
# gears and whether it is likely to fit inside the lathe housing.
#
# For interference calculations, My gears have a diametric pitch of 1 mm,
# which is to say: 
#    pitch_diameter = tooth_count * 1mm
#
# pitch radius is half of that.
#--------------------------------------------------------------------
def check_valid(gears):
    num_used = len(gears)

    if num_used >= 3:
        if gears[2] != gears[1]:
            if gears[2]-gears[1] > gears[0]-23:
                # gear 2 hits the lead screw shaft.
                return False
        else:
            if gears[1] != 1: return False;

    if num_used == 5:
        if gears[3] == gears[4] and gears[3] != 1: return False

        if gears[3] > gears[4]:
            # Gear 3 hits the spindle
            return False

        if gears[4] != gears[3] and gears[2] != gears[1]:
            if gears[2]-gears[1] < gears[4]-gears[3]+6:
                # Gear 4 hits gear 1.
                return False

        width=(gears[0]+gears[1]+gears[2]+gears[3])/2
        if width > 131.5:
            #print("too wide",gears)
            return False # Axle spacing is too wide for the mounting bar
        elif width > 105 and gears[4] == 80:
            # If last gear is 80 tooth and higher up than this, the cover won't close.
            return False;
        
        if width+gears[4]/2 < 138:
            has_anygear = False
            for g in gears:
                if g == 1: has_anygear = True
                
            # May not reach the spindle, though for smallest gear on top,
            # may have to go even higher than this so the gear mounting bar
            # itself doesn't hit the spindle.

            if not has_anygear: return False

    return True # No interference found

#--------------------------------------------------------------------
# Select five gears.
#--------------------------------------------------------------------
def pick_gears(gears_have, gears_used, still_add):
    nused = len(gears_used)

    if still_add == 0:
        if not check_valid(gears_used): return
        #print ("Valid:",now_used)
        gear_ratio = 54.0/gears_used[0]*gears_used[1]/gears_used[2]*gears_used[3]/gears_used[4]
        pitch = gear_ratio*leadscrew_pitch

        gears_str = ""
        for x in range (0,len(gears_used)):
            if x == 1 or x == 3: gears_str = gears_str+"  "
            g = gears_used[x]
            if g == 1:
                gears_str += "Any,"
            else:
                gears_str += "%3d,"%(g)

        # for TPI intead of mm pitch:
        if do_inches:
           pitch = 25.4/pitch

        global sequence
        sequence += 1;
        OutStr = "%8.4f,  "%(pitch) +"%5d,"%(sequence) +gears_str
        #print(OutStr)
        global gear_combos
        gear_combos = gear_combos + [OutStr]
        return


    if (nused == 1 or nused == 3) and still_add >= 2:
        # Try Single gear on post, number of teeth doesn't matter.
        # We can use any remaining gears, so it doesn't use up a gear.
        now_used = gears_used+[1,1]
        pick_gears(gears_have, now_used, still_add-2)

    for gn in range (0,len(gears_have)):
        now_used = gears_used+[gears_have[gn]]
        gears_remaining = gears_have[0:gn] + gears_have[gn+1:]
        pick_gears(gears_remaining, now_used, still_add-1)

gear_combos = []
sequence = 0;

pick_gears(gears_have, [],5)
gear_combos.sort()


target = targets.pop(0)
target_index = 0

prev_pitch="0"
unique_ratios = 0

def ShowGearsEntry(p, target=0):
    err_str = ""
    if target:
        pitch = float(p[:8])
        err = (pitch-target)/target*100
        err_str = "  E=%6.3f%%"%(err)

    print (p[:10]+p[17:]+err_str)


print ("\nGear threading table, Lead screw gear first, gear engaging spindle last")
print ("'E=' indicates % error from target pitch value\n")
for i,g in enumerate(gear_combos):
    if prev_pitch != g[:8] or KeepDuplicates:
        unique_ratios += 1
        prev_pitch = g[:8]

        pitch = float(g[:8])
        if pitch > target:
            if i > 0 and ShowTargetsOnly:
                ShowGearsEntry(gear_combos[i-1],target)

            print("--------", target, label, "--------");

            if ShowTargetsOnly:
                ShowGearsEntry(g, target)
                print ("")

            if targets:
                target = targets.pop(0)
            else:
                target = 10000


        if not ShowTargetsOnly: ShowGearsEntry(g)

print ("Total gear combinations (including duplicates):",len(gear_combos))
print ("Total gear ratios:",unique_ratios)
