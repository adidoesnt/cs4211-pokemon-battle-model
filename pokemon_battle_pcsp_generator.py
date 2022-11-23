import os
import pandas as pd
import math
import random

def remove_old_model(csp_filename):
    if os.path.exists(csp_filename):
        os.remove(csp_filename)
        print("Old model removed")

# Returns an array of that pokemon's moveset
def get_moves(pokemon, team_df):
    moves = ['move1', 'move2', 'move3', 'move4']
    pokemon_moves = []
    for move in moves:
        pokemon_moves.append(team_df.loc[team_df['pokemon'] == pokemon][move].values[0])
    return pokemon_moves

# Returns an array with the move info
# Index info corresponds to -> 0: Type, 1: Power, 2: Acc., 3:Effect
# Effect is used to check for High critical hit ratio moves only
def get_move_info(move, moves_df):
    info_names = ['Type', 'Power', 'Acc.', 'Damage_class', 'Effect']
    info_values = []

    for info in info_names:
            info_values.append(moves_df.loc[moves_df['Name'] == move][info].values[0])
    return info_values

def get_pokemon_stats(pokemon, team_df):
    stat_name_list = ['attack', 'defense', 'sp. attack', 'sp. defense']
    stats = []
    for stat in stat_name_list:
        stats.append(team_df.loc[team_df['pokemon'] == pokemon][stat].values[0])
    return stats

# Returns a list of lists
# List of pokemon
# Each pokemon is a list of its attributes
def get_trainer_pokemon_data(team_df, pokemon_df):
    pokemon_list = []
    for pokemon_name in team_df['pokemon']:
        # Add info from provided csv
        pokemon = []
        raw_data = team_df.loc[team_df['pokemon'] == pokemon_name].values[0]
        for i in range(7):
            pokemon.append(raw_data[i])
        moves = []
        for i in range(7, len(raw_data)):
            moves.append(raw_data[i])
        pokemon.append(moves)

        # Get pokemon type from database csvs
        types = []
        for i in range(1,3):
            type_name = pokemon_df.loc[pokemon_df['Name'] == pokemon_name]['Type' + str(i)].values[0]
            if(isinstance(type_name, str)):
                types.append(type_name)
        pokemon.append(types)
        pokemon_list.append(pokemon)

    return pokemon_list

def get_hp(trainerPokemons, trainer, pokemon):
    return trainerPokemons[trainer][pokemon][2]

def get_type_effectiveness_multiplier(move_type, pokemon, type_vs_type_df):
    pokemon_types = pokemon[8]
    multiplier = 1
    for def_type in pokemon_types:
        next_mult = (type_vs_type_df.loc[
            (type_vs_type_df['Atk. Move Type'] == move_type) & 
            (type_vs_type_df['Def. Pokemon Type'] == def_type)
            ]
            ['Damage Multiplier'].values[0])
        if(not math.isnan(next_mult)):
            multiplier = multiplier * next_mult
    return multiplier

def get_damage_without_crit(atk_pokemon, def_pokemon, move_info, type_effectiveness_multiplier):
    atk_stat = atk_pokemon[5] if (move_info[3] == 'Special') else atk_pokemon[3]
    def_stat = def_pokemon[6] if (move_info[3] == 'Special') else def_pokemon[4]
    atk_level = atk_pokemon[1]

    
    # Same type attack bonus
    STAB = 1
    for type_name in atk_pokemon[8]:
        if(move_info[0] == type_name):
            STAB = 1.5

    random_int = random.randint(85, 100) / 100

    damage = (((((2 * atk_level / 5) + 2) * move_info[1] * (atk_stat / def_stat))
            / 50) * 
            STAB * type_effectiveness_multiplier * random_int)
    
    
    
    return round(damage)

def get_probability(rank):
    probability = 1
    if(rank == 3):
        return 0.9
    elif(rank == 2):
        return 0.06
    elif(rank == 1):
        return 0.03
    else:
        return 0.01

