import re


class Combo:
    def __init__(self, moves, preserves_vt=False):
        self.preserves_vt = preserves_vt
        self.moves = moves
        self.bars_spent = 0
        for move in self.moves:
            if move.is_EX:
                self.bars_spent += 1
            elif move.is_super:
                self.bars_spent += 3

    def damage(self, counterhit=False, life=1000, max_life=1000, scaling=1):
        total_damage = 0
        damages = []
        for move in self.moves:
            move_life_damage, move_stun_damage = move.damage(scaling, counterhit=counterhit, life=life,
                                                             max_life=max_life)
            total_damage += move_life_damage
            life -= move_life_damage
            damages.append(total_damage)
            scaling -= .1
        return total_damage, damages

    def __str__(self):
        return ','.join(move.name for move in self.moves)


def combo_filter(list_of_combos, move_rules, max_bars=3):
    filtered_list_of_combos = []
    for combo in list_of_combos:
        if combo.bars_spent > max_bars:
            continue
        for move_rule in move_rules:
            if re.search(move_rule, str(combo)) is not None:
                break
            if re.search(move_rule, str(combo).replace(',VT,', '')) is not None:
                break
        else:
            filtered_list_of_combos.append(combo)
    return filtered_list_of_combos


def generate_combos(character, max_length=5, max_bars=3, have_vt=False):
    combos = []
    vt = next(x for x in character.moves if x.name == 'VT')
    for l in range(1, max_length + 1):
        combos_of_length_l = []
        for move in character.moves:
            if l == 1:
                combos_of_length_l.append(Combo([move], preserves_vt=True))
            else:
                for c in combos_of_length_l_minus_1:
                    last_move = c.moves[-1]
                    if \
                                            move.startup < last_move.adv_on_hit or \
                                    (
                                                    last_move.is_special_cancellable and
                                                    move.is_special_move and
                                                    move.startup < last_move.adv_on_cancel
                                    ) \
                            :
                        combos_of_length_l.append(Combo(c.moves + [move]))
                    elif last_move.is_vt_cancellable and have_vt and c.preserves_vt and vt.startup + move.startup < last_move.adv_on_cancel:
                        combos_of_length_l.append(Combo(c.moves + [vt, move], preserves_vt=False))


        combos_of_length_l = combo_filter(combos_of_length_l, character.move_rules, max_bars=max_bars)
        combos.extend(combos_of_length_l)
        combos_of_length_l_minus_1 = combos_of_length_l
    combos.sort(key=lambda x: x.damage()[0])

    for x in combos: print x, x.damage()[0]
    print len(combos)


class Move:
    def __init__(self, name, life_damages, startup, adv_on_block, adv_on_hit,
                 stun_damages=None,
                 critical_art=False,
                 is_EX = False,
                 adv_on_cancel=None,
                 is_special_move=False,
                 is_special_cancellable=False,
                 is_vt_cancellable=False,
                 vt_version=None):
        self.name = name
        self.startup = startup
        self.life_damages = life_damages
        self.adv_on_block = adv_on_block
        self.adv_on_hit = adv_on_hit
        self.is_special_cancellable = is_special_cancellable
        self.is_vt_cancellable = is_vt_cancellable
        self.vt_version = vt_version
        # self.adv_on_ch = adv_on_ch
        self.is_special_move = is_special_move
        if adv_on_cancel is None:
            self.adv_on_cancel = self.adv_on_hit
        else:
            self.adv_on_cancel = adv_on_cancel
        if stun_damages is None:
            self.stun_damages = [0 for _ in life_damages]
        else:
            self.stun_damages = stun_damages
        self.is_super = critical_art
        self.is_EX = is_EX

    def damage(self, hit_scaling, counterhit=False, life=1000, max_life=1000):
        if hit_scaling < .1:
            hit_scaling = .1
        if hit_scaling < .5 and self.is_super:
            hit_scaling = .5
        hits = self.life_damages
        total_life_damage = 0
        total_stun_damage = 0
        first_hit = True
        for hit_life_damage, hit_stun_damage in zip(self.life_damages, self.stun_damages):
            if life / max_life < .1:
                life_scaling = .75
            elif life / max_life < .25:
                life_scaling = .9
            elif life / max_life < .5:
                life_scaling = .95
            else:
                life_scaling = 1
            if counterhit and hit_scaling == 1 and first_hit:
                hit_life_damage = round(hit_life_damage * 1.2)
                hit_stun_damage = round(hit_stun_damage * 1.2)
            first_hit = False
            scaled_life_damage = round(hit_scaling * life_scaling * hit_life_damage)
            scaled_stun_damage = round(hit_scaling * hit_stun_damage)
            total_life_damage += scaled_life_damage
            life -= scaled_life_damage
            total_stun_damage += scaled_stun_damage
        return total_life_damage, total_stun_damage


