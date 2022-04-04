import game

w = game.Window()
bg = game.Image(w, './assets/Img/Background/H3.png', (0, 0))
w.add(bg)
g = game.Game(w)
g.start()

while True:
    g.update()