# Returns an array of floats as probabilities
# [chance of miss, chance of hit and hit is non critical, chance of hit and hit is critical]
def get_move_hit_probabilities(acc, is_high_crit):
    high_crit_probability = 0.125
    normal_crit_probability = 0.0664
    hit_probability = acc / 100

    if(is_high_crit):
        chance_of_normal_hit = round(hit_probability * (1 - high_crit_probability), 2)
        chance_of_crit_hit = round(hit_probability * high_crit_probability, 2)
    else:
        chance_of_normal_hit = round(hit_probability * (1 - normal_crit_probability), 2)
        chance_of_crit_hit = round(hit_probability * normal_crit_probability, 2)
    
    chance_of_miss = round(1 - chance_of_crit_hit - chance_of_normal_hit, 2)

    return [chance_of_miss, chance_of_normal_hit, chance_of_crit_hit]

def is_high_crit_ratio(move, moves_df):
    effect = moves_df.loc[moves_df['Name'] == move]['Effect'].values[0]
    if(not isinstance(effect, str)):
        return False
    else:
        return "High critical hit ratio" in effect

def write_defines(file):
    file.write('#define active 1; //trainer active\n')
    file.write('#define inactive 0; //trainer inactive\n')
    file.write('#define win 2; // trainer wins\n')
    file.write('#define lose -1; //trainer loses\n')

def write_initial_states(file):
    file.write("var trainer[2] = [active, inactive]; //initial trainer states\n")
    file.write("var currentPokemon[2] = [0, 0]; // index of trainers current pokemon\n")

def write_rotate(file):
    rotate_state = "rotate() = \n\
        [trainer[0] == active && trainer[1] == inactive]switchTrainer{trainer[0] = inactive; trainer[1] = active} -> move(1)\n\
        []\n\
        [trainer[1] == active && trainer[0] == inactive]switchTrainer{trainer[1] = inactive; trainer[0] = active} -> move(0);\n"
    file.write(rotate_state)


def write_switch(file):
    switch = ("switch(i, c) =\n" + 
              "\t[i == 1]sendPokemon.i{if (trainer1HealthStats[c] <= 0) {currentPokemon[i] = c + 1}} -> end()\n" +
              "\t[]\n" +
              "\t[i == 0]sendPokemon.i{if (trainer0HealthStats[c] <= 0) {currentPokemon[i] = c + 1}} -> end();\n")
    file.write(switch)


def write_start(file):
    start = ("start() = \n" +
	"\ttrainer0start{trainer[0] = active; trainer[1] = inactive} -> move(0)\n" +
	"\t[]\n" +
	"\ttrainer1start{trainer[1] = active; trainer[0] = inactive} -> move(1);\n")
    file.write(start)

def write_simulate_assert(file):
    simulate = ("simulate = start();\n" +
    "\n" +
    "#define trainer0wins (trainer[0] == win && trainer[1] == lose);\n" +
    "#define trainer1wins (trainer[1] == win && trainer[0] == lose);\n" +
    "#define bothtrainerswin (trainer[0] == win && trainer[1] == win);\n" +
    "#define bothtrainerslose (trainer[0] == lose && trainer[1] == lose);\n" +
    "\n" +
    "#assert simulate reaches trainer0wins;\n" +
    "#assert simulate reaches trainer1wins;\n" +
    "#assert simulate reaches bothtrainerswin;\n" +
    "#assert simulate reaches bothtrainerslose;\n"
    "#assert simulate reaches trainer0wins with prob;\n"
    "#assert simulate reaches trainer1wins with prob;\n")

    file.write(simulate)

def write_comment(file, line):
    file.write("// " + str(line) + "\n")


def write_team_composition_comment(file, teams_df_list):
    for i in range(2):
        trainer = "trainer" + str(i)
        pokemons = teams_df_list[i]['pokemon']

        write_comment(file, trainer + "'s team:")
        for pokemon in pokemons:
            write_comment(file, pokemon)
            
            # Write pokemon stats
            stats = get_pokemon_stats(pokemon, teams_df_list[i])
            stat_line = ""
            stat_name_list = ['attack', 'defense', 'sp. attack', 'sp. defense']
            for j in range(4):
                stat_line = stat_line + stat_name_list[j] + ": " + str(stats[j]) + " "
            stat_line = stat_line[:-1]
            write_comment(file, "\t" + stat_line)

            moves = get_moves(pokemon, teams_df_list[i])
            for move in moves:
                move_info = get_move_info(move, moves_df)
                info_names = ['Type', 'Power', 'Acc.', 'Effect']
                move_info_line = ""
                for j in range(4):
                    move_info_line = move_info_line + info_names[j] + ": " + str(move_info[j]) + " "
                move_info_line = "\t" + move_info_line[:-1]
                write_comment(file, "\t{0:<15}{1}".format(move, move_info_line))
        file.write("\n")