class Character:
    def __init__(self):
        self.combos = dict()
        self.moves = list()
        self.VT_moves = list()
        self.move_rules = list()

    def add_combo(self, name, move_names):
        moves = [self.moves[move_name] for move_name in move_names]
        self.combos[name] = Combo(moves)
        return self.combos[name]


# adv on cancel are all estimates based on the longest special you can cancel into
# verify with V-trigger cancels

Chun_Li = Character()
for move in [
    Move('sLP', [30], 3, 2, 5, is_special_cancellable=True, adv_on_cancel=14, is_vt_cancellable=True),
    Move('sMP', [60], 4, 3, 6, is_special_cancellable=True, adv_on_cancel=15, is_vt_cancellable=True),
    Move('sHP', [80], 10, -3, 0),
    Move('sLK', [40], 3, -3, 1, is_special_cancellable=True, adv_on_cancel=11, is_vt_cancellable=True),
    Move('sMK', [60], 7, -2, 2),
    Move('sHK', [90], 11, -2, 1, is_vt_cancellable=True),
    Move('cLP', [20], 2, 2, 5, is_special_cancellable=True, adv_on_cancel=11, is_vt_cancellable=True),
    Move('cMP', [60], 9, -8, -3),
    Move('cHP', [60, 40], 6, -5, 2),
    Move('cHP_1hit', [60], 6, 0, 0, is_special_cancellable=True, adv_on_cancel=22, is_vt_cancellable=True),
    Move('cLK', [20], 2, -1, 1),
    Move('cMK', [50], 5, -2, 0, is_special_cancellable=True, adv_on_cancel=15, is_vt_cancellable=True),
    Move('cHK', [100], 6, -12, 0),
    Move('hands', [90], 6, 2, 3, is_special_cancellable=True, adv_on_cancel=15, is_vt_cancellable=True),
    Move('upkick', [70], 6, 0, 2),
    Move('poke', [60], 6, 0, 2),
    Move('spinkick', [80], 17, -2, 2),
    Move('legs_LK', [20] * 4, 4, -8, 3, is_special_move=True),
    Move('legs_MK', [20] * 5, 9, -9, 2, is_special_move=True),
    Move('legs_HK', [20] * 6, 13, -10, 1, is_special_move=True),
    Move('legs_EX', [10] * 9 + [50], 4, -2, 0, is_special_move=True, is_EX=True),
    Move('kikou_LP', [60], 12, -6, 0, is_special_move=True),
    Move('kikou_MP', [60], 10, -5, -1, is_special_move=True),
    Move('kikou_HP', [60], 8, -4, -2, is_special_move=True),
    Move('kikou_EX', [50] * 2, 10, 1, 4, is_special_move=True, is_EX=True),
    Move('SBK_LK', [20] * 4 + [40], 8, -6, 0, is_special_move=True),
    Move('SBK_MK', [25] + [15] * 5 + [40], 14, -8, 0, is_special_move=True),
    Move('SBK_HK', [10] + [15] * 7 + [45], 21, -10, 0, is_special_move=True),
    Move('SBK_EX', [30] * 4 + [50], 4, -12, 0, is_special_move=True, is_EX=True),
    Move('VT', [0], 4, 0, 0),
    Move('CA', [30] + [20] + [5] * 34 + [120], 4, 0, 0, critical_art=True)

    # Move('VT_cHP', [55, 5, 5, 35, 5, 5]),
    # Move('VT_cHP_1hit', [55, 5, 5]),
    # Move('VT_cLP', [30]),
    # Move('VT_cMK', [55, 5]),
    # Move('VT_hands', [90, 5, 5],),
    # jLP
    # jMP,
    # Move('jHP', [50] * 2),
    # Move('VT_jHP', [45, 5, 5, 45, 5, 5]),
    # Move('VT_jHP_4hits', [45, 5, 5, 45]),
    # jLK
    # jMK
    # jHK
    # Move('toe_taps1', [40]),
    # Move('toe_taps2', [50]),
    # Move('toe_taps3', [60]),
    # Move('VT_toe_taps1', [45, 5]),
    # Move('VT_toe_taps2', [55, 5]),
    # Move('VT_toe_taps3', [65, 5]),
    # Move('VT_legs_LK', [20, 20, 20, 30]),
    # Move('VT_legs_EX', [10] * 9 + [60]),
    # Move('legs_2hits', [20] * 2),
    # Move('jlegs_LK', [20] * 4),
    # Move('jlegs_MK', [20] * 5),
    # Move('jlegs_HK', [20] * 6),
    # Move('VT_jlegs_HK', [20, 20, 30, 20, 20, 20]),
    # Move('jlegs_EX', [25] * 7),
    # Move('VT_jlegs_EX', [25] + [35] + [25] * 5),
    # Move('VT_kikou_LP', [60]),
    # Move('VT_kikou_MP', [60]),
    # Move('VT_kikou_HP', [60]),
    # Move('VT_kikou_EX', [50, 70]),
    # Move('VT_SBK_LK', [20] * 4 + [50]),
    # Move('VT_SBK_MK', [25] + [15] * 5 + [50]),
    # Move('VT_SBK_HK', [10] + [15] * 7 + [55]),
    # Move('VS', [40]),
    # Move('VT_VS', [50]),
    # Move('VT_VS', [50])
]:
    Chun_Li.moves.append(move)

