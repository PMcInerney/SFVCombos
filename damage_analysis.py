import matplotlib.pyplot as plt
import combo_tool

# for char, color in [(combo_tool.Chun_Li, 'blue'), (combo_tool.Guile, 'green'), (combo_tool.Nash, 'brown')]:
# for char, color in [(combo_tool.Chun_Li, 'blue'), (combo_tool.Nash, 'brown')]:
#     c = char.moves['CA']
#     xs = range(1001)
#     for scaling in [1, .9, .8, .7, .6, .5]:
#         ys = [c.damage(scaling, life=x)[0] for x in xs]
#         plt.plot(xs, ys, color)
for combo_name in [
    # 'super confirm 1',
    # 'super confirm 3',
    # 'super confirm 4',
    # 'super punish 1',
    # 'super punish 2',
    # 'super punish 3'
    # 'CA off DP 1',
    # 'CA off DP 7',
    # 'CA off DP 6'
    'DP punish 1',
    'DP punish 2'
]:
    c = combo_tool.Chun_Li.combos[combo_name]
    print c.damage(counterhit=True)
    xs = range(1001)
    ys = [c.damage(life=x, counterhit=True)[0] for x in xs]
    print ys[-1]
    plt.plot(xs, ys, label = combo_name)
    plt.legend()

for line_y in range(0, 500, 10):
    ys = [line_y for _ in xs]
    plt.plot(xs, ys, 'grey')

xs = range(400)
ys = xs
plt.plot(xs, ys, 'k')

plt.show()