def write_health_stats(file, trainerPokemons):
    for i in range(2):
        trainerHealthStats = ("var trainer{0}HealthStats[" + str(len(trainerPokemons[i])) + "] = [").format(str(i))
        for pokemon in trainerPokemons[i]:
            hp = pokemon[2]
            trainerHealthStats = trainerHealthStats + str(hp) + ", "
        trainerHealthStats = trainerHealthStats[:-2]
        trainerHealthStats = trainerHealthStats + "];\n"
        file.write(trainerHealthStats)


def write_damage_pcase_line(file, probability, i, trainer):
    if (probability == 0):
        return
    
    if (i == 0):
        process = "missFoe"
        damage = 0
    elif (i == 1):
        process = "hitFoe"
        damage = "d"
    else:
        process = "criticalHitFoe"
        damage = "(d * 2)"
    

    trainerHealth = "trainer1HealthStats" if (trainer == 0) else "trainer0HealthStats"
    
    line = "        [" + str(probability) + "]: " + process + ".i{" + trainerHealth + "[m] = " + trainerHealth + "[m] - " + str(damage) + "} -> switch(" + str((trainer + 1) % 2) + ", m)\n"
    file.write(line)


def write_move(file, trainerPokemons):
    move = "move(i) = \n"
    for i in range(2):
        for j in range(len(trainerPokemons[(i + 1) % 2])):
            trainer = str(i)
            otherTrainer = str((i + 1) % 2)
            otherTrainerPokemon = str(j)
            move = move + (
                "\t[i == " + trainer + " && currentPokemon[" + otherTrainer + "] == " + otherTrainerPokemon +"]" +
                "attackFoe.i -> attack(i, " + otherTrainerPokemon + ")")
            if (not (i == 1 and j == len(trainerPokemons[(i + 1) % 2]) - 1)):
                move = move + "\n\t[]\n"
    move = move + ";\n"
    file.write(move)

def write_end(file, trainerPokemons):
    end = "end() =\n"
    num_trainer0Pokemon = str(len(trainerPokemons[0]) - 1)
    num_trainer1Pokemon = str(len(trainerPokemons[1]) - 1)
    for i in range(2):
        trainer = str(i)
        otherTrainer = str((i + 1) % 2)
        end = end + (
             "\t[currentPokemon[" + trainer + "] > " + str(len(trainerPokemons[i]) - 1) + "]" +
             "trainer" + otherTrainer + "win{trainer[" + trainer + "] = lose; trainer[" + otherTrainer + "] = win} -> Stop\n" +
             "\t[]\n"
        )
    end = end + (
        "\t[currentPokemon[0] <=" + num_trainer0Pokemon + " && currentPokemon[1] <= " + num_trainer1Pokemon +"] " +
        "rotate();\n"
    )
    file.write(end)

def rank_moves(damage_list):
    rank_list = [-1, -1, -1, -1]
    for i in range(4):
        count = 0
        for j in range(4):
            if(i == j):
                continue
            if(damage_list[i] > damage_list[j]):
                count = count + 1
        rank_list[i] = count
    
    has_duplicates = True
    while(has_duplicates):
        has_duplicates = False
        for i in range(4):
            count = 0
            for j in range(4):
                if(i == j):
                    continue
                if(rank_list[i] == rank_list[j]):
                    count = count + 1
                    has_duplicates = True
            rank_list[i] = rank_list[i] + count
    return rank_list

trainer0TeamInfo_df = pd.read_csv('trainer1.csv')
trainer1TeamInfo_df = pd.read_csv('trainer2.csv')
moves_df = pd.read_csv('df_moves.csv')
pokemon_df = pd.read_csv('df_pokemon.csv')
type_vs_type_df = pd.read_csv('bridge_type_type_MOVE_EFFECTIVENESS_ON_POKEMON.csv')

trainers = ['trainer0', 'trainer1']
moves = ['move1', 'move2', 'move3', 'move4']
NAME = 0
LEVEL = 1
HP = 2
ATK = 3
DEF = 4
SP_ATK = 5
SP_DEF = 6
MOVES = 7 
TYPES = 8