for move_rule in [
    # pushback
    'sMP,sMP',
    'sMP,cLP',
    'cLP,sMP,sLP',
    'cLP,sMP,cLK',
    'sLP,sMP,sLP',
    'sLP,sMP,sLK',
    'sLP,sMP,cLK',
    'sLP,sMP,cMK',
    'sMP,sLP,sLP',
    'sMP,sLP,sMP',
    'sMP,sLP,sLK',
    'sMP,sLP,cLP',
    'sMP,sLP,cLK',
    'cLP,sMP,sLK',
    'sLP,sLP,sMP',
    'sLP,cLP,sMP',
    'cLP,sLP,sMP',
    'hands,cLP',
    'hands, cLK',
    'cLP,sMP,SBK_EX',
    'sLP,sMP,SBK_EX',
    'sMP,cMK,SBK_EX',
    'hands,legs_LK,cLP',
    'legs_LK,cLP,sMP',
    'sMP,cMK,legs_LK,cLP',
    'legs_LK,cLP,legs_LK,cLP',
    'sMP,legs_LK,cLP',
    'cHP_1hit,legs_LK,cLP,sLK',
    'sMP,sLK,legs_LK,cLP',
    'sMP,sLP,legs_LK,cLP',
    'cHP_1hit,legs_LK,cLP,sLP',
    'legs_LK,cLP,cLP',
    'legs_LK,cLP,sLP',
    'cMK,legs_LK,cLP,sLK',
    'sLP,sLK,legs_LK,cLP',
    'sLP,legs_LK,cLP',
    'hands,VT,cHP_1hit,legs_LK,cLP',
    'hands,VT,hands',
    'hands,VT,cMK,legs_LK,cLP',
    'hands,VT,sMP',
    'hands,VT,sLK,legs_LK,cLP',
    'sMP,VT,cHP_1hit,legs_LK,cLP',
    'cHP_1hit,VT,cMK,legs_LK,cLP',
    'sMP,VT,hands',
    'hands,kikou_EX,sLK,legs_LK,cLP',
    'hands,VT,sLP,sLP',
    # charge
    'sMP,sLP,SBK_EX',
    'kikou_EX,sLP,SBK_LK',
    'kikou_EX,sLP,SBK_EX',
    'kikou_EX,sLP,kikou_EX',
    'kikou_EX,sLK,SBK_EX',
    'kikou_EX,cLP,SBK_EX',
    'kikou_EX, sLK, SBK_LK',
    'kikou_EX,sLK,SBK_EX',
    'kikou_EX,cLP,SBK_EX'
    'legs_LK,cLP,SBK_EX',
    'sMP,sLK,SBK_EX',
    'sLP,sMP,SBK_MK'

]:
    Chun_Li.move_rules.append(move_rule)