pcsp_filename = "battle_simulator_multiple_pokemon_real_data.pcsp"
remove_old_model(pcsp_filename)

pcsp = open(pcsp_filename, 'w')

# Set up required data
trainerPokemons = []
trainerPokemons.append(get_trainer_pokemon_data(trainer0TeamInfo_df, pokemon_df))
trainerPokemons.append(get_trainer_pokemon_data(trainer1TeamInfo_df, pokemon_df))

# Write team info as comments to pcsp
teams = [trainer0TeamInfo_df, trainer1TeamInfo_df]
write_team_composition_comment(pcsp, teams)

# Write model template
write_defines(pcsp)
pcsp.write("\n")
write_initial_states(pcsp)
pcsp.write("\n")
write_health_stats(pcsp, trainerPokemons)
pcsp.write("\n")
write_rotate(pcsp)
pcsp.write("\n")
write_move(pcsp, trainerPokemons)
pcsp.write("\n")


# Write attack process -> attack(i, m)
pcsp.write("attack(i, m) = ")
for i in range(2):
    for j in range(len(trainerPokemons[i])):
        for k in range(len(trainerPokemons[(i + 1) % 2])):
            pcsp.write("[i == {0} && currentPokemon[i] == {1} && m == {2}]pokemon{1}attack -> pcase ".format(str(i), str(j), str(k)) + "{\n")
            
            atk_pokemon_moves = trainerPokemons[i][j][MOVES]
            atk_pokemon_moves_info = []
            def_pokemon = trainerPokemons[(i + 1) % 2][k]
            atk_pokemon = trainerPokemons[i][j]

            for move in atk_pokemon_moves:
                atk_pokemon_moves_info.append(get_move_info(move, moves_df))

            atk_moves_damage = []
            for move_info in atk_pokemon_moves_info:
                effectiveness = get_type_effectiveness_multiplier(move_info[0], def_pokemon, type_vs_type_df)
                damage = get_damage_without_crit(atk_pokemon, def_pokemon, move_info, effectiveness)
                atk_moves_damage.append(damage)
            
            moves_damage_ranking = rank_moves(atk_moves_damage)
            for l in range(4):
                probability = get_probability(moves_damage_ranking[l])
                pcsp.write("\t[{0}]: damage({1}, {2}, {3}, {4}, m)\n".format(str(probability), str(i), str(j), str(l), str(atk_moves_damage[l])))
            
            if(not(
                i == 1 and 
                j == len(trainerPokemons[i]) - 1 and 
                k == len(trainerPokemons[(i + 1) % 2]) - 1)):
                pcsp.write("\t} [] ")
            else:
                pcsp.write("\t};\n")

pcsp.write("\n")


# Write Damage process
pcsp.write("//i: Trainer j: Trainer pokemon l: pokemon move m: opponent pokemon\n")
pcsp.write("damage(i, j, l, d, m) = \n")

for i in range(2):
    for j in range(len(trainerPokemons[i])):
        for k in range(4):
            pcsp.write("\t[i == {0} && j == {1} && l == {2}]damageFoe.i".format(str(i), str(j), str(k)))
            pcsp.write(" -> pcase {\n")
            move = trainerPokemons[i][j][MOVES][k]
            move_info = get_move_info(move, moves_df)
            move_acc = int(move_info[2]) if (move_info[2].isnumeric()) else 100
            move_is_high_crit = is_high_crit_ratio(move, moves_df)
            move_hit_probabilities = get_move_hit_probabilities(move_acc, move_is_high_crit)

            for l in range(3):
                prob = move_hit_probabilities[l]
                write_damage_pcase_line(pcsp, prob, l, i)

            if(not(
                i == 1 and 
                j == len(trainerPokemons[i]) - 1 and 
                k == 3)):
                pcsp.write("\t}\n")
                pcsp.write("\t[]\n")
            else:
                pcsp.write("\t};\n")
pcsp.write("\n")

write_switch(pcsp)
pcsp.write("\n")
write_end(pcsp, trainerPokemons)
pcsp.write("\n")
write_start(pcsp)
pcsp.write("\n")
write_simulate_assert(pcsp)


pcsp.close()