Guile = Character()
# for name, move in [
#     Move('LP', [30], stun_damages=[70]),
#     Move('MP', [60], stun_damages=[100]),
#     Move('HP', [80], stun_damages=[150]),
#     Move('LK', [30], stun_damages=[70]),
#     Move('MK', [60], stun_damages=[100]),
#     Move('HK', [80], stun_damages=[150]),
#     Move('cLP', [30], stun_damages=[100]),
#     Move('cMP', [60], stun_damages=[150]),
#     Move('cHP', [90], stun_damages=[70]),
#     Move('cLK', [20], stun_damages=[100]),
#     Move('cMK', [60], stun_damages=[150]),
#     Move('cHK', [90], stun_damages=[90]),
#     Move('cHK_2nd_hit', [70], stun_damages=[100]),
#     Move('jLP', [40], stun_damages=[70]),
#     Move('jMP', [70], stun_damages=[100]),
#     Move('jHP', [90], stun_damages=[150]),
#     Move('jLK', [40], stun_damages=[70]),
#     Move('jMK', [60], stun_damages=[100]),
#     Move('jHK', [90], stun_damages=[150]),
#     Move('sonic_boom_LP', [50], stun_damages=[50]),
#     Move('sonic_boom_MP', [50], stun_damages=[50]),
#     Move('sonic_boom_HP', [50], stun_damages=[50]),
#     Move('sonic_boom_EX', [50] * 2, stun_damages=[50, 50]),
#     Move('flash_kick_LK', [120], stun_damages=[200]),
#     Move('flash_kick_MK', [120], stun_damages=[200]),
#     Move('flash_kick_HK', [120], stun_damages=[200]),
#     Move('flash_kick_EX', [90, 60], stun_damages=[100, 100]),
#     Move('flash_kick_LK_late_hit', [90], stun_damages=[200]),
#     Move('flash_kick_MK_late_hit', [90], stun_damages=[200]),
#     Move('flash_kick_HK_late_hit', [90], stun_damages=[200]),
#     Move('flash_kick_EX_late_hit', [60, 60], stun_damages=[100, 100]),
#     Move('CA', [40, 40, 40, 40, 40, 120], critical_art=True),
#     Move('CA_VT', [18] * 14 + [108], critical_art=True),
#     Move('VS', [40]),
#     Move('VT', [0])
# ]:
#     Guile.moves[name] = move

# Nash = Character()
# for name, move in [
#     Move('LP', [30], stun_damages=[70]),
#     Move('MP', [60], stun_damages=[100]),
#     Move('HP', [90], stun_damages=[150]),
#     Move('LK', [30], stun_damages=[70]),
#     Move('MK', [60], stun_damages=[100]),
#     Move('HK', [80], stun_damages=[150]),
#     Move('cLP', [30], stun_damages=[70]),
#     Move('cMP', [60], stun_damages=[100]),
#     Move('cHP', [80], stun_damages=[750]),
#     Move('cLK', [20], stun_damages=[70]),
#     Move('cMK', [50], stun_damages=[100]),
#     Move('cHK', [100], stun_damages=[750]),
#     Move('jLP', [40], stun_damages=[70]),
#     Move('jMP', [70], stun_damages=[100]),
#     Move('jHP', [90], stun_damages=[150]),
#     Move('jLK', [40], stun_damages=[70]),
#     Move('jMK', [60], stun_damages=[100]),
#     Move('jHK', [90], stun_damages=[150]),
#     Move('njHK', [90], stun_damages=[150]),
#
#     Move('Sonic Scythe LK', [80], stun_damages=[100]),
#     Move('Sonic Scythe MK', [100], stun_damages=[100]),
#     Move('Sonic Scythe HK', [80, 40], stun_damages=[100, 100]),
#     Move('Sonic Scythe EX', [30] * 5, stun_damages=[30, 30, 30, 30, 80]),
#     (Move('CA', [35] * 9 + [25])
# ]:
# Nash.moves[name] = move
#
# print combo_damage([HP,VT,VT_VS,VT_toe_taps1,VT_toe_taps2,VT_toe_taps3,VT_jHP_4hits,CA],1,counterhit = True)
# print combo_damage([HK,VT,VT_VS,VT_toe_taps1,VT_toe_taps2,VT_toe_taps3,VT_jHP_4hits,CA],1,counterhit = True)
# Chun_Li.add_combo('super confirm 1',
#                   ['MP', 'MK', 'CA'])
# Chun_Li.add_combo('super confirm 3',
#                   ['HP', 'CA'])
# Chun_Li.add_combo('super confirm 4',
#                   ['MP', 'MK', 'legs_2hits', 'CA'])
# Chun_Li.add_combo('super punish 1',
#                   ['cHP_1hit', 'legs_LK', 'cLP', 'legs_2hits', 'CA'])
# Chun_Li.add_combo('super punish 2',
#                   ['hands', 'kikou_LP', 'CA'])
# Chun_Li.add_combo('super punish 3',
#                   ['hands', 'CA'])
# Chun_Li.add_combo('CA off DP 1',
#                   ['HK', 'HP', 'CA'])
# Chun_Li.add_combo('CA off DP 2',
#                   ['HK', 'cMK', 'legs_LK', 'cLP', 'legs_2hits', 'CA'])
# Chun_Li.add_combo('CA off DP 3',
#                   ['HK', 'cMK', 'legs_LK', 'cLP', 'CA'])
# Chun_Li.add_combo('CA off DP 4',
#                   ['HK', 'cMK', 'legs_2hits', 'CA'])
# Chun_Li.add_combo('CA off DP 5',
#                   ['MP', 'cMK', 'CA'])
# Chun_Li.add_combo('CA off DP 6',
#                   ['HK', 'MP', 'cMK', 'CA'])
# Chun_Li.add_combo('CA off DP 7',
#                   ['HK', 'MP', 'cMK', 'legs_2hits', 'CA'])
# Chun_Li.add_combo('DP punish 1',
#                   ['HK', 'cMK', 'legs_LK', 'cLP', 'SBK_LK'])
# Chun_Li.add_combo('DP punish 2',
#                   ['HK', 'MP', 'cMK', 'SBK_MK'])
#
generate_combos(Chun_Li, max_bars=4, max_length=6, have_vt=True)

# print combo_damage([jHP, hands, kikou_EX, poke, VT, VT_hands, VT_SBK_HK], 1)
# Nash.add_combo('derp', ['jHK', 'cMP', 'MP', 'Sonic Scythe MK', 'CA'])
